import asyncio
import threading
import time

from PyQt5.QtCore import pyqtSignal, QThread

from config import Config
from helpers.GameHelper import GameHelper, AnimationArea
from helpers.ImageLocator import ImageLocator
from helpers.ScreenHelper import ScreenHelper

from models import BidModel
from models import FarmerModel
from models import LandlordModel

from douzero.env.game_new import GameEnv
from douzero.env.move_detector import get_move_type
from douzero.evaluation.deep_agent_new import DeepAgent

from utils import normalize_score

# 玩家位置（0：地主上家，1：地主，2：地主下家）
PlayerPosition = ['landlord_up', 'landlord', 'landlord_down']

AllEnvCard = [3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7, 8, 8, 8, 8, 9, 9, 9, 9, 10, 10, 10, 10, 11, 11, 11, 11, 12, 12, 12, 12, 13, 13, 13, 13, 14, 14, 14, 14, 17, 17, 17, 17, 20, 30]

RealCard2EnvCard = {'3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14, '2': 17, 'X': 20, 'D': 30}

EnvCard2RealCard = {3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: 'T', 11: 'J', 12: 'Q', 13: 'K', 14: 'A', 17: '2', 20: 'X', 30: 'D'}

Bombs = [[3, 3, 3, 3],
         [4, 4, 4, 4],
         [5, 5, 5, 5],
         [6, 6, 6, 6],
         [7, 7, 7, 7],
         [8, 8, 8, 8],
         [9, 9, 9, 9],
         [10, 10, 10, 10],
         [11, 11, 11, 11],
         [12, 12, 12, 12],
         [13, 13, 13, 13],
         [14, 14, 14, 14],
         [17, 17, 17, 17],
         [20, 30]]

def run_async_task_in_thread(loop, future):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(future)

class WorkerThread(QThread):
    # finished_signal = pyqtSignal()

    def __init__(self):
        super(WorkerThread, self).__init__()
        self.config = Config.load()
        self.screenHelper = ScreenHelper()
        self.imageLocator = ImageLocator(self.screenHelper)
        self.gameHelper = GameHelper(self.imageLocator, self.screenHelper)
        self.worker_runing = False              # 线程是否在运行
        self.play_cards_automatically = True   # 是否自动打牌（无需人为操作）
        self.in_game_start_screen = False       # 是否进入开始游戏界面
        self.game_started = False               # 游戏是否已开局
        self.landlord_confirmed = False         # 是否已确认地主
        self.env = None
        self.three_cards = ''                   # 三张底牌
        self.three_cards_env = None
        self.my_position_code = None            # 我的位置（角色）代码（0：landlord_up, 1：landlord, 2：landlord_down）
        self.my_position = None                 # 我的位置（角色）
        self.data_initializing = False          # 是否正在初始化数据（执行 initial_data 函数）
        self.data_initialized = False           # 是否完成数据初始化
        self.play_order = None                  # 出牌顺序（0：我先出牌，1：我的下家先出牌，2：我的上家先出牌）
        self.play_order_of_next = None          # 下一次出牌顺序（0：我，1：我的下家，2：我的上家）
        self.card_playing = False               # 是否在出牌中（已经有人出过牌为 true 否则 false）
        self.my_hand_cards = ''                 # 我的手牌
        self.my_hand_cards_env = None
        self.other_player_cards = None          # 其他玩家的手牌（整副牌减去我的手牌，后续再减掉历史出牌）
        self.other_player_cards_str = None
        self.all_player_card_data = None

        self.right_played_completed = False         # 右侧玩家是否完成一次出牌
        self.left_played_completed = False          # 左侧玩家是否完成一次出牌
        self.my_played_completed = False            # 我是否完成一次出牌
        self.waiting_for_animation_to_end = False   # 是否正在等待动画结束

        self.auto_bidding_in_progress = False
        self.auto_redouble_in_progress = False
        self.round_count = 0

        self.model_path_dict = {
            'landlord': "baselines/resnet/resnet_landlord.ckpt",
            'landlord_up': "baselines/resnet/resnet_landlord_up.ckpt",
            'landlord_down': "baselines/resnet/resnet_landlord_down.ckpt"
        }

        LandlordModel.init_model("baselines/resnet/resnet_landlord.ckpt")

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.run_task())
        finally:
            self.loop.close()

    async def run_task(self):
        self.worker_runing = True
        while self.worker_runing:
            print()
            print("----- WORKER STARTED -----")
            print()

            # 第一次截图，用于获取窗口宽高等数据
            await self.screenHelper.getScreenshot()

            # 检测是否开局
            while self.worker_runing and not self.game_started:
                await self.before_start()
                time.sleep(1.2)

            # 确认地主之后，并且数据尚未初始化
            while self.worker_runing and self.landlord_confirmed and not self.data_initialized:
                # 如果`正在初始化中`或`已初始化完成`，就直接 continue 跳过本次循环
                if self.data_initializing or self.data_initialized:
                    continue

                await self.initial_data()
            
            # 初始化数据之后，并且出牌尚未开始
            while self.worker_runing and self.data_initialized and not self.card_playing:
                await self.run_game()

            await asyncio.sleep(1)
            
            print()
            print("----- WORKER FINISHED -----")
            print()

        # self.finished_signal.emit()

    async def before_start(self):
        print('正在检测是否开局...')

        self.in_game_start_screen = await self.gameHelper.check_if_in_game_start_screen()
        while self.worker_runing and not self.in_game_start_screen:
            if self.play_cards_automatically:
                await self.gameHelper.clickBtn('quick_start_btn')
            print("等待手动进入开始游戏界面...")
            self.in_game_start_screen = await self.gameHelper.check_if_in_game_start_screen()
            time.sleep(1)

        game_started = False
        if self.in_game_start_screen:
            print("您已进入开始游戏界面")

            game_started = await self.gameHelper.check_if_game_started()
            if not game_started:
                print("对局尚未开始")

            while self.worker_runing and not game_started:
                if self.play_cards_automatically:
                    await self.gameHelper.clickBtn('start_game_btn')
                print("等待手动开始对局...")
                game_started = await self.gameHelper.check_if_game_started()
                time.sleep(1)
        
        if game_started:
            print("对局已开始")
            print()
            self.game_started = True

            await self.autoBidding()
            await self.getThreeCards()
            await self.getMyPosition()
            await self.getMyHandCards()
            await self.autoRedouble()

    async def initial_data(self):
        self.data_initializing = True

        print("正在处理本次牌局数据...")
        self.initOtherPlayerHandCards()
        self.initAllPlayerCardData()
        print()

        self.play_order = 0 if self.my_position == "landlord" else 1 if self.my_position == "landlord_up" else 2
        playOrderArr = ['我先出牌', '我的下家先出牌', '我的上家先出牌']
        print('出牌顺序: ', playOrderArr[self.play_order])
        print()

        if self.round_count == 0:
            self.create_ai_representer()
        self.env.card_play_init(self.all_player_card_data)

        self.data_initialized = True
        self.data_initializing = False

    async def run_game(self):
        print('准备就绪，玩家开始出牌...')
        print()
        self.card_playing = True
        self.play_order_of_next = self.play_order

        firstOfRound = True
        while self.worker_runing and self.card_playing:
            if self.waiting_for_animation_to_end:
                continue

            if self.play_order_of_next == 0:
                haveAnimation = await self.gameHelper.haveAnimation(AnimationArea.MY_PLAYED_ANIMATION.value)
                if haveAnimation:
                    self.waiting_for_animation_to_end = True
                    print('等待我的动画结束...')
                    print()
                    time.sleep(0.6)

                self.waiting_for_animation_to_end = False
                await self.getMyPlayedCards(firstOfRound)
            elif self.play_order_of_next == 1:
                haveAnimation = await self.gameHelper.haveAnimation(AnimationArea.RIGHT_PLAYED_ANIMATION.value)
                if haveAnimation:
                    self.waiting_for_animation_to_end = True
                    print('等待右侧动画结束...')
                    print()
                    time.sleep(0.6)

                self.waiting_for_animation_to_end = False
                await self.getRightPlayedCards(firstOfRound)
            elif self.play_order_of_next == 2:
                haveAnimation = await self.gameHelper.haveAnimation(AnimationArea.LEFT_PLAYED_ANIMATION.value)
                if haveAnimation:
                    self.waiting_for_animation_to_end = True
                    print('等待左侧动画结束...')
                    print()
                    time.sleep(0.6)
                
                self.waiting_for_animation_to_end = False
                await self.getLeftPlayedCards(firstOfRound)
                
            firstOfRound = False
            game_overed = await self.gameHelper.check_if_game_overed()
            if game_overed:
                self.round_count += 1
                self.reset_status()
                self.reset_ai_env()
                print('本轮对局已结束')
                print()

    def reset_status(self):
        self.in_game_start_screen = False
        self.game_started = False
        self.landlord_confirmed = False
        self.three_cards = ''
        self.three_cards_env = None
        self.my_position_code = None
        self.my_position = None
        self.data_initializing = False
        self.data_initialized = False
        self.play_order = None
        self.play_order_of_next = None
        self.card_playing = False
        self.my_hand_cards = ''
        self.my_hand_cards_env = None
        self.other_player_cards = None
        self.other_player_cards_str = None
        self.all_player_card_data = None

    def stop_task(self):
        self.worker_runing = False
        self.round_count = 0
        self.reset_status()
        print("正在停止工作线程...")
    
    async def getThreeCards(self):
        print("正在识别三张底牌...")

        while self.worker_runing and len(self.three_cards) != 3:
            self.three_cards = await self.gameHelper.get_three_cards()
            time.sleep(0.2)

        self.three_cards_env = [RealCard2EnvCard[c] for c in list(self.three_cards)]

        print(f"三张底牌：{self.three_cards}")
        print()

    async def getMyPosition(self):
        print("正在识别我的角色...")

        while self.worker_runing and self.my_position_code is None:
            self.my_position_code = await self.gameHelper.get_my_position()
            time.sleep(0.2)

        self.my_position = PlayerPosition[self.my_position_code]

        print("我的角色：", self.my_position)
        print()

    async def getMyHandCards(self):
        print("正在识别我的手牌...")

        success = False
        self.my_hand_cards = await self.gameHelper.get_my_hand_cards()
        if self.my_position_code == 1:
            while self.worker_runing and len(self.my_hand_cards) != 20 and not success:
                self.my_hand_cards = await self.gameHelper.get_my_hand_cards()
                success = len(self.my_hand_cards) == 20
                time.sleep(0.2)

            self.my_hand_cards_env = [RealCard2EnvCard[c] for c in list(self.my_hand_cards)]
        else:
            while self.worker_runing and len(self.my_hand_cards) != 17 and not success:
                self.my_hand_cards = await self.gameHelper.get_my_hand_cards()
                success = len(self.my_hand_cards) == 17
                time.sleep(0.2)

            self.my_hand_cards_env = [RealCard2EnvCard[c] for c in list(self.my_hand_cards)]

        print("我的手牌：", self.my_hand_cards)
        print()

    def initOtherPlayerHandCards(self):
        self.other_player_cards = []
        self.all_player_card_data = {}

        for i in set(AllEnvCard):
            # 对于每一张牌（i），计算它在整副牌 AllEnvCard 中出现的次数，减去玩家手牌中该牌出现的次数，即为其他玩家手牌中该牌的数量
            self.other_player_cards.extend([i] * (AllEnvCard.count(i) - self.my_hand_cards_env.count(i)))

        # 将 self.other_player_hand_cards 中的 env牌编码转换为实际的牌面字符，并将它们组合成一个字符串，最后将其反转
        self.other_hands_cards_str = str(''.join([EnvCard2RealCard[c] for c in self.other_player_cards]))[::-1]

    def initAllPlayerCardData(self):
        # 这里将牌局的相关数据更新到 self.all_player_card_data 中，包括底牌和每个角色的手牌
        self.all_player_card_data.update({
            'three_landlord_cards':
                self.three_cards_env,
            PlayerPosition[(self.my_position_code + 0) % 3]:
                self.my_hand_cards_env,
            # 上家和下家的手牌是从 self.other_player_hand_cards 中截取的前 17 张和后 17 张牌
            # 具体分配逻辑根据玩家的角色编码 self.my_position_code 和取模操作 (self.my_position_code + n) % 3 决定
            PlayerPosition[(self.my_position_code + 1) % 3]:
                self.other_player_cards[0:17] if (self.my_position_code + 1) % 3 != 1 else self.other_player_cards[17:],
            PlayerPosition[(self.my_position_code + 2) % 3]:
                self.other_player_cards[0:17] if (self.my_position_code + 1) % 3 == 1 else self.other_player_cards[17:]
        })

    async def getRightPlayedCards(self, firstOfRound):
        if self.right_played_completed:
            return
        
        rightBuchu = None
        if not firstOfRound:
            rightBuchu = await self.gameHelper.get_right_played_text(template='buchu')
        rightPlayedCards = await self.gameHelper.get_right_played_cards()

        if rightBuchu is not None:
            print("右侧玩家 >>> 不出牌")
            print()
            time.sleep(0.3)
        
        rightPlayed = rightPlayedCards is not None and len(rightPlayedCards) > 0
        if rightPlayed:
            print(f"右侧玩家 >>> 已出牌：{rightPlayedCards}")
            print()
            time.sleep(0.3)
    
        if rightBuchu is not None or rightPlayed:
            self.right_played_completed = True
            self.left_played_completed = False
            self.play_order_of_next = 2

    async def getLeftPlayedCards(self, firstOfRound):
        if self.left_played_completed:
            return

        leftBuchu = None
        if not firstOfRound:
            leftBuchu = await self.gameHelper.get_left_played_text(template='buchu')
        leftPlayedCards = await self.gameHelper.get_left_played_cards()

        if leftBuchu is not None:
            print("左侧玩家 >>> 不出牌")
            print()
            time.sleep(0.3)
        
        leftPlayed = leftPlayedCards is not None and len(leftPlayedCards) > 0
        if leftPlayed:
            print(f"左侧玩家 >>> 已出牌：{leftPlayedCards}")
            print()
            time.sleep(0.3)
        
        if leftBuchu is not None or leftPlayed:
            self.left_played_completed = True
            self.my_played_completed = False
            self.play_order_of_next = 0
    
    async def getMyPlayedCards(self, firstOfRound):
        if self.my_played_completed:
            return
        
        myBuchu = None
        if not firstOfRound:
            myBuchu = await self.gameHelper.get_my_played_text(template='buchu')
        myPlayedCards = await self.gameHelper.get_my_played_cards()

        if myBuchu is not None:
            print("我 >>> 不出牌")
            print()
            time.sleep(0.3)
        
        myPlayed = myPlayedCards is not None and len(myPlayedCards) > 0
        if myPlayed:
            print(f"我 >>> 已出牌：{myPlayedCards}")
            print()
            time.sleep(0.3)

        if (myBuchu is not None) or myPlayed:
            self.my_played_completed = True
            self.right_played_completed = False
            self.play_order_of_next = 1

    async def autoBidding(self):
        if not self.play_cards_automatically:
            return
        
        self.auto_bidding_in_progress = True
        win_rate = await self.get_bid_win_rate()
        while self.worker_runing and self.auto_bidding_in_progress:
            if win_rate > self.config.bid_threshold:
                call_success = await self.gameHelper.clickBtn('call_landlord_btn')
                if call_success:
                    continue
                scramble_success = await self.gameHelper.clickBtn('scramble_landlord_btn')
                if scramble_success:
                    continue
            else:
                not_call_success = await self.gameHelper.clickBtn('not_call_landlord_btn')
                if not_call_success:
                    continue
                not_scramble_success = await self.gameHelper.clickBtn('not_scramble_landlord_btn')
                if not_scramble_success:
                    continue

            three_cards = await self.gameHelper.get_three_cards()
            if len(three_cards) == 3:
                self.auto_bidding_in_progress = False
            
            time.sleep(0.2)

    async def autoRedouble(self):
        if not self.play_cards_automatically:
            self.landlord_confirmed = True
            return
        
        self.auto_redouble_in_progress = True
        win_rate = await self.get_game_win_rate()
        while self.worker_runing and self.auto_redouble_in_progress:
            success = False
            if win_rate > self.config.super_redouble_threshold:
                success = await self.gameHelper.clickBtn('super_redouble_btn')
                if not success:
                    success = await self.gameHelper.clickBtn('redouble_btn')
            elif win_rate > self.config.redouble_threshold:
                success = await self.gameHelper.clickBtn('redouble_btn')
            else:
                success = await self.gameHelper.clickBtn('not_redouble_btn')
            
            if success:
                self.auto_redouble_in_progress = False
                self.landlord_confirmed = True

            time.sleep(0.2)

    def create_ai_representer(self):
        AI = [0, 0]
        AI[0] = self.my_position
        AI[1] = DeepAgent(self.my_position, self.model_path_dict[self.my_position])
        self.env = GameEnv(AI)

    def reset_ai_env(self):
        if self.env is not None:
            self.env.game_over = True
            self.env.reset()

    async def get_bid_win_rate(self):
        success = False
        my_hand_cards = await self.gameHelper.get_my_hand_cards()
        while self.worker_runing and len(my_hand_cards) != 17 and not success:
            my_hand_cards = await self.gameHelper.get_my_hand_cards()
            success = len(my_hand_cards) == 17
            time.sleep(0.2)

        notBidScore = FarmerModel.predict(my_hand_cards, "farmer")
        print(f"预测不叫地主胜率：{str(round(notBidScore, 3))}")
        print()

        result = BidModel.predict_score(my_hand_cards)
        print(f"预测叫地主胜率：{str(round(result, 3))}")
        print()

        win_rate = round(result, 3)
        return win_rate

    async def get_game_win_rate(self):
        if self.my_position_code == 1:
            result = LandlordModel.predict_by_model(self.my_hand_cards, self.three_cards)
            print("本局我是地主，预测胜率：", round(result, 3))
            print()
        elif self.my_position_code == 2:
            result = FarmerModel.predict(self.my_hand_cards, "down")
            print("本局我是农民（地主下家），预测胜率：", round(result, 3))
            print()
        else:
            result = FarmerModel.predict(self.my_hand_cards, "up")
            print("本局我是农民（地主上家），预测胜率：", round(result, 3))
            print()
        
        win_rate = round(result, 3)
        return win_rate
