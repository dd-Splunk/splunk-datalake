import configparser
import logging
import sys


class Archive:
    def __init__(
        self,
        host=None,
        access_key=None,
        secret_key=None,
        compliancy_bucket=None,
    ):
        self.host = host if host is not None else "localhost:9000"
        self.access_key = access_key if access_key is not None else "admin"
        self.secret_key = secret_key if secret_key is not None else "?"
        self.compliancy_bucket = (
            compliancy_bucket if compliancy_bucket is not None else "compliancy-bucket"
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.host} {self.access_key} \
{self.secret_key} {self.compliancy_bucket}"


class Destination:
    def __init__(
        self,
        host=None,
        token=None,
    ):
        self.host = host if host is not None else "localhost:8088"
        self.token = token if token is not None else "aa-bb"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.host} {self.token}"


config_file = "configs/splunk/app.ini"
parser = configparser.ConfigParser()
try:
    parser.read_file(open(config_file))
except FileNotFoundError:
    logging.error(f"Config file {config_file} not found")
    sys.exit(1)

# Initilize with default values
archive = Archive()
section_name = "minio"
# Try to get config values
try:
    section = parser[section_name]
    archive = Archive(
        section.get("HOST"),
        section.get("ACCESS_KEY"),
        section.get("SECRET_KEY"),
        section.get("COMPLIANCY_BUCKET"),
    )
except KeyError:
    logging.warning(f"Missing section {section_name} in {config_file}")

logging.debug(archive)

# Initialize with default values
destination = Destination()
section_name = "splunk"
# Try to get config values
try:
    section = parser[section_name]
    destination = Destination(
        section.get("HOST"),
        section.get("TOKEN"),
    )
except KeyError:
    logging.warning(f"Missing section {section_name} in {config_file}")


logging.debug(destination)
