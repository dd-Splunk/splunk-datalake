import datetime
import logging
import zlib
from http import HTTPStatus
from typing import Literal

import requests
from minio import Minio

Proto = Literal["http", "https"]
Url = str


class Archive:
    def __init__(
        self,
        host: str = None,
        port: int = None,
        access_key: str = None,
        secret_key: str = None,
        compliancy_bucket: str = None,
        ssl_verify: bool = None,
    ):
        self.log = logging.getLogger("Minio")
        self.log.setLevel(logging.INFO)

        self.host = host if host is not None else "localhost"
        self.port = port if port is not None else "9000"
        self.access_key = access_key if access_key is not None else "admin"
        self.secret_key = secret_key if secret_key is not None else "?"
        self.compliancy_bucket = (
            compliancy_bucket if compliancy_bucket is not None else "compliancy-bucket"
        )
        self.ssl_verify = ssl_verify if ssl_verify is not None else False

        self.client = Minio(
            endpoint=f"{self.host}:{self.port}",
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=True,
            cert_check=self.ssl_verify,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.host} {self.access_key} \
{self.secret_key} {self.compliancy_bucket}"

    def bucket_prefix(self, thisday: datetime, sourcetype: str = None) -> str:
        prefix = f"year={thisday.year:0{4}}"
        prefix += f"/month={thisday.month:0{2}}"
        prefix += f"/day={thisday.day:0{2}}/"

        if sourcetype is not None:
            prefix += f"sourcetype={sourcetype}/"

        self.log.debug(f"Bucket prefix {prefix}")

        return prefix

    def list_objects(self, thisday: datetime, sourcetype: str = None):
        objects = self.client.list_objects(
            bucket_name=self.compliancy_bucket,
            prefix=self.bucket_prefix(thisday, sourcetype),
            # Recurse in case sourcetype is ommitted but present in archived object
            recursive=True,
        )
        return objects

    def get_lines(self, object_name: str) -> bytes:
        response = self.client.get_object(
            bucket_name=self.compliancy_bucket, object_name=object_name
        )
        # Read data from response.
        items = response.read(decode_content=True)
        # Decode .gz
        # https://stackoverflow.com/questions/1838699/how-can-i-decompress-a-gzip-stream-with-zlib
        lines = zlib.decompress(items, 15 + 32)
        return lines

    @property
    def url(self) -> Url:
        return f"https://{self.host}:{self.port}"

    @property
    def check_connectivity(self) -> bool:
        requests.packages.urllib3.disable_warnings()
        self.log.info(f"Checking Archive Server {self.url} reachability.")
        minio_reachable = False
        try:
            response = requests.post(
                url=self.url,
                headers=dict(),
                data=dict(),
                verify=False,
            )
            minio_reachable = True
            self.log.debug(f"Status: {response.status_code}")

        except Exception:
            self.log.warning(f"Archive host {self.url} not reachable!")

        return minio_reachable

    @property
    def check_compliancy_bucket(self) -> bool:
        self.log.info(f"Checking availability of {self.compliancy_bucket} in archive")

        buckets = self.client.list_buckets()
        compliancy_bucket_exists = self.compliancy_bucket in buckets

        return compliancy_bucket_exists


class Destination:
    def __init__(
        self,
        host: str = None,
        port: int = None,
        token: str = None,
        proto: Proto = None,
        ssl_verify: bool = None,
    ):
        self.log = logging.getLogger("HEC")
        self.log.setLevel(logging.INFO)

        self.host = host if host is not None else "localhost"
        self.port = port if port is not None else "8088"

        self.token = token if token is not None else "aa-bb"
        self.proto = proto if proto is not None else "https"
        self.ssl_verify = ssl_verify if ssl_verify is not None else False

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.host} {self.token}"

    @property
    def url(self) -> Url:
        return f"{self.proto}://{self.host}:{self.port}/services/collector/event"

    @property
    def headers(self) -> dict:
        return {
            "Authorization": "Splunk " + self.token,
            "Content-Type": "application/json",
        }

    @property
    def check_connectivity(self) -> bool:
        requests.packages.urllib3.disable_warnings()
        self.log.info("Checking HEC Server URI reachability.")
        hec_reachable = False
        # acceptable_status_codes = [400, 401, 403]
        # heath_warning_status_codes = [500, 503]
        try:
            response = requests.post(
                url=self.url,
                headers=self.headers,
                data=dict(),
                verify=False,
            )
            hec_reachable = True
            self.log.debug(f"Status: {response.status_code}")

        except Exception:
            self.log.error(f"Splunk Server {self.host} is unreachable.")

        return hec_reachable

    def sendMultiLines(self, payload: str) -> HTTPStatus:
        requests.packages.urllib3.disable_warnings()
        status = HTTPStatus.SERVICE_UNAVAILABLE
        try:
            response = requests.post(
                url=self.url,
                headers=self.headers,
                data=payload,
                verify=self.ssl_verify,
            )
            status = response.status_code
            self.log.debug(f"Status: {response.status_code}")
        except Exception:
            logging.error(f"Connection to {self.host} refused!")

        return status


if __name__ == "__main__":
    from config import destination

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    payload = """{"time":1701388800,"event":"Current Time = 01:00:00\\n",
    "host":"uf1","source":"/opt/splunkforwarder/etc/apps/normal/bin/heure.py",
    "sourcetype":"heure","index":"cust1","fields":{"cust":"customer-normal"}}\n
    {"time":1701388800,"event":"Current Time = 01:00:00\\n","host":"uf0",
    "source":"/opt/splunkforwarder/etc/apps/unlimited-speed/bin/heure.py",
    "sourcetype":"heure","index":"cust0","fields":{"cust":"customer-unlimited"}}\n"""
    status = destination.sendMultiLines(payload)
    logging.debug(f"Status: {status}")
