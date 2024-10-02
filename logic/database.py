import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler

from PySide6.QtGui import Qt
from PySide6.QtSql import QSqlDatabase, QSqlQueryModel
from PySide6.QtWidgets import QComboBox
from sqlalchemy import create_engine as ce
from sqlalchemy.orm import Session

from logic import configure_file_handler
from logic.config import properties
from logic.model import create_tables, Person, InventoryItem, Base, VersionInfo, EncryptionState

rfh: RotatingFileHandler = configure_file_handler("database")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(rfh)

logger.info("Logger initialised")

db = ce("sqlite:///pyIM.db")


def init_database(app_launch: bool = True):
    if app_launch:
        logger.info("Connecting to database {}".format(db))

    db.connect()

    if app_launch:
        logger.info("Initializing database")
        create_tables(db)

        logger.info("Connect database to PySide")
    database = QSqlDatabase.addDatabase("QSQLITE")
    database.setDatabaseName("pyIM.db")

    if not database.open():
        logger.info("Unable to open database")
        sys.exit(1)


def find_by_id(identifier: int, entities):
    s = properties.open_session()
    result = s.query(entities).filter_by(id=identifier).first()
    s.close()
    return result


def find_all_of(entities) -> list:
    s = properties.open_session()
    result: list = s.query(entities).all()
    s.close()
    return result


def load_persons(persons):
    with Session(db) as session:
        for p in persons:
            person = Person(
                id=p["id"] + 1,
                firstname=p["firstName"],
                lastname=p["lastName"],
                email=p["email"]
            )
            session.add(person)
        session.commit()


def load_inventory(inventory):
    with Session(db) as session:
        for i in inventory:
            inventory_item = InventoryItem(
                id=i["id"] + 1,
                name=i["name"],
                available=i["available"],
                lending_date=convert_date(i["lendingDate"]),
                lender_id=i["lender"],
                info=i["info"],
                category=i["category"],
                mot_required=i["motRequired"],
                next_mot=convert_date(i["nextMot"])
            )
            session.add(inventory_item)
        session.commit()


def convert_date(date_str: str):
    date_pattern = "%Y-%m-%d"
    if len(date_str) > 0:
        return datetime.strptime(date_str, date_pattern)
    else:
        return None


def configure_query_model(box: QComboBox, query: str):
    model = QSqlQueryModel(box)
    model.setQuery(query)
    model.setHeaderData(0, Qt.Horizontal, "Name")
    box.setModel(model)
    box.setEditable(True)


def persist_item(item: Base):
    s = properties.open_session()
    s.add(item)
    s.commit()
    logger.info("Added new item to database: %s", item)


def delete_item(item: Base):
    s = properties.open_session()
    s.delete(item)
    s.commit()
    logger.info("Removed entry from database: %s", item)


def update_inventory(value_dict: dict):
    s = properties.open_session()
    item_id = value_dict["item_id"]
    item: InventoryItem = s.query(InventoryItem).filter_by(id=item_id).first()
    item.name = value_dict["name"]
    item.category = value_dict["category"]
    item.info = value_dict["info"]
    item.mot_required = value_dict["mot_required"]
    item.next_mot = value_dict["next_mot"]
    item.available = value_dict["available"]

    lender_id = value_dict["lender"]
    item.lender_id = lender_id
    s.commit()


def update_person(value_dict: dict):
    s = properties.open_session()
    person: Person = s.query(Person).filter_by(id=value_dict["item_id"]).first()
    person.firstname = value_dict["firstname"]
    person.lastname = value_dict["lastname"]
    person.email = value_dict["email"]
    s.commit()


def update_version_info(version: int):
    s = properties.open_session()
    vi = s.query(VersionInfo).first()
    vi.version = version
    s.commit()


def set_encryption_state(state: bool):
    s = properties.open_session()
    es = s.query(EncryptionState).first()
    es.encryption_state = state
    s.commit()
