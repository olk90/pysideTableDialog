import sys
from datetime import date, datetime

from PySide6 import QtCore
from PySide6.QtCore import QFile, QCoreApplication
from PySide6.QtGui import QColor, QBrush, QPen, Qt
from PySide6.QtWidgets import QComboBox, QSpinBox
from dateutil import relativedelta as rd

from logic.config import properties


def load_ui_file(filename):
    ui_file = QFile(filename)
    if not ui_file.open(QFile.ReadOnly):
        print("Cannot open {}: {}".format(filename, ui_file.errorString()))
        sys.exit(-1)
    return ui_file


def translate(context, text):
    return QCoreApplication.translate(context, text, None)


def get_min_date():
    today = date.today()
    month_abbr = today.strftime("%b")
    min_year = today.year
    return month_abbr, min_year


def configure_next_mot(month_cb: QComboBox, year_sp: QSpinBox):
    min_date = get_min_date()
    index = month_cb.findText(min_date[0], QtCore.Qt.MatchFixedString)
    if index >= 0:
        month_cb.setCurrentIndex(index)
    year_sp.setMinimum(min_date[1])


def calculate_background(mot_date, option, painter):
    dark_theme: bool = properties.theme_index == 0
    today = datetime.today()
    r = rd.relativedelta(mot_date, today)
    num_months = r.months + (12 * r.years)
    color: QColor = painter.brush().color()
    update_background: bool = False
    if 6 <= num_months < 12:
        color = QColor("#006600") if dark_theme else QColor("#00ff00")
        update_background = True
    elif 4 <= num_months < 6:
        color = QColor("#b3b300") if dark_theme else QColor("#ffff00")
        update_background = True
    elif 1 <= num_months < 4:
        color = QColor("#e68a00") if dark_theme else QColor("#ff9900")
        update_background = True
    elif num_months <= 0:
        color = QColor("#cc0000") if dark_theme else QColor("#ff0000")
        update_background = True

    if update_background:
        brush: QBrush = QBrush(color)
        painter.setBrush(brush)
        pen = QPen()
        pen.setStyle(Qt.NoPen)
        painter.setPen(pen)
        painter.drawRect(option.rect)


def contains_search_text(search_text: str, items: list) -> bool:
    for string in items:
        if search_text.lower() in string.lower():
            return True
    return False
