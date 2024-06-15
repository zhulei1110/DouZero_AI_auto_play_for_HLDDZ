import asyncio
from PIL import Image
from PyQt5.QtCore import QThread
from helpers.image_locator import ImageLocator
from helpers.screen_helper import ScreenHelper
from worker import Worker

# async def run_thread(thread):
#     thread.start()
#     while thread.isRunning():
#         await asyncio.sleep(0.1)

# 玩家角色：0-地主上家, 1-地主, 2-地主下家
def findMyPostion():
    imageLocator = ImageLocator()
    screenHelper = ScreenHelper()
    screenHelper.getScreenshot()

    rightLandlordHatRegion = screenHelper.getLeftLandlordFlagPos()
    testImage = Image.open('test123.png')
    result1 = imageLocator.LocateOnScreen("landlord_hat", rightLandlordHatRegion, img=testImage)
    if result1 is not None:
        return 0 # 如果右边是地主，我就是地主上家

    leftLandlordHatRegion = screenHelper.getLeftLandlordFlagPos()
    result2 = imageLocator.LocateOnScreen("landlord_hat", leftLandlordHatRegion, img=testImage)
    if result2 is not None:
        return 2 # 如果左边是地主，我就是地主下家

    myLandlordHatRegion = screenHelper.getMyLandlordFlagPos()
    result3 = imageLocator.LocateOnScreen("landlord_hat", myLandlordHatRegion, img=testImage)
    if result3 is not None:
        return 1

async def main():
    my_position_code = findMyPostion()
    print("my_position_code: ", my_position_code)

    # thread = Worker()
    # thread.auto_sign = True

    # try:
    #     await run_thread(thread)
    # finally:
    #     thread.stop()
    #     thread.wait()

if __name__ == '__main__':
    # import signal
    # import sys

    # print('ddz card recorder started')

    # # Handle keyboard interruption to stop the thread
    # def signal_handler(sig, frame):
    #     print('You pressed Ctrl+C!')
    #     asyncio.get_event_loop().stop()

    # signal.signal(signal.SIGINT, signal_handler)

    # try:
        asyncio.run(main())
    # except (KeyboardInterrupt, SystemExit):
    #     print('Shutting down gracefully...')
    # finally:
    #     print('ddz card recorder stopped')
