import configparser
import logging
import sys
from pathlib import Path

from .classes import Archive, Destination

CONFIG_FILE = Path("configs", "python", "app.ini")
MANDATORY_SECTIONS = ["minio", "splunk"]

try:
    config = configparser.ConfigParser()
    config.read_file(open(CONFIG_FILE))
except FileNotFoundError:
    logging.error("Config file %s not found", CONFIG_FILE)
    sys.exit(1)

for section in MANDATORY_SECTIONS:
    if not config.has_section(section):
        logging.error("Missing section %s in file %s", section, CONFIG_FILE)
        sys.exit(1)


archive = Archive(config)
logging.debug(archive)

destination = Destination(config)
logging.debug(destination)
