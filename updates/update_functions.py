from logic.config import properties
from logic.database import persist_item
from logic.model import EncryptionState


def dummy_update():
    """Example of an update function"""
    s = properties.open_session()
    # Update code to be inserted
    s.commit()


def insert_encryption_state():
    es = EncryptionState(encryption_state=False)
    persist_item(es)
