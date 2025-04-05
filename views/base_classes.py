import os
import sys
from datetime import datetime
from typing import Union

import qdarktheme
from PySide6.QtCore import QItemSelectionModel, QModelIndex, \
    QPersistentModelIndex, Qt, QSortFilterProxyModel
from PySide6.QtGui import QPainter, QIcon
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QDialog, QWidget, QDialogButtonBox, QHBoxLayout, QMainWindow, QComboBox, QApplication, \
    QLineEdit, QTableView, QAbstractItemView, QHeaderView, QItemDelegate, QStyleOptionViewItem, QMessageBox, \
    QToolButton, QPushButton, QStyle

from logic.config import properties
from logic.crypt import decrypt_persons, encrypt_persons, generate_key
from logic.database import set_encryption_state
from logic.table_models import SearchTableModel
from views.base_functions import load_ui_file
from views.confirmationDialogs import ConfirmRestartDialog


class EditorDialog(QDialog):

    def __init__(self, parent: QWidget, ui_file_name: str):
        super(EditorDialog, self).__init__()
        self.parent = parent
        self.setModal(True)
        self.setMinimumWidth(450)
        self.setWindowTitle(" ")

        self.widget = EditorWidget(ui_file_name)

        self.button_box: QDialogButtonBox = self.get_widget(QDialogButtonBox, "buttonBox")

    def configure_widgets(self):
        self.button_box.accepted.connect(self.commit)
        self.button_box.rejected.connect(self.close)
        self.button_box.button(QDialogButtonBox.Ok).setText(self.tr("OK"))
        self.button_box.button(QDialogButtonBox.Ok).setFixedSize(150, 36)
        self.button_box.button(QDialogButtonBox.Cancel).setText(self.tr("Cancel"))
        self.button_box.button(QDialogButtonBox.Cancel).setFixedSize(150, 36)

    def commit(self):
        """Must be implemented by subclass"""

    def get_widget(self, widget_type: type, name: str):
        return self.widget.widget.findChild(widget_type, name)

    def clear_fields(self):
        self.widget.clear_fields()


class EditorWidget(QWidget):

    def __init__(self, ui_file_name: str, item_id: int = None):
        super(EditorWidget, self).__init__()

        self.validation_fields = []

        self.item_id = item_id
        ui_file = load_ui_file(ui_file_name)

        loader = QUiLoader()
        self.widget = loader.load(ui_file)
        ui_file.close()

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)

        self.buttonBox: QDialogButtonBox = self.widget.buttonBox
        self.configure_buttons()

    def configure_buttons(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setText(self.tr("OK"))
        self.buttonBox.button(QDialogButtonBox.Cancel).setText(self.tr("Cancel"))
        self.toggle_buttons(False, False)

    def toggle_buttons(self, activate_ok: bool, activate_cancel: bool = True):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(activate_ok)
        self.buttonBox.button(QDialogButtonBox.Cancel).setEnabled(activate_cancel)

    def validate(self) -> bool:
        enable = True
        for field in self.validation_fields:
            if isinstance(field, QLineEdit):
                if not field.text():
                    enable = False
                    break
        self.toggle_buttons(enable)
        return enable

    def append_validation_fields(self, *fields):
        for field in fields:
            self.validation_fields.append(field)

    def get_values(self) -> dict:
        """Must be implemented by subclass"""

    def fill_fields(self, item):
        """Must be implemented by subclass"""

    def clear_fields(self):
        """Must be implemented by subclass"""


class EncryptEditorDialog(EditorDialog):

    def __init__(self, parent: QMainWindow):
        super().__init__(parent=parent, ui_file_name="ui/encryptEditor.ui")

        self.key_edit: QLineEdit = self.get_widget(QLineEdit, "keyEdit")
        self.clipboard_button: QToolButton = self.get_widget(QToolButton, "clipboardButton")
        self.generate_button: QPushButton = self.get_widget(QPushButton, "generateButton")
        self.encrypt_button: QPushButton = self.get_widget(QPushButton, "encryptButton")
        self.decrypt_button: QPushButton = self.get_widget(QPushButton, "decryptButton")

        self.configure_widgets()

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)

    def configure_widgets(self):
        super(EncryptEditorDialog, self).configure_widgets()

        app = QApplication.instance()
        copy_icon = QIcon(app.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarNormalButton))
        self.clipboard_button.setIcon(copy_icon)

        self.generate_button.clicked.connect(self.generate_key)
        self.clipboard_button.clicked.connect(self.copy_to_clipboard)
        self.encrypt_button.clicked.connect(self.encrypt_database)
        self.decrypt_button.clicked.connect(self.decrypt_database)
        self.widget.toggle_buttons(True)

    def generate_key(self):
        key = generate_key()
        self.key_edit.setText(key)

    def encrypt_database(self):
        key = properties.encryption_key
        if key is not None:
            self.encrypt(key)
        else:
            key = self.key_edit.text()
            if key is not None:
                self.encrypt(key)

    @staticmethod
    def encrypt(key):
        from logic.database import set_encryption_state
        encrypt_persons(key)
        set_encryption_state(True)

    def decrypt_database(self):
        key = properties.encryption_key
        if key is not None:
            self.decrypt(key)
        else:
            key = self.key_edit.text()
            if key is not None:
                self.decrypt(key)

    @staticmethod
    def decrypt(key):
        decrypt_persons(key)
        set_encryption_state(False)

    def copy_to_clipboard(self):
        app = QApplication.instance()
        value = self.key_edit.text()
        app.clipboard().setText(value)

    def commit(self):
        key = self.key_edit.text()
        properties.encryption_key = key
        self.close()


