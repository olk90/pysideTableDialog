from PySide6.QtGui import Qt
from PySide6.QtSql import QSqlQueryModel

from logic.queries import person_query, inventory_query, lending_history_query


class SearchTableModel(QSqlQueryModel):
    def __init__(self, search: str = ""):
        super(SearchTableModel, self).__init__()
        self.search = search


class PersonModel(SearchTableModel):
    def __init__(self, search: str = ""):
        super(PersonModel, self).__init__(search)
        query = person_query(self.search)
        self.setQuery(query)
        self.setHeaderData(0, Qt.Horizontal, "ID")
        self.setHeaderData(1, Qt.Horizontal, self.tr("First Name"))
        self.setHeaderData(2, Qt.Horizontal, self.tr("Last Name"))
        self.setHeaderData(3, Qt.Horizontal, self.tr("E-Mail"))


class InventoryModel(SearchTableModel):
    def __init__(self, search: str = ""):
        super(InventoryModel, self).__init__(search)
        query = inventory_query(self.search)
        self.setQuery(query)
        self.setHeaderData(0, Qt.Horizontal, "ID")
        self.setHeaderData(1, Qt.Horizontal, self.tr("Category"))
        self.setHeaderData(2, Qt.Horizontal, self.tr("Device"))
        self.setHeaderData(3, Qt.Horizontal, self.tr("Available"))
        self.setHeaderData(4, Qt.Horizontal, self.tr("Lending Date"))
        self.setHeaderData(5, Qt.Horizontal, self.tr("Lend to"))
        self.setHeaderData(6, Qt.Horizontal, self.tr("Next MOT"))


class LendingHistoryModel(SearchTableModel):
    def __init__(self, search: str =""):
        super(LendingHistoryModel, self).__init__(search)
        query = lending_history_query(search)
        self.setQuery(query)
        self.setHeaderData(0, Qt.Horizontal, "ID")
        self.setHeaderData(1, Qt.Horizontal, self.tr("Device"))
        self.setHeaderData(2, Qt.Horizontal, self.tr("Lent to"))
        self.setHeaderData(3, Qt.Horizontal, self.tr("Lending Date"))
        self.setHeaderData(4, Qt.Horizontal, self.tr("Return Date"))
