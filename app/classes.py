import configparser
import logging
import zlib
from dataclasses import dataclass, field
from datetime import datetime
from functools import cached_property
from http import HTTPStatus
from pathlib import Path
from typing import Generator, Literal, Optional

import requests
from minio import Minio

# Type aliases for better readability
Proto = Literal["http", "https"]
Url = str

logging.basicConfig(level=logging.INFO)


@dataclass
class Archive:
    """Client for interacting with MinIO archive storage."""

    config: configparser.ConfigParser
    host: str = field(default="localhost")
    port: int = field(default=9000)
    access_key: str = field(default="admin")
    secret_key: str = field(default="", repr=False)  # Excluded from repr
    compliancy_bucket: str = field(default="compliancy-bucket")
    ssl_verify: bool = field(default=False)

    # Initialize logger using class attribute
    logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger("Minio"), init=False
    )

    def __post_init__(self) -> None:
        """Initialize MinIO client after dataclass initialization."""
        self.logger.setLevel(logging.DEBUG)
        SECTION = "minio"
        self.host = self.config.get(SECTION, "HOST", fallback=self.host)
        self.port = self.config.getint(SECTION, "PORT", fallback=self.port)
        if self.port < 1 or self.port > 65535:
            raise ValueError("Invalid port value")
        self.access_key = self.config.get(
            SECTION, "ACCESS_KEY", fallback=self.access_key
        )
        self.secret_key = self.config.get(
            SECTION, "SECRET_KEY", fallback=self.secret_key
        )
        if not self.secret_key:
            raise ValueError("Missing SECRET KEY")
        self.compliancy_bucket = self.config.get(
            SECTION, "COMPLIANCY_BUCKET", fallback=self.compliancy_bucket
        )
        self.ssl_verify = self.config.getboolean(
            SECTION, "SSL_VERIFY", fallback=self.ssl_verify
        )

        self.client = Minio(
            endpoint=f"{self.host}:{self.port}",
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=True,
            cert_check=self.ssl_verify,
        )

    def bucket_prefix(self, date: datetime, sourcetype: Optional[str] = None) -> str:
        """Generate bucket prefix based on date and optional sourcetype."""
        prefix = Path(
            f"year={date.year:04d}", f"month={date.month:02d}", f"day={date.day:02d}"
        )

        if sourcetype:
            prefix = prefix / f"sourcetype={sourcetype}"

        prefix_str = f"{prefix}/"
        self.logger.debug("Bucket prefix: %s", prefix_str)
        return prefix_str

    def list_objects(
        self, date: datetime, sourcetype: Optional[str] = None, recurse: bool = True
    ) -> Generator:
        """List objects in the bucket matching the given criteria."""
        return self.client.list_objects(
            bucket_name=self.compliancy_bucket,
            prefix=self.bucket_prefix(date, sourcetype),
            recursive=recurse,
        )

    def get_lines(self, object_name: str) -> bytes:
        """Retrieve and decompress object content."""
        with self.client.get_object(self.compliancy_bucket, object_name) as obj:
            gzip_content = obj.read()
            # Add 32 to window size for automatic header detection
            return zlib.decompress(gzip_content, wbits=15 + 32)

    @cached_property
    def url(self) -> Url:
        """Get the server URL."""
        return f"https://{self.host}:{self.port}"

    @property
    def check_connectivity(self) -> bool:
        """Check if the archive server is reachable."""
        requests.packages.urllib3.disable_warnings()
        self.logger.info("Checking Archive Server %s reachability", self.url)

        try:
            response = requests.post(
                url=self.url,
                headers={},
                data={},
                verify=False,
            )
            self.logger.debug("Status: %s", response.status_code)
            return True
        except requests.RequestException:
            self.logger.warning("Archive host %s not reachable!", self.url)
            return False

    @property
    def check_compliancy_bucket(self) -> bool:
        """Check if the compliancy bucket exists."""
        self.logger.info(
            "Checking availability of %s in archive", self.compliancy_bucket
        )
        return self.compliancy_bucket in self.client.list_buckets()


@dataclass
class Destination:
    """Client for sending data to HTTP Event Collector."""

    config: configparser.ConfigParser
    host: str = field(default="localhost")
    port: int = field(default=8088)
    token: str = field(default="", repr=False)
    proto: Proto = field(default="https")
    ssl_verify: bool = field(default=False)

    logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger("HEC"), init=False
    )

    def __post_init__(self) -> None:
        """Set up logging after dataclass initialization."""
        self.logger.setLevel(logging.INFO)

        SECTION = "splunk"
        self.host = self.config.get(SECTION, "HOST", fallback=self.host)
        self.port = self.config.getint(SECTION, "PORT", fallback=self.port)
        if self.port < 1 or self.port > 65535:
            raise ValueError("Invalid port value")
        self.token = self.config.get(SECTION, "TOKEN", fallback=self.token)
        if not self.token:
            raise ValueError("Missing TOKEN")
        self.proto = self.config.get(SECTION, "PROTO", fallback=self.proto)
        self.ssl_verify = self.config.getboolean(
            SECTION, "SSL_VERIFY", fallback=self.ssl_verify
        )

    @cached_property
    def url(self) -> Url:
        """Get the HEC endpoint URL."""
        return f"{self.proto}://{self.host}:{self.port}/services/collector/event"

    @property
    def headers(self) -> dict:
        """Get the required headers for HEC requests."""
        return {
            "Authorization": f"Splunk {self.token}",
            "Content-Type": "application/json",
        }

    @property
    def check_connectivity(self) -> bool:
        """Check if the HEC server is reachable."""
        requests.packages.urllib3.disable_warnings()
        self.logger.info("Checking HEC Server URI reachability")

        try:
            response = requests.post(
                url=self.url,
                headers=self.headers,
                data={},
                verify=False,
            )
            self.logger.debug("Status: %s", response.status_code)
            return True
        except requests.RequestException:
            self.logger.error("Splunk Server %s is unreachable", self.host)
            return False

    def send_multilines(self, payload: str) -> HTTPStatus:
        """Send multiple lines of data to HEC."""
        requests.packages.urllib3.disable_warnings()

        try:
            response = requests.post(
                url=self.url,
                headers=self.headers,
                data=payload,
                verify=self.ssl_verify,
            )
            self.logger.debug("Status: %s", response.status_code)
            return response.status_code
        except requests.RequestException:
            self.logger.error("Connection to %s refused!", self.host)
            return HTTPStatus.SERVICE_UNAVAILABLE


if __name__ == "__main__":
    from .config import destination

    test_payload = """
    {"time":1701388800,"event":"Current Time = 01:00:00\\n",
    "host":"uf1","source":"/opt/splunkforwarder/etc/apps/normal/bin/heure.py",
    "sourcetype":"heure","index":"cust1","fields":{"cust":"customer-normal"}}

    {"time":1701388800,"event":"Current Time = 01:00:00\\n","host":"uf0",
    "source":"/opt/splunkforwarder/etc/apps/unlimited-speed/bin/heure.py",
    "sourcetype":"heure","index":"cust0","fields":{"cust":"customer-unlimited"}}
    """.strip()

    status = destination.send_multilines(test_payload)
    logging.info("Archive sent status: %s", status)
