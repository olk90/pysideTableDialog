from sqlalchemy import (Column, Integer, String, Boolean, Date, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
personTableName = "Person"
inventoryTableName = "InventoryItem"
versionInfoTableName = "VersionInfo"
encryptionStateName = "EncryptionState"


class DatabaseExport(object):

    def __init__(self, identifier, persons, items, history):
        self.identifier = identifier
        self.persons = persons
        self.items = items
        self.history = history


class AccessRecord(object):

    def __init__(self, file_path, last_access_time):
        self.file_path = file_path
        self.last_access_time = last_access_time


class Person(Base):
    __tablename__ = personTableName

    id = Column(Integer, primary_key=True)
    firstname = Column(String(100), nullable=False)
    lastname = Column(String(100), nullable=False)
    email = Column(String(100))

    items = relationship(inventoryTableName, back_populates="lender")

    def get_full_name(self):
        return "{} {}".format(self.firstname, self.lastname)

    def lower(self):
        return self.get_full_name().lower()


class InventoryItem(Base):
    __tablename__ = inventoryTableName

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    available = Column(Boolean, nullable=False)
    lending_date = Column(Date)
    info = Column(String(500))
    category = Column(String(100), nullable=False)
    mot_required = Column(Boolean, nullable=False)
    next_mot = Column(Date)

    lender_id = Column(Integer, ForeignKey("Person.id"))
    lender = relationship(personTableName, back_populates="items")


class VersionInfo(Base):
    __tablename__ = versionInfoTableName

    id = Column(Integer, primary_key=True)
    version = Column(Integer, nullable=False, default=0)


class EncryptionState(Base):
    __tablename__ = encryptionStateName

    id = Column(Integer, primary_key=True)
    encryption_state = Column(Boolean, nullable=False)


def create_tables(engine):
    Base.metadata.create_all(engine)