class OptionsEditorDialog(EditorDialog):

    def __init__(self, parent: QMainWindow):
        super().__init__(parent=parent, ui_file_name="ui/optionsEditor.ui")

        self.locale_box: QComboBox = self.get_widget(QComboBox, "localeBox")
        self.theme_box: QComboBox = self.get_widget(QComboBox, "themeBox")
        self.button_box: QDialogButtonBox = self.get_widget(QDialogButtonBox, "buttonBox")

        self.configure_widgets()

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)

    def configure_widgets(self):
        super(OptionsEditorDialog, self).configure_widgets()

        self.locale_box.addItems(properties.locales)
        self.locale_box.setCurrentIndex(properties.locale_index)

        self.theme_box.addItems(properties.get_themes())
        self.theme_box.setCurrentIndex(properties.theme_index)

        self.widget.toggle_buttons(True)

    def commit(self):
        restart_required: bool = self.update_locale()
        self.update_theme()

        properties.write_config_file()
        if restart_required:
            dialog = ConfirmRestartDialog(self)
            button = dialog.exec_()
            if button == QMessageBox.AcceptRole:
                os.execl(sys.executable, sys.executable, *sys.argv)
        self.close()

    def update_locale(self) -> bool:
        selected_index = self.locale_box.currentIndex()
        restart_required: bool = selected_index != properties.locale_index
        properties.locale_index = selected_index
        return restart_required

    def update_theme(self):
        selected_index = self.theme_box.currentIndex()
        properties.theme_index = selected_index
        if selected_index == 0:
            qdarktheme.setup_theme()
        elif selected_index == 1:
            qdarktheme.setup_theme("light")
        elif selected_index == 2:
            qdarktheme.setup_theme("auto")


