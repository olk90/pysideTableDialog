import calendar
import datetime as dt
import sys

from PySide6.QtCore import QFile
from PySide6.QtWidgets import QComboBox, QSpinBox

from logic.config import properties
from logic.model import EncryptionState
from views.lists import MonthList


def load_ui_file(filename):
    ui_file = QFile(filename)
    if not ui_file.open(QFile.ReadOnly):
        print("Cannot open {}: {}".format(filename, ui_file.errorString()))
        sys.exit(-1)
    return ui_file


def configure_month_box(month_box: QComboBox, date=dt.date.today()):
    items = MonthList().months
    month_box.addItems(items)
    month: int = date.month - 1  # indices start at 0!
    month_box.setCurrentIndex(month)


def configure_year_box(year_box: QSpinBox, date=dt.date.today()):
    year: int = date.year
    year_box.setMinimum(year)
    year_box.setValue(year)
    year_box.setMaximum(9999)


def get_day_range(month: int, year: int) -> range:
    end_day = calendar.monthrange(year, month)[1]
    day_range = range(1, end_day + 1)
    return day_range


def get_date(mot_required: bool, month: int, year: int) -> dt.date | None:
    if not mot_required:
        return None
    day_range = get_day_range(month, year)
    day = day_range[-1]
    return dt.date(year, month, day)


def login_prompt():
    with properties.open_session() as s:
        es: EncryptionState = s.query(EncryptionState).first()
        if es and es.encryption_state:
            from login import spawn_login_prompt
            spawn_login_prompt()
