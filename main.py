import asyncio
import sys
import qasync

from main_window import MainWindow

if __name__ == '__main__':
    app = qasync.QApplication(sys.argv)

    mainWindow = MainWindow()
    mainWindow.show()

    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    with loop:
        loop.run_forever()

    # Execute application
    sys.exit(app.exec_())
