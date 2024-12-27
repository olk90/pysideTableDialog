from typing import Callable, Union, Any

from sqlalchemy import DDL, text

from logic.database import logger, find_all_of, persist_item, update_version_info, init_database
from logic.model import VersionInfo
from updates.update_functions import dummy_update, insert_encryption_state


class Update:

    def __init__(self, version: int, description: str, action: Union[str, Callable[..., Any]], **kwargs):
        self.version = version
        self.description = description
        self.kwargs = kwargs
        self.action = action
        if isinstance(action, str):
            self.action = create_script(action)

    def execute(self):
        logger.info(f"##### {self} #####")
        if isinstance(self.action, DDL):
            self.db_update()
        elif callable(self.action):
            self.action(**self.kwargs)
        else:
            t = type(self.action)
            msg = f"Action must be either a DDL containing a valid SQL string or a callable function, but was {t}"
            logger.error(msg)
            raise TypeError(msg)

    def db_update(self):
        try:
            engine = init_database()
            with engine.connect() as conn:
                conn.execute(self.action)
                conn.commit()
        except Exception as e:
            logger.error(f"{self} failed: {e}")

    def __str__(self):
        return f"Update({self.version}: {self.description})"


def create_script(update_script: str):
    if any(k in update_script for k in ["CREATE", "ALTER", "DROP"]):
        return DDL(update_script)
    else:
        return text(update_script)


# list that contains all updates
updates = [
    Update(1, "add age column", "ALTER TABLE Person ADD COLUMN age INTEGER DEFAULT 0;"),
    Update(2, "dummy update", dummy_update),
    Update(3, "insert encryption state", insert_encryption_state)
]


def execute_updates():
    version_infos = find_all_of(VersionInfo)
    if len(version_infos) == 0:
        vi = VersionInfo()
        persist_item(vi)
        last_update: Update = max(updates, key=lambda x: x.version)
        current_version = last_update.version
    else:
        vi = version_infos[0]
        current_version = vi.version

    filtered_updates = list(filter(lambda u: u.version > current_version, updates))
    if len(filtered_updates) == 0:
        return

    logger.info("Found {} updates".format(len(filtered_updates)))
    for update in filtered_updates:
        update.execute()

    new_version = max(filtered_updates, key=lambda u: u.version)
    update_version_info(new_version.version)
