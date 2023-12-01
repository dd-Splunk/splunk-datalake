import os
import io
import sys
import urllib3

urllib3.disable_warnings()

from datetime import date
from minio import Minio

import zlib
import jsonlines


# Extract individual log lines
def process_ndjson(lines):
    fp = io.BytesIO(lines)  # readable file-like object
    reader = jsonlines.Reader(fp)
    for obj in reader:
        print(obj)

    reader.close()
    fp.close()


endpoint = os.getenv("MINIO_URL", "localhost:9000")
access_key = os.getenv("MINIO_ACCESS_KEY", "admin")
secret_key = os.getenv("MINIO_SECRET_KEY", "Password$")


client = Minio(
    endpoint=endpoint,
    access_key=access_key,
    secret_key=secret_key,
    secure=True,
    cert_check=False,
)

thisday = date.today()
# filter on today's buckets
bucket_prefix = (
    f"year={thisday.year:0{4}}/month={thisday.month:0{2}}/day={thisday.day:0{2}}/"
)


# Get buckets
try:
    buckets = client.list_buckets()
except:
    print(f"No connection to {endpoint} !")
    sys.exit(1)

# Process Objects in buckets
for bucket in buckets:
    print(bucket.name, bucket.creation_date)
    objects = client.list_objects(bucket.name, prefix=bucket_prefix, recursive=True)
    for obj in objects:
        print(obj.object_name)
        try:
            response = client.get_object(bucket.name, obj.object_name)
            # Read data from response.
            items = response.read(decode_content=True)
            # Decode .gz
            lines = zlib.decompress(items, 15 + 32)
            # Process .ndjson
            process_ndjson(lines)

        finally:
            response.close()
            response.release_conn()
        print("---")
