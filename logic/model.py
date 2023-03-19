from sqlalchemy import (Column, Integer, String, Boolean, Date, ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()
personTableName = "Person"
inventoryTableName = "InventoryItem"
lendingHistoryTableName = "LendingHistory"


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
    history = relationship(lendingHistoryTableName, back_populates="lender")

    def get_full_name(self):
        return "{} {}".format(self.firstname, self.lastname)


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

    lendings = relationship(lendingHistoryTableName, back_populates="item")

    lender_id = Column(Integer, ForeignKey("Person.id"))
    lender = relationship(personTableName, back_populates="items")


class LendingHistory(Base):
    __tablename__ = lendingHistoryTableName

    id = Column(Integer, primary_key=True)
    lending_date = Column(Date)
    return_date = Column(Date)

    lender_id = Column(Integer, ForeignKey("Person.id"), nullable=False)
    lender = relationship("Person", back_populates="history")

    item_id = Column(Integer, ForeignKey("InventoryItem.id"), nullable=False)
    item = relationship("InventoryItem", back_populates="lendings")


def create_tables(engine):
    Base.metadata.create_all(engine)
