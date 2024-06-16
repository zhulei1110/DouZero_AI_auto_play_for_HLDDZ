import time
from PIL import Image
from PyQt5.QtCore import pyqtSignal, QThread

from helpers.game_helper import GameHelper
from helpers.image_locator import ImageLocator
from helpers.screen_helper import ScreenHelper

# 玩家角色：0-地主上家, 1-地主, 2-地主下家
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
    # auto_start = pyqtSignal(int)
    # manual_start = pyqtSignal(int)
    stop = pyqtSignal(int)

    def __init__(self):
        super(Worker, self).__init__()
        self.gameHelper = GameHelper()
        self.imageLocator = ImageLocator()
        self.screenHelper = ScreenHelper()
        self.auto_running = False
        self.in_game_screen = False      # 是否在开始游戏界面内
        self.landlord_confirmed = False  # 是否已确认地主
        self.data_initializing = False   # 是否正在初始化数据（执行 initial_data 函数）
        self.data_initialized = False
        self.game_started = False        # 游戏是否已开始
        self.game_running = False        # 是否正在进行对弈
        self.my_position_code = None
        self.my_position = None
        self.three_cards = None
        self.three_cards_env = None
        self.my_hand_cards = None
        self.my_hand_cards_env = None
        self.play_order = None
        self.other_player_hand_cards = None     # 其他玩家的手牌（整副牌减去我的手牌，后续再减掉历史出牌）
        self.other_player_hands_cards_str = None
        self.all_player_card_data = None

    def run(self):
        # 第一次截图，用于获取窗口宽高等数据
        self.screenHelper.getScreenshot()

        # 用于测试
        # self.gameHelper.findMyHandCards()

        if self.auto_running:
            print("现在是自动模式...")
        else:
            print("现在是手动模式...")

        # # 检测是否开局
        while not self.game_started:
            self.before_start()
            time.sleep(0.2)

        # 确认地主之后，初始化数据
        while self.landlord_confirmed:
            # 如果 正在初始化中 或 已初始化完成，就直接 continue 跳过本次循环
            if self.data_initializing or self.data_initialized:
                continue
            self.initial_data()
            self.data_initialized = True
            time.sleep(0.2)
        
        # 初始化数据之后，开始对局
        while self.data_initialized:
            if self.game_running:
                break
            self.run_game()
            time.sleep(0.2)

        # 开始对局之后，检测对局是否结束
        while self.game_running:
            self.check_if_game_overed()
            time.sleep(0.5)

    def before_start(self):
        self.in_game_screen = False
        self.in_game_screen = self.check_if_in_game_screen()
        while self.in_game_screen == False:
            print("未进入开始游戏界面")
            self.in_game_screen = self.check_if_in_game_screen()
            time.sleep(0.5)

        if self.in_game_screen and not self.game_started:
            print("已进入开始游戏界面")

            game_started = self.check_if_game_started()
            if not game_started:
                print("对局未开始")

            while game_started == False:
                print("等待对局开始...")
                game_started = self.check_if_game_started()
                time.sleep(0.5)
        
        print("对局已开始")
        self.game_started = True
        self.getThreeCards()

    def check_if_in_game_screen(self):
        region = self.screenHelper.getChatBtnPos()
        result = self.imageLocator.LocateOnScreen("chat_btn", region) # OK
        in_game_screen = result is not None
        return in_game_screen
    
    def check_if_game_started(self):
        region = self.screenHelper.getThreeCardFrontCoverPos()
        result = self.imageLocator.LocateOnScreen("three_card_front_cover", region) # OK
        game_started = result is not None
        return game_started

    def check_if_game_overed(self):
        region = self.screenHelper.getWinOrLoseBeansPos()
        win = self.imageLocator.LocateOnScreen("beans_win", region)
        lose = self.imageLocator.LocateOnScreen("beans_lose", region)
        if win is not None or lose is not None:
            self.resetStatus()
            # 通知 AI 结果

    def resetStatus(self):
        self.landlord_confirmed = False
        self.data_initializing = False
        self.data_initialized = False
        self.game_started = False
        self.game_running = False

    def initial_data(self):
        self.data_initializing = True
        print("正在初始化卡牌数据...")

        self.getMyPosition()
        self.getMyHandCards()
        self.getOtherPlayerHandCards()

        # 这里将牌局的相关数据更新到 self.all_player_card_data 中，包括底牌和每个角色的手牌
        self.all_player_card_data.update({
            'three_cards':
                self.three_cards_env,
            PlayerPosition[(self.my_position_code + 0) % 3]:
                self.my_hand_cards_env,
            # 上家和下家的手牌是从 self.other_player_hand_cards 中截取的前 17 张和后 17 张牌
            # 具体分配逻辑根据玩家的角色编码 self.my_position_code 和取模操作 (self.my_position_code + n) % 3 决定
            PlayerPosition[(self.my_position_code + 1) % 3]:
                self.other_player_hand_cards[0:17] if (self.my_position_code + 1) % 3 != 1 else self.other_player_hand_cards[17:],
            PlayerPosition[(self.my_position_code + 2) % 3]:
                self.other_player_hand_cards[0:17] if (self.my_position_code + 1) % 3 == 1 else self.other_player_hand_cards[17:]
        })

        # 出牌顺序：0-我出牌, 1-我的下家出牌, 2-我的上家出牌
        self.play_order = 0 if self.my_position == "landlord" else 1 if self.my_position == "landlord_up" else 2
        print('play_order: ', self.play_order)

        self.data_initializing = False
        print("已完成卡牌数据初始化")

    # 获取三张底牌
    def getThreeCards(self):
        print("正在识别三张底牌...")
        while self.three_cards is None or len(self.three_cards) != 3:
            if not self.game_started:
                continue

            self.three_cards = self.gameHelper.findThreeCards()
            time.sleep(0.2)
        
        self.landlord_confirmed = True      # 成功获取三张底牌，意味着地主已确定 
        self.three_cards_env = [RealCard2EnvCard[c] for c in list(self.three_cards)]
        print("三张底牌：", self.three_cards)

    # 获取我的角色
    def getMyPosition(self):
        print("正在识别我的角色...")
        while self.my_position_code is None:
            if not self.game_started:
                continue

            self.my_position_code = self.findMyPostion()
            time.sleep(0.2)

        self.my_position = PlayerPosition[self.my_position_code]
        print("我的角色：", self.my_position)

    # 玩家角色：0-地主上家, 1-地主, 2-地主下家
    def findMyPostion(self):
        rightLandlordHatRegion = self.screenHelper.getRightLandlordFlagPos()
        result1 = self.imageLocator.LocateOnScreen("landlord_hat", rightLandlordHatRegion)
        if result1 is not None:
            return 0 # 如果右边是地主，我就是地主上家

        leftLandlordHatRegion = self.screenHelper.getLeftLandlordFlagPos()
        result2 = self.imageLocator.LocateOnScreen("landlord_hat", leftLandlordHatRegion)
        if result2 is not None:
            return 2 # 如果左边是地主，我就是地主下家

        myLandlordHatRegion = self.screenHelper.getMyLandlordFlagPos()
        result3 = self.imageLocator.LocateOnScreen("landlord_hat", myLandlordHatRegion)
        if result3 is not None:
            return 1

    # 获取我的手牌
    def getMyHandCards(self):
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

    # 其它玩家的手牌
    def getOtherPlayerHandCards(self):
        self.other_player_hand_cards = []
        self.all_player_card_data = {}

        for i in set(AllEnvCard):
            # 对于每一张牌（i），计算它在整副牌 AllEnvCard 中出现的次数，减去玩家手牌中该牌出现的次数，即为其他玩家手牌中该牌的数量
            self.other_player_hand_cards.extend([i] * (AllEnvCard.count(i) - self.my_hand_cards_env.count(i)))

        # 将 self.other_player_hand_cards 中的 env牌编码转换为实际的牌面字符，并将它们组合成一个字符串，最后将其反转
        self.other_hands_cards_str = str(''.join([EnvCard2RealCard[c] for c in self.other_player_hand_cards]))[::-1]

    def run_game(self):
        print("开始出牌...")
        self.game_running = True

        while self.game_running:
            rightPlayedCards = self.gameHelper.findRightPlayedCards()
            if rightPlayedCards is not None:
                print("右侧玩家出牌：", rightPlayedCards)

            leftPlayedCards = self.gameHelper.findLeftPlayedCards()
            if leftPlayedCards is not None:
                print("左侧玩家出牌：", leftPlayedCards)

            myPlayedCards = self.gameHelper.findMyPlayedCards()
            if myPlayedCards is not None:
                print("我的出牌：", myPlayedCards)

            time.sleep(0.2)

    def auto_operation(self):
        if self.auto_running:
            self.detect_and_click_continue_game_btn()
            self.detect_and_click_quick_start_btn()
            self.detect_and_click_start_btn()
        else:
            pass

    def detect_and_click_quick_start_btn(self):
        region = self.screenHelper.getQuickStartBtnPos()
        result = self.imageLocator.LocateOnScreen("quick_start_btn", region) # OK
        if result is not None:
            # self.gameHelper.ClickOnImage("quick_start_btn", region)
            print('模拟点击 ·快速开始· 按钮')
            # time.sleep(1)
    
    def detect_and_click_start_btn(self):
        region = self.screenHelper.getStartGameBtnPos()
        result = self.imageLocator.LocateOnScreen("start_game_btn", region) # OK
        if result is not None:
            # self.gameHelper.ClickOnImage("start_game_btn", region)
            print('模拟点击 ·开始游戏· 按钮')
            # time.sleep(1)

    def detect_and_click_continue_game_btn(self):
        region = self.screenHelper.getContinueGameBtnPos()
        result = self.imageLocator.LocateOnScreen("continue_game_btn", region) # OK
        if result is not None:
            self.game_started = False
            # 通知 AI 结果
            # self.gameHelper.ClickOnImage("continue_game_btn", region)
            print('模拟点击 ·继续游戏· 按钮')

        