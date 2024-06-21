import asyncio
import sys

import qasync
from PyQt5.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel

from worker_thread import WorkerThread

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("线程控制示例")
        self.setGeometry(100, 100, 300, 200)

        self.button = QPushButton("启动线程", self)
        self.button.clicked.connect(self.handle_button)
        self.label = QLabel("状态: 等待中", self)

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        layout.addWidget(self.label)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.worker_thread = None

    def handle_button(self):
        if not self.worker_thread or not self.worker_thread.isRunning():
            self.worker_thread = WorkerThread()
            self.worker_thread.finished_signal.connect(self.thread_finished)
            self.worker_thread.start()
            self.button.setText("停止线程")
        else:
            self.worker_thread.stop()
            self.worker_thread.quit()
            self.worker_thread.wait()
            self.button.setText("启动线程")

    def thread_finished(self):
        self.label.setText("状态: 线程已完成")
        self.button.setText("启动线程")


if __name__ == '__main__':
    app = qasync.QApplication(sys.argv)

    main_window = MainWindow()
    main_window.show()

    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    with loop:
        loop.run_forever()

    sys.exit(app.exec_())
