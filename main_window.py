from PyQt5 import QtWidgets, QtGui, QtCore

from helpers.ScreenHelper import ScreenHelper
from worker import WorkerThread


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.screenHelper = ScreenHelper()
        self.max_width = 778
        self.max_height = 480

        self.setWindowTitle("QQ 游戏大厅 - 欢乐斗地主 AI 辅助")
        self.setGeometry(320, 160, self.max_width, self.max_height)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout  = QtWidgets.QVBoxLayout(central_widget)

        self.create_comboBox()
        self.create_card_table()
        self.create_three_card_label()
        self.create_three_tables()
        self.create_actions()

        # self.startBtn = QtWidgets.QPushButton("Start Thread", self)
        # self.startBtn.clicked.connect(self.handle_button)
        # self.main_layout.addWidget(self.startBtn)

        self.workerThread = None
        self.screenHelper.setWindowSize()

    # 禁用窗口拖拽和缩放
    def resizeEvent(self, event):
        self.setFixedSize(self.max_width, self.max_height)

    def moveEvent(self, event):
        self.move(self.x(), self.y())

    def create_comboBox(self):
        combo_layout = QtWidgets.QHBoxLayout()
        combo_layout.setContentsMargins(0, 0, 0, 10)

        label_font = QtGui.QFont("微软雅黑", 8)
        comboBox_font = QtGui.QFont("微软雅黑", 9)

        # 叫地主策略
        layout1 = QtWidgets.QVBoxLayout()
        label1 = QtWidgets.QLabel("叫地主策略：")
        label1.setFont(label_font)
        label1.setAlignment(QtCore.Qt.AlignLeft)

        comboBox1 = QtWidgets.QComboBox()
        comboBox1.addItems(["保守（0.7）", "平稳（0.6）", "激进（0.5）"])
        comboBox1.setFont(comboBox_font)
        comboBox1.setFixedWidth(180)
        comboBox1.setCurrentIndex(1)

        layout1.addWidget(label1)
        layout1.addWidget(comboBox1)
        layout1.setAlignment(QtCore.Qt.AlignLeft)
        combo_layout.addLayout(layout1)

        # 加倍x2策略
        layout2 = QtWidgets.QVBoxLayout()
        label2 = QtWidgets.QLabel("加倍 x2 策略：")
        label2.setFont(label_font)
        label2.setAlignment(QtCore.Qt.AlignLeft)

        comboBox2 = QtWidgets.QComboBox()
        comboBox2.addItems(["保守（0.75）", "平稳（0.65）", "激进（0.55）"])
        comboBox2.setFont(comboBox_font)
        comboBox2.setFixedWidth(180)
        comboBox2.setCurrentIndex(1)

        layout2.addWidget(label2)
        layout2.addWidget(comboBox2)
        layout2.setAlignment(QtCore.Qt.AlignLeft)
        combo_layout.addLayout(layout2)

        # 加倍x4策略
        layout3 = QtWidgets.QVBoxLayout()
        label3 = QtWidgets.QLabel("加倍 x4 策略：")
        label3.setFont(label_font)
        label3.setAlignment(QtCore.Qt.AlignLeft)

        comboBox3 = QtWidgets.QComboBox()
        comboBox3.addItems(["保守（0.8）", "平稳（0.7）", "激进（0.6）"])
        comboBox3.setFont(comboBox_font)
        comboBox3.setFixedWidth(180)
        comboBox3.setCurrentIndex(0)

        layout3.addWidget(label3)
        layout3.addWidget(comboBox3)
        layout3.setAlignment(QtCore.Qt.AlignLeft)
        combo_layout.addLayout(layout3)

        # 明牌策略
        layout4 = QtWidgets.QVBoxLayout()
        label4 = QtWidgets.QLabel("明牌策略：")
        label4.setFont(label_font)
        label4.setAlignment(QtCore.Qt.AlignLeft)

        comboBox4 = QtWidgets.QComboBox()
        comboBox4.addItems(["保守（1.0）", "平稳（0.95）", "激进（0.9）"])
        comboBox4.setFont(comboBox_font)
        comboBox4.setFixedWidth(180)
        comboBox4.setCurrentIndex(0)

        layout4.addWidget(label4)
        layout4.addWidget(comboBox4)
        layout4.setAlignment(QtCore.Qt.AlignLeft)
        combo_layout.addLayout(layout4)

        combo_layout.addStretch()
        self.main_layout.addLayout(combo_layout)

    def create_card_table(self):
        # 创建 QTableWidget
        self.tableWidget = QtWidgets.QTableWidget(self)
        self.tableWidget.setGeometry(0, 0, 750, 100)  # 设置表格位置和大小
        self.tableWidget.setFixedHeight(102)
        self.tableWidget.setRowCount(2)
        self.tableWidget.setColumnCount(15)

        # 隐藏表头和行头
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setVisible(False)

        # 去除网格线
        self.tableWidget.setShowGrid(False)

        # 设置行高和列宽
        for row in range(2):
            self.tableWidget.setRowHeight(row, 50)
        for col in range(15):
            self.tableWidget.setColumnWidth(col, 50)

        # 设置卡牌名称和数量
        card_names = ['大', '小', '2', 'A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3']
        card_counts = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        font1 = QtGui.QFont("微软雅黑", 9, QtGui.QFont.Bold)
        font2 = QtGui.QFont("微软雅黑", 10, QtGui.QFont.Bold)

        for col, name in enumerate(card_names):
            item = QtWidgets.QTableWidgetItem(name)
            item.setFont(font1)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setBackground(QtGui.QColor('#7c7c7c'))
            item.setForeground(QtGui.QColor('#202020'))
            self.tableWidget.setItem(0, col, item)

        for col, count in enumerate(card_counts):
            item = QtWidgets.QTableWidgetItem(str(count))
            item.setFont(font2)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            item.setBackground(QtGui.QColor('#404040'))
            item.setForeground(QtGui.QColor('#ffffff'))
            self.tableWidget.setItem(1, col, item)

        # 设置表格不可滚动
        self.tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tableWidget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.tableWidget.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        
        self.main_layout.addWidget(self.tableWidget)

    def create_three_card_label(self):
        label_layout = QtWidgets.QHBoxLayout()
        label_layout.setContentsMargins(0, 0, 0, 10)
        label_layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        font = QtGui.QFont("微软雅黑", 8)
        label = QtWidgets.QLabel("底牌：")
        label.setFont(font)

        font2 = QtGui.QFont("微软雅黑", 9, QtGui.QFont.Bold)
        label2 = QtWidgets.QLabel("---")
        label2.setFont(font2)

        label_layout.addWidget(label)
        label_layout.addWidget(label2)

        self.main_layout.addLayout(label_layout)
        self.main_layout.addStretch()

    def create_three_tables(self):
        self.create_predict_info_table()
        self.create_suggestion_table()
        self.create_played_card_table()

        table_layout = QtWidgets.QHBoxLayout()
        table_layout.addWidget(self.predictInfoTable)
        table_layout.addWidget(self.suggestionTable)
        table_layout.addWidget(self.playedCardsTable)

        self.main_layout.addLayout(table_layout)

    def create_predict_info_table(self):
        self.predictInfoTable = QtWidgets.QTableWidget(self)
        self.predictInfoTable.setGeometry(0, 0, 200, 150)
        self.predictInfoTable.setFixedSize(200, 150)
        self.predictInfoTable.setRowCount(4)
        self.predictInfoTable.setColumnCount(2)

        self.predictInfoTable.verticalHeader().setVisible(False)
        self.predictInfoTable.horizontalHeader().setVisible(False)
        self.predictInfoTable.setShowGrid(False)

        for row in range(4):
            self.predictInfoTable.setRowHeight(row, 33)

        self.predictInfoTable.setColumnWidth(0, 118)
        self.predictInfoTable.setColumnWidth(1, 78)

        headers = ['AI 预测', '胜率']
        contents = [
            ('叫地主', '-'),
            ('不叫地主', '-'),
            ('本回合', '-')
        ]

        font_header = QtGui.QFont("微软雅黑", 8)
        font_content = QtGui.QFont("微软雅黑", 8, QtGui.QFont.Bold)

        for col, header in enumerate(headers):
            item = QtWidgets.QTableWidgetItem(header)
            item.setFont(font_header)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.predictInfoTable.setItem(0, col, item)

        for row, (left, right) in enumerate(contents, start=1):
            left_item = QtWidgets.QTableWidgetItem(left)
            left_item.setFont(font_content)
            left_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.predictInfoTable.setItem(row, 0, left_item)

            right_item = QtWidgets.QTableWidgetItem(right)
            right_item.setFont(font_content)
            right_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.predictInfoTable.setItem(row, 1, right_item)

        self.predictInfoTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.predictInfoTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.predictInfoTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.predictInfoTable.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        self.predictInfoTable.setStyleSheet("""
            QTableWidget::item {
                background-color: #F3F3F3;
            }
            QTableWidget::item:alternate {
                background-color: #E3E3E3;
            }
        """)

        self.predictInfoTable.setAlternatingRowColors(True)

    def create_suggestion_table(self):
        self.suggestionTable = QtWidgets.QTableWidget(self)
        self.suggestionTable.setGeometry(0, 209, 266, 150)
        self.suggestionTable.setFixedSize(266, 150)
        self.suggestionTable.setRowCount(4)
        self.suggestionTable.setColumnCount(2)

        self.suggestionTable.verticalHeader().setVisible(False)
        self.suggestionTable.horizontalHeader().setVisible(False)
        self.suggestionTable.setShowGrid(False)

        for row in range(4):
            self.suggestionTable.setRowHeight(row, 33)

        self.suggestionTable.setColumnWidth(0, 168)
        self.suggestionTable.setColumnWidth(1, 94)

        headers = ['AI 建议出牌', '胜率']
        contents = [
            ('-', '-'),
            ('-', '-'),
            ('-', '-')
        ]

        font_header = QtGui.QFont("微软雅黑", 8)
        font_content = QtGui.QFont("微软雅黑", 8, QtGui.QFont.Bold)

        for col, header in enumerate(headers):
            item = QtWidgets.QTableWidgetItem(header)
            item.setFont(font_header)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.suggestionTable.setItem(0, col, item)

        for row, (left, right) in enumerate(contents, start=1):
            left_item = QtWidgets.QTableWidgetItem(left)
            left_item.setFont(font_content)
            left_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.suggestionTable.setItem(row, 0, left_item)

            right_item = QtWidgets.QTableWidgetItem(right)
            right_item.setFont(font_content)
            right_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.suggestionTable.setItem(row, 1, right_item)

        self.suggestionTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.suggestionTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.suggestionTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.suggestionTable.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        self.suggestionTable.setStyleSheet("""
            QTableWidget::item {
                background-color: #F3F3F3;
            }
            QTableWidget::item:alternate {
                background-color: #E3E3E3;
            }
        """)

        self.suggestionTable.setAlternatingRowColors(True)

    def create_played_card_table(self):
        self.playedCardsTable = QtWidgets.QTableWidget(self)
        self.playedCardsTable.setGeometry(0, 484, 266, 150)
        self.playedCardsTable.setFixedSize(266, 150)
        self.playedCardsTable.setRowCount(4)
        self.playedCardsTable.setColumnCount(2)

        self.playedCardsTable.verticalHeader().setVisible(False)
        self.playedCardsTable.horizontalHeader().setVisible(False)
        self.playedCardsTable.setShowGrid(False)

        for row in range(4):
            self.playedCardsTable.setRowHeight(row, 33)
            
        self.playedCardsTable.setColumnWidth(0, 94)
        self.playedCardsTable.setColumnWidth(1, 168)

        headers = ['玩家', '上一次出牌']
        contents = [
            ('上家', '-'),
            ('我的', '-'),
            ('下家', '-')
        ]

        font_header = QtGui.QFont("微软雅黑", 8)
        font_content = QtGui.QFont("微软雅黑", 8, QtGui.QFont.Bold)

        for col, header in enumerate(headers):
            item = QtWidgets.QTableWidgetItem(header)
            item.setFont(font_header)
            item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.playedCardsTable.setItem(0, col, item)

        for row, (left, right) in enumerate(contents, start=1):
            left_item = QtWidgets.QTableWidgetItem(left)
            left_item.setFont(font_content)
            left_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.playedCardsTable.setItem(row, 0, left_item)

            right_item = QtWidgets.QTableWidgetItem(right)
            right_item.setFont(font_content)
            right_item.setTextAlignment(QtCore.Qt.AlignCenter)
            self.playedCardsTable.setItem(row, 1, right_item)

        self.playedCardsTable.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.playedCardsTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.playedCardsTable.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.playedCardsTable.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        self.playedCardsTable.setStyleSheet("""
            QTableWidget::item {
                background-color: #F3F3F3;
            }
            QTableWidget::item:alternate {
                background-color: #E3E3E3;
            }
        """)

        self.playedCardsTable.setAlternatingRowColors(True)

    def create_actions(self):
        right_layout = QtWidgets.QHBoxLayout()
        right_layout.setContentsMargins(0, 10, 0, 0)
        right_layout.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        font = QtGui.QFont("微软雅黑", 10)

        comboBox = QtWidgets.QComboBox()
        comboBox.addItems(["自动模式", "手动模式"])
        comboBox.setFont(font)
        comboBox.setFixedWidth(120)
        comboBox.setFixedHeight(40)
        # comboBox.setStyleSheet("padding-left: 10px;")
        
        button = QtWidgets.QPushButton("启动")
        button.setFont(font)
        button.setFixedWidth(120)
        button.setFixedHeight(40)

        right_layout.addWidget(comboBox)
        right_layout.addWidget(button)

        self.main_layout.addLayout(right_layout)
        self.main_layout.addStretch()

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