import configparser
import logging
import sys
from pathlib import Path

from .classes import Archive, Destination

CONFIG_FILE = Path("configs", "python", "app.ini")

try:
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
except FileNotFoundError:
    logging.error("Config file %s not found", CONFIG_FILE)
    sys.exit(1)


def get_config_value(section, key, default=None):
    try:
        return config.get(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError):
        logging.debug("Missing %s in section %s of %s", key, section, CONFIG_FILE)
        return default


# Initialize archive with default values
SECTION = "minio"
archive = Archive(
    host=get_config_value(SECTION, "HOST", default="localhost"),
    port=get_config_value(SECTION, "PORT", default=9000),
    access_key=get_config_value(SECTION, "ACCESS_KEY", default="admin"),
    secret_key=get_config_value(SECTION, "SECRET_KEY"),
    compliancy_bucket=get_config_value(
        SECTION, "COMPLIANCY_BUCKET", default="compliancy-bucket"
    ),
    ssl_verify=get_config_value(SECTION, "SSL_VERYFY", default=False),
)

logging.debug(archive)

# Initialize destination with default values
SECTION = "splunk"
destination = Destination(
    host=get_config_value(SECTION, "HOST", default="localhost"),
    port=get_config_value(SECTION, "PORT", default=8088),
    token=get_config_value(SECTION, "TOKEN"),
    proto=get_config_value(SECTION, "PROTO", default="https"),
    ssl_verify=get_config_value(SECTION, "SSL_VERIFY", default=False),
)

logging.debug(destination)
