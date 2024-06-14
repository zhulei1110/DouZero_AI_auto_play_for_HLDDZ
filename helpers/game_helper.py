import cv2
import numpy as np
from PIL import Image

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
            resizeScale = scale
            if scale is not None and (card == "X" or card == "D"):
                if mark == "my":
                    resizeScale = scale *  0.88
                if mark == "three":
                    resizeScale = scale *  0.75

            template = self.templateImages[card]
            result = self.imageLocator.LocateAllOnImage(image, template, region=pos, scale=resizeScale, confidence=confidence)
            if len(result) > 0:
                count, posList = cards_filter(list(result), self.distance)
                if card == "X" or card == "D":
                    for p in posList:
                        classifier = CC.ColorClassifier(debug=True)
                        img1 = image[pos[1]:pos[1] + pos[3], pos[0]:pos[0] + pos[2]]
                        img2 = img1[p[1]:p[1] + p[3] - int((p[1] + p[3]) * 0.72), p[0]:p[0] + 16]
                        result = classifier.classify(img2)
                        for r in result:
                            if r[0] == "Red":
                                if r[1] > 0.6:
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
        myHandCardsPos = self.screenHelper.getMyHandCardsPos()
        image = cv2.cvtColor(np.asarray(screenshot), cv2.COLOR_RGB2BGR)
        scale = self.imageLocator.getResizeScale(image)
        my_hand_cards = self.findCards(image, myHandCardsPos, mark='my', scale=scale)
        return my_hand_cards
    
    def findThreeCards(self):
        screenshot, _ = self.screenHelper.getScreenshot()
        threeCardsPos = self.screenHelper.getThreeCardsPos()
        image = cv2.cvtColor(np.asarray(screenshot), cv2.COLOR_RGB2BGR)
        scale = self.imageLocator.getResizeScale(image) * 0.72      # 0.68 ~ 0.76
        three_cards = self.findCards(image, threeCardsPos, mark='three', scale=scale)
        return three_cards
    
    def findLeftPlayedCards(self):
        screenshot, _ = self.screenHelper.getScreenshot()
        leftPlayedCardsPos = self.screenHelper.getLeftPlayedCardsPos()
        image = cv2.cvtColor(np.asarray(screenshot), cv2.COLOR_RGB2BGR)
        scale = self.imageLocator.getResizeScale(image) * 0.89      # 0.84 ~ 0.93
        left_played_cards = self.findCards(image, leftPlayedCardsPos, mark='LPC', scale=scale)
        return left_played_cards
    

if __name__ == "__main__":
    gameHelper = GameHelper()
    
    my_hand_cards = gameHelper.findMyHandCards()
    print('my_hand_cards: ', my_hand_cards)

    three_cards = gameHelper.findThreeCards()
    print('three_cards: ', three_cards)

    left_played_cards = gameHelper.findLeftPlayedCards()
    print('left_played_cards: ', left_played_cards)