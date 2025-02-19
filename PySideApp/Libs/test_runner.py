import time

from PySide6.QtCore import Signal, QTimer
from PySide6.QtWidgets import QDialog

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
        self.tabWidget_test_runner.setTabEnabled(0, False)
        self.tabWidget_test_runner.setTabEnabled(1, True)
        self.tabWidget_test_runner.setCurrentWidget(self.tab_test_runner)
        a = self.textEdit_mark.toPlainText()
        self.test_module.init_test_task(uuid=int(self.lineEdit_uuid.text()), note=a)
        self.refresh()
        self.timer.start(333)  # 设置0.3秒刷新一次

    def refresh(self):
        step_item, last_step = self.test_module.test_task.return_step()
        self.label_current_test.setText(self.test_module.name)
        self.label_step_describe.setText(step_item.describe)
        if last_step:  # 没有下一步
            self.pushButton_next_step.setDisabled(True)
            self.pushButton_finish.setEnabled(True)
        self.refresh_timer_label(True)  # 重新计时

    def reset(self):
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
        self.reset()
        self.lineEdit_uuid.setText(str(uuid))
        self.lineEdit_calculate_item.setText(str(module.name))
        self.lineEdit_calculate_item.setDisabled(True)

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