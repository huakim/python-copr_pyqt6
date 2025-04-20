from .uistatusbar import WindowFrame

# import datetime
from copr_gui.static.spec_types import getName, getId, getType
try:
    from PyQt6 import QtWidgets, QtGui, QtCore
except ImportError:
    from PySide6 import QtWidgets, QtGui, QtCore

QVBoxLayout = QtWidgets.QVBoxLayout
QHBoxLayout = QtWidgets.QHBoxLayout
QPushButton = QtWidgets.QPushButton
QApplication = QtWidgets.QApplication
QTableView = QtWidgets.QTableView
QMenu = QtWidgets.QMenu
QKeySequence = QtGui.QKeySequence
QClipboard = QtGui.QClipboard
QCursor = QtGui.QCursor
QAction = QtGui.QAction
Qt = QtCore.Qt
QAbstractTableModel = QtCore.QAbstractTableModel
ClipMode = QClipboard.Mode
QClipboard = QApplication.clipboard
ItemDataRole = Qt.ItemDataRole
SortOrder = Qt.SortOrder
Orientation = Qt.Orientation
ContextMenuPolicy = Qt.ContextMenuPolicy
StandardKey = QKeySequence.StandardKey
ItemFlag = Qt.ItemFlag
CheckState = Qt.CheckState


class Index(list):
    def __init__(self, row, col):
        list.__init__(self, (row, col))

    def GetRow(self):
        return self[0]

    def GetCol(self):
        return self[1]


class ContextMenu(QMenu):
    def __init__(self, parent, menus):
        super().__init__(parent)
        self.parent = parent
        for i in menus:
            nameid = getId(i)
            name = getName(i)
            item = QAction(name, self)
            self.addAction(item)
            setattr(self, nameid, item)
            nameid = f"on_{nameid}_option"
            if hasattr(self, nameid):
                item.triggered.connect(getattr(self, nameid))


