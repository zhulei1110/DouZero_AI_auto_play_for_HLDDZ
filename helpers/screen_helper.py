import ctypes
import win32gui
import win32ui

from ctypes import windll
from PIL import Image

from config import Config

class ScreenHelper:
    def __init__(self):
        self.ScreenZoomRate = None
        self.config = Config.load()
        self.Handle = win32gui.FindWindow(self.config.window_class_name, None)
        self.WindowWidth = self.config.window_width
        self.WindowHeight = self.config.window_height
        self.getZoomRate()

    def getZoomRate(self):
        self.ScreenZoomRate = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
    
    # 3张底牌区域
    def getThreeCardsPos(self):
        left = int(self.WindowWidth * 0.42)
        top = int(self.WindowHeight * 0.04)
        width = self.WindowWidth - int(self.WindowWidth * 0.84)
        height = int(self.WindowHeight * 0.13)
        return (left, top, width, height)

    # 我的手牌区域
    def getMyHandCardsPos(self):
        left = int(self.WindowWidth * 0.15)
        top = int(self.WindowHeight * 0.7)
        width = int(self.WindowWidth * 0.7)
        height = self.WindowHeight - top - int(self.WindowHeight * 0.1)
        return (left, top, width, height)

    # 我的出牌区域
    def getMyPlayedCardsPos(self):
        left = int(self.WindowWidth * 0.3)
        top = int(self.WindowHeight * 0.5)
        width = self.WindowWidth - int(self.WindowWidth * 0.6)
        height = self.WindowHeight - top - int(self.WindowHeight * 0.3)
        return (left, top, width, height)

    # 左边玩家出牌区域
    def getLeftPlayedCardsPos(self):
        left = int(self.WindowWidth * 0.22)
        top = int(self.WindowHeight * 0.33)
        width = self.WindowWidth - left - int(self.WindowWidth * 0.5)
        height = self.WindowHeight - top - int(self.WindowHeight * 0.47)
        return (left, top, width, height)
    
    # 右边玩家出牌区域
    def getRightPlayedCardsPos(self):
        left = int(self.WindowWidth * 0.5)
        top = int(self.WindowHeight * 0.33)
        width = self.WindowWidth - left - int(self.WindowWidth * 0.22)
        height = self.WindowHeight - top - int(self.WindowHeight * 0.47)
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

    # 左边玩家地主标志
    def getLeftLandlordFlagPos(self):
        left = int(self.WindowWidth * 0.08)
        top = int(self.WindowHeight * 0.28)
        width = int(self.WindowWidth * 0.05)
        height = int(self.WindowHeight * 0.1)
        return (left, top, width, height)
    
    # 右边玩家地主标志
    def getRightLandlordFlagPos(self):
        left = int(self.WindowWidth * 0.857)
        top = int(self.WindowHeight * 0.285)
        width = int(self.WindowWidth * 0.05)
        height = int(self.WindowHeight * 0.1)
        return (left, top, width, height)
    
    # 我的地主标志
    def getMyLandlordFlagPos(self):
        left = int(self.WindowWidth * 0.004)
        top = int(self.WindowHeight * 0.8)
        width = int(self.WindowWidth * 0.05)
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
                
                print('captureScreenshot image: ', image)
                print('captureScreenshot result: ', result)

                if image is None:
                    raise Exception("getScreenshot failed")
                
                # image.save('screenshot.png')
                # image = image.resize((self.WindowWidth, self.WindowHeight))
                
                if region is not None:
                    image = image.crop((region[0], region[1], region[0] + region[2], region[1] + region[3]))
                    # image('screenshot_region.png')

                if result:
                    success = True
                    return image, (left, top)

            except Exception as e:
                print("getScreenshot error:", repr(e))

        return None, (0, 0)