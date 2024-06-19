import cv2
import numpy as np
import time

from PIL import Image
from skimage.metrics import structural_similarity as ssim

# import helpers.color_classifier as CC
from helpers.color_recognizer import ColorRecognizer
from helpers.image_locator import ImageLocator
from helpers.screen_helper import ScreenHelper

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

class GameHelper:
    def __init__(self):
        self.distance = 30
        self.colorRecognizer = ColorRecognizer()
        self.imageLocator = ImageLocator()
        self.screenHelper = ScreenHelper()
        self.templateImages = self.imageLocator.templateImages

    def findCards(self, image, pos, mark=None, scale=None, confidence=0.8):
        if mark is None:
            return None
        
        cards = ""
        D_king = 0
        X_king = 0

        if scale is None:
            scale = self.imageLocator.get_resize_scale(image)

        for card in AllCards:
            templateName = f'{mark}_{card}'
            template = self.templateImages[templateName]
            result = self.imageLocator.locate_all_match_on_image(image, template, templateName=templateName, region=pos, scale=scale, confidence=confidence)
            if len(result) > 0:
                count, posList = cards_filter(list(result), self.distance)
                if card == "X" or card == "D":
                    for p in posList:
                        # print('position:', p)
                        # p: (117, 49, 1334, 215) : (left, top, width, height)
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
                        # img1Key = self.imageLocator.compute_image_unique_key(img1)
                        # posText = f'{p[1]}-{interceptHeight}_{p[0]}-{interceptWidth}'
                        # cv2.imwrite(f'screenshots/logs/cc_{card}_{img1Key}_img1.png', img1)
                        # cv2.imwrite(f'screenshots/logs/cc_{card}_{img1Key}_{posText}_img2.png', img2)

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
    
    def findThreeCards(self):
        screenshot, _ = self.screenHelper.getScreenshot()
        threeCardsPos = self.screenHelper.getThreeCardsPos()
        image = cv2.cvtColor(np.asarray(screenshot), cv2.COLOR_RGB2BGR)
        three_cards = self.findCards(image, threeCardsPos, mark='three')
        # print(three_cards)
        return three_cards
    
    def findMyHandCards(self):
        screenshot, _ = self.screenHelper.getScreenshot()
        myHandCardsPos = self.screenHelper.getMyHandCardsPos()
        image = cv2.cvtColor(np.asarray(screenshot), cv2.COLOR_RGB2BGR)
        my_hand_cards = self.findCards(image, myHandCardsPos, mark='my')
        # print(my_hand_cards)
        return my_hand_cards
    
    def findRightPlayedCards(self):
        screenshot, _ = self.screenHelper.getScreenshot()
        rightPlayedCardsPos = self.screenHelper.getRightPlayedCardsPos()
        image = cv2.cvtColor(np.asarray(screenshot), cv2.COLOR_RGB2BGR)
        right_played_cards = self.findCards(image, rightPlayedCardsPos, mark='play')
        # print('right_played_cards:', right_played_cards)
        return right_played_cards
    
    def findLeftPlayedCards(self):
        screenshot, _ = self.screenHelper.getScreenshot()
        leftPlayedCardsPos = self.screenHelper.getLeftPlayedCardsPos()
        image = cv2.cvtColor(np.asarray(screenshot), cv2.COLOR_RGB2BGR)
        left_played_cards = self.findCards(image, leftPlayedCardsPos, mark='play')
        # print('left_played_cards:', left_played_cards)
        return left_played_cards
    
    def findMyPlayedCards(self):
        screenshot, _ = self.screenHelper.getScreenshot()
        myPlayedCardsPos = self.screenHelper.getMyPlayedCardsPos()
        image = cv2.cvtColor(np.asarray(screenshot), cv2.COLOR_RGB2BGR)
        my_played_cards = self.findCards(image, myPlayedCardsPos, mark='play')
        # print('my_played_cards:', my_played_cards)
        return my_played_cards

    def findRightBuchu(self):
        screenshot, _ = self.screenHelper.getScreenshot()
        rightPassPos = self.screenHelper.getRightBuchuTextPos()

        image = cv2.cvtColor(np.asarray(screenshot), cv2.COLOR_RGB2BGR)
        scale = self.imageLocator.get_resize_scale(image)

        templateName = 'buchu'
        template = self.templateImages[templateName]
        result = self.imageLocator.locate_first_match_on_image(image, template, templateName=templateName, region=rightPassPos, scale=scale)
        return result
    
    def findLeftBuchu(self):
        screenshot, _ = self.screenHelper.getScreenshot()
        leftPassPos = self.screenHelper.getLeftBuchuTextPos()

        image = cv2.cvtColor(np.asarray(screenshot), cv2.COLOR_RGB2BGR)
        scale = self.imageLocator.get_resize_scale(image)

        templateName = 'buchu'
        template = self.templateImages[templateName]
        result = self.imageLocator.locate_first_match_on_image(image, template, templateName=templateName, region=leftPassPos, scale=scale)
        return result
    
    def findMyBuchu(self):
        screenshot, _ = self.screenHelper.getScreenshot()
        myPassPos = self.screenHelper.getMyBuchuTextPos()

        image = cv2.cvtColor(np.asarray(screenshot), cv2.COLOR_RGB2BGR)
        scale = self.imageLocator.get_resize_scale(image)

        templateName = 'buchu'
        template = self.templateImages[templateName]
        result = self.imageLocator.locate_first_match_on_image(image, template, templateName=templateName, region=myPassPos, scale=scale)
        return result

    def compare_image(self, img1, img2):
        # 转换为灰度图
        gray1 = cv2.cvtColor(np.asarray(img1), cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(np.asarray(img2), cv2.COLOR_BGR2GRAY)

        cv2.imwrite(f'screenshots/logs/compare_image_{self.imageLocator.compute_image_unique_key(gray1)}.png', gray1)
        cv2.imwrite(f'screenshots/logs/compare_image_{self.imageLocator.compute_image_unique_key(gray2)}.png', gray2)

        # 使用结构相似性指数（SSIM）比较相似度
        ssim_index, _ = ssim(gray1, gray2, full=True)
        if ssim_index < 0.99:
            return True

        return False
    
    def have_animation(self, screenshotWaitingTime=0.2, regions=None):
        if regions is None:
            return False
        
        image, _ = self.screenHelper.getScreenshot()
        previousImage = image
        for i in range(2):
            time.sleep(screenshotWaitingTime)
            image, _ = self.screenHelper.getScreenshot()
            for region in regions:
                if self.compare_image(image.crop(region), previousImage.crop(region)):
                    return True
            previousImage = image

        return False

# if __name__ == "__main__":
#     gameHelper = GameHelper()
#     gameHelper.findThreeCards()
#     gameHelper.findMyHandCards()
#     gameHelper.findRightPlayedCards()
#     gameHelper.findLeftPlayedCards()
#     gameHelper.findMyPlayedCards()