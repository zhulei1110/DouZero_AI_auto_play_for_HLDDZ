import ctypes
import win32gui
import win32ui

from ctypes import windll
from PIL import Image

from config import Config

class ScreenHelper:
    def __init__(self):
        self.config = Config.load()
        self.ScreenZoomRate = None
        self.Handle = win32gui.FindWindow(self.config.window_class_name, None)
        self.WindowWidth = self.config.window_width
        self.WindowHeight = self.config.window_height
        self.getZoomRate()

    def getZoomRate(self):
        self.ScreenZoomRate = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    
    # 聊天按钮区域
    def getChatBtnPos(self):
        left = int(self.WindowWidth * 0.91)
        top = int(self.WindowHeight * 0.925)
        width = int(self.WindowWidth * 0.089)
        height = int(self.WindowHeight * 0.08)
        return (left, top, width, height)
    
    # 底牌封面
    def getThreeCardFrontCoverPos(self):
        left = int(self.WindowWidth * 0.42)
        top = int(self.WindowHeight * 0.035)
        width = int(self.WindowWidth * 0.065)
        height = int(self.WindowHeight * 0.135)
        return (left, top, width, height)  

    # 3张底牌区域
    def getThreeCardsPos(self):
        left = int(self.WindowWidth * 0.41)
        top = int(self.WindowHeight * 0.035)
        width = self.WindowWidth - int(self.WindowWidth * 0.82)
        height = int(self.WindowHeight * 0.135)
        return (left, top, width, height)

    # 左边玩家地主标志
    def getLeftLandlordFlagPos(self):
        left = int(self.WindowWidth * 0.075)
        top = int(self.WindowHeight * 0.272)
        width = int(self.WindowWidth * 0.06)
        height = int(self.WindowHeight * 0.125)
        return (left, top, width, height)
    
    # 右边玩家地主标志
    def getRightLandlordFlagPos(self):
        left = int(self.WindowWidth * 0.858)
        top = int(self.WindowHeight * 0.272)
        width = int(self.WindowWidth * 0.06)
        height = int(self.WindowHeight * 0.125)
        return (left, top, width, height)
    
    # 我的地主标志
    def getMyLandlordFlagPos(self):
        left = int(self.WindowWidth * 0.002)
        top = int(self.WindowHeight * 0.789)
        width = int(self.WindowWidth * 0.06)
        height = int(self.WindowHeight * 0.125)
        return (left, top, width, height)

    # 我的手牌区域
    def getMyHandCardsPos(self):
        left = int(self.WindowWidth * 0.15)
        top = int(self.WindowHeight * 0.7)
        width = int(self.WindowWidth * 0.7)
        height = self.WindowHeight - top - int(self.WindowHeight * 0.1)
        return (left, top, width, height)

    # 右边玩家出牌区域
    def getRightPlayedCardsPos(self):
        left = int(self.WindowWidth * 0.5)
        top = int(self.WindowHeight * 0.33)
        width = self.WindowWidth - left - int(self.WindowWidth * 0.22)
        height = self.WindowHeight - top - int(self.WindowHeight * 0.47)
        return (left, top, width, height)

    # 左边玩家出牌区域
    def getLeftPlayedCardsPos(self):
        left = int(self.WindowWidth * 0.22)
        top = int(self.WindowHeight * 0.33)
        width = self.WindowWidth - left - int(self.WindowWidth * 0.5)
        height = self.WindowHeight - top - int(self.WindowHeight * 0.47)
        return (left, top, width, height)
    
    # 我的出牌区域
    def getMyPlayedCardsPos(self):
        left = int(self.WindowWidth * 0.3)
        top = int(self.WindowHeight * 0.5)
        width = self.WindowWidth - int(self.WindowWidth * 0.6)
        height = self.WindowHeight - top - int(self.WindowHeight * 0.3)
        return (left, top, width, height)

    # 对局结束输赢数量区域
    def getWinOrLoseBeansPos(self):
        left = int(self.WindowWidth * 0.749)
        top = int(self.WindowHeight * 0.27)
        width = int(self.WindowWidth * 0.194)
        height = int(self.WindowHeight * 0.07)
        return (left, top, width, height)

    # 我的 -> 不要
    def getMyPassPos(self):
        left = int(self.WindowWidth * 0.455)
        top = int(self.WindowHeight * 0.59)
        width = int(self.WindowWidth * 0.09)
        height = int(self.WindowHeight * 0.08)
        return (left, top, width, height)
    
    # 左边 -> 不要
    def getLeftPassPos(self):
        left = int(self.WindowWidth * 0.255)
        top = int(self.WindowHeight * 0.448)
        width = int(self.WindowWidth * 0.09)
        height = int(self.WindowHeight * 0.08)
        return (left, top, width, height)
    
    # 右边 -> 不要
    def getRightPassPos(self):
        left = int(self.WindowWidth * 0.66)
        top = int(self.WindowHeight * 0.448)
        width = int(self.WindowWidth * 0.09)
        height = int(self.WindowHeight * 0.08)
        return (left, top, width, height)

    # 要不起
    def getPassBtnPos(self):
        left = int(self.WindowWidth * 0.48)
        top = int(self.WindowHeight * 0.59)
        width = int(self.WindowWidth * 0.11)
        height = int(self.WindowHeight * 0.1)
        return (left, top, width, height)
    
    # 叫地主 or 抢地主
    def getCallLandlordBtnPos(self):
        left = int(self.WindowWidth * 0.345)
        top = int(self.WindowHeight * 0.595)
        width = int(self.WindowWidth * 0.11)
        height = int(self.WindowHeight * 0.1)
        return (left, top, width, height)
    
    # 不叫 or 不抢
    def getDoNotCallLandlordBtnPos(self):
        left = int(self.WindowWidth * 0.545)
        top = int(self.WindowHeight * 0.595)
        width = int(self.WindowWidth * 0.11)
        height = int(self.WindowHeight * 0.1)
        return (left, top, width, height)
    
    # 出牌
    def getPlayCardsBtnPos(self):
        left = int(self.WindowWidth * 0.295)
        top = int(self.WindowHeight * 0.59)
        width = int(self.WindowWidth * 0.11)
        height = int(self.WindowHeight * 0.1)
        return (left, top, width, height)
    
    # 不出
    def getDoNotPlayBtnPos(self):
        left = int(self.WindowWidth * 0.48)
        top = int(self.WindowHeight * 0.59)
        width = int(self.WindowWidth * 0.11)
        height = int(self.WindowHeight * 0.1)
        return (left, top, width, height)

    # 左边玩家剩余牌数
    def getLeftCardsNumPos(self):
        left = int(self.WindowWidth * 0.19)
        top = int(self.WindowHeight * 0.482)
        width = int(self.WindowWidth * 0.027)
        height = int(self.WindowHeight * 0.062)
        return (left, top, width, height)
    
    # 右边玩家剩余牌数
    def getRightCardsNumPos(self):
        left = int(self.WindowWidth * 0.785)
        top = int(self.WindowHeight * 0.482)
        width = int(self.WindowWidth * 0.025)
        height = int(self.WindowHeight * 0.06)
        return (left, top, width, height)

    # 快速开始按钮
    def getQuickStartBtnPos(self):
        left = int(self.WindowWidth * 0.792)
        top = int(self.WindowHeight * 0.875)
        width = int(self.WindowWidth * 0.192)
        height = int(self.WindowHeight * 0.1)
        return (left, top, width, height)
    
    # 开始游戏按钮
    def getStartGameBtnPos(self):
        left = int(self.WindowWidth * 0.514)
        top = int(self.WindowHeight * 0.605)
        width = int(self.WindowWidth * 0.15)
        height = int(self.WindowHeight * 0.1)
        return (left, top, width, height)
    
    # 继续游戏按钮
    def getContinueGameBtnPos(self):
        left = int(self.WindowWidth * 0.75)
        top = int(self.WindowHeight * 0.777)
        width = int(self.WindowWidth * 0.134)
        height = int(self.WindowHeight * 0.072)
        return (left, top, width, height)
    
    # 对局结束后各个玩家输赢豆
    def getBeansRegionsPos(self):
        # 我
        left1 = int(self.WindowWidth * 0.224)
        top1 = int(self.WindowHeight * 0.602)
        width1 = int(self.WindowWidth * 0.028)
        height1 = int(self.WindowHeight * 0.05)
        # 左
        left2 = int(self.WindowWidth * 0.226)
        top2 = int(self.WindowHeight * 0.268)
        width2 = int(self.WindowWidth * 0.028)
        height2 = int(self.WindowHeight * 0.05)
        # 右
        left3 = int(self.WindowWidth * 0.627)
        top3 = int(self.WindowHeight * 0.269)
        width3 = int(self.WindowWidth * 0.028)
        height3 = int(self.WindowHeight * 0.05)
        return [(left1, top1, width1, height1), (left2, top2, width2, height2), (left3, top3, width3, height3)]

    def getLoseTextPos(self):
        left = int(self.WindowWidth * 0.514)
        top = int(self.WindowHeight * 0.212)
        width = int(self.WindowWidth * 0.141)
        height = int(self.WindowHeight * 0.151)
        return (left, top, width, height)
    
    def getWinTextPos(self):
        left = int(self.WindowWidth * 0.514)
        top = int(self.WindowHeight * 0.212)
        width = int(self.WindowWidth * 0.141)
        height = int(self.WindowHeight * 0.126)
        return (left, top, width, height)

    def captureScreenshot(self, gameWindow, width, height):
        try:
            gwDC = win32gui.GetWindowDC(gameWindow)
            mfcDC = win32ui.CreateDCFromHandle(gwDC)
            saveDC = mfcDC.CreateCompatibleDC()
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            result = windll.user32.PrintWindow(gameWindow, saveDC.GetSafeHdc(), 3)
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            image = Image.frombuffer("RGB", (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(gameWindow, gwDC)
            return image, result
        except Exception as e:
            print("captureScreenshot error:", repr(e))
            return None, False

    def getScreenshot(self, region=None):
        try_count = 3
        success = False
        while try_count > 0 and not success:
            try:
                try_count -= 1
                self.Handle = win32gui.FindWindow(self.config.window_class_name, None)
                win32gui.SetActiveWindow(self.Handle)
                gameWindow = self.Handle
                left, top, right, bottom = win32gui.GetClientRect(gameWindow) 
                # print('left:', left, ', top:', top, ', right:', right, ', bottom:', bottom)
                width = right - left
                height = bottom - top
                if self.ScreenZoomRate == 1:
                    self.WindowWidth = width
                    self.WindowHeight = height
                    # win32gui.MoveWindow(gameWindow, left, top, self.WindowWidth, self.WindowHeight, True)
                    image, result = self.captureScreenshot(gameWindow, width, height)
                else:
                    # 窗口实际大小 * 缩放比例
                    captureWidth = int(width * self.ScreenZoomRate)
                    captureHeight = int(height * self.ScreenZoomRate)
                    self.WindowWidth = captureWidth
                    self.WindowHeight = captureHeight
                    image, result = self.captureScreenshot(gameWindow, captureWidth, captureHeight)
                
                # print('Screenshot captured successfully: ', image)

                if image is None:
                    raise Exception("getScreenshot failed")

                if region is not None:
                    image = image.crop((region[0], region[1], region[0] + region[2], region[1] + region[3]))

                if result:
                    success = True
                    return image, (left, top)

            except Exception as e:
                print("getScreenshot error:", repr(e))

        return None, (0, 0)