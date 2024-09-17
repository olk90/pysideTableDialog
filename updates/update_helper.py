from typing import Callable, Union, Any

from sqlalchemy import DDL

from logic.database import db, logger, find_all_of, persist_item, update_version_info
from logic.model import VersionInfo
from updates.update_functions import dummy_update, insert_encryption_state


class Update:

    def __init__(self, version: int, action: Union[str, Callable[..., Any]], **kwargs):
        self.version = version
        self.kwargs = kwargs
        self.action = action
        if isinstance(action, str):
            self.action = DDL(action)

    def execute(self):
        logger.info(f"Update {self.version}: {self.action}")
        if isinstance(self.action, str):
            self.db_update()
        elif callable(self.action):
            self.action(**self.kwargs)
        else:
            raise TypeError("Action must be either an SQL string or a callable function")

    def db_update(self):
        try:
            engine = db.engine
            with engine.connect() as conn:
                conn.execute(self.action)
        except Exception as e:
            logger.error(f"Update {self.version} failed: {e}")


# list that contains all updates
updates = [
    Update(1, "ALTER TABLE Person ADD COLUMN age INTEGER DEFAULT 0;"),
    Update(2, dummy_update),
    Update(3, insert_encryption_state)
]


def execute_updates():
    version_infos = find_all_of(VersionInfo)
    if len(version_infos) == 0:
        vi = VersionInfo()
        persist_item(vi)
        current_version = max(updates, key=lambda x: x.version)
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
