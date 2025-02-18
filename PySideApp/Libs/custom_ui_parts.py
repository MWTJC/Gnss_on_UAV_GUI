from PySide6.QtCore import QRect, QSize, QPoint
from PySide6.QtGui import Qt, QIcon
from PySide6.QtWidgets import QSizePolicy, QToolButton, QWidget, QScrollArea, QVBoxLayout, QHBoxLayout


class FlowWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self._widgets = []
        self._spacing = 6  # 默认间距

    def addWidget(self, widget):
        widget.setParent(self)
        self._widgets.append(widget)
        self.updateGeometry()

    def removeWidget(self, widget):
        if widget in self._widgets:
            self._widgets.remove(widget)
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
        for widget in self._widgets:
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

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self._spacing

        margins = self.contentsMargins()
        x += margins.left()
        y += margins.top()
        rect_right = rect.right() - margins.right()

        for widget in self._widgets:
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


def add_func_block_single(tab_page:QWidget, layout:QVBoxLayout|QHBoxLayout, text:str):
    scrollArea = QScrollArea(tab_page)
    scrollArea.setWidgetResizable(True)
    scrollAreaWidgetContents = QWidget()
    verticalLayout_3 = QVBoxLayout(scrollAreaWidgetContents)
    toolButton_expand = QToolButton(scrollAreaWidgetContents)
    toolButton_expand.setText(text)
    sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    sizePolicy.setHorizontalStretch(0)
    sizePolicy.setVerticalStretch(0)
    sizePolicy.setHeightForWidth(toolButton_expand.sizePolicy().hasHeightForWidth())
    toolButton_expand.setSizePolicy(sizePolicy)
    toolButton_expand.setIconSize(QSize(10, 10))
    toolButton_expand.setCheckable(True)
    toolButton_expand.setChecked(True)
    toolButton_expand.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
    toolButton_expand.setArrowType(Qt.ArrowType.DownArrow)
    verticalLayout_3.addWidget(toolButton_expand)
    flow_widget = FlowWidget(scrollAreaWidgetContents)
    verticalLayout_3.addWidget(flow_widget)
    scrollArea.setWidget(scrollAreaWidgetContents)
    layout.addWidget(scrollArea)
    return toolButton_expand, flow_widget