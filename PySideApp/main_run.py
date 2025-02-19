import asyncio
import os
import sys
import locale
import time

from PySideApp.Libs.test_runner import TestRunner

locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')

from PySide6 import QtCore
from PySide6.QtCore import Signal, QSettings
from PySide6.QtGui import QPixmap, QIcon, Qt
from PySide6.QtWidgets import QSplashScreen, QApplication, QMainWindow, QMessageBox, QTabWidget, QHeaderView, \
    QVBoxLayout, QLineEdit, QSpacerItem, QSizePolicy, QScrollArea, QWidget
from qasync import QEventLoop

from PySideApp.Libs.calculation_lib import get_all_test
from PySideApp.Libs.custom_ui_parts import add_func_single, add_func_block_single
from PySideApp.Libs.settings_window import SettingsManager

sys.path.append('./pyui')
for _ in sys.path:
    print(_)
from PySideApp.pyui import MainWindowUI

os.environ["QT_API"] = "PySide6"
iconpath = ":/ico/app_icon.ico"
splashpath = ":/img/splash.jpg"


class SplashScreen(QSplashScreen):
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


class MainWindow(QMainWindow, MainWindowUI.Ui_MainWindow):  # 手搓函数，实现具体功能
    func_a_ok_signal = Signal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.loop = asyncio.get_event_loop()  # 异步loop取得
        self.init_main_parts()
        self.bind_func()
        # self.bind_signal()

    def init_main_parts(self):  # 目前无法异步，因为涉及类的初始化，使用异步需要大改
        # 初始化设置管理器
        self.init_settings_manager()
        # 初始化表格组件
        self.init_table_widget()
        # 初始化功能盒
        self.init_func_box()
        # 初始化测试执行器
        self.init_test_runner()

    def init_test_runner(self):
        self.test_runner = TestRunner()

    def bind_func(self):
        """
        绑定ui组件到具体函数
        :return:
        """
        self.actionSettings.triggered.connect(self.open_settings_dialog)
        # self.toolButton_expand_area_common.pressed.connect(self.area_common_expand)

    def init_func_box(self):
        # 搜索框
        verticalLayout_func_box = QVBoxLayout(self.tab_new_task)
        self.lineEdit_func_box = QLineEdit(self.tab_new_task)
        self.lineEdit_func_box.setPlaceholderText('键入以搜索...')
        verticalLayout_func_box.addWidget(self.lineEdit_func_box)
        # 主滚动背景层
        self.scrollArea_main_func_box = QScrollArea(self.tab_new_task)
        self.scrollArea_main_func_box.setWidgetResizable(True)
        scrollAreaWidgetContents = QWidget()
        self.scrollArea_main_func_box.setWidget(scrollAreaWidgetContents)
        verticalLayout_func_box.addWidget(self.scrollArea_main_func_box)
        self.scrollArea_main_layout = QVBoxLayout(scrollAreaWidgetContents)
        # 添加哪些功能
        self.add_func_to_box()
        # 添加spacer防止布局异常
        self.scrollArea_main_layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

    def add_func_to_box(self):
        test_module_list = get_all_test()
        # 先根据名称排序
        test_module_list = sorted(test_module_list, key=lambda x: locale.strxfrm(x.name))
        # 统计有哪几类
        type_list = []
        for test_module in test_module_list:
            type_list.append(test_module.test_type)
        # 对类型排序
        type_list_set = set(type_list)
        type_list = sorted(type_list_set, key=type_list.index)
        for single_type in type_list:
            # 添加功能区并绑定展开折叠
            block_button, flow_widget = add_func_block_single(
                self.scrollArea_main_func_box,
                self.scrollArea_main_layout,
                single_type,
            )
            self.bind_expand_button(block_button, flow_widget)
            for test_module in test_module_list:
                if test_module.test_type in single_type:
                    # todo 添加功能并绑定
                    func_button = add_func_single(text=test_module.name, flow_widget=flow_widget)
                    self.bind_test_button(func_button, test_module.name)

    def bind_expand_button(self, button, flow_widget):
        def expand_handler():
            checked = button.isChecked()
            button.setArrowType(
                QtCore.Qt.ArrowType.DownArrow if not checked else QtCore.Qt.ArrowType.RightArrow
            )
            flow_widget.setVisible(not checked)
        button.pressed.connect(expand_handler)

    def bind_test_button(self, button, test_name:str):
        def click_handler():
            uuid = int(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))
            self.test_runner.set_test_info(uuid, test_name)
            self.test_runner.show()
        button.clicked.connect(click_handler)

    def bind_signal(self):
        self.func_a_ok_signal.connect(self.func_a_ok)

    def init_table_widget(self):
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def init_settings_manager(self):
        # 定义需要保存状态的部件
        self.state_save_list = [self.tabWidget, self]
        # 主题色变量
        self.theme = '跟随系统'
        self.settings_manager = SettingsManager(self.apply_settings)

    def apply_settings(self, settings: dict):
        if 'Theme' in settings:
            self.theme = settings['Theme']
            self.apply_theme()

    def open_settings_dialog(self):
        settings_ditc = {
            'Theme': self.theme
        }
        self.settings_manager.get_settings(settings_ditc)
        self.settings_manager.tabWidget_settings_main.setCurrentIndex(0)
        self.settings_manager.show()

    def apply_theme(self):
        if self.theme == '跟随系统':
            QApplication.styleHints().setColorScheme(Qt.ColorScheme.Unknown)
        elif self.theme == '深色':
            QApplication.styleHints().setColorScheme(Qt.ColorScheme.Dark)
        elif self.theme == '浅色':
            QApplication.styleHints().setColorScheme(Qt.ColorScheme.Light)
        self.update()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "询问", '确认关闭？',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            event.ignore()
            return
        QApplication.closeAllWindows()
        self.loop.stop()
        event.accept()

    def saveSettings(self):
        settings = QSettings("settings.ini", QSettings.Format.IniFormat)
        # 主题色
        settings.setValue('Theme', self.theme)
        # 布局
        for item in self.state_save_list:
            if isinstance(item, QMainWindow):
                settings.setValue(f'{item.objectName()}Geometry', item.saveGeometry())
                settings.setValue(f'{item.objectName()}State', item.saveState())
            elif isinstance(item, QTabWidget):
                settings.setValue(f'{item.objectName()}TabIndex', item.currentIndex())

    def loadSettings(self):
        settings = QSettings("settings.ini", QSettings.Format.IniFormat)
        # 主题色
        self.theme = settings.value('Theme', '跟随系统')
        self.apply_theme()
        # 布局
        for item in self.state_save_list:
            if isinstance(item, QMainWindow):
                self.restoreGeometry(settings.value(f'{item.objectName()}Geometry'))
                self.restoreState(settings.value(f'{item.objectName()}State'))
            if isinstance(item, QTabWidget):
                item.setCurrentIndex(settings.value(f'{item.objectName()}TabIndex', 0, int))


def main():
    app = QApplication(sys.argv)  # 实例化，传参
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)  # 全局异步能力
    splash = SplashScreen()
    app.processEvents()  # 处理主进程事件
    # 主窗口
    window = MainWindow()
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