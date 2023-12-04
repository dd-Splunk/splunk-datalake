import json
import logging
from http import HTTPStatus

import requests

from classes import Destination

requests.packages.urllib3.disable_warnings()


def send_to_hec(event, destination: Destination) -> HTTPStatus:
    status_code = HTTPStatus.REQUEST_TIMEOUT

    try:
        # https://medium.com/@rysartem/sending-data-to-splunk-hec-in-a-right-way-4a84af3c44e2
        response = requests.post(
            url=destination.url(),
            headers=destination.headers(),
            data=json.dumps(event, ensure_ascii=False).encode("utf-8"),
            verify=False,
        )
        status_code = response.status_code
    except Exception:
        logging.error(f"Connection to {destination.url()} refused!")
    return status_code


if __name__ == "__main__":
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
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

    status = send_to_hec(event=event, destination=destination)
    logging.info(f"Event sent, status {status}")
