from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog
from PySideApp.pyui.SettingsUI import Ui_Dialog_settings
from PySideApp.pyui.img_resource_rc import *
iconpath = ":/ico/app_icon.ico"

class SettingsManager(QDialog, Ui_Dialog_settings):
    def __init__(self, apply_settings_callback):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(iconpath))
        self.apply_to = apply_settings_callback
        self.settings = {}
        # 信号绑定
        self.pushButton_settings_ok.clicked.connect(self.apply_settings)
        self.pushButton_settings_cancel.clicked.connect(self.close)

    def get_settings(self, settings_read:dict):
        self.settings = settings_read

    def show(self):
        self.display_settings()
        super().show()

    def display_settings(self):
        if 'Theme' in self.settings:
            theme = self.settings['Theme']
            self.comboBox_settings_theme.setCurrentText(theme)

    def apply_settings(self):
        if len(self.settings) == 0:
            self.close()
        self.settings = {
            'Theme': self.comboBox_settings_theme.currentText()
        }
        self.apply_to(self.settings)
        self.close()
