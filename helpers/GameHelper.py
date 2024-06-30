import copy
import cv2
import numpy as np
import time

from collections import defaultdict
from enum import Enum
from skimage.metrics import structural_similarity as ssim

from helpers.ColorRecognizer import ColorRecognizer
from helpers.ImageLocator import ImageLocator
from helpers.ScreenHelper import ScreenHelper, ScreenshotArea

from constants import RealCards, RealCard2EnvCard
from douzero.env import move_detector as md


# 牌检测结果滤波
# 过滤掉相互距离太近的牌，只保留相距超过一定距离的牌
def cards_filter(location, distance):
    if len(location) == 0:
        return 0

    locList = [location[0][0]]  # 用于存储已经确认保留的牌的 x 坐标
    posList = [location[0]]     # 用于存储已经确认保留的牌的坐标
    count = 1                   # 用于计数保留的牌数，初始化为 1，因为至少会保留第一张牌

    for e in location:
        flag = 1                                # 检查当前位置 e 是否与已保留的牌的位置相距超过 distance
        for have in locList:                    # 对于每个位置 e，初始化 flag 为 1，然后遍历 locList 中已保留的牌的 x 坐标
            if abs(e[0] - have) <= distance:    # 如果当前牌的位置 e[0] 与任何已保留牌的位置 have 之间的绝对距离小于或等于 distance
                flag = 0                        # 则将 flag 置为 0 并跳出循环
                break
        if flag:
            count += 1                          # 如果 flag 仍然为 1，表示当前牌的位置与所有已保留牌的位置都相距超过 distance，于是将其计入保留的牌
            locList.append(e[0])
            posList.append(e)

    return count, posList


def find_repeated_cards_click_position(cards, cards_pos_dict):
    result = {}
    cards_count = {card: cards.count(card) for card in set(cards)}  # 统计传入的每种卡牌的数量

    for card in cards:
        if card in cards_pos_dict:
            if card not in result:
                result[card] = []
            card_positions = cards_pos_dict[card]
            count_needed = cards_count[card]
            count_selected = len(result[card])

            while count_selected < count_needed and count_selected < len(card_positions):
                result[card].append(card_positions[count_selected])
                count_selected += 1

    # 确保每种卡牌只取到需要的数量，并且如果有多个，则取第一个和最后一个
    for card in result:
        if len(result[card]) > 1:
            result[card] = [result[card][0], result[card][-1]]
        elif len(result[card]) == 1:
            result[card] = [result[card][0]]

    return result

def find_serial_cards_click_position(cards, cards_pos_dict):
    result = None
    
    # 顺子第一张和最后一张牌
    first_card = cards[0]
    last_card = cards[-1]
    
    if first_card in cards_pos_dict and last_card in cards_pos_dict:
        first_position = cards_pos_dict[first_card][0]
        last_position = cards_pos_dict[last_card][0]
        result = [first_position, last_position]
    
    return result


class AnimationArea(Enum):
    RIGHT_PLAYED_ANIMATION = "right_played_animation"
    LEFT_PLAYED_ANIMATION = "left_played_animation"
    MY_PLAYED_ANIMATION = "my_played_animation"

