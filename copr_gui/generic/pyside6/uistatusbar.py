from PySide6 import QtWidgets, QtGui
from PySide6.QtWidgets import QDialog
from PySide6.QtWidgets import QApplication, QMessageBox

def error(label, window, parent=None):
    msg_box = QtWidgets.QMessageBox(parent)
    msg_box.setWindowTitle(window)
    msg_box.setText(label)
    msg_box.setIcon(QtWidgets.QMessageBox.Icon.Critical)
    msg_box.addButton(QtWidgets.QMessageBox.StandardButton.Ok)
    msg_box.exec()

class WindowFrame(QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def Show(self):
        return super().show()

    def SetTitle(self, title):
        return super().setWindowTitle(title)

    def Close(self):
        return super().close()

    def SetIconFromPath(self, path):
        return super().setWindowIcon(QtGui.QIcon(path))

def Frame(parent, title=""):
    return WindowFrame(parent, windowTitle=title)
    # frame.setIconFromPath = lambda path: frame.setWindowIcon(QtGui.QIcon(path))



from PySide6 import QtCore
import datetime

def wx_datetime_to_date(pyside_dt):
    if isinstance(pyside_dt, datetime.date):
        return pyside_dt
    elif isinstance(pyside_dt, int):
        return datetime.datetime.fromtimestamp(pyside_dt).date()
    elif isinstance(pyside_dt, QtCore.QDate):
        return datetime.date(pyside_dt.year(), pyside_dt.month(), pyside_dt.day())

    year = pyside_dt.year()
    month = pyside_dt.month()
    day = pyside_dt.day()
    return datetime.date(year, month, day)

def wx_datetime_to_time(pyside_dt):
    if isinstance(pyside_dt, datetime.time):
        return pyside_dt
    elif isinstance(pyside_dt, int):
        return datetime.datetime.fromtimestamp(pyside_dt).time()
    elif isinstance(pyside_dt, QtCore.QTime):
        return datetime.time(pyside_dt.hour(), pyside_dt.minute(), pyside_dt.second(), pyside_dt.msec() * 1000)

    hour = pyside_dt.hour()
    minute = pyside_dt.minute()
    second = pyside_dt.second()
    microsecond = pyside_dt.msec() * 1000
    return datetime.time(hour, minute, second, microsecond)

def date_to_wx_datetime(py_date):
    if isinstance(py_date, QtCore.QDate):
        return py_date
    elif isinstance(py_date, int):
        return QtCore.QDateTime.fromSecsSinceEpoch(py_date).date()
    elif isinstance(py_date, datetime.datetime):
        return QtCore.QDate(py_date.year, py_date.month, py_date.day)

    pyside_dt = QtCore.QDate()
    pyside_dt.setDate(py_date.year, py_date.month, py_date.day)
    return pyside_dt

def time_to_wx_datetime(py_time):
    if isinstance(py_time, QtCore.QTime):
        return py_time
    elif isinstance(py_time, int):
        return QtCore.QDateTime.fromSecsSinceEpoch(py_time).time()
    elif isinstance(py_time, datetime.datetime):
        return QtCore.QTime(py_time.hour, py_time.minute, py_time.second, py_time.microsecond // 1000)

    pyside_dt = QtCore.QTime()
    pyside_dt.setHMS(py_time.hour, py_time.minute, py_time.second, py_time.microsecond // 1000)
    return pyside_dt


from PySide6 import QtWidgets, QtGui, QtCore

def CreateApp():
    return QtWidgets.QApplication([])

def InitApp(app):
    return app.exec()

def browser(url):
    QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

def show_text_frame(text, title="Text Frame", parent=None):
    app = QtWidgets.QApplication.instance() if QtWidgets.QApplication.instance() else create_app()
    frame = QtWidgets.QWidget(parent, QtCore.Qt.Window)
    frame.setWindowTitle(title)
    frame.resize(400, 300)
    layout = QtWidgets.QVBoxLayout(frame)
    layout.setContentsMargins(0, 0, 0, 0)
    text_edit = QtWidgets.QPlainTextEdit(frame)
    text_edit.setReadOnly(True)
    text_edit.setPlainText(text)
    layout.addWidget(text_edit)
    frame.show()
    app.exec()

def question(label, window, parent=None):
    msg_box = QtWidgets.QMessageBox(parent)
    msg_box.setWindowTitle(window)
    msg_box.setText(label)
    msg_box.setIcon(QtWidgets.QMessageBox.Icon.Question)
    msg_box.addButton(QtWidgets.QMessageBox.StandardButton.Yes)
    msg_box.addButton(QtWidgets.QMessageBox.StandardButton.No)
    answer = msg_box.exec()
    return answer == QtWidgets.QMessageBox.StandardButton.Yes

from PySide6 import QtCore, QtWidgets

class ProgressThread(QtCore.QThread):
    def __init__(self, generator, progress_dialog):
        super().__init__()
        self.stop_req = False
        self.generator = generator
        self.progress_dialog = progress_dialog

    def stop(self):
        self.stop_req = True

    def run(self):
        i = 0
        for item in self.generator:
            if self.stop_req:
                return
            i += 1
            QtCore.QMetaObject.invokeMethod(self.progress_dialog, "update", QtCore.Qt.QueuedConnection, QtCore.Q_ARG(int, i))

        QtCore.QMetaObject.invokeMethod(self.progress_dialog, "close_call", QtCore.Qt.QueuedConnection)

class ProgressDialog(QtWidgets.QProgressDialog):
    def __init__(self, parent, title, message, label, maximum, close):
        super().__init__(message, None, 0, maximum, parent)
        self.setWindowTitle(title)
        self.setLabelText(label)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setAutoClose(True)
        self.setAutoReset(False)
        self.canceled.connect(self.close)

        self.__close = close

    @QtCore.Slot(int)
    def update(self, value):
        try:
            self.setValue(value)
        except RuntimeError:
            pass

    @QtCore.Slot()
    def close_call(self):
        close = self.__close
        if callable(close):
            close()
        elif close:
            self.close()

    def closeEvent(self, event):
        if hasattr(self, 'thread'):
            self.thread.stop()
        super().closeEvent(event)

    CloseEvent=closeEvent
    CloseCall = close_call
    Update = update


def job_generator(data, function):
    for i in data:
        yield function(i)

def execute_data_with_progress(data, job, label, window, close=True):
    return execute_with_progress(job_generator(data, job), len(data), label, window, close)

def execute_with_progress(generator, length, label, window, close=True):
    dialog = ProgressDialog(None, window, label, label, length, close)
    thread = ProgressThread(generator, dialog)
    dialog.thread = thread
    thread.start()
    dialog.show()
    return dialog

if __name__ == '__main__':
    import time
    def job_function(ev):
        time.sleep(1)
        print(ev)
    class MainWindow(QtWidgets.QWidget):
      def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Main Window")
        layout = QtWidgets.QVBoxLayout(self)

        button = QtWidgets.QPushButton("Start Job", self)
        layout.addWidget(button)

        button.clicked.connect(lambda: execute_data_with_progress(job=job_function, data=[1, 2, 3, 4, 5, 6, 7, 8], label="Points", window="Progress Window", close=False))
    app = CreateApp()

    frame = Frame(None, 'fine')
    panel = MainWindow(frame)

    frame.show()

    InitApp(app)

