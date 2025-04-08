from qasync import asyncio, asyncSlot
import queue
import sys
from multiprocessing import Manager

import aioserial
import serial
import serial.tools.list_ports
from PySide6 import QtCore
from PySide6.QtWidgets import QMessageBox, QApplication, QWidget, QPushButton

from PySideApp.pyui.SerialSettingsUi import Ui_Form


@asyncSlot()
async def read_and_print(aioserial_instance: aioserial.AioSerial):
    while True:
        print((await aioserial_instance.read_async()).decode(errors='ignore'), end='', flush=True)

@asyncSlot()
async def read_gpgga_to_list(aioserial_instance: aioserial.AioSerial, list_storage: list):
    while True:
        list_storage.append((await aioserial_instance.read_async()).decode(errors='ignore'))

@asyncSlot()
async def read_hex_(aioserial_instance: aioserial.AioSerial):
    while True:
        print((await aioserial_instance.read_async()), end='', flush=True)

class SerialAssistant(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.data_storage = []
        self.setupUi(self)
        self.pushButton_open_serial.setEnabled(False)
        # 初始化serial对象 用于串口通信
        self.ser = aioserial.AioSerial()
        # 变量
        self.port_dict = None
        self.queue = queue.Queue()
        # 初始化串口配置文件
        # self.serial_cfg()

        # 初始化与绑定槽
        self.unit_serial()

        # 初始化循环计时器
        self.timer_plot = QtCore.QTimer(self)
        self.timer_status = QtCore.QTimer(self)

        # 多进程共享变量管理
        self.manager = Manager()
        # self.data_storage.command_status = self.manager.list()

    def set_status_button(self, button:QPushButton):
        self.pushButton_serial_status = button

    def start_reading(self):
        self.ser.close()
        self.ser.open()
        self.data_storage = []
        # self.serial_reader = SerialReader(self.ser, self.queue, self.data_storage)
        # self.serial_reader.start()
        self.timer_status.timeout.connect(self.display_data)
        self.timer_status.start(1000)  # 每隔一秒更新一次信息

    def stop_core(self):

        def fun_d():
            self.ser.close()
            self.ser.open()
            return True

        functions = [fun_d]
        all_success = True
        for func in functions:
            try:
                result = func()
                if not result:
                    print(f"Function {func.__name__} failed")
                    all_success = False
            except Exception as e:
                print(f"Error in function {func.__name__}: {str(e)}")
                all_success = False

        self.progressBar_status_port.setMaximum(1)
        self.progressBar_status_port.setValue(0)

        if all_success:
            self.pushButton_serial_status.setStyleSheet('QPushButton{background:'
                                                + '#B3B3B3'
                                                + ';}')
            self.pushButton_serial_status.setText("已停止")
        else:
            self.pushButton_serial_status.setStyleSheet('QPushButton{background:'
                                                + '#FFB300'
                                                + ';}')
            self.pushButton_serial_status.setText("停止异常")


    def display_data(self):
        # 设置状态，目前区分为：灰色，停止，绿色，正常运作， 黄色，正在自适应调节，红色，丢包，需要重开
        t_c = "#000000"
        c = "#37FF2B"
        t = "正常"
        self.pushButton_serial_status.setStyleSheet('QPushButton{background:'
                                            + c
                                            + ';color:'
                                            + t_c
                                            + '}'
                                            )
        self.pushButton_serial_status.setText(t)


    def unit_serial(self):
        # 预设 下拉菜单
        self.comboBox_scheme.addItems([
            "不使用",
            "地面电台直连"
        ])
        # 波特率 下拉菜单
        self.comboBox_baud.addItems(['100', '300', '600', '1200', '2400', '4800', '9600', '14400', '19200',
                                     '38400', '56000', '57600', '115200', '128000', '256000'])
        self.comboBox_baud.setCurrentIndex(12)
        # 数据位 下拉菜单
        self.comboBox_data_bit.addItems(['8', '7', '6', '5'])
        self.comboBox_data_bit.setCurrentIndex(0)
        # 校验位 下拉菜单
        self.comboBox_parity_bit.addItems(['N', 'E', 'O'])  # 校验位N－无校验，E－偶校验，O－奇校验
        self.comboBox_parity_bit.setCurrentIndex(0)
        # 停止位 下拉菜单
        self.comboBox_stop_bit.addItems(['1', '1.5', '2'])
        self.comboBox_stop_bit.setCurrentIndex(0)

        self.pushButton_detect_port.clicked.connect(self.port_detect)
        self.pushButton_open_serial.clicked.connect(self.port_open_close)

        self.progressBar_status_port.setMaximum(8184)


    # 串口检测
    def port_detect(self):
        self.pushButton_open_serial.setEnabled(True)
        # 检测所有存在的串口 将信息存在字典中
        self.port_dict = {}
        # serial.tools.list_ports.comports()返回计算机上所有的port口信息
        # 将其存在列表中
        port_list = list(serial.tools.list_ports.comports())
        # 清除下拉列表中已有的选项
        self.comboBox_port_choose.clear()
        for port in port_list:
            # 添加到字典里
            self.port_dict["%s" % port[0]] = "%s" % port[1]
            # 添加到下拉列表选项
            self.comboBox_port_choose.addItem(port[0] + '：' + port[1])
        if len(self.port_dict) == 0:
            self.comboBox_port_choose.addItem('无串口')
        self.comboBox_port_choose.setEnabled(True)

    # 获取端口号（串口选择界面想显示完全 但打开串口只需要串口号COMX）
    def get_port_name(self):
        full_name = self.comboBox_port_choose.currentText()
        # rfind会找到：的位置
        com_name = full_name[0:full_name.rfind('：')]
        return com_name

    # 打开/关闭 串口
    def port_open_close(self):
        if (self.pushButton_open_serial.text() == '开串口') and self.port_dict:
            port_name = self.get_port_name()  # 获取端口名称
            baudrate = int(self.comboBox_baud.currentText())  # 波特率
            bytesize = int(self.comboBox_data_bit.currentText())  # 数据位
            parity = self.comboBox_parity_bit.currentText()  # 校验位
            stopbits = int(self.comboBox_stop_bit.currentText())  # 停止位

            try:
                # 打开串口
                self.ser = aioserial.AioSerial(port=port_name, baudrate=baudrate,
                                               bytesize=bytesize, parity=parity,
                                               stopbits=stopbits)
            except aioserial.SerialException as e:
                QMessageBox.critical(self, '错误', str(e))
                return None

            # 判断 串口的打开状态
            if self.ser.is_open:
                self.pushButton_open_serial.setText('关串口')
                # self.pushButton_open_serial.setIcon(QIcon('close_button.png'))
                self.progressBar_status_port.setValue(1)
                # self.set_setting_enable(False)
                self.groupBox_serial_sett.setEnabled(False)
            loop = asyncio.get_running_loop()
            loop.run_until_complete(read_and_print(self.ser))

        # 按打开串口按钮 但 没有读取到串口
        elif (self.pushButton_open_serial.text() == '开串口') and (self.comboBox_port_choose.currentText() == '无串口'):
            QMessageBox.warning(self, '警告', '没有可打开的串口！')
            return None
        # 点击关闭串口按钮
        elif self.pushButton_open_serial.text() == '关串口':
            # 停止定时器
            # self.serial_receive_timer.stop()
            try:
                self.ser.close()
            except:
                QMessageBox.critical(self, '警告', '此串口不能正常关闭！')
                return None
            self.pushButton_open_serial.setText('开串口')
            # self.pushButton_open_serial.setIcon(QIcon('open_button.png'))
            # self.serial_state_gb.setTitle('串口状态')
            self.groupBox_serial_sett.setEnabled(True)

            self.progressBar_status_port.setValue(0)



if __name__ == '__main__':
    app = QApplication(sys.argv)  # 实例化，传参
    app.processEvents()  # 处理主进程事件
    # 主窗口
    window = SerialAssistant()
    window.show()
    if "-test" in sys.argv:  # 用于在构建时测试是否正常运行
        print("startup test OK...")
        sys.exit()
    sys.exit(app.exec())

