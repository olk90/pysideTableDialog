from PySide6.QtCore import QAbstractTableModel, QModelIndex
from PySide6.QtGui import Qt

from logic.config import properties
from logic.crypt import decrypt_string
from logic.database import find_all_of
from logic.model import Person
from views.helpers import contains_search_text


class SearchTableModel(QAbstractTableModel):
    def __init__(self, col_count, search: str = "", items=None):
        super(SearchTableModel, self).__init__()
        self.col_count = col_count
        self.search = search.lower()  # Normalize to lowercase for easier matching
        if items is None:
            items = []
        self.all_items = items  # Store full, unfiltered list of items
        self.items = self.filter_items()  # Start with filtered list

    def set_search(self, search: str):
        """Update the search string and reapply filtering."""
        self.search = search.lower()
        self.items = self.filter_items()
        self.layoutChanged.emit()  # Notify the view that the data has changed

    def filter_items(self):
        """Filter items based on the search string. Must be implemented by subclasses."""
        return self.all_items

    def rowCount(self, parent=QModelIndex()):
        return len(self.items)

    def columnCount(self, parent=QModelIndex()):
        return self.col_count

    def data(self, index, role=Qt.DisplayRole):
        """Must be implemented by subclass."""
        pass

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Must be implemented by subclass."""
        pass


class PersonModel(SearchTableModel):
    def __init__(self, search: str = ""):
        items = find_all_of(Person)
        super(PersonModel, self).__init__(4, search, items)

    def filter_items(self):
        """Filter persons based on the search string."""
        if not self.search:
            return self.all_items  # No search; return all items

        key = properties.encryption_key
        # Normalize search value to lowercase for case-insensitive matching
        search_lower = self.search.lower()
        filtered = []
        for person in self.all_items:
            # Decrypt fields when necessary and match them against the search string
            first_name = decrypt_string(key, person.firstname).lower() if key else person.firstname.lower()
            last_name = decrypt_string(key, person.lastname).lower() if key else person.lastname.lower()
            email = decrypt_string(key, person.email).lower() if key and person.email else person.email.lower()

            items = [first_name, last_name, email]
            match = contains_search_text(search_lower, items)

            if match:
                filtered.append(person)

        return filtered

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
