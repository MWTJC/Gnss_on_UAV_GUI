from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWebEngineCore import QWebEnginePage


class WebHandler(QObject):
    # 定义信号用于向JavaScript发送数据
    sendToJs = Signal(list)

    def __init__(self, page:QWebEnginePage):
        super().__init__()
        self.page = page
        self.ruler_end_callback = None

    @Slot(list, float)
    def receiveData(self, points, distance):
        """接收JavaScript发送的数据"""
        print("Received points:", points)
        print("Distance:", distance)
        # 这里可以处理接收到的数据

    def sendDataToJs(self, data):
        """发送数据到JavaScript"""
        # 通过执行JavaScript函数发送数据
        script = f"receiveFromPython({data})"
        self.page.runJavaScript(script)

    @Slot()
    def handleDrawEnd(self):
        self.ruler_end_callback()