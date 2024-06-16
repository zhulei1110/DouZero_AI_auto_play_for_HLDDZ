import asyncio
from PIL import Image
from PyQt5.QtCore import QThread

from helpers.image_locator import ImageLocator
from helpers.screen_helper import ScreenHelper

from worker import Worker

async def run_thread(thread):
    thread.start()
    while thread.isRunning():
        await asyncio.sleep(0.1)

async def main():
    thread = Worker()
    thread.auto_sign = True

    try:
        await run_thread(thread)
    finally:
        thread.stop()
        thread.wait()

if __name__ == '__main__':
    import signal
    import sys

    print('ddz card recorder started')

    # Handle keyboard interruption to stop the thread
    def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        asyncio.get_event_loop().stop()

    signal.signal(signal.SIGINT, signal_handler)

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Shutting down gracefully...')
    finally:
        print('ddz card recorder stopped')
