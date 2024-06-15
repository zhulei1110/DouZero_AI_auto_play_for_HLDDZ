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
    auto_start = pyqtSignal(int)
    manual_start = pyqtSignal(int)
    stop = pyqtSignal(int)

    def __init__(self):
        super(Worker, self).__init__()
        self.gameHelper = GameHelper()
        self.imageLocator = ImageLocator()
        self.screenHelper = ScreenHelper()
        self.auto_sign = None
        self.loop_sign = None
        self.landlord_confirmed = None
        self.data_initializing = None   # 是否正在初始化数据（执行 initial_data 函数）
        self.data_initialized = None
        self.in_game_screen = None      # 是否在开始游戏界面内
        self.game_started = None        # 游戏是否已开始
        self.game_running = None        # 是否正在进行对弈
        self.game_over = None
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
        self.screenHelper.getScreenshot()

        if self.auto_sign:
            print("现在是自动模式...")
        else:
            print("现在是手动模式...")

        self.loop_sign = True
        self.landlord_confirmed = False

        while not self.game_started:
            self.before_start()
            time.sleep(0.25)

        while self.landlord_confirmed:
            if self.data_initializing:
                continue

            if not self.data_initialized:
                self.initial_data()
                self.data_initializing = False
                self.data_initialized = True

            time.sleep(0.2)
        
        while self.data_initialized:
            if self.game_running:
                break
            
            self.start_game()

    def before_start(self):
        self.in_game_screen = False
        self.in_game_screen = self.check_if_in_game_screen()
        while self.in_game_screen == False:
            time.sleep(1)
            print("未进入开始游戏界面")
            self.in_game_screen = self.check_if_in_game_screen()

        time.sleep(0.3)
        if self.in_game_screen and not self.game_started:
            print("已进入开始游戏界面")

            game_started = self.check_if_game_started()
            if not game_started:
                print("对局未开始")

            while game_started == False:
                time.sleep(0.5)
                print("等待对局开始...")
                game_started = self.check_if_game_started()
        
        print("对局开始...")
        self.game_started = True
        self.getThreeCards()    # 对局开始后，获取三张底牌，用于判断是否已确认地主

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

        print("开始对局...")

        # 出牌顺序：0-我出牌, 1-我的下家出牌, 2-我的上家出牌
        self.play_order = 0 if self.my_position == "landlord" else 1 if self.my_position == "landlord_up" else 2

    # 获取其它玩家的手牌
    def getOtherPlayerHandCards(self):
        self.other_player_hand_cards = []
        self.all_player_card_data = {}

        for i in set(AllEnvCard):
            # 对于每一张牌（i），计算它在整副牌 AllEnvCard 中出现的次数，减去玩家手牌中该牌出现的次数，即为其他玩家手牌中该牌的数量
            self.other_player_hand_cards.extend([i] * (AllEnvCard.count(i) - self.my_hand_cards_env.count(i)))

        # 将 self.other_player_hand_cards 中的 env牌编码转换为实际的牌面字符，并将它们组合成一个字符串，最后将其反转
        self.other_hands_cards_str = str(''.join([EnvCard2RealCard[c] for c in self.other_player_hand_cards]))[::-1]

    # 获取我的手牌
    def getMyHandCards(self):
        print("正在识别我的手牌...")
        self.my_hand_cards = self.gameHelper.findMyHandCards()
        if self.my_position_code == 1:
            while len(self.my_hand_cards) != 20:
                if not self.game_started:
                    continue

                self.my_hand_cards = self.gameHelper.findMyHandCards()
                time.sleep(0.2)

            self.my_hand_cards_env = [RealCard2EnvCard[c] for c in list(self.my_hand_cards)]
        else:
            while len(self.my_hand_cards) != 17:
                if not self.game_started:
                    continue

                self.my_hand_cards = self.gameHelper.findMyHandCards()
                time.sleep(0.2)

            self.my_hand_cards_env = [RealCard2EnvCard[c] for c in list(self.my_hand_cards)]

        print("我的手牌：", self.my_hand_cards)

    # 获取三张底牌
    def getThreeCards(self):
        print("正在识别三张底牌...")
        while self.three_cards is None or len(self.three_cards) != 3:
            if not self.game_started:
                continue

            self.three_cards = self.gameHelper.findThreeCards()
            time.sleep(0.2)
        
        self.landlord_confirmed = True
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
        rightLandlordHatRegion = self.screenHelper.getLeftLandlordFlagPos()
        testImage = Image.open('test123.png')
        result1 = self.imageLocator.LocateOnScreen("landlord_hat", rightLandlordHatRegion, img=testImage)
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

    def start_game(self):
        self.game_running = True
        return False

    def auto_operate(self):
        self.check_if_game_is_over()
        if self.auto_sign:
            self.detect_and_click_continue_game_btn()
            # self.check_if_game_results()
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
            time.sleep(1)
    
    def detect_and_click_start_btn(self):
        region = self.screenHelper.getStartGameBtnPos()
        result = self.imageLocator.LocateOnScreen("start_game_btn", region) # OK
        if result is not None:
            # self.gameHelper.ClickOnImage("start_game_btn", region)
            print('模拟点击 ·开始游戏· 按钮')
            time.sleep(1)

    def detect_and_click_continue_game_btn(self):
        region = self.screenHelper.getContinueGameBtnPos()
        result = self.imageLocator.LocateOnScreen("continue_game_btn", region) # OK
        if result is not None:
            if not self.loop_sign:
                print("对局已结束")
            else:
                self.game_started = False
                # 通知 AI 结果
                # self.gameHelper.ClickOnImage("continue_game_btn", region)
                print('模拟点击 ·继续游戏· 按钮')
 
    def check_if_game_is_over(self):
        beansRegions = self.screenHelper.getBeansRegionsPos() # 这个方式不太稳妥，页面显示的时候过短，有可能识别不到
        for i in beansRegions:
            result = self.imageLocator.LocateOnScreen("beans", region=i)
            if result is not None:
                print("对局已结束")
                self.game_started = False
                time.sleep(3)
                break

    def check_if_game_results(self):
        loseRegion = self.screenHelper.getLoseTextPos()
        winRegion = self.screenHelper.getWinTextPos()
        lose = self.imageLocator.LocateOnScreen("lose", loseRegion)
        win = self.imageLocator.LocateOnScreen("win", winRegion)
        if win is not None or lose is not None:
            if not self.loop_sign:
                print("对局已结束")
            else:
                self.game_started = False
                # 通知 AI 结果
                time.sleep(1)

        