import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel, QMessageBox
)
from PySide6.QtCore import QThread, Signal

# 确保 src 在路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from src.main import main as experiment_main

class ExperimentThread(QThread):
    log_signal = Signal(str)
    finished_signal = Signal()

    def run(self):
        sys.stdout = self
        sys.stderr = self
        try:
            experiment_main()
        except Exception as e:
            self.log_signal.emit(f"程序异常: {e}\n")
        finally:
            self.finished_signal.emit()

    def write(self, msg):
        self.log_signal.emit(str(msg))

    def flush(self):
        pass

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("阀门控制系统实验平台 GUI")
        self.setMinimumSize(800, 540)

        layout = QVBoxLayout(self)

        self.title = QLabel("<h2>阀门控制系统实验平台</h2>")
        layout.addWidget(self.title)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background:#222;color:#eee;font-family:Consolas,monospace;font-size:14px;")
        layout.addWidget(self.log_output, stretch=1)

        btn_layout = QHBoxLayout()
        self.btn_init = QPushButton("初始化")
        self.btn_start = QPushButton("开始实验")
        self.btn_stop = QPushButton("停止实验")
        self.btn_save = QPushButton("保存数据")
        self.btn_exit = QPushButton("退出")

        btn_layout.addWidget(self.btn_init)
        btn_layout.addWidget(self.btn_start)
        btn_layout.addWidget(self.btn_stop)
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_exit)
        layout.addLayout(btn_layout)

        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.btn_save.setEnabled(False)

        self.thread = None

        self.btn_init.clicked.connect(self.on_init)
        self.btn_start.clicked.connect(self.on_start)
        self.btn_stop.clicked.connect(self.on_stop)
        self.btn_save.clicked.connect(self.on_save)
        self.btn_exit.clicked.connect(self.close)

    def on_init(self):
        self.log_output.append("系统初始化完成。")
        self.btn_start.setEnabled(True)
        self.btn_init.setEnabled(False)

    def on_start(self):
        self.log_output.append("实验开始运行...")
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.btn_save.setEnabled(False)
        self.thread = ExperimentThread()
        self.thread.log_signal.connect(self.log_output.append)
        self.thread.finished_signal.connect(self.on_experiment_finished)
        self.thread.start()

    def on_stop(self):
        self.log_output.append("实验强制终止。")
        QMessageBox.warning(self, "警告", "实验将被强制终止，部分数据可能丢失。")
        os._exit(0)

    def on_save(self):
        self.log_output.append("数据保存功能请在实验结束后查看输出目录。")
        QMessageBox.information(self, "提示", "数据已自动保存到指定目录。")

    def on_experiment_finished(self):
        self.log_output.append("实验已完成。")
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.btn_save.setEnabled(True)
        self.btn_init.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec()) 