class TableModel(QAbstractTableModel):
    def __getattr__(self, name):
        if name == "column_names":
            func = getName
        elif name == "column_ids":
            func = getId
        elif name == "column_types":

            def func(item, default="str"):
                return getType(item, default)

        else:
            raise AttributeError(name)
        try:
            return self.__data[name]
        except KeyError:
            data = self.__data[name] = [func(i) for i in self.columns]
            return data

    def __init__(self, columns, data=None):
        super().__init__()
        self.__data = dict()
        self.__last_sort = None
        self.columns = [{"id": "check_state", "name": "", "type": "bool"}] + columns
        #  self.column_names = [''] + [getName(i) for i in column_names]
        #  self.types = ['bool'] + [getType(i, 'str') for i in column_names]
        data = self.__rows = [] if data is None else data
        self.sort_col = None
        all = True
        for i in data:
            if not data[0]:
                all = False
                break
        self.all = all
        self.sort_reverse = False

    def DropItems(self, items):
        rows = []
        for i, item in enumerate(self.__rows):
            if item not in items:
                rows.append(i)
        self.beginResetModel()
        self.__rows = [self.__rows[i] for i in rows]
        self.endResetModel()

    def DropByCheck(self, check=False):
        rows = []
        for i, item in enumerate(self.__rows):
            if bool(item[0]) == check:
                rows.append(i)
        self.beginResetModel()
        self.__rows = [self.__rows[i] for i in rows]
        self.endResetModel()

    def CheckAll(self, check=True):
        for row in self.__rows:
            row[0] = 1 if check else ""
        self.all = check
        self.dataChanged.emit(
            self.index(0, 0),
            self.index(self.rowCount() - 1, 0),
            [ItemDataRole.CheckStateRole],
        )

    def GetNumberRows(self):
        return len(self.__rows)

    def GetNumberCols(self):
        return len(self.column_names)

    def IsEmptyCell(self, row, col):
        return False

    def GetRowItem(self, rowid):
        return self.__rows[rowid]

    def GetItemsByCheck(self, check=True):
        return [i for i in self.__rows if bool(i[0]) == check]

    def GetValue(self, row, col):
        return self.__rows[row][col]

    def SetValue(self, row, col, value):
        if col == 0:
            if not value:
                self.all = False
        self.__rows[row][col] = value

    def GetColLabelValue(self, col):
        return self.column_names[col]

    def AllChecked(self):
        return self.all

    def AppendRow(self, *row_data):
        for i in row_data:
            self.appendRow(i)

    def RestoreLastSort(self):
        self.sort(
            self.sort_col,
            (
                SortOrder.DescendingOrder
                if not self.sort_reverse
                else SortOrder.AscendingOrder
            )
        )

    def SortByColumn(self, col):
        if self.sort_col == col:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_col = col
            self.sort_reverse = False
        self.RestoreLastSort()

    def rowCount(self, parent=None):
        return len(self.__rows)

    def columnCount(self, parent=None):
        return len(self.columns)

    def data(self, index, role=ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if role == ItemDataRole.DisplayRole and self.column_types[col] != "bool":
            return str(self.__rows[row][col])
        elif role == ItemDataRole.CheckStateRole and self.column_types[col] == "bool":
            return (
                CheckState.Checked
                if bool(self.__rows[row][col])
                else CheckState.Unchecked
            )

        return None

    def setData(self, index, value, role=ItemDataRole.EditRole):
        if not index.isValid():
            return False

        row = index.row()
        col = index.column()

        if role == ItemDataRole.CheckStateRole and self.column_types[col] == "bool":
            self.__rows[row][col] = value != 0
            if col == 0 and value != CheckState.Checked:
                self.all = False
            self.dataChanged.emit(index, index, [role])
            return True

        return False

    def headerData(self, section, orientation, role=ItemDataRole.DisplayRole):
        if orientation == Orientation.Horizontal and role == ItemDataRole.DisplayRole:
            return self.column_names[section]
        elif orientation == Orientation.Vertical and role == ItemDataRole.DisplayRole:
            return str(section + 1)

        return None

    def flags(self, index):
        flags = ItemFlag.ItemIsEnabled | ItemFlag.ItemIsSelectable

        if self.column_types[index.column()] == "bool":
            flags |= ItemFlag.ItemIsUserCheckable

        return flags

    def sort(self, column, order=SortOrder.AscendingOrder):
        sort_reverse = order == SortOrder.DescendingOrder

        self.__rows.sort(key=lambda x: x[column], reverse=sort_reverse)
        self.layoutChanged.emit()

    def appendRow(self, row_data):
        self.beginInsertRows(
            self.index(len(self.__rows), 0), len(self.__rows), len(self.__rows)
        )
        self.__rows.append(row_data)
        self.endInsertRows()

    def removeRows(self, row, count, parent=None):
        self.beginRemoveRows(self.index(row, 0, parent), row, row + count - 1)
        del self.__rows[row: row + count]
        self.endRemoveRows()

    def clear(self):
        if self.rowCount() > 0:
            self.beginRemoveRows(self.index(0, 0), 0, self.rowCount() - 1)
            self.__rows.clear()
            self.endRemoveRows()

    RowCount = rowCount
    Clear = clear
    ColumnCount = columnCount


class CustomTable(QTableView):

    def PopupMenu(self, menu):
        cursor_position = self.mapFromGlobal(QCursor.pos())
        return menu.exec(self.mapToGlobal(cursor_position))

    def __init__(self, parent, table_model):
        super().__init__(parent)
        self.table_model = table_model
        self.setModel(table_model)
        self.verticalHeader().setDefaultSectionSize(25)
        self.setColumnWidth(0, 35)  # Set the width of the first column (Check column)
        for col in range(1, self.model().columnCount()):
            label = table_model.headerData(col, Orientation.Horizontal)
            width = (
                self.fontMetrics().boundingRect(label).width() + 40
            )  # Calculate the width based on the label
            self.setColumnWidth(col, width)  # Set the width of the column
        self.horizontalHeader().sectionClicked.connect(self.handleHeaderClick)
        copy_action = self.addAction("Copy")
        copy_action.setShortcut(StandardKey.Copy)
        copy_action.triggered.connect(self.copySelection)

    #      self.clicked.connect(self.onLabelLeftClick)
    def handleHeaderClick(self, index):
        self.table_model.SortByColumn(index)

    def keyPressEvent(self, event):
        if event.matches(StandardKey.Copy):
            self.copySelection()
        else:
            super().keyPressEvent(event)

    def copySelection(self):
        selection = self.selectionModel().selection()
        if selection:
            indexes = selection.indexes()
            rows = set(index.row() for index in indexes)
            columns = set(index.column() for index in indexes)

            data = []
            for row in rows:
                row_data = []
                for col in columns:
                    index = self.model().index(row, col)
                    value = self.model().data(index, ItemDataRole.DisplayRole)
                    row_data.append(str(value))
                data.append(row_data)

            text = "\n".join(["\t".join(row) for row in data])
            clipboard = QClipboard()
            clipboard.setText(text, mode=ClipMode.Clipboard)


class MonitorFrame(WindowFrame):
    def __init__(self, parent, button_names, column_names, title=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(1000, 600)

        vertical = self.vertical_layout = QVBoxLayout(self)
        vertical.setContentsMargins(5, 5, 5, 5)

        self.button_layout = QHBoxLayout()
        self.buttons = []  # List to store custom buttons
        self.addCustomButton("All")

        for name in button_names:
            self.addCustomButton(name)

        self.vertical_layout.addLayout(self.button_layout)

        model = self.model = TableModel(column_names)
        table = self.custom_table = CustomTable(self, model)
        table.setModel(self.model)

        table.doubleClicked.connect(self.onTableDoubleClicked)

        self.vertical_layout.addWidget(self.custom_table)

        table.setContextMenuPolicy(ContextMenuPolicy.CustomContextMenu)
        table.customContextMenuRequested.connect(self.onTableRightClicked)

    def PopupMenu(self, menu):
        self.custom_table.PopupMenu(menu)

    def getSelected(self):
        selected_indexes = self.custom_table.selectedIndexes()
        if selected_indexes:
            index = selected_indexes[0]
            row = index.row()
            column = index.column()
            return Index(row, column)
        return None

    def onTableRightClicked(self, position):
        index = self.getSelected()
        if index:
            return self.OnCellRightClick(index)

    def onTableDoubleClicked(self, event):
        index = self.getSelected()
        if index:
            return self.OnCellDoubleClick(index)

    def addCustomButton(self, label):
        label_text = getName(label)
        label = getId(label)
        button = QPushButton(label_text, self)
        self.button_layout.addWidget(button)
        label = f"button_{label}"
        setattr(self, label, button)
        label = f"{label}_clicked"
        if hasattr(self, label):
            button.clicked.connect(getattr(self, label))

    def button_all_clicked(self):
        model = self.model
        model.CheckAll(not model.AllChecked())
        self.custom_table.viewport().update()


# if __name__ == "__main__":
#     app = CreateApp()

#     button_names = ["Button 1", "Button 2", "Button 3"]
#     column_names = ["Column 1", "Column 2", "Column 3"]

#     frame = MonitorFrame(None, button_names, column_names)

#     # Add rows to the custom table
#     model = frame.model
#     model.setColumnCount(len(column_names))
#     model.setHorizontalHeaderLabels(column_names)

#     row_data = [
#         ["1", "Value 1", "Value 2", "Value 3"],
#         ["", "Value 4", "Value 5", "Value 6"],
#         ['', 'Value 5', 'Value 2', 'Value 4'],
#         ['', 'Value 4', 'Value 5', 'Value 6']
#     ]

#     for row in row_data:
#         items = [QStandardItem(item) for item in row]
#     model.AppendRow(*row_data)

#     InitApp(app)