class TableDialog(QWidget):

    def __init__(self, has_editor=True, configure_widgets: bool = True):
        super(TableDialog, self).__init__()
        loader = QUiLoader()

        table_file = load_ui_file("ui/tableView.ui")
        self.table_widget = loader.load(table_file)
        table_file.close()
        self.search_line: QLineEdit = self.table_widget.searchLine
        self.proxy_model = QSortFilterProxyModel()

        self.has_editor = has_editor
        if has_editor:
            self.editor: EditorWidget = self.get_editor_widget()
            # set this field in subclass!
            self.add_dialog: EditorDialog

        self.layout = QHBoxLayout(self)

        if has_editor:
            self.layout.addWidget(self.table_widget, stretch=2)
            self.layout.addWidget(self.editor, stretch=1)
        else:
            self.layout.addWidget(self.table_widget)

        if configure_widgets:
            # widgets might be configured in a subclass afterwards
            self.configure_widgets()

    def get_table(self) -> QTableView:
        return self.table_widget.table

    def setup_table(self, model: SearchTableModel, header_range: range):
        tableview: QTableView = self.get_table()

        self.proxy_model.setSourceModel(model)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setFilterKeyColumn(-1)  # Filter all columns

        tableview.setModel(self.proxy_model)
        tableview.setSelectionBehavior(QTableView.SelectRows)
        tableview.setSelectionMode(QAbstractItemView.SingleSelection)
        tableview.selectionModel().selectionChanged.connect(self.reload_editor)

        # ID column is just used for loading the object from the DB tu the editor
        tableview.setColumnHidden(0, True)

        header = tableview.horizontalHeader()
        for i in header_range:
            header.setSectionResizeMode(i, QHeaderView.Stretch)

    def reload_table_contents(self, model: SearchTableModel):
        tableview: QTableView = self.get_table()
        tableview.setModel(model)
        if self.has_editor:
            tableview.selectionModel().selectionChanged.connect(self.reload_editor)

    def reload_editor(self):
        item = self.get_selected_item()
        if item and self.has_editor:
            self.editor.fill_fields(item)
            self.editor.toggle_buttons(True)

    def configure_widgets(self):
        self.table_widget.addButton.clicked.connect(self.add_item)
        self.table_widget.deleteButton.clicked.connect(self.delete_item)
        self.search_line.textChanged.connect(self.proxy_model.setFilterRegularExpression)
        if self.has_editor:
            self.editor.buttonBox.accepted.connect(self.commit_changes)
            self.editor.buttonBox.rejected.connect(self.revert_changes)

    def get_selected_item(self):
        tableview: QTableView = self.get_table()
        selection_model: QItemSelectionModel = tableview.selectionModel()
        indexes: QModelIndex = selection_model.selectedRows()
        model = tableview.model()
        if len(indexes) > 0:
            index = indexes[0]
            return model.data(model.index(index.row(), 0))
        else:
            return None

    def get_editor_widget(self) -> EditorWidget:
        """Must be implemented by subclass"""

    def add_item(self):
        self.add_dialog.clear_fields()
        self.add_dialog.exec_()

    def delete_item(self):
        """Must be implemented by subclass"""

    def commit_changes(self):
        """Must be implemented by subclass"""

    def revert_changes(self):
        """Must be implemented by subclass"""


class CenteredItemDelegate(QItemDelegate):

    def __init__(self):
        super(CenteredItemDelegate, self).__init__()

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: Union[QModelIndex, QPersistentModelIndex]):
        option.displayAlignment = Qt.AlignCenter

        model = index.model()
        data = model.index(index.row(), index.column()).data()
        if data is None or data == "None":
            self.drawDisplay(painter, option, option.rect, "--")
        else:
            super(CenteredItemDelegate, self).paint(painter, option, index)


class DateItemDelegate(CenteredItemDelegate):

    # year - month -day
    def format_ymd(self, index, option, painter):
        model = index.model()
        ymd_date: datetime.date = model.index(index.row(), index.column()).data()
        text: str = ""
        if ymd_date:
            text = ymd_date.strftime("%a, %d %b %Y")
        option.displayAlignment = Qt.AlignCenter
        self.drawDisplay(painter, option, option.rect, text)

    # year - month
    def formal_ym(self, index, option, painter):
        model = index.model()
        ym_date: datetime.date = model.index(index.row(), index.column()).data()
        text: str = ""
        if ym_date:
            text = ym_date.strftime("%b/%Y")
        option.displayAlignment = Qt.AlignCenter
        self.drawDisplay(painter, option, option.rect, text)
