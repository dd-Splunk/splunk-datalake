import io
import logging
import sys
import zlib
from datetime import datetime

import jsonlines
import urllib3
from minio import Minio

from config import archive
from hec import send_to_hec

urllib3.disable_warnings()
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


# Extract individual log lines
def process_ndjson(lines: bytes) -> None:
    fp = io.BytesIO(lines)  # readable file-like object
    reader = jsonlines.Reader(fp)
    for obj in reader:
        status = send_to_hec(event=obj)
        logging.debug(f"Event sent, status {status}")

    reader.close()
    fp.close()


def get_objects(thisday: datetime, client: Minio) -> None:
    bucket_prefix = (
        f"year={thisday.year:0{4}}/month={thisday.month:0{2}}/day={thisday.day:0{2}}/"
    )
    # Get buckets
    try:
        buckets = client.list_buckets()
    except Exception:
        logging.error(f"Connection to {archive.host} failed!")
        sys.exit(1)

    if archive.compliancy_bucket not in buckets:
        logging.error(f"Bucket {archive.compliancy_bucket} not found")
        sys.exit(1)

    # Process Objects in bucket

    objects = client.list_objects(
        bucket_name=archive.compliancy_bucket, prefix=bucket_prefix, recursive=True
    )
    for obj in objects:
        logging.info(obj.object_name)
        try:
            response = client.get_object(archive.compliancy_bucket, obj.object_name)
            # Read data from response.
            items = response.read(decode_content=True)
            # Decode .gz
            # https://stackoverflow.com/questions/1838699/how-can-i-decompress-a-gzip-stream-with-zlib
            lines = zlib.decompress(items, 15 + 32)
            process_ndjson(lines)

        finally:
            response.close()
            response.release_conn()

    return None


if __name__ == "__main__":
    client = Minio(
        endpoint=archive.host,
        access_key=archive.access_key,
        secret_key=archive.secret_key,
        secure=True,
        cert_check=False,
    )

    # Select a given day
    thisday = datetime(2023, 12, 1)
    get_objects(thisday, client)
