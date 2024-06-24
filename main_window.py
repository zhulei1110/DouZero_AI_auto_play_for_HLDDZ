from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton
from worker import WorkerThread

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tutorial")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Doudizhu AI Worker")
        self.setGeometry(100, 100, 600, 480)

        self.button = QPushButton("Start Thread", self)
        self.button.clicked.connect(self.handle_button)

        layout = QVBoxLayout()
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.workerThread = None

    def handle_button(self):
        if self.workerThread is None:
            self.workerThread = WorkerThread()

        if not self.workerThread.isRunning():
            # self.workerThread.finished_signal.connect(self.thread_finished)
            self.workerThread.start()
            self.button.setText("Stop Thread")
        else:
            self.workerThread.stop_task()
            self.workerThread.quit()
            self.workerThread.wait()
            self.button.setText("Start Thread")

    # def thread_finished(self):
    #     self.button.setText("Start Thread")