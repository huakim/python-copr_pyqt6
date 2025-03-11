from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QHBoxLayout, QApplication


class ListWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create a layout for the widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create a list to keep track of the line edits and remove buttons
        self.line_edits = []

    def add_line_edit(self):
        # Create a QHBoxLayout to hold the line edit and remove button
        h_layout = QHBoxLayout()

        # Create a QLineEdit and add it to the layout
        line_edit = QLineEdit()

        # Create a QPushButton with "-" sign and add it to the layout
        remove_button = QPushButton("-")
        remove_button.setFixedWidth(50)
        h_layout.addWidget(remove_button)
        h_layout.addWidget(line_edit)
        h_layout.setContentsMargins(0, 0, 0, 0)

        # Connect the remove button's clicked signal to a slot
        remove_button.clicked.connect(lambda: self.remove_line_edit(h_layout))

        # Add the QHBoxLayout to the main layout
        self.layout().insertLayout(len(self.line_edits), h_layout)

        # Add the line edit and remove button to the list
        self.line_edits.append((line_edit, remove_button))

    def remove_line_edit(self, h_layout):
        # Remove the QHBoxLayout from the main layout
        for i in reversed(range(h_layout.count())):
            h_layout.itemAt(i).widget().setParent(None)

        # Remove the line edit and remove button from the list
        for line_edit, remove_button in self.line_edits:
            if remove_button.parent() is None:
                self.line_edits.remove((line_edit, remove_button))
                break

    def set_list(self, values):
        # Clear the current line edits and remove buttons
        for line_edit, remove_button in self.line_edits:
            line_edit.setParent(None)
            remove_button.setParent(None)
        self.line_edits.clear()

        # Add line edits for each value in the list
        for value in values:
            self.add_line_edit()
            self.line_edits[-1][0].setText(value)

    def get_list(self):
        # Get the values from the line edits
        return [line_edit.text() for line_edit, _ in self.line_edits]

    def get_size(self):
        # Get the current number of line edits
        return len(self.line_edits)

    def set_size(self, size):
        current_size = self.get_size()

        if size > current_size:
            # Add line edits to reach the desired size
            for _ in range(size - current_size):
                self.add_line_edit()
        elif size < current_size:
            # Remove line edits to reach the desired size
            for _ in range(current_size - size):
                self.remove_line_edit(self.layout().itemAt(size).layout())


from PySide6 import QtWidgets
from PySide6.QtWidgets import QSizePolicy


