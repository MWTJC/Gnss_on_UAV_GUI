import asyncio
import json
import logging
import os
import pickle
import sys
import locale
import time
from pathlib import Path
from natsort import natsorted

from PySide6.QtWebChannel import QWebChannel
from loguru import logger
from PySide6 import QtCore
from PySide6.QtCore import Signal, QSettings, QUrl, Slot
from PySide6.QtGui import QPixmap, QIcon, Qt
from PySide6.QtWidgets import QSplashScreen, QApplication, QMainWindow, QMessageBox, QTabWidget, QHeaderView, \
    QVBoxLayout, QLineEdit, QSpacerItem, QSizePolicy, QScrollArea, QWidget, QTableWidgetItem, \
    QToolButton, QFileDialog
from pandas.io.clipboard import paste
from qasync import QEventLoop

locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
os.environ["QT_API"] = "PySide6"
splashpath = ":/img/splash.jpg"
os.environ["QTWEBENGINE_REMOTE_DEBUGGING"] = "9222"
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-web-security"
# MAP_HTML_DIR = str(Path(f"{os.path.abspath(os.path.dirname(__file__))}/Libs/self_map"))
MAP_HTML_DIR = str(Path(f"{os.path.abspath(os.path.dirname(__file__))}/Libs/vite-leaflet/dist"))
sys.path.insert(0, str(Path(f"{os.path.abspath(os.path.dirname(__file__))}/pyui")))
logger.info(sys.path)

from PySideApp.Libs.read_pva_file import PVAPacket, gps_to_datetime
from PySideApp.Libs.map_webchannel import WebHandler
from PySideApp.Libs.nmea_decode import parse_and_convert_GP
from PySideApp.Libs.test_runner import TestRunner
from PySideApp.Libs.test_tasks_lib import TestTask, TestModule
from PySideApp.Libs.TestModuleLib import get_all_test
from PySideApp.Libs.custom_ui_parts import add_func_single, add_func_block_single, FlowWidget, SearchDict, \
    ActivityIndicator
from PySideApp.Libs.settings_window import SettingsManager
from PySideApp.Libs.map_server import LocalServer
from PySideApp.Libs.settings_serial import SerialAssistant
from PySideApp.pyui.MainWindowUI import Ui_MainWindow

def custom_excepthook(exc_type, exc_value, exc_traceback):
    # 记录异常信息
    logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    # 退出程序
    sys.exit(1)

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


