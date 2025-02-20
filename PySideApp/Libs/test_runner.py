import time

from PySide6.QtCore import Signal, QTimer
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import QDialog, QLabel, QHBoxLayout, QLineEdit, QFormLayout, QGroupBox

from PySideApp.Libs.calculation_lib import TestModule, GBT2038058_2019_6_4_5
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

    def test_redo_step(self):
        self.test_module.test_task.redo_step()
        self.refresh()

    def test_start(self):
        if self.param_input_lineedit_list:
            # 存储输入参数
            for lineedit, param_class in zip(self.param_input_lineedit_list, self.test_module.get_input_list()):
                param_class.set_value(lineedit.text())

        self.tabWidget_test_runner.setTabEnabled(0, False)
        self.tabWidget_test_runner.setTabEnabled(1, True)
        self.tabWidget_test_runner.setCurrentWidget(self.tab_test_runner)
        a = self.textEdit_mark.toPlainText()
        self.test_module.init_test_task(uuid=int(self.lineEdit_uuid.text()), note=a)
        self.refresh()
        self.timer.start(333)  # 设置0.3秒刷新一次

    def refresh(self):
        step_item, last_step = self.test_module.test_task.get_steps()
        self.label_current_test.setText(self.test_module.name)
        self.label_step_describe.setText(step_item.describe)
        if last_step:  # 没有下一步
            self.pushButton_next_step.setDisabled(True)
            self.pushButton_finish.setEnabled(True)
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

    def set_test_info(self, uuid:int, module:TestModule|GBT2038058_2019_6_4_5):
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
            # 为每个输入参数创建控件
            self.param_input_lineedit_list = []  # 记录输入函数框以方便取值
            for index, param in enumerate(input_list):
                # 创建标签
                label = QLabel(self.groupBox_params)
                label.setText(f"{param.name}")

                # 创建水平布局来包含输入框和单位标签
                h_layout = QHBoxLayout()

                # 创建输入框
                input_field = QLineEdit(self.groupBox_params)
                input_field.setValidator(double_validator)
                input_field.setText(str(param.value))

                # 创建单位标签
                unit_label = QLabel(self.groupBox_params)
                unit_label.setText(param.unit)

                # 将输入框和单位标签添加到水平布局
                h_layout.addWidget(input_field)
                h_layout.addWidget(unit_label)

                # 将标签和水平布局添加到参数表单布局
                self.formLayout_params.setWidget(index, QFormLayout.ItemRole.LabelRole, label)
                self.formLayout_params.setLayout(index, QFormLayout.ItemRole.FieldRole, h_layout)

                # 记录lineedit
                self.param_input_lineedit_list.append(input_field)
            # 添加进现有布局
            self.verticalLayout_4.insertWidget(1, self.groupBox_params)  # 有参数
        else:  # 没参数
            label = QLabel(self.groupBox_params)
            label.setText("无输入参数")

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