import json
import locale
import sys
from pathlib import Path

import qdarktheme
from PySide6 import QtCore
from PySide6.QtCore import QTranslator, QLocale
from PySide6.QtWidgets import QApplication, QWidget

from logic.config import properties
from logic.database import init_database
from views.mainView import MainWindow

userHome = Path.home()
configDirectory = Path.joinpath(userHome, ".pyIM")
configFile = Path.joinpath(configDirectory, "config.json")


def load_translations():
    translator = QTranslator(app)
    path = './translations'
    if properties.locale_index == 1:
        translator.load(QLocale(QLocale.German, QLocale.Germany), 'base', '_', path)
        locale.setlocale(locale.LC_TIME, "de_DE.utf8")
        app.installTranslator(translator)


def load_theme():
    if properties.theme_index == 0:
        app.setStyleSheet(qdarktheme.load_stylesheet())
    elif properties.theme_index == 1:
        app.setStyleSheet(qdarktheme.load_stylesheet("light"))


def write_config_file():
    config_dict = {
        "history": []
    }
    config = json.dumps(config_dict, indent=4)
    with open(configFile, "w") as f:
        f.write(config)
        f.close()


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)

    properties.load_config_file()

    init_database()

    app = QApplication()

    load_translations()
    load_theme()

    form = QWidget(None)
    MainWindow(form)
    form.show()
    sys.exit(app.exec())
