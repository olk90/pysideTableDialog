from PySide6.QtWidgets import QMainWindow, QLineEdit, QHBoxLayout, QApplication

from logic.config import properties
from views.base_classes import EditorDialog


class LoginPrompt(EditorDialog):

    def __init__(self, parent: QMainWindow):
        super().__init__(parent=parent, ui_file_name="ui/loginPrompt.ui")

        self.key_edit: QLineEdit = self.get_widget(QLineEdit, "keyEdit")

        self.configure_widgets()

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)

    def configure_widgets(self):
        super(LoginPrompt, self).configure_widgets()
        self.widget.toggle_buttons(True)

    def commit(self):
        key = self.key_edit.text()
        properties.encryption_key = key
        # add all other decrypt methods
        self.close()


def spawn_login_prompt():
    app = QApplication.instance()
    main_window = app.activeWindow()
    login = LoginPrompt(main_window)
    login.exec_()
