import asyncio
from helpers.screen_helper import ScreenHelper

async def main():
    screenHelper = ScreenHelper()
    image, position = screenHelper.getScreenshot()
    print('image 1: ', image, ', position: ', position)

    passBtnPos = screenHelper.getThreeCardsPos()
    print('passBtnPos: ', passBtnPos)

    image, position = screenHelper.getScreenshot(passBtnPos)
    print('image 2: ', image, ', position: ', position)

if __name__ == '__main__':
    print('ddz card recorder started')
    asyncio.run(main())
    print('ddz card recorder stopped')
