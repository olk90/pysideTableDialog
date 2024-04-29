from PySide6.QtCore import QAbstractTableModel, QModelIndex
from PySide6.QtGui import Qt

from logic.config import properties
from logic.crypt import decrypt_string
from logic.database import find_all_of
from logic.model import Person


class SearchTableModel(QAbstractTableModel):
    def __init__(self, col_count, search: str = "", items=None):
        super(SearchTableModel, self).__init__()
        self.col_count = col_count
        self.search = search
        if items is None:
            items = []
        self.items = items

    def rowCount(self, parent=QModelIndex()):
        return len(self.items)

    def columnCount(self, parent=QModelIndex()):
        return self.col_count

    def data(self, index, role=Qt.DisplayRole):
        """Must be implemented by subclass"""
        pass

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Must be implemented by subclass"""
        pass


class PersonModel(SearchTableModel):
    def __init__(self, search: str = ""):
        items = find_all_of(Person)
        super(PersonModel, self).__init__(4, search, items)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            person: Person = self.items[index.row()]
            column = index.column()
            key = properties.encryption_key
            if column == 0:
                return person.id
            elif column == 1:
                if key is not None:
                    return decrypt_string(key, person.firstname)
                else:
                    return person.firstname
            elif column == 2:
                if key is not None:
                    return decrypt_string(key, person.lastname)
                else:
                    return person.lastname
            elif column == 3:
                email = person.email
                if key is not None and email is not None:
                    return decrypt_string(key, email)
                else:
                    return email
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section == 0:
                return "ID"
            elif section == 1:
                return self.tr("First Name")
            elif section == 2:
                return self.tr("Last Name")
            elif section == 3:
                return self.tr("E-Mail")
        return None
