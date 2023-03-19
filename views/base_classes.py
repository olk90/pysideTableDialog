import os
import sys
from datetime import datetime
from typing import Union

import qdarktheme
from PySide6.QtCore import QItemSelectionModel, QModelIndex, \
    QPersistentModelIndex, Qt
from PySide6.QtGui import QPainter
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QDialog, QWidget, QDialogButtonBox, QHBoxLayout, QMainWindow, QComboBox, QApplication, \
    QLineEdit, QTableView, QAbstractItemView, QHeaderView, QItemDelegate, QStyleOptionViewItem, QMessageBox, QSpinBox

from logic.config import properties
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
        self.button_box.button(QDialogButtonBox.Cancel).setText(self.tr("Cancel"))

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
        app = QApplication.instance()
        if selected_index == 0:
            app.setStyleSheet(qdarktheme.load_stylesheet())
        elif selected_index == 1:
            app.setStyleSheet(qdarktheme.load_stylesheet("light"))
        else:
            app.setStyleSheet(None)


class TableDialog(QWidget):

    def __init__(self, has_editor=True, configure_widgets: bool = True):
        super(TableDialog, self).__init__()
        loader = QUiLoader()

        table_file = load_ui_file("ui/tableView.ui")
        self.table_widget = loader.load(table_file)
        table_file.close()
        self.searchLine: QLineEdit = self.table_widget.searchLine

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
            self.configure_search()

    def get_table(self) -> QTableView:
        return self.table_widget.table

    def setup_table(self, model: SearchTableModel, header_range: range):
        tableview: QTableView = self.get_table()
        tableview.setModel(model)
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

    def configure_search(self):
        """Must be implemented by subclass"""

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
        super(CenteredItemDelegate, self).paint(painter, option, index)


class DateItemDelegate(CenteredItemDelegate):

    # year - month -day
    def format_ymd(self, index, option, painter):
        model = index.model()
        date_str: str = model.index(index.row(), index.column()).data()
        text: str = ""
        if date_str:
            ymd_date = datetime.strptime(date_str, '%Y-%m-%d')
            text = ymd_date.strftime("%a, %d %b %Y")
        option.displayAlignment = Qt.AlignCenter
        self.drawDisplay(painter, option, option.rect, text)

    # year - month
    def formal_ym(self, index, option, painter):
        model = index.model()
        date_str: str = model.index(index.row(), index.column()).data()
        text: str = ""
        if date_str:
            ym_date = datetime.strptime(date_str, '%Y-%m-%d')
            text = ym_date.strftime("%b/%Y")
        option.displayAlignment = Qt.AlignCenter
        self.drawDisplay(painter, option, option.rect, text)
