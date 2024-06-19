import time
import threading

from PIL import Image
from PyQt5.QtCore import pyqtSignal, QThread

from helpers.game_helper import GameHelper
from helpers.image_locator import ImageLocator
from helpers.screen_helper import ScreenHelper

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

class Worker(QThread):
    finished_signal = pyqtSignal(int)

    def __init__(self):
        super(Worker, self).__init__()
        self.gameHelper = GameHelper()
        self.imageLocator = ImageLocator()
        self.screenHelper = ScreenHelper()
        self.worker_runing = False              # 线程是否在运行
        self.play_cards_automatically = False   # 是否自动打牌（无需人为操作）
        self.in_game_start_screen = False       # 是否进入开始游戏界面
        self.game_started = False               # 游戏是否已开局
        self.landlord_confirmed = False         # 是否已确认地主
        self.three_cards = None                 # 三张底牌
        self.three_cards_env = None
        self.my_position_code = None            # 我的位置（角色）代码（0：landlord_up, 1：landlord, 2：landlord_down）
        self.my_position = None                 # 我的位置（角色）
        self.data_initializing = False          # 是否正在初始化数据（执行 initial_data 函数）
        self.data_initialized = False           # 是否完成数据初始化
        self.play_order = None                  # 出牌顺序（0：我先出牌，1：我的下家先出牌，2：我的上家先出牌）
        self.card_playing = False               # 是否在出牌中（已经有人出过牌为 true 否则 false）
        self.my_hand_cards = None               # 我的手牌
        self.my_hand_cards_env = None
        self.other_player_cards = None          # 其他玩家的手牌（整副牌减去我的手牌，后续再减掉历史出牌）
        self.other_player_cards_str = None
        self.all_player_card_data = None
        self.right_play_done = threading.Event()
        self.left_play_done = threading.Event()
        self.my_play_done = threading.Event()
        self.right_play_completed = False       # 右侧玩家是否完成一次出牌
        self.left_play_completed = False        # 左侧玩家是否完成一次出牌
        self.my_play_completed = False          # 我是否完成一次出牌
        self.waiting_animation_to_end = False   # 是否正在等待动画结束

    def run(self):
        self.worker_runing = True
        while self.worker_runing:
            print("----- WORKER STARTED -----")
            # 第一次截图，用于获取窗口宽高等数据
            self.screenHelper.getScreenshot()

            # 检测是否开局
            while not self.game_started:
                self.before_start()
                time.sleep(1.2)

            # 确认地主之后，并且数据尚未初始化
            while self.landlord_confirmed and not self.data_initialized:
                # 如果`正在初始化中`或`已初始化完成`，就直接 continue 跳过本次循环
                if self.data_initializing or self.data_initialized:
                    continue

                self.initial_data()
            
            # 初始化数据之后，并且出牌尚未开始
            while self.data_initialized and not self.card_playing:
                self.run_game()

            print("----- WORKER FINISHED -----")
            print()
            self.finished_signal.emit(1)

    def stop(self):
        self.worker_runing = False
        print("----- WORKER STOPPED -----")
    
    def reset_status(self):
        self.in_game_start_screen = False
        self.game_started = False
        self.landlord_confirmed = False
        self.three_cards = None
        self.three_cards_env = None
        self.my_position_code = None
        self.my_position = None
        self.data_initializing = False
        self.data_initialized = False
        self.play_order = None
        self.card_playing = False
        self.my_hand_cards = None
        self.my_hand_cards_env = None
        self.other_player_cards = None
        self.other_player_cards_str = None
        self.all_player_card_data = None

        self.my_play_done.set()
        self.right_play_done.set()
        self.left_play_done.set()

    def before_start(self):
        print('正在检测是否开局...')
        self.in_game_start_screen = self.check_if_in_game_start_screen()
        while not self.in_game_start_screen:
            print("等待手动进入开始游戏界面...")
            self.in_game_start_screen = self.check_if_in_game_start_screen()
            time.sleep(1.2)

        if self.in_game_start_screen:
            print("您已进入开始游戏界面")

            game_started = self.check_if_game_started()
            if not game_started:
                print("对局尚未开始")

            while not game_started:
                print("等待手动开始对局...")
                game_started = self.check_if_game_started()
                time.sleep(1.2)
        
        if game_started:
            print("对局已开始")
            print()
            self.game_started = True
            self.get_three_cards()

    def get_three_cards(self):
        print("正在识别三张底牌...")
        while self.three_cards is None or len(self.three_cards) != 3:
            self.three_cards = self.gameHelper.findThreeCards()
            time.sleep(1.2)
        
        # 成功获取到三张底牌，意味着地主已确定 
        self.landlord_confirmed = True
        self.three_cards_env = [RealCard2EnvCard[c] for c in list(self.three_cards)]
        print(f"三张底牌：{self.three_cards}")
        print()

    def get_my_position(self):
        print("正在识别我的角色...")
        while self.my_position_code is None:
            self.my_position_code = self.find_my_postion()
            time.sleep(0.2)

        self.my_position = PlayerPosition[self.my_position_code]
        print("我的角色：", self.my_position)
        print()

    def get_my_hand_cards(self):
        print("正在识别我的手牌...")
        success = False
        self.my_hand_cards = self.gameHelper.findMyHandCards()
        if self.my_position_code == 1:
            while len(self.my_hand_cards) != 20 and not success:
                self.my_hand_cards = self.gameHelper.findMyHandCards()
                success = len(self.my_hand_cards) == 20
                time.sleep(0.2)

            self.my_hand_cards_env = [RealCard2EnvCard[c] for c in list(self.my_hand_cards)]
        else:
            while len(self.my_hand_cards) != 17 and not success:
                self.my_hand_cards = self.gameHelper.findMyHandCards()
                success = len(self.my_hand_cards) == 17
                time.sleep(0.2)

            self.my_hand_cards_env = [RealCard2EnvCard[c] for c in list(self.my_hand_cards)]

        print("我的手牌：", self.my_hand_cards)
        print()

    def initial_data(self):
        self.data_initializing = True

        self.get_my_position()
        self.get_my_hand_cards()

        print("正在处理本次牌局数据...")
        self.get_other_player_hand_cards()
        # 这里将牌局的相关数据更新到 self.all_player_card_data 中，包括底牌和每个角色的手牌
        self.all_player_card_data.update({
            'three_cards':
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
        print()

        self.play_order = 0 if self.my_position == "landlord" else 1 if self.my_position == "landlord_up" else 2
        playOrderDescMap = ['我先出牌', '下家先出牌', '上家先出牌']
        print('本局出牌顺序: ', playOrderDescMap[self.play_order])
        print()

        self.data_initialized = True
        self.data_initializing = False

    def run_game(self):
        print('准备就绪，玩家开始出牌...')
        self.card_playing = True

        thread_right = threading.Thread(target=self.get_right_played_cards)
        thread_left = threading.Thread(target=self.get_left_played_cards)
        thread_my = threading.Thread(target=self.get_my_played_cards)

        thread_right.start()
        thread_left.start()
        thread_my.start()

        if self.play_order == 0:        # 顺序：我 --> 右边玩家 --> 左边玩家
            self.my_play_done.set()
        elif self.play_order == 1:      # 顺序：右边玩家 --> 左边玩家 --> 我
            self.right_play_done.set()
        elif self.play_order == 2:      # 顺序：左边玩家 --> 我 --> 右边玩家
            self.left_play_done.set()

        while self.card_playing:
            # print('正在检测对局是否结束...')
            self.check_if_game_overed()
            # self.check_if_player_cards_count_zero()
            time.sleep(2)
        
        # 等待所有线程完成
        thread_my.join()
        thread_right.join()
        thread_left.join()

    def check_if_in_game_start_screen(self):
        region = self.screenHelper.getChatBtnPos()
        result = self.imageLocator.locate_match_on_screen("chat_btn", region)
        in_game_screen = result is not None
        return in_game_screen
    
    def check_if_game_started(self):
        region = self.screenHelper.getThreeCardsFrontCoverPos()
        result = self.imageLocator.locate_match_on_screen("three_card_front_cover", region) # OK
        game_started = result is not None
        return game_started

    def check_if_game_overed(self):
        region = self.screenHelper.getGameResultPos()
        win = self.imageLocator.locate_match_on_screen("beans_win", region)
        lose = self.imageLocator.locate_match_on_screen("beans_lose", region)
        if win is not None or lose is not None:
            self.reset_status()
            print('本轮对局已结束')
            # 通知 AI 结果

    def get_right_played_cards(self, first=False):
        while self.card_playing:
            self.right_play_done.wait()
            if not self.card_playing:
                break

            if self.right_play_completed:
                time.sleep(0.6)
                continue

            if self.waiting_animation_to_end:
                continue

            rightAnimation1Pos = self.screenHelper.getRightAnimation1Pos()
            rightAnimation2Pos = self.screenHelper.getRightAnimation2Pos()
            rightPlayedCardsPos = self.screenHelper.getRightPlayedCardsPos()
            left, top, width, height = rightPlayedCardsPos
            rightPlayedAnimationPos = (left, top, left + width, top + height)
            haveAnimation = self.gameHelper.have_animation(regions=[rightAnimation1Pos, rightAnimation2Pos, rightPlayedAnimationPos])
            if haveAnimation:
                self.waiting_animation_to_end = True
                print('等待动画结束...')
                print()
                time.sleep(0.8)

            self.waiting_animation_to_end = False
            rightBuchu = None
            rightPlayedCards = None

            if not first:
                rightBuchu = self.gameHelper.findRightBuchu()
            rightPlayedCards = self.gameHelper.findRightPlayedCards()

            if rightBuchu is not None:
                time.sleep(0.4)
                print("右侧玩家 >>> 不出牌")
            
            rightPlayed = rightPlayedCards is not None and len(rightPlayedCards) > 0
            if rightPlayed:
                print(f"右侧玩家 >>> 已出牌：{rightPlayedCards}")
                time.sleep(0.2)
        
            if rightBuchu is not None or rightPlayed:
                self.right_play_completed = True
                self.left_play_completed = False
                self.right_play_done.clear()
                self.left_play_done.set()

    def get_left_played_cards(self, first=False):
        while self.card_playing:
            self.left_play_done.wait()
            if not self.card_playing:
                break

            if self.left_play_completed:
                time.sleep(0.6)
                continue

            if self.waiting_animation_to_end:
                continue

            leftAnimation1Pos = self.screenHelper.getLeftAnimation1Pos()
            leftAnimation2Pos = self.screenHelper.getLeftAnimation2Pos()
            leftPlayedCardsPos = self.screenHelper.getLeftPlayedCardsPos()
            left, top, width, height = leftPlayedCardsPos
            leftPlayedAnimationPos = (left, top, left + width, top + height)
            haveAnimation = self.gameHelper.have_animation(regions=[leftAnimation1Pos, leftAnimation2Pos, leftPlayedAnimationPos])
            if haveAnimation:
                self.waiting_animation_to_end = True
                print('等待动画结束...')
                print()
                time.sleep(0.8)
            
            self.waiting_animation_to_end = False
            leftBuchu = None
            leftPlayedCards = None
            
            if not first:
                leftBuchu = self.gameHelper.findLeftBuchu()
            leftPlayedCards = self.gameHelper.findLeftPlayedCards()

            if leftBuchu is not None:
                time.sleep(0.4)
                print("左侧玩家 >>> 不出牌")
            
            leftPlayed = leftPlayedCards is not None and len(leftPlayedCards) > 0
            if leftPlayed:
                print(f"左侧玩家 >>> 已出牌：{leftPlayedCards}")
                time.sleep(0.2)
            
            if leftBuchu is not None or leftPlayed:
                self.left_play_completed = True
                self.my_play_completed = False
                self.left_play_done.clear()
                self.my_play_done.set()
    
    def get_my_played_cards(self, first=False):
        while self.card_playing:
            self.my_play_done.wait()
            if not self.card_playing:
                break

            if self.my_play_completed:
                time.sleep(0.6)
                continue

            if self.waiting_animation_to_end:
                continue

            myAnimationPos = self.screenHelper.getMyPlayedAnimationPos()
            myPlayedCardsPos = self.screenHelper.getMyPlayedCardsPos()
            left, top, width, height = myPlayedCardsPos
            myPlayedAnimationPos = (left, top, left + width, top + height)
            haveAnimation = self.gameHelper.have_animation(regions=[myAnimationPos, myPlayedAnimationPos])
            if haveAnimation:
                self.waiting_animation_to_end = True
                print('等待动画结束...')
                print()
                time.sleep(0.8)

            self.waiting_animation_to_end = False
            myBuchu = None
            myPlayedCards = None
            
            if not first:
                myBuchu = self.gameHelper.findMyBuchu()
            myPlayedCards = self.gameHelper.findMyPlayedCards()

            if myBuchu is not None:
                time.sleep(0.4)
                print("我 >>> 不出牌")
            
            myPlayed = myPlayedCards is not None and len(myPlayedCards) > 0
            if myPlayed:
                print(f"我 >>> 已出牌：{myPlayedCards}")
                time.sleep(0.2)

            if (myBuchu is not None) or myPlayed:
                self.my_play_completed = True
                self.right_play_completed = False
                self.my_play_done.clear()
                self.right_play_done.set()

    def get_other_player_hand_cards(self):
        self.other_player_cards = []
        self.all_player_card_data = {}

        for i in set(AllEnvCard):
            # 对于每一张牌（i），计算它在整副牌 AllEnvCard 中出现的次数，减去玩家手牌中该牌出现的次数，即为其他玩家手牌中该牌的数量
            self.other_player_cards.extend([i] * (AllEnvCard.count(i) - self.my_hand_cards_env.count(i)))

        # 将 self.other_player_hand_cards 中的 env牌编码转换为实际的牌面字符，并将它们组合成一个字符串，最后将其反转
        self.other_hands_cards_str = str(''.join([EnvCard2RealCard[c] for c in self.other_player_cards]))[::-1]

    def find_my_postion(self):
        # 玩家角色：0-地主上家, 1-地主, 2-地主下家

        rightLandlordHatRegion = self.screenHelper.getRightLandlordFlagPos()
        result1 = self.imageLocator.locate_match_on_screen("landlord_hat", rightLandlordHatRegion)
        if result1 is not None:
            return 0 # 如果右边是地主，我就是地主上家

        leftLandlordHatRegion = self.screenHelper.getLeftLandlordFlagPos()
        result2 = self.imageLocator.locate_match_on_screen("landlord_hat", leftLandlordHatRegion)
        if result2 is not None:
            return 2 # 如果左边是地主，我就是地主下家

        myLandlordHatRegion = self.screenHelper.getMyLandlordFlagPos()
        result3 = self.imageLocator.locate_match_on_screen("landlord_hat", myLandlordHatRegion)
        if result3 is not None:
            return 1

    def check_if_player_cards_count_zero(self):
        my_hand_cards = self.gameHelper.findMyHandCards()
        rightCardsNumPos = self.screenHelper.getRightCardsNumPos()
        leftCardsNumPos = self.screenHelper.getLeftCardsNumPos()
        rightCardsCountZero = self.imageLocator.locate_match_on_screen("cards_count_zero", rightCardsNumPos)
        leftCardsCountZero = self.imageLocator.locate_match_on_screen("cards_count_zero", leftCardsNumPos)
        if len(my_hand_cards) == 0 or rightCardsCountZero is not None or leftCardsCountZero is not None:
            self.reset_status()
            print('本轮对局已结束')
            # 通知 AI 结果

    def auto_operation(self):
        if self.play_cards_automatically:
            self.detect_and_click_continue_game_btn()
            self.detect_and_click_quick_start_btn()
            self.detect_and_click_start_btn()
        else:
            pass

    def detect_and_click_quick_start_btn(self):
        region = self.screenHelper.getQuickStartBtnPos()
        result = self.imageLocator.locate_match_on_screen("quick_start_btn", region) # OK
        if result is not None:
            # self.gameHelper.ClickOnImage("quick_start_btn", region)
            print('模拟点击 ·快速开始· 按钮')
            # time.sleep(1)
    
    def detect_and_click_start_btn(self):
        region = self.screenHelper.getStartGameBtnPos()
        result = self.imageLocator.locate_match_on_screen("start_game_btn", region) # OK
        if result is not None:
            # self.gameHelper.ClickOnImage("start_game_btn", region)
            print('模拟点击 ·开始游戏· 按钮')
            # time.sleep(1)

    def detect_and_click_continue_game_btn(self):
        region = self.screenHelper.getContinueGameBtnPos()
        result = self.imageLocator.locate_match_on_screen("continue_game_btn", region) # OK
        if result is not None:
            self.game_started = False
            # 通知 AI 结果
            # self.gameHelper.ClickOnImage("continue_game_btn", region)
            print('模拟点击 ·继续游戏· 按钮')

        