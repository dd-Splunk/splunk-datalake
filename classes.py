import datetime
import json
import logging
from http import HTTPStatus

import requests
from minio import Minio


class Archive:
    def __init__(
        self,
        host=None,
        access_key=None,
        secret_key=None,
        compliancy_bucket=None,
    ):
        self.log = logging.getLogger("Minio")
        self.log.setLevel(logging.INFO)

        self.host = host if host is not None else "localhost" + ":9000"
        self.access_key = access_key if access_key is not None else "admin"
        self.secret_key = secret_key if secret_key is not None else "?"
        self.compliancy_bucket = (
            compliancy_bucket if compliancy_bucket is not None else "compliancy-bucket"
        )
        self.client = Minio(
            endpoint=self.host,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=True,
            cert_check=False,
        )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.host} {self.access_key} \
{self.secret_key} {self.compliancy_bucket}"

    @property
    def url(self) -> str:
        return f"https://{self.host}"

    def bucket_prefix(self, thisday: datetime, sourcetype: str = None) -> str:
        prefix = f"year={thisday.year:0{4}}"
        prefix += f"/month={thisday.month:0{2}}"
        prefix += f"/day={thisday.day:0{2}}/"

        if sourcetype is not None:
            prefix += f"sourcetype={sourcetype}/"

        self.log.debug(f"Bucket prefix {prefix}")

        return prefix

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
        host=None,
        port=None,
        token=None,
    ):
        self.log = logging.getLogger("HEC")
        self.log.setLevel(logging.INFO)

        self.host = host if host is not None else "localhost"
        self.port = port if port is not None else "8088"

        self.token = token if token is not None else "aa-bb"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.host} {self.token}"

    @property
    def url(self) -> str:
        return f"https://{self.host}:{self.port}/services/collector/event"

    @property
    def headers(self) -> dict:
        return {"Authorization": "Splunk " + self.token}

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
            self.log.error("Splunk Server URI is unreachable.")

        return hec_reachable

    def sendEvent(self, payload) -> HTTPStatus:
        requests.packages.urllib3.disable_warnings()
        status = HTTPStatus.SERVICE_UNAVAILABLE
        self.log.debug("Single Submit: Sticking the event on the queue.")
        self.log.debug(f"event: {payload}")
        try:
            # https://medium.com/@rysartem/sending-data-to-splunk-hec-in-a-right-way-4a84af3c44e2
            response = requests.post(
                url=self.url,
                headers=self.headers,
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                verify=False,
            )
            status = response.status_code
        except Exception:
            logging.error(f"Connection to {self.url} refused!")

        return status


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    archive = Archive(
        "localhost:9000",
        "L4iTAngnHaoIjHnXiJz4",
        "nAoIBDDUqr3VIR3emTH7oyux1VJ2TDG48vF0l7LR",
    )
    print(archive.check_connectivity)
    print(archive.bucket_prefix(datetime.datetime(2023, 12, 1), "heure"))
    print(archive.bucket_prefix(datetime.datetime(2023, 2, 3)))
    # Test data
    event = {
        "time": 1701433088,
        "event": "Current Time = 13:18:08\n",
        "host": "uf2",
        "source": "/opt/splunkforwarder/etc/apps/double-speed/bin/heure.py",
        "sourcetype": "heure",
        "index": "cust2",
        "fields": {"cust": "customer-double"},
    }
    destination = Destination(token="abcd-1234-efgh-5678")

    print(destination.check_connectivity)
    status = destination.sendEvent(event)
    logging.info(f"Event sent, status {status}")
