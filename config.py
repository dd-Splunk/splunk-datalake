import configparser
import logging
import sys

from classes import Archive, Destination

config_file = "configs/splunk/app.ini"
parser = configparser.ConfigParser()
try:
    parser.read_file(open(config_file))
except FileNotFoundError:
    logging.error(f"Config file {config_file} not found")
    sys.exit(1)

# Initilize archive with default values
archive = Archive()
section_name = "minio"
# Try to get config values
try:
    section = parser[section_name]
    archive = Archive(
        host=section.get("HOST"),
        port=section.get("PORT"),
        access_key=section.get("ACCESS_KEY"),
        secret_key=section.get("SECRET_KEY"),
        compliancy_bucket=section.get("COMPLIANCY_BUCKET"),
    )
except KeyError:
    logging.warning(f"Missing section {section_name} in {config_file}")

logging.debug(archive)

# Initialize destination with default values
destination = Destination()
section_name = "splunk"
# Try to get config values
try:
    section = parser[section_name]
    destination = Destination(
        section.get("HOST"),
        section.get("PORT"),
        section.get("TOKEN"),
    )
except KeyError:
    logging.warning(f"Missing section {section_name} in {config_file}")


logging.debug(destination)
