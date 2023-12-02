import json
import requests

requests.packages.urllib3.disable_warnings()

class http_event_collector:
    pass

def send_to_hec(event) -> int:
    hec_host = "https://localhost:8088"
    hec_token = "abcd-1234-efgh-5678"
    hec_endpoint = "/services/collector/event"

    url = hec_host + hec_endpoint
    headers = {"Authorization": "Splunk " + hec_token}

    # https://medium.com/@rysartem/sending-data-to-splunk-hec-in-a-right-way-4a84af3c44e2
    response = requests.post(
        url=url,
        headers=headers,
        data=json.dumps(event, ensure_ascii=False).encode("utf-8"),
        verify=False,
    )
    return response.status_code


if __name__ == "__main__":
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

    status = send_to_hec(event=event)
    print(f"Event sent, status {status}")
