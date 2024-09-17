from PySide6.QtWidgets import QHBoxLayout, QWidget, QMessageBox, QDialogButtonBox, QLabel, QLineEdit, QTableView

from logic.config import properties
from logic.crypt import decrypt_string
from logic.database import persist_item, delete_item, find_by_id, update_person
from logic.model import Person
from logic.table_models import PersonModel
from views.base_classes import TableDialog, EditorDialog, EditorWidget, CenteredItemDelegate
from views.confirmationDialogs import ConfirmDeletionDialog


class AddPersonDialog(EditorDialog):

    def __init__(self, parent: QWidget):
        super(AddPersonDialog, self).__init__(parent=parent, ui_file_name="ui/personEditor.ui")

        self.get_widget(QLabel, "editorTitle").setText(self.tr("Add Person"))

        self.firstname_edit: QLineEdit = self.get_widget(QLineEdit, "firstNameEdit")
        self.lastname_edit: QLineEdit = self.get_widget(QLineEdit, "lastNameEdit")

        self.firstname_edit.textChanged.connect(self.widget.validate)
        self.lastname_edit.textChanged.connect(self.widget.validate)

        self.widget.append_validation_fields(self.firstname_edit, self.lastname_edit)

        self.email_edit: QLineEdit = self.get_widget(QLineEdit, "emailEdit")

        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.widget)
        self.button_box: QDialogButtonBox = self.widget.buttonBox

        self.configure_widgets()

    def commit(self):
        first_name: str = self.firstname_edit.text()
        last_name: str = self.lastname_edit.text()
        email: str = self.email_edit.text()

        person = Person(firstname=first_name, lastname=last_name, email=email)
        persist_item(person)
        self.parent.reload_table_contents(model=PersonModel())
        self.close()


class PersonEditorWidget(EditorWidget):

    def __init__(self, item_id=None):
        super(PersonEditorWidget, self).__init__(ui_file_name="ui/personEditor.ui", item_id=item_id)

        self.firstname_edit = self.widget.firstNameEdit
        self.lastname_edit = self.widget.lastNameEdit
        self.email_edit = self.widget.emailEdit

        self.firstname_edit.textChanged.connect(self.validate)
        self.lastname_edit.textChanged.connect(self.validate)

        self.append_validation_fields(self.firstname_edit, self.lastname_edit)

    def fill_fields(self, person: Person):
        self.item_id = person.id
        firstname = person.firstname
        lastname = person.lastname
        email = person.email

        key = properties.encryption_key
        if key is not None:
            firstname = decrypt_string(key, firstname)
            lastname = decrypt_string(key, lastname)
            email = decrypt_string(key, email)

        self.firstname_edit.setText(firstname)
        self.lastname_edit.setText(lastname)
        self.email_edit.setText(email)

    def get_values(self) -> dict:
        return {
            "item_id": self.item_id,
            "firstname": self.firstname_edit.text(),
            "lastname": self.lastname_edit.text(),
            "email": self.email_edit.text(),
        }

    def clear_fields(self):
        self.firstname_edit.setText("")
        self.lastname_edit.setText("")
        self.email_edit.setText("")
        self.toggle_buttons(False)


class PersonWidget(TableDialog):

    def __init__(self):
        super(PersonWidget, self).__init__()
        self.add_dialog = AddPersonDialog(self)
        self.setup_table(PersonModel(), range(1, 4))

        tableview: QTableView = self.get_table()
        delegate = CenteredItemDelegate()
        tableview.setItemDelegate(delegate)

    def get_editor_widget(self) -> EditorWidget:
        return PersonEditorWidget()

    def delete_item(self):
        dialog = ConfirmDeletionDialog(self)
        button = dialog.exec_()
        if button == QMessageBox.AcceptRole:
            person: Person = self.get_selected_item()
            delete_item(person)
            search = self.search_line.text()
            self.reload_table_contents(model=PersonModel(search))
            self.editor.clear_fields()

    def get_selected_item(self):
        item_id = super().get_selected_item()
        person = find_by_id(item_id, Person)
        return person

    def commit_changes(self):
        value_dict: dict = self.editor.get_values()
        update_person(value_dict)
        search = self.search_line.text()
        self.reload_table_contents(model=PersonModel(search))
        self.editor.clear_fields()

    def revert_changes(self):
        person: Person = find_by_id(self.editor.item_id, Person)
        self.editor.fill_fields(person)
