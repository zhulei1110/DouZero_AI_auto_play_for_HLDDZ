import cv2
import numpy as np
import time

from PIL import Image
from skimage.metrics import structural_similarity as ssim

import helpers.color_classifier as CC
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
        self.imageLocator = ImageLocator()
        self.screenHelper = ScreenHelper()
        self.templateImages = self.imageLocator.templateImages

    def findCards(self, image, pos, mark='my', scale=None, confidence=0.8):
        cards = ""
        D_king = 0
        X_king = 0

        for card in AllCards:
            scaleValue = scale
            confidenceValue = confidence
            if card == "X" or card == "D":
                confidenceValue = 0.73
                if scale is not None:
                    if mark == "my":
                        scaleValue = scale *  0.88
                    if mark == "myPlayedCards" or mark == "rightPlayedCards" or mark == "leftPlayedCards":
                        scaleValue = scale *  0.82
                    if mark == "three":
                        scaleValue = scale *  0.75
            
            # print(f'card:{card}, scale:{scaleValue}, confidence:{confidenceValue}')

            template = self.templateImages[card]
            result = self.imageLocator.LocateAllOnImage(image, template, region=pos, scale=scaleValue, confidence=confidenceValue)
            if len(result) > 0:
                count, posList = cards_filter(list(result), self.distance)
                if card == "X" or card == "D":
                    for p in posList:
                        classifier = CC.ColorClassifier(debug=True)

                        # p: (117, 49, 1334, 215) : (left, top, width, height)
                        # print('position:', p)
                        if mark == "my":
                            interceptHeight = p[1] + int(p[3] * 0.18)
                            interceptWidth = p[0] + int(p[2] * 0.022)
                        if mark == "playedCards":
                            self.screenHelper.WindowHeight
                            interceptHeight = p[1] + int(p[3] * 0.140)
                            interceptWidth = p[0] + int(p[2] * 0.035)
                        if mark == "three":
                            interceptHeight = p[1] + int(p[3] * 0.174)
                            interceptWidth = p[0] + int(p[2] * 0.052)
                        
                        # print(f'card_{card}_截取高度: ', interceptHeight - p[1])
                        # print(f'card_{card}_截取宽度: ', interceptWidth - p[0])

                        img1 = image[pos[1]:pos[1] + pos[3], pos[0]:pos[0] + pos[2]]
                        img2 = img1[p[1]:interceptHeight, p[0]:interceptWidth]

                        # 图片日志
                        posText = f'{p[1]}-{interceptHeight}_{p[0]}-{interceptWidth}'
                        cv2.imwrite(f'logs/color_classify_{card}.png', img1)
                        cv2.imwrite(f'logs/color_classify_{card}_{posText}.png', img2)

                        result = classifier.classify(img2)
                        for r in result:
                            if r[0] == "Red":
                                if r[1] > 0.7:
                                    D_king = 1
                                else:
                                    X_king = 1
                else:
                    cards += card[0] * count

        if X_king:
            cards += "X"
            cards = cards[-1] + cards[:-1]

        if D_king:
            cards += "D"
            cards = cards[-1] + cards[:-1]

        return cards
    
    def findMyHandCards(self):
        screenshot, _ = self.screenHelper.getScreenshot()
        # screenshot = Image.open('screenshots/test_my_hand_cards_for_X.png')
        myHandCardsPos = self.screenHelper.getMyHandCardsPos()

        image = cv2.cvtColor(np.asarray(screenshot), cv2.COLOR_RGB2BGR)
        scale = self.imageLocator.getResizeScale(image)

        my_hand_cards = self.findCards(image, myHandCardsPos, mark='my', scale=scale)
        # print(my_hand_cards)
        return my_hand_cards
    
    def findThreeCards(self):
        screenshot, _ = self.screenHelper.getScreenshot()
        threeCardsPos = self.screenHelper.getThreeCardsPos()

        image = cv2.cvtColor(np.asarray(screenshot), cv2.COLOR_RGB2BGR)
        scale = self.imageLocator.getResizeScale(image) * 0.72      # 0.68 ~ 0.76

        three_cards = self.findCards(image, threeCardsPos, mark='three', scale=scale)
        return three_cards
    
    def findRightPlayedCards(self):
        screenshot, _ = self.screenHelper.getScreenshot()
        rightPlayedCardsPos = self.screenHelper.getRightPlayedCardsPos()

        image = cv2.cvtColor(np.asarray(screenshot), cv2.COLOR_RGB2BGR)
        scale = self.imageLocator.getResizeScale(image) * 0.89      # 0.84 ~ 0.93

        right_played_cards = self.findCards(image, rightPlayedCardsPos, mark='playedCards', scale=scale)
        return right_played_cards
    
    def findLeftPlayedCards(self):
        screenshot, _ = self.screenHelper.getScreenshot()
        # screenshot = Image.open('screenshots/test_left_played_cards_for_X.png')
        leftPlayedCardsPos = self.screenHelper.getLeftPlayedCardsPos()

        image = cv2.cvtColor(np.asarray(screenshot), cv2.COLOR_RGB2BGR)
        scale = self.imageLocator.getResizeScale(image) * 0.89      # 0.84 ~ 0.93

        left_played_cards = self.findCards(image, leftPlayedCardsPos, mark='playedCards', scale=scale)
        # print(left_played_cards)
        return left_played_cards
    
    def findMyPlayedCards(self):
        screenshot, _ = self.screenHelper.getScreenshot()
        # screenshot = Image.open('screenshots/test_my_played_cards_for_D.png')
        myPlayedCardsPos = self.screenHelper.getMyPlayedCardsPos()

        image = cv2.cvtColor(np.asarray(screenshot), cv2.COLOR_RGB2BGR)
        scale = self.imageLocator.getResizeScale(image) * 0.89      # 0.84 ~ 0.93

        my_played_cards = self.findCards(image, myPlayedCardsPos, mark='playedCards', scale=scale)
        # print(my_played_cards)
        return my_played_cards

    def compareImage(img1, img2):
        # 转换为灰度图
        gray1 = cv2.cvtColor(np.asarray(img1), cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(np.asarray(img2), cv2.COLOR_BGR2GRAY)

        # 使用结构相似性指数（SSIM）比较相似度
        ssim_index, _ = ssim(gray1, gray2, full=True)
        if ssim_index < 0.99:
            return True

        return False
    
    def haveAnimation(self, waitingTime=0.1, regions=None):
        if regions is None:
            return False
        
        image, _ = self.screenHelper.getScreenshot()
        previousImage = image
        for i in range(2):
            time.sleep(waitingTime)
            image, _ = self.screenHelper.getScreenshot()
            for region in regions:
                if self.compareImage(image.crop(region), previousImage.crop(region)):
                    return True
            previousImage = image

        return False

if __name__ == "__main__":
    gameHelper = GameHelper()
    
    my_hand_cards = gameHelper.findMyHandCards()
    print('my_hand_cards: ', my_hand_cards)

    three_cards = gameHelper.findThreeCards()
    print('three_cards: ', three_cards)

    print()
    left_played_cards = gameHelper.findLeftPlayedCards()
    print('left_played_cards: ', left_played_cards)

    print()
    right_played_cards = gameHelper.findRightPlayedCards()
    print('right_played_cards: ', right_played_cards)

    print()
    my_played_cards = gameHelper.findMyPlayedCards()
    print('my_played_cards: ', my_played_cards)

    print()