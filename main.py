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
from updates.update_helper import execute_updates
from views.base_functions import login_prompt
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
        qdarktheme.setup_theme()
    elif properties.theme_index == 1:
        qdarktheme.setup_theme("light")
    elif  properties.theme_index == 2:
        qdarktheme.setup_theme("auto")


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

    app = QApplication()

    properties.load_config_file()

    init_database()

    load_translations()
    load_theme()

    execute_updates()

    login_prompt()

    form = QWidget(None)
    MainWindow(form)
    form.show()
    sys.exit(app.exec())
