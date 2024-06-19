import asyncio
import sys

# import qasync
# from PyQt5.QtWidgets import QApplication

from worker_controller import WorkerController

async def main():
    controller = WorkerController()
    await controller.start_thread()

    while True:
        await asyncio.sleep(1)

def signal_handler(sig, frame):
    print(f'sig: {sig}')
    print(f'frame: {frame}')
    print('You pressed `Ctrl + C`!')

    asyncio.get_event_loop().stop()

if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal_handler)

    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('程序已正常关闭')
