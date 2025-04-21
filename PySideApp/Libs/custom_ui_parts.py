from functools import wraps

from PySide6.QtCore import QRect, QSize, QPoint, QTimer, QObject, Signal, Slot
from PySide6.QtGui import Qt, QIcon
from PySide6.QtWidgets import QSizePolicy, QToolButton, QWidget, QScrollArea, QVBoxLayout, QHBoxLayout, QPushButton


class SearchDict:
    def __init__(self, keywords:list[str], button:QToolButton|QPushButton):
        self.keywords = keywords  # list[str]
        self.button = button  # 关联的按钮

    def matches(self, search_text):
        """检查搜索文本是否匹配任何关键词"""
        if not search_text:
            return True  # 空搜索显示所有

        search_text = search_text.lower()
        return any(keyword.lower().find(search_text) >= 0 for keyword in self.keywords)

class FlowWidget(QWidget):
    def __init__(self, parent=None, expand_button:QToolButton|None=None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self._widgets = []
        self._visible_widgets = []  # 跟踪可见的控件
        self._spacing = 6  # 默认间距
        self.expand_button = expand_button

    def addWidget(self, widget):
        widget.setParent(self)
        self._widgets.append(widget)
        self._visible_widgets.append(widget)
        self.updateGeometry()

    def removeWidget(self, widget):
        if widget in self._widgets:
            self._widgets.remove(widget)
            if widget in self._visible_widgets:
                self._visible_widgets.remove(widget)
            widget.setParent(None)
            self.updateGeometry()

    def setSpacing(self, spacing):
        self._spacing = spacing
        self.updateGeometry()

    def spacing(self):
        return self._spacing

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for widget in self._visible_widgets:
            size = size.expandedTo(widget.minimumSize())
        margins = self.contentsMargins()
        size += QSize(2 * margins.left(), 2 * margins.top())
        return size

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), True)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._do_layout(self.rect(), False)

    def updateVisibleWidgets(self):
        """更新可见控件列表"""
        if self.expand_button:
            if self.expand_button.isChecked():
                pass
            else:
                self.expand_button.click()
            # self.expand_button.setChecked(True)


        self._visible_widgets = [w for w in self._widgets if w.isVisible()]
        self.updateGeometry()
        self._do_layout(self.rect(), False)
        if self._visible_widgets:
            pass
        else:
            self.expand_button.click()
            # self.expand_button.setChecked(False)


    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self._spacing

        margins = self.contentsMargins()
        x += margins.left()
        y += margins.top()
        rect_right = rect.right() - margins.right()

        for widget in self._visible_widgets:
            space_x = spacing
            space_y = spacing

            next_x = x + widget.sizeHint().width() + space_x
            if next_x - space_x > rect_right and line_height > 0:
                x = rect.x() + margins.left()
                y = y + line_height + space_y
                next_x = x + widget.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                widget.setGeometry(QRect(QPoint(x, y), widget.sizeHint()))

            x = next_x
            line_height = max(line_height, widget.sizeHint().height())

        return y + line_height - rect.y() + margins.bottom()


def add_func_single(text: str, flow_widget:FlowWidget, icon=None, ):
    toolButton = QToolButton()
    toolButton.setText(text)
    if icon is None:
        icon = QIcon(QIcon.fromTheme(u"folder"))
    toolButton.setIcon(icon)
    toolButton.setIconSize(QSize(32, 32))
    toolButton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
    flow_widget.addWidget(toolButton)
    return toolButton


def add_func_block_single(area:QScrollArea, layout:QVBoxLayout|QHBoxLayout, text:str):
    toolButton_expand = QToolButton(area)
    toolButton_expand.setText(text)
    sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(toolButton_expand.sizePolicy().hasHeightForWidth())
    toolButton_expand.setSizePolicy(sizePolicy)
    toolButton_expand.setIconSize(QSize(8, 8))
    toolButton_expand.setCheckable(True)
    toolButton_expand.setChecked(True)
    toolButton_expand.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
    toolButton_expand.setArrowType(Qt.ArrowType.DownArrow)
    layout.addWidget(toolButton_expand)
    flow_widget = FlowWidget(area, expand_button=toolButton_expand)
    layout.addWidget(flow_widget)

    return toolButton_expand, flow_widget


class ActivityIndicator(QObject):
    activity_signal = Signal()

    def __init__(self, button: QPushButton,
                 active_style="background-color: green;",
                 inactive_style="background-color: gray;",
                 duration=100):
        """
        初始化活动指示器

        Args:
            button: 用作指示灯的QPushButton
            active_style: 活动状态的样式
            inactive_style: 非活动状态的样式
            duration: 亮起持续时间(毫秒)
        """
        super().__init__()
        self.button = button
        self.active_style = active_style
        self.inactive_style = inactive_style
        self.original_style = button.styleSheet()
        self.duration = duration

        # 设置计时器
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.reset_button)

        # 连接信号和槽
        self.activity_signal.connect(self.on_activity)

    @Slot()
    def on_activity(self):
        """当收到活动信号时触发"""
        self.button.setStyleSheet(self.active_style)
        self.timer.start(self.duration)  # 指定时间后恢复

    def reset_button(self):
        """重置按钮样式"""
        self.button.setStyleSheet(self.inactive_style or self.original_style)

    def notify(self):
        """通知有活动发生"""
        self.activity_signal.emit()

    def decorate(self, func):
        """装饰器，用于监控函数执行"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            self.notify()
            return func(*args, **kwargs)

        return wrapper