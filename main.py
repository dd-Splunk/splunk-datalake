import io
import logging
import sys
import zlib
from datetime import datetime

import jsonlines
import urllib3
from minio import Minio

from classes import Archive, Destination
from config import archive, destination

urllib3.disable_warnings()
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)


# Extract individual log lines
def send_ndjson(lines: bytes, destination: Destination) -> None:
    fp = io.BytesIO(lines)  # readable file-like object
    reader = jsonlines.Reader(fp)
    for obj in reader:
        status = destination.sendEvent(obj)
        logging.debug(f"Event sent, status {status}")

    reader.close()
    fp.close()


def restore_objects(
    onThatDay: datetime, archive: Archive, destination: Destination
) -> None:
    # Get buckets
    client = Minio(
        endpoint=f"{archive.host}:{archive.port}",
        access_key=archive.access_key,
        secret_key=archive.secret_key,
        secure=True,
        cert_check=archive.ssl_verify,
    )

    if not archive.check_connectivity:
        logging.error(f"Archive host {archive.host} unreachable!")
        sys.exit(1)
    if not archive.check_compliancy_bucket:
        logging.error(f"Bucket {archive.compliancy_bucket} not found")
        sys.exit(1)
    if not destination.check_connectivity:
        logging.error(f"Destination host {destination.host} unreachable!")
        sys.exit(1)

    # Process Objects in bucket

    bucket_prefix = archive.bucket_prefix(onThatDay)
    objects = client.list_objects(
        bucket_name=archive.compliancy_bucket, prefix=bucket_prefix, recursive=True
    )
    for obj in objects:
        logging.info(obj.object_name)
        try:
            response = client.get_object(
                bucket_name=archive.compliancy_bucket, object_name=obj.object_name
            )
            # Read data from response.
            items = response.read(decode_content=True)
            # Decode .gz
            # https://stackoverflow.com/questions/1838699/how-can-i-decompress-a-gzip-stream-with-zlib
            lines = zlib.decompress(items, 15 + 32)
            send_ndjson(lines, destination)

        finally:
            response.close()
            response.release_conn()

    return None


if __name__ == "__main__":
    # Select a given day
    onThatDay = datetime(2023, 12, 1)
    # Restore from archive to destination
    restore_objects(onThatDay, archive, destination)