class SettingsScrolledWindowClass(QtWidgets.QScrollArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setWidget(QtWidgets.QWidget())
   #     self.widget().setLayout(QtWidgets.QVBoxLayout())
   #     self.widget().layout().setAlignment(QtCore.Qt.AlignTop)
        self.setScrollRate(10, 10)

    def setScrollRate(self, rate_x, rate_y):
        self.verticalScrollBar().setSingleStep(rate_y)


def SettingsScrolledWindow(self):
    layout = QVBoxLayout(self)
    f = SettingsScrolledWindowClass(self)
    layout.addWidget(f)
    self.setLayout(layout)
    f.setSizePolicy(
        QSizePolicy.Expanding,
        QSizePolicy.Expanding
    )
    return f.widget()

from PySide6 import QtCore, QtWidgets

from PySide6.QtWidgets import QPlainTextEdit



from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget, QTextEdit
from PySide6.QtGui import QFontMetrics
from PySide6.QtCore import Qt

class ExpandoTextCtrl(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.textChanged.connect(self.updateHeight)  # Connect the textChanged signal to the updateHeight slot

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.updateHeight()

    def setText(self, text):
        super().setText(text)
        self.updateHeight()

    def updateHeight(self):
        document = self.document()
        height = document.size().height()+5
        self.setMaximumHeight(height)
        self.setMinimumHeight(height)


#ExpandoTextCtrl=QtWidgets.QPlainTextEdit

from PySide6.QtWidgets import QDateEdit, QTimeEdit
from PySide6.QtCore import QDate, Qt, QTime

class TimePickerCtrl(QTimeEdit):
    def __init__(time_edit, parent=None):
        super().__init__(parent)

        time_edit.setDisplayFormat('hh:mm:ss')
        time_edit.setTime(QTime.currentTime())
        time_edit.setAlignment(Qt.AlignCenter)
        time_edit.setReadOnly(False)


class DatePickerCtrl(QDateEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDisplayFormat('yyyy-MM-dd')
        self.setDate(QDate.currentDate())
        self.setAlignment(Qt.AlignCenter)
        self.setCalendarPopup(True)


class UiSettingsPanel(QtWidgets.QWidget):
    def addTabWidget(self):
        notebook = QtWidgets.QTabWidget(self.scrolled_window)
        self.form_sizer.addWidget(notebook, 1, QtCore.Qt.AlignTop)
        notebook.setContentsMargins(0, 0, 0, 0)
        return notebook

    def addList(self):
        notebook = ListWidget(self.scrolled_window)
        self.form_sizer.addWidget(notebook, 1, QtCore.Qt.AlignTop)
        return notebook

    def incTabWidget(self, notebook, checkbox, value):
        notebook.addTab(checkbox, value)

    @staticmethod
    def incList(fields):
        fields.add_line_edit()

    def addLabelPlusButton(self, field_name):
        list_panel = QtWidgets.QWidget(self.scrolled_window)
        list_sizer = QtWidgets.QHBoxLayout(list_panel)
        list_sizer.setContentsMargins(0, 0, 0, 0)
        list_panel.setLayout(list_sizer)
        self.form_sizer.addWidget(list_panel, alignment=QtCore.Qt.AlignTop)
        label = QtWidgets.QLabel(f'{field_name}', list_panel)
        add_button = QtWidgets.QPushButton('+', list_panel)
        add_button.setFixedWidth(50)
 #       add_button.setMaximumSize(50, -1)
        list_sizer.addWidget(add_button)
        list_sizer.addWidget(label)
        return add_button

    def addText(self):
        text_ctrl = ExpandoTextCtrl(self.scrolled_window)
        self.form_sizer.addWidget(text_ctrl)
        return text_ctrl

    @staticmethod
    def bindCheckBox(checkbox, func):
        checkbox.stateChanged.connect(func)

    @staticmethod
    def bindButton(checkbox, func):
        checkbox.clicked.connect(func)

    def addButton(self, field_name):
        checkbox = QtWidgets.QPushButton(field_name, self.scrolled_window)
        self.form_sizer.addWidget(checkbox)
        return checkbox

    def addCheckBox(self, field_name):
        checkbox = QtWidgets.QCheckBox(field_name, self.scrolled_window)
        self.form_sizer.addWidget(checkbox)
        return checkbox

    def addHorBox(self):
        panel = SimplePanel(self.scrolled_window)
        self.form_sizer.addWidget(panel)
        return panel

    def addLine(self):
        text_ctrl = QtWidgets.QLineEdit(self.scrolled_window)
        self.form_sizer.addWidget(text_ctrl)
        return text_ctrl

    def addDate(self):
        text_ctrl = DatePickerCtrl(self.scrolled_window)
        self.form_sizer.addWidget(text_ctrl)
        return text_ctrl

    def addTime(self):
        text_ctrl = TimePickerCtrl(self.scrolled_window)
        self.form_sizer.addWidget(text_ctrl)
        return text_ctrl

    @staticmethod
    def bindComboBox(combobox, func):
        combobox.currentIndexChanged.connect(func)

    def addComboBox(self, values):
        combobox = QtWidgets.QComboBox(self.scrolled_window)
        combobox.addItems(values)
        self.form_sizer.addWidget(combobox)
        combobox.setCurrentIndex(0)
        return combobox

    def addLabel(self, field_name):
        label = QtWidgets.QLabel(f'\t{field_name}', self.scrolled_window)
        self.form_sizer.addWidget(label)

    @staticmethod
    def createVerticalLayout():
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment( Qt.AlignTop)
        return layout

    @staticmethod
    def create_panel(self):
        layout = UiSettingsPanel.createVerticalLayout()
        f = QWidget(self)
        layout.addWidget(f)
        self.setLayout(layout)
        f.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Expanding
        )
        return f

    def addCheckBoxPanel(self):
        panel=WrapCheckBoxPanel(self)
        self.form_sizer.addWidget(panel)
        return panel

    def addButtonPanel(self):
        panel=WrapButtonPanel(self)
        self.form_sizer.addWidget(panel)
        return panel

    def Init(self):
        scrolled_window = self.scrolled_window
        scrolled_window.setLayout(self.form_sizer)

    def startInit(self):
#        self.vertical_layout = self.createVerticalLayout()
        self.form_sizer = form_sizer = self.createVerticalLayout()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        parent = self.parentWidget()
        if not parent is None:
            layout = parent.layout()
            if layout is None:
                layout = self.createVerticalLayout()
                parent.setLayout(layout)
            layout.addWidget(self)


    SetTextValue = staticmethod(ExpandoTextCtrl.setPlainText)
    SetLineValue = staticmethod(QtWidgets.QLineEdit.setText)
    SetDateValue = staticmethod(DatePickerCtrl.setDate)
    SetTimeValue = staticmethod(TimePickerCtrl.setTime)
    SetCheckBoxValue = staticmethod(QtWidgets.QCheckBox.setChecked)
    SetListValue = staticmethod(ListWidget.set_list)
    SetComboBoxSelection = staticmethod(QtWidgets.QComboBox.setCurrentIndex)
    SetTabWidgetSelection = staticmethod(QtWidgets.QTabWidget.setCurrentIndex)


    GetTextValue = staticmethod(ExpandoTextCtrl.toPlainText)
    GetLineValue = staticmethod(QtWidgets.QLineEdit.text)
    GetDateValue = staticmethod(DatePickerCtrl.date)
    GetTimeValue = staticmethod(TimePickerCtrl.time)
    GetCheckBoxValue = staticmethod(QtWidgets.QCheckBox.isChecked)
    GetListValue = staticmethod(ListWidget.get_list)
    GetComboBoxSelection = staticmethod(QtWidgets.QComboBox.currentIndex)
    GetTabWidgetSelection = staticmethod(QtWidgets.QTabWidget.currentIndex)




from PySide6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QPushButton, QHBoxLayout
from PySide6.QtCore import Qt, QEvent


class WrapPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.form_sizer = QVBoxLayout(self)
        self.form_sizer.setAlignment(Qt.AlignTop)
        self.form_sizer.setSpacing(3)
        self.form_sizer.setContentsMargins(3, 3, 3, 3)

    def finish_widget(self, widget):
        widget.installEventFilter(self)
        return widget

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize:
            self.wrap_widgets()
        return super().eventFilter(obj, event)

    def wrap_widgets(self):
        width = self.width()
        row_width = 0
        row_height = 0
        total_height = 0  # Track the total height of all rows

        for i in range(self.form_sizer.count()):
            widget = self.form_sizer.itemAt(i).widget()
            widget_width = widget.sizeHint().width()
            widget_height = widget.sizeHint().height()

            if row_width + widget_width > width:
                # Wrap to the next row
                row_width = 0
                total_height += row_height
                row_height = 0

            row_width += widget_width
            row_height = max(row_height, widget_height)

            widget.setGeometry(row_width - widget_width, total_height + row_height - widget_height, widget_width, widget_height)

            row_width += 3  # Add spacing between widgets

        total_height += row_height
        self.setMinimumHeight(total_height)

    def add_widget(self, widget):
        self.form_sizer.addWidget(widget)
        widget.installEventFilter(self)



class WrapCheckBoxPanel(WrapPanel):
    def __init__(self, parent):
        super().__init__()

    def add(self, label, checked=False):
        checkbox = QCheckBox(label)
        checkbox.setChecked(checked)
        self.add_widget(checkbox)
        return checkbox

    def bind(self, checkbox, callback):
        checkbox.stateChanged.connect(callback)

class WrapButtonPanel(WrapPanel):
    def __init__(self, parent):
        super().__init__()

    def add(self, label):
        button = QPushButton(label)
        self.add_widget(button)
        return button

    def bind(self, button, callback):
        button.clicked.connect(callback)