class GameHelper:
    mark_dict = {
        'three_cards': 'three',
        'my_hand_cards': 'my',
        'right_played_cards': 'play',
        'left_played_cards': 'play',
        'my_played_cards': 'play'
    }

    def __init__(self, imageLocator:ImageLocator, screenHelper:ScreenHelper):
        self.distance = 30
        self.colorRecognizer = ColorRecognizer()
        self.imageLocator = imageLocator
        self.screenHelper = screenHelper
        self.resizeScale = None
        self.tolerance = 3

    async def __findCards(self, image, pos, mark, scale=None, confidence=0.8):
        if not mark:
            return None
        
        cards = ""
        D_king = 0
        X_king = 0

        if not scale:
            scale = await self.imageLocator.get_resize_scale(image)
            self.resizeScale = scale

        for card in RealCards:
            templateName = f'{mark}_{card}'
            result = await self.imageLocator.locate_all_match_on_image(image=image, templateName=templateName, region=pos, scale=scale, confidence=confidence)
            
            if len(result) > 0:
                count, posList = cards_filter(list(result), self.distance)
                if card == "X" or card == "D":
                    for p in posList:
                        # p: (117, 49, 1334, 215) 
                        # p: (left, top, width, height)

                        if mark == "my":
                            captureWidth = int(self.screenHelper.WindowWidth * scale * 0.0188) + 1
                            captureHeight = int(self.screenHelper.WindowHeight * scale * 0.0352) + 1
                        if mark == "play":
                            captureWidth = int(self.screenHelper.WindowWidth * scale * 0.01198) + 1
                            captureHeight = int(self.screenHelper.WindowHeight * scale * 0.02315) + 1
                        if mark == "three":
                            captureWidth = int(self.screenHelper.WindowWidth * scale * 0.01042) + 1
                            captureHeight = int(self.screenHelper.WindowHeight * scale * 0.01852) + 1
                        
                        interceptWidth = p[0] + captureWidth
                        interceptHeight = p[1] + captureHeight

                        img1 = image[pos[1]:pos[1] + pos[3], pos[0]:pos[0] + pos[2]]
                        img2 = img1[p[1]:interceptHeight, p[0]:interceptWidth]

                        # 图片日志
                        if self.screenHelper.config.king_color_compare_image_logs:
                            unique_key = self.screenHelper.compute_image_unique_key(img1)
                            posText = f'{p[1]}-{interceptHeight}_{p[0]}-{interceptWidth}'
                            cv2.imwrite(f'screenshots/logs/k_c_c_{card}_{unique_key}.png', img1)
                            cv2.imwrite(f'screenshots/logs/k_c_c_{card}_{unique_key}_{posText}.png', img2)

                        color = self.colorRecognizer.check_image_is_red_or_black(img2)
                        if card == "X" and color == "black":
                            X_king = 1
                            break

                        if card == "D" and (color == "red" or color == "red2"):
                            D_king = 1
                            break
                else:
                    cards += card[0] * count

        if X_king:
            cards += "X"
            cards = cards[-1] + cards[:-1]

        if D_king:
            cards += "D"
            cards = cards[-1] + cards[:-1]

        return cards
    
    async def findCards(self, areaName):
        pos = self.screenHelper.getCapturePosition(areaName)
        mark = self.mark_dict[areaName]
        screenshot, _ = await self.screenHelper.getScreenshot()
        image = cv2.cvtColor(np.asarray(screenshot), cv2.COLOR_RGB2BGR)
        result = await self.__findCards(image, pos, mark)
        return result

    async def findImage(self, areaName):
        pos = self.screenHelper.getCapturePosition(areaName)
        result = await self.imageLocator.locate_match_on_screen(templateName=areaName, region=pos)
        return result
    
    def __compareImage(self, img1, img2):
        # 转换为灰度图
        gray1 = cv2.cvtColor(np.asarray(img1), cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(np.asarray(img2), cv2.COLOR_BGR2GRAY)

        # 使用结构相似性指数（SSIM）比较相似度
        ssim_index, _ = ssim(gray1, gray2, full=True)
        if ssim_index < 0.99:
            return True

        # 图片日志
        if self.screenHelper.config.animation_image_compare_logs:
            unique_key = self.screenHelper.compute_image_unique_key(gray1)
            cv2.imwrite(f'screenshots/logs/i_c_{unique_key}_current.png', gray1)
            cv2.imwrite(f'screenshots/logs/i_c_{unique_key}_previous.png', gray2)

        return False
    
    async def __haveAnimation(self, intervals=0.2, regions=None):
        if not regions:
            return False
        
        image, _ = await self.screenHelper.getScreenshot()
        previousImage = image

        for i in range(2):
            time.sleep(intervals)

            image, _ = await self.screenHelper.getScreenshot()
            for region in regions:
                if self.__compareImage(image.crop(region), previousImage.crop(region)):
                    return True
            
            previousImage = image

        return False

    async def haveAnimation(self, areaName, intervals=0.2):
        haveAnimation = False

        if areaName == AnimationArea.RIGHT_PLAYED_ANIMATION.value:
            animationPos1 = self.screenHelper.getCapturePosition2(ScreenshotArea.RIGHT_PLAYED_CARDS.value)
            animationPos2 = self.screenHelper.getCapturePosition2(ScreenshotArea.RIGHT_PLAYED_ANIMATION_1.value)
            # animationPos3 = self.screenHelper.getCapturePosition2(ScreenshotArea.RIGHT_PLAYED_ANIMATION_2.value)
            haveAnimation = await self.__haveAnimation(intervals, regions=[animationPos2])

        if areaName == AnimationArea.LEFT_PLAYED_ANIMATION.value:
            animationPos1 = self.screenHelper.getCapturePosition2(ScreenshotArea.LEFT_PLAYED_CARDS.value)
            animationPos2 = self.screenHelper.getCapturePosition2(ScreenshotArea.LEFT_PLAYED_ANIMATION_1.value)
            # animationPos3 = self.screenHelper.getCapturePosition2(ScreenshotArea.LEFT_PLAYED_ANIMATION_2.value)
            haveAnimation = await self.__haveAnimation(intervals, regions=[animationPos2])

        if areaName == AnimationArea.MY_PLAYED_ANIMATION.value:
            animationPos1 = self.screenHelper.getCapturePosition2(ScreenshotArea.MY_PLAYED_CARDS.value)
            animationPos2 = self.screenHelper.getCapturePosition2(ScreenshotArea.MY_PLAYED_ANIMATION.value)
            haveAnimation = await self.__haveAnimation(intervals, regions=[animationPos1, animationPos2])

        return haveAnimation

    async def check_if_in_game_start_screen(self):
        result = await self.findImage(ScreenshotArea.CHAT_BTN.value)
        in_start_game_screen = result is not None
        return in_start_game_screen

    async def check_if_game_started(self):
        result = await self.findImage(ScreenshotArea.THREE_CARDS_FRONT_COVER.value)
        game_started = result is not None
        return game_started
    
    async def check_if_game_overed(self):
        pos = self.screenHelper.getCapturePosition(ScreenshotArea.GAME_RESULT.value)
        win = await self.imageLocator.locate_match_on_screen("beans_win", region=pos)
        lose = await self.imageLocator.locate_match_on_screen("beans_lose", region=pos)
        game_overed = win is not None or lose is not None
        return game_overed

    async def get_my_position(self):
        # 玩家角色：0-地主上家, 1-地主, 2-地主下家

        pos1 = self.screenHelper.getCapturePosition(ScreenshotArea.RIGHT_LANDLORD_FLAG.value)
        result1 = await self.imageLocator.locate_match_on_screen("landlord_hat", region=pos1)
        if result1 is not None:
            return 0 # 如果右边是地主，我就是地主上家

        pos2 = self.screenHelper.getCapturePosition(ScreenshotArea.LEFT_LANDLORD_FLAG.value)
        result2 = await self.imageLocator.locate_match_on_screen("landlord_hat", pos2)
        if result2 is not None:
            return 2 # 如果左边是地主，我就是地主下家

        pos3 = self.screenHelper.getCapturePosition(ScreenshotArea.MY_LANDLORD_FLAG.value)
        result3 = await self.imageLocator.locate_match_on_screen("landlord_hat", pos3)
        if result3 is not None:
            return 1

    async def get_three_cards(self):
        three_cards = await self.findCards(ScreenshotArea.THREE_CARDS.value)
        return three_cards

    async def get_my_hand_cards(self):
        my_hand_cards = await self.findCards(ScreenshotArea.MY_HAND_CARDS.value)
        return my_hand_cards
    
    async def get_right_played_cards(self):
        right_played_cards = await self.findCards(ScreenshotArea.RIGHT_PLAYED_CARDS.value)
        return right_played_cards
    
    async def get_left_played_cards(self):
        left_played_cards = await self.findCards(ScreenshotArea.LEFT_PLAYED_CARDS.value)
        return left_played_cards
    
    async def get_my_played_cards(self):
        my_hand_cards = await self.findCards(ScreenshotArea.MY_PLAYED_CARDS.value)
        return my_hand_cards

    async def get_right_played_text(self, template):
        pos = self.screenHelper.getCapturePosition(ScreenshotArea.RIGHT_PLAYED_TEXT.value)
        result = await self.imageLocator.locate_match_on_screen(templateName=template, region=pos)
        return result
    
    async def get_left_played_text(self, template):
        pos = self.screenHelper.getCapturePosition(ScreenshotArea.LEFT_PLAYED_TEXT.value)
        result = await self.imageLocator.locate_match_on_screen(templateName=template, region=pos)
        return result
    
    async def get_my_played_text(self, template):
        pos = self.screenHelper.getCapturePosition(ScreenshotArea.MY_PLAYED_TEXT.value)
        result = await self.imageLocator.locate_match_on_screen(templateName=template, region=pos)
        return result
    
    async def get_my_hand_card_pos(self, image, card, used_left_pos_list):
        area_name = ScreenshotArea.MY_HAND_CARDS.value
        mark = self.mark_dict[area_name]
        template_name = f'{mark}_{card}'

        result = await self.imageLocator.locate_all_match_on_image(image, templateName=template_name, confidence=0.75)
        if len(result) > 0:
            count, posList = cards_filter(list(result), self.distance)
            points = [pos for pos in posList if pos[0] not in used_left_pos_list]
            if points:
                cardPos = min(points, key=lambda x: x[0])
                return (cardPos[0], cardPos[1])
            
        return None

    async def get_my_hand_cards_pos_list(self, my_hand_cards=None):
        if not my_hand_cards:
            my_hand_cards = await self.get_my_hand_cards()
        
        pos_list = None
        cards_num = len(my_hand_cards)
        if cards_num > 0:
            screenshot, _ = await self.screenHelper.getScreenshot()
            image = cv2.cvtColor(np.asarray(screenshot), cv2.COLOR_RGB2BGR)

            pos_list = []
            used_left_pos_list = set()
            for i in range(cards_num):
                card = my_hand_cards[i]
                card_pos = await self.get_my_hand_card_pos(image, card, used_left_pos_list)
                if card_pos:
                    pos_list.append(card_pos)
                    used_left_pos_list.add(card_pos[0])  # 只添加 left 值
                    
        return pos_list

    def __check_selected_cards(self, initial_dict, selected_dict, selected_cards):
        actual_selected = []
        for card, positions in initial_dict.items():
            for i, (left, top) in enumerate(positions):
                if card in selected_dict and i < len(selected_dict[card]):
                    new_left, new_top = selected_dict[card][i]
                    if top - new_top > 5:
                        actual_selected.append(card)

        # 统计 AI 选择的每张卡牌的数量
        from collections import Counter
        selected_count = Counter(selected_cards)
        actual_selected_count = Counter(actual_selected)

        missing_cards = []
        extra_cards = []
        
        # 找出缺失的卡牌
        for card, count in selected_count.items():
            if actual_selected_count[card] < count:
                missing_cards.extend([card] * (count - actual_selected_count[card]))
        
        # 找出多余的卡牌
        for card, count in actual_selected_count.items():
            if selected_count[card] < count:
                extra_cards.extend([card] * (count - selected_count[card]))

        if len(missing_cards) > 0:
            for card in missing_cards:
                if card in initial_dict:
                    # 点击还未被选中的卡牌位置
                    positions = initial_dict[card]
                    for position in positions:
                        if position not in selected_dict[card]:
                            x, y = position
                            self.screenHelper.leftClick2(x, y)
                            break
        
        if len(extra_cards) > 0:
            for card in extra_cards:
                if card in initial_dict:
                    # 点击已经被选中的卡牌位置
                    positions = selected_dict[card]
                    for position in positions:
                        if position in selected_dict[card]:
                            x, y = position
                            self.screenHelper.leftClick2(x, y)
                            break
        
        return missing_cards, extra_cards

    async def verify_and_reselect(self, initial_pos_dict, play_cards):
        my_hand_cards = await self.get_my_hand_cards()
        pos_list = await self.get_my_hand_cards_pos_list(my_hand_cards)
        if not pos_list:
            return
        
        cards_pos_defaultdict = defaultdict(list)
        for key, value in zip(my_hand_cards, pos_list):
            cards_pos_defaultdict[key].append(value)

        selected_pos_dict = dict(cards_pos_defaultdict)
        selected_cards = list(play_cards)

        print(f"initial_pos_dict: {initial_pos_dict}")
        print()
        print(f"selected_pos_dict: {selected_pos_dict}")
        print()

        missing_cards, extra_cards = self.__check_selected_cards(initial_pos_dict, selected_pos_dict, selected_cards)
        print(f'missing_cards: {missing_cards}')
        print()
        print(f'extra_cards: {extra_cards}')
        print()
        
    async def clickCards(self, cards):
        my_hand_cards = await self.get_my_hand_cards()
        pos_list = await self.get_my_hand_cards_pos_list(my_hand_cards)
        if not pos_list:
            return
        
        # defaultdict 允许重复的 key
        cards_pos_defaultdict = defaultdict(list)
        for key, value in zip(my_hand_cards, pos_list):
            cards_pos_defaultdict[key].append(value)

        # 点击前的所有手牌位置（将 defaultdict 转换为普通字典）
        cards_pos_dict = dict(cards_pos_defaultdict)
        initial_pos_dict = copy.deepcopy(cards_pos_dict)

        action = [RealCard2EnvCard[c] for c in list(cards)]
        m_type = md.get_move_type(action)
        if m_type["type"] not in [md.TYPE_1_SINGLE, md.TYPE_8_SERIAL_SINGLE]:
            click_pos_dict = find_repeated_cards_click_position(cards, cards_pos_dict)
            print(click_pos_dict)
            if len(click_pos_dict) > 0:
                for card, coords in click_pos_dict.items():
                    if len(coords) == 2:
                        start_x, start_y = coords[0]
                        end_x, end_y = coords[1]
                        self.screenHelper.leftClickAndDrag(start_x, start_y, end_x, end_y)
                        # print(f"卡牌 {card} 已被选中多张")
                        # print()
                        time.sleep(0.2)
                    elif len(coords) == 1:
                        x, y = coords[0]
                        self.screenHelper.leftClick2(x, y)
                        # print(f"卡牌 {card} 已被点击选中")
                        # print()
                        time.sleep(0.2)

        if m_type["type"] == md.TYPE_8_SERIAL_SINGLE:
            pos_list = find_serial_cards_click_position(cards, cards_pos_dict)
            if pos_list:
                start_x, start_y = pos_list[0]
                end_x, end_y = pos_list[1]
                self.screenHelper.leftClickAndDrag(start_x, start_y, end_x, end_y)
                # print(f"顺子 {cards} 已被选中多张")
                # print()
                time.sleep(0.2)

        if m_type["type"] == md.TYPE_1_SINGLE:
            pos_list = cards_pos_dict[cards[0]]
            if pos_list:
                x, y = pos_list[0]
                self.screenHelper.leftClick2(x, y)
                # print(f"卡牌 {cards} 已被点击选中")
                # print()
                time.sleep(0.2)

        await self.verify_and_reselect(initial_pos_dict, play_cards=cards)

    async def clickBtn(self, btnName):
        btnPos = self.screenHelper.getCapturePosition(areaName=btnName)
        result = await self.imageLocator.locate_match_on_screen(templateName=btnName, region=btnPos, confidence=0.7)
        if not result:
            return False
        
        self.screenHelper.leftClick(result[0], result[1])
        return True
