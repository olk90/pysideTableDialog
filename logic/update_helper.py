from sqlalchemy import DDL

from logic.database import db, logger, find_all_of, persist_item, update_version_info
from logic.model import VersionInfo


class Update:

    def __init__(self, version: int, update_script: str):
        self.version = version
        self.update_script = DDL(update_script)

    def execute(self):
        logger.info(f"Update {self.version}: {self.update_script}")
        try:
            engine = db.engine
            with engine.connect() as conn:
                conn.execute(self.update_script)
        except Exception as e:
            logger.error(f"Update {self.version} failed: {e}")


# list that contains all updates
updates = [
    Update(1, "ALTER TABLE Person ADD COLUMN age INTEGER DEFAULT 0;")
]


def execute_updates():
    version_infos = find_all_of(VersionInfo)
    if len(version_infos) == 0:
        vi = VersionInfo()
        persist_item(vi)
        current_version = 0
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
