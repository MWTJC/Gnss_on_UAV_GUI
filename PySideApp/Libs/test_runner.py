import time

from PySide6.QtCore import Signal, QTimer
from PySide6.QtGui import QDoubleValidator, QIntValidator, Qt
from PySide6.QtWidgets import QDialog, QLabel, QHBoxLayout, QLineEdit, QFormLayout, QGroupBox, QMessageBox, QPushButton, \
    QFileDialog
from loguru import logger

from PySideApp.Libs.TestModuleLib import GBT38058_2019
from PySideApp.Libs.read_pva_file import parse_pva_file, PVASheet
from PySideApp.Libs.test_tasks_lib import TestModule, ParamType, TestTask
from PySideApp.pyui.TestRunnerUI import Ui_Dialog


class TestRunner(Ui_Dialog, QDialog):
    signal_test_start = Signal()
    signal_test_over = Signal()
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.bind_signal()
        self.timer_var = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_timer_label)
        self.groupBox_params:QGroupBox|None = None
        self.param_input_lineedit_list:list[QLineEdit]|list[list[QLineEdit]]|None = None

    def bind_signal(self):
        self.pushButton_start_test.clicked.connect(self.test_start)
        self.pushButton_next_step.clicked.connect(self.test_next_step)
        self.pushButton_prev_step.clicked.connect(self.test_prev_step)
        self.pushButton_redo_step.clicked.connect(self.test_redo_step)
        self.pushButton_finish.clicked.connect(self.test_finished)
        self.pushButton_import_data.clicked.connect(self.import_data)
        self.pushButton_calcu_file.clicked.connect(self.PVA_calculate)  # 计算触发

    def import_data(self):
        if self.checkBox_import_from_file.isChecked():
            self.read_local_PVA_file()
        else:
            pass

    def read_local_PVA_file(self):
        fname, ftype = QFileDialog.getOpenFileName(
            self, "打开录制文件...", "",
            "txt文件(*.txt);;hex文件(*.DAT)",
        )
        if fname:
            logger.info(f"开始解析文件 {fname}...")
            packets, valid_count, offset_count = parse_pva_file(fname)
            if len(packets) == 0:
                logger.warning("未解析到任何报文")
                QMessageBox.warning(self, "警告", "未能解析到任何报文，请确认载入了正确的hex文件...")
                return
            else:
                logger.success(f"解析了{len(packets)}条PVA, 通过{valid_count}条, 跳跃{offset_count}次")
        else:
            logger.warning('取消打开...')
            return
        self.tabWidget_test_runner.setTabEnabled(1, True)
        self.tabWidget_test_runner.setCurrentIndex(1)
        self.textEdit_info.clear()
        md_text = (f"## 文件名\n"
                   f"{fname}\n"
                   f"## 总条数\n"
                   f"{len(packets)}\n"
                   f"## CRC通过\n"
                   f"{valid_count}\n"
                   f"## 跳跃次数\n"
                   f"{offset_count}\n"
                   f"- 跳跃次数应为0，否则可能存在损坏片段")
        self.textEdit_info.setMarkdown(md_text)


    def refresh_timer_label(self, to_zero=False):
            if not self.timer_var or to_zero:
                self.timer_var = time.time()

            time_now = time.time()
            seconds = time_now-self.timer_var
            # 分离整数秒和小数部分
            seconds = int(seconds)  # 获取整数秒部分
            # 计算时、分、秒
            minutes = (seconds % 3600) // 60
            seconds = seconds % 60
            self.label_timer.setText(f"{int(minutes):02d}:{int(seconds):02d}")

    def test_next_step(self):
        self.test_module.test_task.next_step()
        self.refresh()

    def test_prev_step(self):
        self.test_module.test_task.prev_step()
        self.refresh()

    def test_redo_step(self):
        self.test_module.test_task.redo_step()
        self.refresh()

    def test_start(self):
        param_list = []
        if self.param_input_lineedit_list:
            # 存储输入参数
            input_list = self.test_module.get_input_list()
            for lineedit, param_class in zip(self.param_input_lineedit_list, input_list):  # 对于单值参数
                if param_class.type in [ParamType.float, ParamType.int]:
                    param_value = lineedit.text()
                    if param_value in ['', None]:
                        QMessageBox.warning(self, "警告", "请确认全部参数已输入...")
                        return
                    param_class.set_value(lineedit.text())
                elif param_class.type in [ParamType.xy_point, ParamType.xyz_point, ParamType.z]:  # 对于多值参数
                    param_storage_list = []
                    for param in lineedit:
                        param_value = param.text()
                        if param_value in ['', None]:
                            QMessageBox.warning(self, "警告", "请确认全部参数已输入...")
                            return
                        param_storage_list.append(param.text())
                    param_class.set_value(param_storage_list)
                # 存储
                param_list.append(param_class)

        self.tabWidget_test_runner.setTabEnabled(0, False)
        self.tabWidget_test_runner.setTabEnabled(2, True)
        self.tabWidget_test_runner.setCurrentWidget(self.tab_test_runner)
        a = self.textEdit_mark.toPlainText()
        self.test_module.init_test_task(
            uuid=int(self.lineEdit_uuid.text()),
            input_param_list=param_list, note=a
        )
        self.signal_test_start.emit()
        self.refresh()
        self.timer.start(333)  # 设置0.3秒刷新一次

    def refresh(self):
        step_item, next_able, prev_able= self.test_module.test_task.get_steps()
        self.label_current_test.setText(self.test_module.name)
        self.label_step_describe.setText(step_item.describe)
        if not next_able:  # 没有下一步
            self.pushButton_next_step.setDisabled(True)
            self.pushButton_finish.setEnabled(True)
        else:
            self.pushButton_next_step.setEnabled(True)
            self.pushButton_finish.setDisabled(True)
        if not prev_able:  # 是第一步
            self.pushButton_prev_step.setDisabled(True)
        else:
            self.pushButton_prev_step.setEnabled(True)
        self.refresh_timer_label(True)  # 重新计时

    def reset_ui(self):
        self.param_input_lineedit_list = None  # 清空防止误用
        self.resize(50, 50)  # 重设窗口大小
        if self.groupBox_params:
            self.groupBox_params.deleteLater()
        self.lineEdit_uuid.clear()
        self.lineEdit_calculate_item.clear()
        self.textEdit_mark.clear()
        self.pushButton_start_test.setEnabled(True)
        self.pushButton_import_data.setDisabled(True)
        self.checkBox_import_from_file.setDisabled(True)
        # self.pushButton_start_test.setText('开始测试')
        self.pushButton_next_step.setEnabled(True)
        self.pushButton_finish.setDisabled(True)
        self.tabWidget_test_runner.setCurrentWidget(self.tab_basic_info)
        self.tabWidget_test_runner.setTabEnabled(0, True)
        self.tabWidget_test_runner.setTabEnabled(1, False)
        self.tabWidget_test_runner.setTabEnabled(2, False)
        self.tabWidget_test_runner.setTabEnabled(3, False)

    def PVA_calculate(self):
        logger.debug("计算")
        # self.test_module.calculate()

    def set_test_info(self, uuid:int=None,
                      module:TestModule|GBT38058_2019.T6_4_5=None,
                      history_task:TestTask=None
                      ):  # 用于显示历史检测记录
        self.test_module = module
        self.current_view_history_task:TestTask = history_task
        self.reset_ui()
        if not uuid:  # 如果是历史记录浏览
            self.pushButton_start_test.setDisabled(True)
            self.pushButton_import_data.setEnabled(True)
            self.checkBox_import_from_file.setEnabled(True)
            if history_task.org_dataframe is None:  # 如果历史数据中不包含在线数据，强制规定必须从外部导入数据
                self.checkBox_import_from_file.setChecked(True)
                self.checkBox_import_from_file.setDisabled(True)
            uuid = history_task.id
        self.lineEdit_uuid.setText(str(uuid))
        self.lineEdit_uuid.setDisabled(True)

        if module:
            name = module.name
        else:
            name = history_task.name
            self.textEdit_mark.setText(history_task.note)
        self.lineEdit_calculate_item.setText(str(name))
        self.lineEdit_calculate_item.setDisabled(True)

        # 创建一个新的 GroupBox 用于容纳参数输入控件
        self.groupBox_params = QGroupBox(self.groupBox_basic_info)
        self.groupBox_params.setTitle("参数设定")  # 可选的标题
        # 为参数 GroupBox 创建表单布局
        self.formLayout_params = QFormLayout(self.groupBox_params)
        self.formLayout_params.setVerticalSpacing(9)

        # 插入参数
        if self.test_module:  # 新建检测的情况
            input_list = self.test_module.get_input_list()
        else:  # 历史浏览的情况
            if not history_task:
                raise "非法输入参数"
            input_list = history_task.input_param_list
        if len(input_list) > 0:
            double_validator = QDoubleValidator()
            int_validator = QIntValidator()
            # 为每个输入参数创建控件
            self.param_input_lineedit_list = []  # 记录输入函数框以防止空值并方便取值
            for index, param in enumerate(input_list):
                # 创建标签
                label = QLabel(self.groupBox_params)
                label.setText(f"{param.name}")

                # 创建水平布局来包含输入框和单位标签
                h_layout = QHBoxLayout()

                if param.type in [ParamType.xy_point, ParamType.xyz_point, ParamType.z]:
                    # 特殊类型处理
                    fields = []

                    if param.type == ParamType.xy_point:
                        # 经纬度输入框
                        for i in range(2):
                            field = QLineEdit(self.groupBox_params)
                            field.setValidator(double_validator)
                            field.setText(str(param.value[i]))
                            h_layout.addWidget(field)
                            fields.append(field)

                    elif param.type == ParamType.xyz_point:
                        # 经纬度和海拔输入框
                        for i in range(3):
                            field = QLineEdit(self.groupBox_params)
                            field.setValidator(double_validator)
                            field.setText(str(param.value[i]))
                            h_layout.addWidget(field)
                            fields.append(field)

                    elif param.type == ParamType.z:
                        # 海拔输入框
                        field = QLineEdit(self.groupBox_params)
                        field.setValidator(double_validator)
                        field.setText(str(param.value[0]))
                        h_layout.addWidget(field)
                        fields.append(field)

                    # 添加获取定位按钮
                    location_btn = QPushButton("获取定位", self.groupBox_params)

                    def create_toggle_handler(btn, input_fields):
                        def toggle_location():
                            if btn.text() == "获取定位":
                                # 这里添加获取定位的逻辑
                                success = True  # 假设获取成功
                                if success:
                                    # 设置值并禁用输入框
                                    for field in input_fields:
                                        field.setDisabled(True)
                                    btn.setText("手动")
                                    btn.setStyleSheet("background-color: #3fa73d;")
                            else:
                                # 恢复手动输入
                                for field in input_fields:
                                    field.setDisabled(False)
                                btn.setText("获取定位")
                                btn.setStyleSheet("")

                        return toggle_location

                    location_btn.clicked.connect(create_toggle_handler(location_btn, fields))
                    h_layout.addWidget(location_btn)

                    self.param_input_lineedit_list.append(fields)  # 独立一个list记录特殊参数

                else:
                    # 创建输入框
                    input_field = QLineEdit(self.groupBox_params)
                    if param.type in [ParamType.float]:
                        input_field.setValidator(double_validator)
                    elif param.type in [ParamType.int]:
                        input_field.setValidator(int_validator)
                    input_field.setText(str(param.value))

                    # 创建单位标签
                    unit_label = QLabel(self.groupBox_params)
                    unit_label.setText(param.unit)

                    # 将输入框和单位标签添加到水平布局
                    h_layout.addWidget(input_field)
                    h_layout.addWidget(unit_label)

                    # 记录lineedit
                    self.param_input_lineedit_list.append(input_field)

                # 将标签和水平布局添加到参数表单布局
                self.formLayout_params.setWidget(index, QFormLayout.ItemRole.LabelRole, label)
                self.formLayout_params.setLayout(index, QFormLayout.ItemRole.FieldRole, h_layout)


        else:  # 没参数
            h_layout = QHBoxLayout()
            label = QLabel("无输入参数")
            h_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.groupBox_params.setLayout(h_layout)
            # 将标签添加到水平布局
            h_layout.addWidget(label)
            self.formLayout_params.setWidget(0, QFormLayout.ItemRole.LabelRole, label)
        # 添加进现有布局
        self.verticalLayout_4.insertWidget(1, self.groupBox_params)

    def test_finished(self):
        self.timer.stop()
        self.tabWidget_test_runner.setTabEnabled(0, False)
        self.tabWidget_test_runner.setTabEnabled(2, False)
        self.tabWidget_test_runner.setTabEnabled(3, True)
        self.tabWidget_test_runner.setCurrentWidget(self.tab_test_over)
        self.signal_test_over.emit()

    def get_task_result(self):
        return self.test_module.export_test_task()

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()