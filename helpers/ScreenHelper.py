import asyncio
import cv2
import numpy as np
import pyautogui
import win32gui
import win32ui

from enum import Enum
from concurrent.futures import ThreadPoolExecutor
from ctypes import windll
from PIL import Image

from config import Config

class ScreenshotArea(Enum):
    QUICK_START_BTN = "quick_start_btn"
    CHAT_BTN = "chat_btn"
    START_GAME_BTN = "start_game_btn"
    MING_PAI_4S_BTN = "ming_pai_4s_btn"
    CALL_LANDLORD_BTN = "call_landlord_btn"
    NOT_CALL_LANDLORD_BTN = "not_call_landlord_btn"
    SCRAMBLE_LANDLORD_BTN = "scramble_landlord_btn"
    NOT_SCRAMBLE_LANDLORD_BTN = "not_scramble_landlord_btn"
    REDOUBLE_BTN = "redouble_btn"
    NOT_REDOUBLE_BTN = "not_redouble_btn"
    SUPER_REDOUBLE_BTN = "super_redouble_btn"
    MING_PAI_BTN = "ming_pai_btn"
    PLAY_CARDS_BTN = "play_cards_btn"
    NOT_PLAY_CARDS_BTN = "not_play_cards_btn"
    CAN_NOT_PLAY_CARDS_BTN = "can_not_play_cards_btn"
    CONTINUE_GAME_BTN = "continue_game_btn"
    THREE_CARDS_FRONT_COVER = "three_cards_front_cover"
    THREE_CARDS = "three_cards"
    RIGHT_LANDLORD_FLAG = "right_landlord_flag"
    LEFT_LANDLORD_FLAG = "left_landlord_flag"
    MY_LANDLORD_FLAG = "my_landlord_flag"
    MY_HAND_CARDS = "my_hand_cards"
    RIGHT_REMAINING_CARDS_COUNT = "right_remaining_cards_count"
    LEFT_REMAINING_CARDS_COUNT = "left_remaining_cards_count"
    RIGHT_PLAYED_CARDS = "right_played_cards"
    LEFT_PLAYED_CARDS = "left_played_cards"
    MY_PLAYED_CARDS = "my_played_cards"
    RIGHT_PLAYED_TEXT = "right_played_text"
    LEFT_PLAYED_TEXT = "left_played_text"
    MY_PLAYED_TEXT = "my_played_text"
    RIGHT_PLAYED_ANIMATION_1 = "right_played_animation_1"
    RIGHT_PLAYED_ANIMATION_2 = "right_played_animation_2"
    LEFT_PLAYED_ANIMATION_1 = "left_played_animation_1"
    LEFT_PLAYED_ANIMATION_2 = "left_played_animation_2"
    MY_PLAYED_ANIMATION = "my_played_animation"
    GAME_RESULT = "game_result"

class ScreenHelper:
    def __init__(self):
        self.config = Config.load()
        self.BaseWidth = 1920
        self.BaseHeight = 1080
        self.WindowLeft = 0
        self.WindowTop = 0
        self.WindowWidth = self.config.window_width
        self.WindowHeight = self.config.window_height
        self.ScreenshotAreas = self.config.screenshot_areas
        self.Handle = win32gui.FindWindow(self.config.window_class_name, None)
        self.ScreenZoomRate = None
        self.getZoomRate()

    def getZoomRate(self):
        self.ScreenZoomRate = windll.shcore.GetScaleFactorForDevice(0) / 100
    
    def compute_image_unique_key(self, image):
        image_bytes = image.tobytes()
        hash_value = hash(image_bytes)
        return hash_value

    async def getScreenshot(self, region=None):
        loop = asyncio.get_running_loop()
        with ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(pool, self._getScreenshot_sync, region)
        return result

    def _getScreenshot_sync(self, region=None):
        try_count = 3
        success = False
        while try_count > 0 and not success:
            try:
                try_count -= 1
                
                self.Handle = win32gui.FindWindow(self.config.window_class_name, None)
                if not self.Handle:
                    raise Exception("invalid window handle")
                
                win32gui.SetActiveWindow(self.Handle)
                gameWindow = self.Handle

                left, top, right, bottom = win32gui.GetClientRect(gameWindow)
                client_point = win32gui.ClientToScreen(gameWindow, (left, top))

                self.WindowLeft = client_point[0]
                self.WindowTop = client_point[1]

                width = right - left
                height = bottom - top
                self.WindowWidth = width
                self.WindowHeight = height

                image, result = self.captureScreenshot(gameWindow, self.WindowWidth, self.WindowHeight)

                if image is None:
                    raise Exception("get screenshot failed")

                if region is not None:
                    image = image.crop((region[0], region[1], region[0] + region[2], region[1] + region[3]))

                # 图片日志
                if self.config.screenshot_logs:
                    imageKey = self.compute_image_unique_key(image)
                    saveImage = cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
                    if region is not None:
                        regionText = str(region).replace(' ', '').replace(',', '-')
                        cv2.imwrite(f'screenshots/logs/{imageKey}_{regionText}.png', saveImage)
                    else:
                        cv2.imwrite(f'screenshots/logs/{imageKey}_no_region.png', saveImage)

                if result:
                    success = True
                    return image, (left, top)

            except Exception as e:
                print("get screenshot error:", repr(e))

        return None, (0, 0)

    def captureScreenshot(self, window, width, height):
        try:
            gwDC = win32gui.GetWindowDC(window)
            mfcDC = win32ui.CreateDCFromHandle(gwDC)
            saveDC = mfcDC.CreateCompatibleDC()
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            result = windll.user32.PrintWindow(window, saveDC.GetSafeHdc(), 3)
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            image = Image.frombuffer("RGB", (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(window, gwDC)
            return image, result
        except Exception as e:
            print("capture screenshot error:", repr(e))
            return None, False

    def parse_and_calculate(self, areaStr):
        # 解析输入字符串
        values = areaStr.split(',')
        left_ratio = round(float(values[0]), 4)
        top_ratio = round(float(values[1]), 4)
        width_ratio = round(float(values[2]), 4)
        height_ratio = round(float(values[3]), 4)
        
        # 计算具体值
        left = int(left_ratio * self.WindowWidth)
        top = int(top_ratio * self.WindowHeight)
        width = int(width_ratio * self.WindowWidth)
        height = int(height_ratio * self.WindowHeight)
        
        return left, top, width, height

    def getCapturePosition(self, areaName):
        areaStr = self.ScreenshotAreas[areaName]
        left, top, width, height = self.parse_and_calculate(areaStr)
        return (left, top, width, height)
    
    def getCapturePosition2(self, areaName):
        areaStr = self.ScreenshotAreas[areaName]
        left, top, width, height = self.parse_and_calculate(areaStr)
        return (left, top, left + width, top + height)

    def leftClick(self, rel_x, rel_y):
        win32gui.SetActiveWindow(self.Handle)

        abs_x = self.WindowLeft + rel_x + 10
        abs_y = self.WindowTop + rel_y + 5

        # 移动鼠标到指定位置并点击
        pyautogui.click(abs_x, abs_y)