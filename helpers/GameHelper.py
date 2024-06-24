import cv2
import numpy as np
import time

from enum import Enum
from skimage.metrics import structural_similarity as ssim

from helpers.ColorRecognizer import ColorRecognizer
from helpers.ImageLocator import ImageLocator
from helpers.ScreenHelper import ScreenHelper, ScreenshotArea

AllCards = ['D', 'X', '2', 'A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3']

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

    async def __findCards(self, image, pos, mark, scale=None, confidence=0.8):
        if mark is None:
            return None
        
        cards = ""
        D_king = 0
        X_king = 0

        if scale is None:
            scale = await self.imageLocator.get_resize_scale(image)

        for card in AllCards:
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
                        if self.screenHelper.config.dx_color_compare_logs:
                            img1Key = self.screenHelper.compute_image_unique_key(img1)
                            posText = f'{p[1]}-{interceptHeight}_{p[0]}-{interceptWidth}'
                            cv2.imwrite(f'screenshots/logs/dx_cc_{card}_{img1Key}_img1.png', img1)
                            cv2.imwrite(f'screenshots/logs/dx_cc_{card}_{img1Key}_{posText}_img2.png', img2)

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

        # 图片日志
        if self.screenHelper.config.image_locate_logs:
            cv2.imwrite(f'screenshots/logs/compare_image_{self.screenHelper.compute_image_unique_key(gray1)}.png', gray1)
            cv2.imwrite(f'screenshots/logs/compare_image_{self.screenHelper.compute_image_unique_key(gray2)}.png', gray2)

        # 使用结构相似性指数（SSIM）比较相似度
        ssim_index, _ = ssim(gray1, gray2, full=True)
        if ssim_index < 0.99:
            return True

        return False
    
    async def __haveAnimation(self, intervals=0.2, regions=None):
        if regions is None:
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
            animationPos3 = self.screenHelper.getCapturePosition2(ScreenshotArea.RIGHT_PLAYED_ANIMATION_2.value)
            haveAnimation = await self.__haveAnimation(intervals, regions=[animationPos1, animationPos2, animationPos3])

        if areaName == AnimationArea.LEFT_PLAYED_ANIMATION.value:
            animationPos1 = self.screenHelper.getCapturePosition2(ScreenshotArea.LEFT_PLAYED_CARDS.value)
            animationPos2 = self.screenHelper.getCapturePosition2(ScreenshotArea.LEFT_PLAYED_ANIMATION_1.value)
            animationPos3 = self.screenHelper.getCapturePosition2(ScreenshotArea.LEFT_PLAYED_ANIMATION_2.value)
            haveAnimation = await self.__haveAnimation(intervals, regions=[animationPos1, animationPos2, animationPos3])

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
    
    async def clickBtn(self, btnName):
        btnPos = self.screenHelper.getCapturePosition(areaName=btnName)
        result = await self.imageLocator.locate_match_on_screen(templateName=btnName, region=btnPos, confidence=0.7)
        if result is None:
            return False
        
        self.screenHelper.leftClick(result[0], result[1])
        return True