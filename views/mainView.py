from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget

from logic.table_models import PersonModel
from views.base_classes import OptionsEditorDialog, TableDialog, EncryptEditorDialog
from views.helpers import load_ui_file
from views.person import PersonWidget


class MainWindow(QMainWindow):

    def __init__(self, form):
        super().__init__(parent=form)
        self.adjustSize()

        form.setWindowTitle("pyIM")
        # note that Windows needs an ico file!
        # form.setWindowIcon(QIcon("icon.svg"))

        self.layout = QVBoxLayout(form)

        self.options_dialog = OptionsEditorDialog(self)

        ui_file_name = "ui/main.ui"
        ui_file = load_ui_file(ui_file_name)

        loader = QUiLoader()
        self.widget = loader.load(ui_file, form)
        ui_file.close()

        self.tabview = self.widget.tabview
        self.encrypt_dialog = EncryptEditorDialog(self)

        self.optionsButton = self.widget.optionsButton
        self.encrypt_button = self.widget.encryptButton

        self.configure_buttons()
        self.configure_tabview()

        self.layout.addWidget(self.widget)

        form.resize(1600, 900)

    def configure_tabview(self):
        tabview = self.widget.tabview

        # example:
        person_widget = PersonWidget()
        tabview.addTab(person_widget, self.tr("Persons"))

        self.tabview.currentChanged.connect(self.reload_current_widget)

    def reload_current_widget(self):
        current: QWidget = self.tabview.currentWidget()
        if isinstance(current, TableDialog):
            search = current.search_line.text()
            # example
            if isinstance(current, PersonWidget):
                current.reload_table_contents(PersonModel(search))

    def configure_buttons(self):
        self.widget.loadDbButton.clicked.connect(self.load_access_history)
        self.encrypt_button.clicked.connect(self.open_encrypt)
        self.optionsButton.clicked.connect(self.open_options)

    def load_access_history(self):
        pass

    def open_options(self):
        self.options_dialog.exec_()

    def open_encrypt(self):
        self.encrypt_dialog.exec_()
        self.reload_current_widget()
