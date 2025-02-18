import asyncio
import os
import sys
import time

from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap, QIcon, Qt
from PySide6.QtWidgets import QSplashScreen, QApplication, QMainWindow, QMessageBox
from qasync import QEventLoop, asyncSlot

sys.path.append('PySideApp/pyui')
for _ in sys.path:
    print(_)
from PySideApp.pyui import MyUI

os.environ["QT_API"] = "PySide6"
iconpath = ":/ico/app_icon.ico"
splashpath = ":/img/splash.jpg"


class MySplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__()
        self.setPixmap(QPixmap(splashpath))  # 设置背景图片
        self.showMessage(
            "正在加载...",
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom,
            Qt.GlobalColor.white
        )
        self.show()

    def ok(self, parent):
        self.finish(parent)  # 加载完成则隐藏
        self.deleteLater()


class MyWindow(QMainWindow, MyUI.Ui_MainWindow):  # 手搓函数，实现具体功能
    func_a_ok_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.loop = asyncio.get_event_loop()  # 异步loop取得
        self.bind_func()
        self.bind_signal()

    def bind_func(self):
        """
        绑定ui组件到具体函数
        :return:
        """
        self.pushButton_func_b.clicked.connect(self.func_b)

    def bind_signal(self):
        self.func_a_ok_signal.connect(self.func_a_ok)

    def func_a(self, count_time: int):
        """
        自定义函数a
        """
        self.pushButton_func_b.setDisabled(True)
        for i in range(count_time):
            self.label.setText(f"{i + 1}")
            time.sleep(1)
        self.label.setText("执行完毕")
        self.pushButton_func_b.setEnabled(True)
        self.func_a_ok_signal.emit()

    def func_a_ok(self):
        """在主线程中显示消息框"""
        QMessageBox.information(self, '提示', "执行完毕...", QMessageBox.StandardButton.Ok)

    @asyncSlot()
    async def func_b(self):
        """
        自定义异步函数
        :return:
        """
        await self.loop.run_in_executor(
            None,  # 主线程
            self.func_a,  # 函数名
            5,  # 输入参数
        )

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "询问", '确认关闭？',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            event.ignore()
            return
        QApplication.closeAllWindows()
        self.loop.stop()
        event.accept()


def main():
    app = QApplication(sys.argv)  # 实例化，传参
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)  # 全局异步能力
    splash = MySplashScreen()
    app.processEvents()  # 处理主进程事件
    # 主窗口
    window = MyWindow()
    window.setWindowIcon(QIcon(iconpath))
    window.show()
    splash.ok(window)
    if "--test" in sys.argv:  # 用于在构建时测试界面部分是否能正常初始化
        print("startup test pass...")
        sys.exit()
    with loop:
        loop.run_forever()

if __name__ == '__main__':
    main()