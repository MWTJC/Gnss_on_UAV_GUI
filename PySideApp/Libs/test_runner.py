from PySide6.QtCore import Signal
from PySide6.QtWidgets import QDialog

from PySideApp.Libs.calculation_lib import TestModule
from PySideApp.pyui.TestRunnerUI import Ui_Dialog


class TestRunner(Ui_Dialog, QDialog):
    signal_test_over = Signal()
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def reset(self):
        self.lineEdit_uuid.clear()
        self.lineEdit_calculate_item.clear()
        self.textEdit_mark.clear()

    def set_test_info(self, uuid:int, module:TestModule):
        self.reset()
        self.lineEdit_uuid.setText(str(uuid))
        self.lineEdit_calculate_item.setText(str(module.name))
        self.lineEdit_calculate_item.setDisabled(True)

    def test_finished(self):
        self.signal_test_over.emit()