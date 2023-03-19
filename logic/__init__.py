import logging
import os.path

from logging.handlers import RotatingFileHandler


def configure_file_handler(name: str) -> RotatingFileHandler:
    if not os.path.exists("logs"):
        os.makedirs("logs")
    rfh = RotatingFileHandler("logs/{}.log".format(name), maxBytes=1024 * 1024, backupCount=5, encoding="utf-8")
    rfh.setLevel(logging.INFO)
    formatter = logging.Formatter(
        fmt="%(asctime)s,%(msecs)03d - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    rfh.setFormatter(formatter)
    return rfh
