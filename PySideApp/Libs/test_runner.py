import time

from PySide6.QtCore import Signal, QTimer
from PySide6.QtGui import QDoubleValidator, QIntValidator, Qt
from PySide6.QtWidgets import QDialog, QLabel, QHBoxLayout, QLineEdit, QFormLayout, QGroupBox, QMessageBox, QPushButton

from PySideApp.Libs.TestModuleLib import GBT38058_2019
from PySideApp.Libs.test_tasks_lib import TestModule
from PySideApp.pyui.TestRunnerUI import Ui_Dialog


class TestRunner(Ui_Dialog, QDialog):
    signal_test_over = Signal()
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.bind_signal()
        self.timer_var = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_timer_label)
        self.groupBox_params:QGroupBox|None = None
        self.param_input_lineedit_list:list[QLineEdit]|None = None

    def bind_signal(self):
        self.pushButton_start_test.clicked.connect(self.test_start)
        self.pushButton_next_step.clicked.connect(self.test_next_step)
        self.pushButton_prev_step.clicked.connect(self.test_prev_step)
        self.pushButton_redo_step.clicked.connect(self.test_redo_step)
        self.pushButton_finish.clicked.connect(self.test_finished)

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
            for lineedit, param_class in zip(self.param_input_lineedit_list, self.test_module.get_input_list()):
                param_value = lineedit.text()
                if param_value in ['', None]:
                    QMessageBox.warning(self, "警告", "请确认全部参数已输入...")
                    return
                param_class.set_value(lineedit.text())
                param_list.append(param_class)

        self.tabWidget_test_runner.setTabEnabled(0, False)
        self.tabWidget_test_runner.setTabEnabled(1, True)
        self.tabWidget_test_runner.setCurrentWidget(self.tab_test_runner)
        a = self.textEdit_mark.toPlainText()
        self.test_module.init_test_task(
            uuid=int(self.lineEdit_uuid.text()),
            input_param_list=param_list, note=a
        )
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
        if self.groupBox_params:
            self.groupBox_params.deleteLater()
        self.lineEdit_uuid.clear()
        self.lineEdit_calculate_item.clear()
        self.textEdit_mark.clear()
        # self.pushButton_start_test.setText('开始测试')
        self.pushButton_next_step.setEnabled(True)
        self.pushButton_finish.setDisabled(True)
        self.tabWidget_test_runner.setCurrentWidget(self.tab_basic_info)
        self.tabWidget_test_runner.setTabEnabled(0, True)
        self.tabWidget_test_runner.setTabEnabled(1, False)
        self.tabWidget_test_runner.setTabEnabled(2, False)

    def set_test_info(self, uuid:int, module:TestModule|GBT38058_2019.T6_4_5):
        self.test_module = module
        self.reset_ui()
        self.lineEdit_uuid.setText(str(uuid))
        self.lineEdit_uuid.setDisabled(True)
        self.lineEdit_calculate_item.setText(str(module.name))
        self.lineEdit_calculate_item.setDisabled(True)

        # 创建一个新的 GroupBox 用于容纳参数输入控件
        self.groupBox_params = QGroupBox(self.groupBox_basic_info)
        self.groupBox_params.setTitle("参数设定")  # 可选的标题
        # 为参数 GroupBox 创建表单布局
        self.formLayout_params = QFormLayout(self.groupBox_params)
        self.formLayout_params.setVerticalSpacing(9)

        # 插入参数
        input_list = self.test_module.get_input_list()
        if len(input_list) > 0:
            double_validator = QDoubleValidator()
            int_validator = QIntValidator()
            # 为每个输入参数创建控件
            self.param_input_lineedit_list = []  # 记录输入函数框以方便取值
            for index, param in enumerate(input_list):
                # 创建标签
                label = QLabel(self.groupBox_params)
                label.setText(f"{param.name}")

                # 创建水平布局来包含输入框和单位标签
                h_layout = QHBoxLayout()

                if param.type in ["xy_point", "xyz_point", "z"]:
                    # 特殊类型处理
                    fields = []

                    if param.type == "xy_point":
                        # 经纬度输入框
                        for _ in range(2):
                            field = QLineEdit(self.groupBox_params)
                            field.setValidator(double_validator)
                            h_layout.addWidget(field)
                            fields.append(field)

                    elif param.type == "xyz_point":
                        # 经纬度和海拔输入框
                        for _ in range(3):
                            field = QLineEdit(self.groupBox_params)
                            field.setValidator(double_validator)
                            h_layout.addWidget(field)
                            fields.append(field)

                    elif param.type == "z":
                        # 海拔输入框
                        field = QLineEdit(self.groupBox_params)
                        field.setValidator(double_validator)
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

                    self.param_input_lineedit_list.extend(fields)

                else:
                    # 创建输入框
                    input_field = QLineEdit(self.groupBox_params)
                    if param.type in ["float"]:
                        input_field.setValidator(double_validator)
                    elif param.type in ["int"]:
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
        self.tabWidget_test_runner.setTabEnabled(1, False)
        self.tabWidget_test_runner.setTabEnabled(2, True)
        self.tabWidget_test_runner.setCurrentWidget(self.tab_test_over)
        self.signal_test_over.emit()

    def get_task_result(self):
        return self.test_module.export_test_task()

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()