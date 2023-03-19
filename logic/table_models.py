from PySide6.QtGui import Qt
from PySide6.QtSql import QSqlQueryModel

from logic.queries import person_query


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
