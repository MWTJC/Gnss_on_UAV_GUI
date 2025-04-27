import copy
from qasync import asyncio, asyncSlot
import sys

import aioserial
import serial
import serial.tools.list_ports
from PySide6 import QtCore
from PySide6.QtWidgets import QMessageBox, QApplication, QWidget, QPushButton

from PySideApp.Libs.read_pva_file import parse_packet, PVAPacket
from PySideApp.pyui.SerialSettingsUi import Ui_Form



@asyncSlot()
async def read_and_print(aioserial_instance: aioserial.AioSerial):
    while True:
        print((await aioserial_instance.read_async(size=158)).decode(errors='ignore'), end='', flush=True)

@asyncSlot()
async def read_pva_hex(aioserial_instance: aioserial.AioSerial, callback):
    while True:
        try:
            callback(await aioserial_instance.read_async(size=158))
        except serial.serialutil.PortNotOpenError:
            return

@asyncSlot()
async def read_gpgga_to_list(aioserial_instance: aioserial.AioSerial, list_storage: list):
    while True:
        list_storage.append((await aioserial_instance.read_async()).decode(errors='ignore'))

@asyncSlot()
async def read_hex_(aioserial_instance: aioserial.AioSerial, callback):
    while True:
        try:
            callback(await aioserial_instance.read_async(size=158))
        except serial.serialutil.PortNotOpenError:
            return

class SerialAssistant(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.data_storage: list[PVAPacket] = []
        self.data_storage_bytes = bytearray()
        self.pushButton_open_serial.setEnabled(False)
        # 初始化serial对象 用于串口通信
        self.ser = aioserial.AioSerial()
        # 变量
        self.port_dict = None
        # 初始化串口配置文件
        # self.serial_cfg()
        # 初始化与绑定槽
        self.unit_serial()

        # 数据包回传主界面回调
        self.package_send_callback = None

    def clear_storage(self):
        self.data_storage = []
        self.data_storage_bytes = bytearray()

    def get_storage(self):
        return copy.deepcopy(self.data_storage), copy.deepcopy(self.data_storage_bytes)

    def set_package_send_callback(self, callback):
        self.package_send_callback = callback

    def set_status_button(self, button:QPushButton):
        self.pushButton_serial_status = button

    def raw_hex_to_display(self, content: bytes):
        md_text = content.hex().upper()
        if not md_text:
            return
        self.textEdit_serial_details.setMarkdown(f"<font size=20 face='Terminal'>{md_text}</font>")

    def pva_hex_to_display(self, content: bytes):
        packet, offset, is_valid = parse_packet(content)
        if not packet:
            return
        packet: PVAPacket
        gps_week_seconds = packet.gps_week_seconds
        time_status = True if packet.time_status == 180 else False
        time_status_text = "<font color='yellow'>未知</font>"
        if packet.time_status==20:
            pass
        elif packet.time_status==100:
            time_status_text = "<font color='yellow'>粗精度</font>"
        elif packet.time_status==180:
            time_status_text = "<font color='green'>高精度</font>"
        combined_status = True if packet.combined_status == 3 else False
        combined_status_text = "<font color='yellow'>未知</font>"
        if packet.combined_status==0:
            combined_status_text = "<font color='red'>未工作</font>"
        elif packet.combined_status==1:
            combined_status_text = "<font color='yellow'>正在对准</font>"
        elif packet.combined_status == 2:
            combined_status_text = "<font color='yellow'>组合但偏差大，疑似GNSS信号差</font>"
        elif packet.combined_status == 3:
            combined_status_text = "<font color='green'>良好</font>"
        elif packet.combined_status == 6:
            combined_status_text = "<font color='orange'>组合，但GNSS结果可能有误</font>"
        elif packet.combined_status == 7:
            combined_status_text = "<font color='orange'>对准完成，需机动以提升精度</font>"
        elif packet.combined_status == 8:
            combined_status_text = "<font color='orange'>轴系稳定中</font>"
        elif packet.combined_status == 9:
            combined_status_text = "<font color='orange'>等待初始位置</font>"
        elif packet.combined_status == 10:
            combined_status_text = "<font color='orange'>等待航向</font>"
        elif packet.combined_status == 11:
            combined_status_text = "<font color='orange'>静止评估中</font>"
        elif packet.combined_status == 12:
            combined_status_text = "<font color='orange'>未对准，有运动</font>"

        position_type = True if packet.position_type == 56 else False
        position_type_text="<font color='orange'>未知</font>"
        if packet.position_type == 0:
            position_type_text = "<font color='red'>未解算</font>"
        elif packet.position_type == 16:
            position_type_text = "<font color='red'>单点解</font>"
        elif packet.position_type == 32:
            position_type_text = "<font color='red'>L1浮点解</font>"
        elif packet.position_type == 48:
            position_type_text = "<font color='red'>L1固定解</font>"
        elif packet.position_type == 53:
            position_type_text = "<font color='orange'>组合单点解</font>"
        elif packet.position_type == 55:
            position_type_text = "<font color='orange'>组合浮点解</font>"
        elif packet.position_type == 56:
            position_type_text = "<font color='green'>组合固定解</font>"
        # ext_status = packet.ext_status.encode('hex')
        ext_status = f"0x{packet.ext_status:08X}"

        # 检查特定位
        for bit_num, mask, description in [
            (0, 0x00000001, "Position Update"),
            (1, 0x00000002, "Phase Update"),
            (2, 0x00000004, "Zero Velocity Update"),
            (3, 0x00000008, "Wheel Sensor Update"),
            (4, 0x00000010, "ALIGN (heading) Update"),
            (5, 0x00000020, "External Position Update"),
            (6, 0x00000040, "INS Solution Convergence Flag")
        ]:
            is_set = bool(packet.ext_status & mask)
            status = "Used" if is_set else "Unused"
            if bit_num == 6:
                status = "收敛" if is_set else "未收敛"
        md_text = (
            "## 实时概况\n"
            "### gnss秒：\n"
            f"{gps_week_seconds}\n"
            "### 时间状态：\n"
            f"{packet.time_status:02X}, {time_status_text}\n"
            "### 组合状态：\n"
            f"{packet.combined_status:02X}, {combined_status_text}\n"
            "### 固定解：\n"
            f"{packet.position_type:02X}, {position_type_text}\n"
            "### 拓展字状态：\n"
            f"{ext_status}, 第六位：{status}\n"
        )
        self.textEdit_serial_details.setMarkdown(md_text)

        # 记录
        self.data_storage.append(packet)
        self.data_storage_bytes.extend(content)

        if self.package_send_callback:
            self.package_send_callback(
                package=packet,
                gnss_ok=time_status is True and combined_status is True and position_type is True  # 状态良好
            )


    def unit_serial(self):
        # 预设 下拉菜单
        self.comboBox_scheme.addItems([
            "不使用",
            "串口PVA接收"
        ])
        # 波特率 下拉菜单
        self.comboBox_baud.addItems(['100', '300', '600', '1200', '2400', '4800', '9600', '14400', '19200',
                                     '38400', '56000', '57600', '115200',
                                     '128000', '256000', '460800', '500000', '512000', '600000',
                                     '750000', '921600', '1000000', '1500000', '2000000'])
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
            # asyncio.ensure_future(read_and_print(self.ser))
            if self.comboBox_scheme.currentText() in ["串口PVA接收"]:
                asyncio.ensure_future(read_pva_hex(self.ser, self.pva_hex_to_display))
            elif self.comboBox_scheme.currentText() in ["不使用"]:
                asyncio.ensure_future(read_hex_(self.ser, self.raw_hex_to_display))

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