class MainWindow(QMainWindow, Ui_MainWindow):  # 手搓函数，实现具体功能
    func_a_ok_signal = Signal()

    def __init__(self):
        super().__init__()
        self.error = False
        self.current_proj_path:Path|None = None
        self.serial_dialog: SerialAssistant|None = None
        self.setupUi(self)
        self.loop = asyncio.get_event_loop()  # 异步loop取得
        self.init_main_parts()
        self.bind_func()
        # self.bind_signal()

    def init_main_parts(self):  # 目前无法异步，因为涉及类的初始化，使用异步需要大改
        # 初始化设置管理器
        self.init_settings_manager()
        # 初始化闪烁指示灯
        self.init_status_flashlight()
        # 初始化串口部分
        self.init_serial()
        # 初始化表格组件
        self.init_table_widget()
        # 初始化功能盒
        self.init_func_box()
        # 初始化测试执行器
        self.init_test_runner()
        # 初始化地图
        # self.init_map()
        # 初始化主窗口状态显示
        self.display_online_info(None, False, reset=True)


    def init_status_flashlight(self):
        self.activity_indicator = ActivityIndicator(
            button=self.pushButton_serial_status,
            # active_style="background-color: #00FF00; border-radius: 7px; border: none;",
            # inactive_style="background-color: gray; border-radius: 7px; border: none;",
            # duration=100  # 亮0.1秒
        )

    def open_serial_dialog(self):
        self.serial_dialog.show()

    def display_online_info(self, package:PVAPacket|None, gnss_ok:bool, reset=False):
        self.activity_indicator.notify()
        if reset:
            self.pushButton_serial_status.setText("-")
            self.label_gnss_status_value.setText("-")
            self.label_device_time_value.setText("-")
            return
        if package is None:
            self.pushButton_serial_status.setText("异常")
            return
        try:
            self.label_gnss_status_value.setText(f"{"良好"if gnss_ok else"否"}")
            self.label_device_time_value.setText(f"{gps_to_datetime(package.gps_week, package.gps_week_seconds).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]} UTC")
            self.label_longitude_online.setText(f"{package.longitude:03.15f}°")
            self.label_latitude_online.setText(f"{package.latitude:03.15f}°")
            self.label_height_online.setText(f"{package.altitude:0.3f}m")
            self.label_speed_east_online.setText(f"{package.east_velocity:0.3f}m/s")
            self.label_speed_north_online.setText(f"{package.north_velocity:0.3f}m/s")
            self.label_speed_sky_online.setText(f"{package.up_velocity:0.3f}m/s")
            self.label_angle_roll_online.setText(f"{package.roll:0.3f}°")
            self.label_angle_pitch_online.setText(f"{package.pitch:0.3f}°")
            self.label_angle_yaw_online.setText(f"{package.heading:0.3f}°")
            self.label_velocity2d_online.setText(f"{(package.east_velocity**2+package.north_velocity**2)**0.5:0.3f}m/s")
            self.label_velocity3d_online.setText(f"{(package.east_velocity**2+package.north_velocity**2+package.up_velocity**2)**0.5:0.3f}m/s")
        except OverflowError:
            pass


    def init_serial(self):
        self.serial_dialog = SerialAssistant()
        self.serial_dialog.set_status_button(self.pushButton_serial_status)
        self.serial_dialog.set_package_send_callback(self.display_online_info)
        self.actionConnectSerial.triggered.connect(self.open_serial_dialog)

    def init_map(self):
        self.map_server = LocalServer(port=28000, dir=MAP_HTML_DIR)
        self.toolButton_map_refresh.clicked.connect(self.webEngineView_map.reload)
        logger.info(MAP_HTML_DIR)
        self.map_server.start()
        self.map_page = self.webEngineView_map.page()
        self.web_channel = QWebChannel()
        self.web_bridge = WebHandler(self.map_page)
        self.web_bridge.ruler_end_callback = self.map_ruler_end
        self.web_channel.registerObject("web_bridge", self.web_bridge)
        self.map_page.setWebChannel(self.web_channel)
        # self.webEngineView_map.setUrl('http://localhost:28000')
        self.webEngineView_map.setUrl('http://localhost:5173')
        self.toolButton_map_ruler.clicked.connect(self.map_call_ruler)
        self.toolButton_map_read_raw.clicked.connect(self.map_read_raw)

    def map_read_raw(self):
        fname, ftype = QFileDialog.getOpenFileName(
            self, "打开raw数据...", "",
            "txt文件(*.txt)",
        )
        if fname:
            logger.success(fname)
            result_list = parse_and_convert_GP(fname)
            # 将数据转换为JSON字符串
            data_json = json.dumps(result_list)
            self.map_page.runJavaScript(f"setTrackData({data_json});")

        else:
            logger.warning('取消打开...')
            return

    def map_ruler_end(self):
        """
        用于从地图收作图结束信号
        """
        self.toolButton_map_ruler.setChecked(False)


    def map_call_ruler(self):
        """
        召唤或者关闭尺子
        """
        if self.toolButton_map_ruler.isChecked():
            # self.map_page.runJavaScript("openDistance();")
            self.map_page.runJavaScript("window.vueBridge.openDistance();")
        else:
            # self.map_page.runJavaScript("closeDistance();")
            self.map_page.runJavaScript("window.vueBridge.closeDistance();")

    def refresh_map(self):
        """
        刷新地图
        """
        self.webEngineView_map.reload()

    def init_test_runner(self):
        self.test_runner = TestRunner()
        self.test_runner.signal_test_over.connect(self.read_result_from_runner)

    def read_result_from_runner(self):
        result = self.test_runner.get_task_result()
        self.task_history_list.append(result)
        self.refresh_fill_table_data()

    def bind_func(self):
        """
        绑定ui组件到具体函数
        :return:
        """
        self.actionSettings.triggered.connect(self.open_settings_dialog)
        self.actionNewProj.triggered.connect(self.create_new_proj)
        self.actionSaveProject.triggered.connect(self.save_proj_to_file)
        self.actionSaveProjAs.triggered.connect(self.save_proj_to_file_as)
        self.actionReadProj.triggered.connect(self.read_proj_from_file)

    def create_new_proj(self):
        if len(self.task_history_list) != 0:
            reply = QMessageBox.question(self, "询问", "确认清空？",
                                         QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No
                                         )
            if reply != QMessageBox.StandardButton.Yes:
                return
        self.task_history_list = []
        self.refresh_fill_table_data()
        QMessageBox.information(self, "信息", "已新建...")

    def save_proj_to_file(self, save_as=False):
        if len(self.task_history_list) == 0:
            QMessageBox.warning(self, "警告", "无数据可保存...")
            return
        if self.current_proj_path is None or save_as:
            if save_as:
                mes = "项目另存为..."
            else:
                mes = "保存项目..."
            path, ext = QFileDialog.getSaveFileName(
                self, mes, "",
                "cruav文件(*.cruav)"
            )
            if not path:  # 判断路径非空
                logger.warning("取消保存...")
                return
            try:
                self.current_proj_path = Path(path)
            except Exception as e:
                logger.warning(f'路径不合法:\n{path}')
                QMessageBox.warning(self, '警告', "路径不合法")
        with open(self.current_proj_path, 'wb') as f:
            pickle.dump(self.task_history_list, f)
        QMessageBox.information(self, "信息", f"已保存到：{self.current_proj_path}")

    def save_proj_to_file_as(self):
        self.save_proj_to_file(save_as=True)

    def read_proj_from_file(self):
        fname, ftype =  QFileDialog.getOpenFileName(
            self, "打开项目...", "",
            "cruav文件(*.cruav)",
        )
        if fname:
            logger.success(fname)
            with open(fname, 'rb') as f:
                self.task_history_list = pickle.load(f)
                self.refresh_fill_table_data()
                self.tabWidget.setCurrentIndex(0)
                self.statusbar.showMessage(f'已载入{fname}', 3000)
        else:
            logger.warning('取消打开...')
            return

    def init_func_box(self):
        # 搜索框
        verticalLayout_func_box = QVBoxLayout(self.tab_new_task)
        self.lineEdit_func_box = QLineEdit(self.tab_new_task)
        self.lineEdit_func_box.setPlaceholderText('键入以搜索...')
        self.lineEdit_func_box.setClearButtonEnabled(True)
        self.lineEdit_func_box.textChanged.connect(self.search_func_box)
        verticalLayout_func_box.addWidget(self.lineEdit_func_box)
        # 搜索用的容器
        self.list_search_class:list[SearchDict] = []
        self.flow_widgets_list:list[FlowWidget] = []
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


    def search_func_box(self, text:str|None=None):
        for item in self.list_search_class:
            if item.button:
                visible = item.matches(text)
                item.button.setVisible(visible)
            # 更新所有FlowWidget的布局
            for flow_widget in self.flow_widgets_list:
                flow_widget.updateVisibleWidgets()
                flow_widget.update()


    def add_func_to_box(self):
        try:
            test_module_list = get_all_test()
        except Exception as e:
            logger.critical('检测模块导入不通过，退出')
            self.error = True
            raise

        # 先根据名称排序
        test_module_list = natsorted(test_module_list, key=lambda x: x.name)
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
            self.flow_widgets_list.append(flow_widget)
            for test_module in test_module_list:
                if test_module.test_type in single_type:
                    # 添加功能并绑定
                    func_button = add_func_single(text=test_module.name, flow_widget=flow_widget)
                    self.bind_test_button(func_button, test_module)
                    kwds = test_module.search_keywords
                    kwds.append(test_module.name)
                    self.list_search_class.append(SearchDict(kwds, func_button))


    def bind_expand_button(self, button:QToolButton, flow_widget):
        def expand_handler():
            checked = button.isChecked()
            button.setArrowType(
                QtCore.Qt.ArrowType.DownArrow if checked else QtCore.Qt.ArrowType.RightArrow
            )
            flow_widget.setVisible(checked)
        button.clicked.connect(expand_handler)
        button.triggered.connect(expand_handler)


    def bind_test_button(self, button, test_module:TestModule):
        def click_handler():
            uuid = int(time.strftime('%Y%m%d%H%M%S', time.localtime(time.time())))
            self.test_runner.set_test_info(uuid=uuid, module=test_module)
            self.test_runner.show()
        button.clicked.connect(click_handler)

    def init_table_widget(self):
        self.task_history_list:list[TestTask] = []
        self.refresh_fill_table_data()

    def refresh_fill_table_data(self):
        self.tableWidget.clear()  # 遇事不决清空
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)  # 动态拉伸
        headers = ["ID", "计算项目", "备注", "状态", "创建时间", "操作"]
        self.tableWidget.setHorizontalHeaderLabels(headers)

        if len(self.task_history_list) == 0:
            return
        # 抽出数据
        data = []
        for history in self.task_history_list:
            calculate_status = '可计算' if history.org_dataframe else '未计算'
            single_raw = [
                history.id,
                f"{history.type}：{history.name}",
                history.note,
                calculate_status,
                time.strftime('%Y年%m月%d日 %H:%M:%S', time.localtime(history.create_timestamp)),
            ]
            data.append(single_raw)

        # 设置行数
        self.tableWidget.setRowCount(len(data))

        # 填充数据
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                self.tableWidget.setItem(row, col, item)

            # 创建最后一列的按钮容器
            widget = FlowWidget()

            # 删除按钮
            delete_btn = QToolButton()
            delete_btn.setText("删除")
            delete_btn.setIcon(
                QIcon(QIcon.fromTheme(u"user-trash"))
            )
            delete_btn.clicked.connect(lambda checked, r=row: self.delete_row(r))

            # 详情按钮
            detail_btn = QToolButton()
            detail_btn.setText("详情")
            detail_btn.setIcon(
                QIcon(QIcon.fromTheme(u"dialog-information"))
            )
            detail_btn.clicked.connect(lambda checked, r=row: self.show_detail(r))

            # # 计算按钮
            # run_caculate_btn = QToolButton()
            # run_caculate_btn.setText("计算")
            # run_caculate_btn.setIcon(
            #     QIcon(QIcon.fromTheme(u"accessories-calculator"))
            # )
            # run_caculate_btn.clicked.connect(lambda checked, r=row: self.show_detail(r))

            # 将按钮添加到布局中
            widget.addWidget(detail_btn)
            # widget.addWidget(run_caculate_btn)
            widget.addWidget(delete_btn)

            # 将按钮容器设置到表格中
            self.tableWidget.setCellWidget(row, 5, widget)

    def delete_row(self, row):
        print(f"删除第 {row + 1} 行")
        # self.tableWidget.removeRow(row)

    def show_detail(self, row):
        print(f"显示第 {row + 1} 行的详情")
        task: TestTask = self.task_history_list[row]
        self.test_runner.set_test_info(history_task=task)
        self.test_runner.show()

    def init_settings_manager(self):
        # 定义需要保存状态的部件
        self.state_save_list = [self.tabWidget, self]
        # 主题色变量
        self.loadSettings()
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
        self.saveSettings()
        QApplication.closeAllWindows()
        # self.loop.stop()
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

@logger.catch
def main():
    app = QApplication(sys.argv)  # 实例化，传参
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)  # 全局异步能力
    splash = SplashScreen()
    app.processEvents()  # 处理主进程事件
    # 主窗口
    window = MainWindow()
    window.show()
    splash.ok(window)
    if "--test" in sys.argv:  # 用于在构建时测试界面部分是否能正常初始化
        if window.error:
            sys.exit(1)
        logger.success("startup test pass...")
        sys.exit()
    with loop:
        loop.run_forever()

if __name__ == '__main__':
    main()