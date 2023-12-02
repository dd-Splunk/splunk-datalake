import os
import io
import sys
import urllib3

urllib3.disable_warnings()

from datetime import date
from minio import Minio
from minio.error import MinioException

import zlib
import jsonlines

from hec import send_to_hec


# Extract individual log lines
def process_ndjson(lines: bytes) -> None:
    fp = io.BytesIO(lines)  # readable file-like object
    reader = jsonlines.Reader(fp)
    for obj in reader:
        status = send_to_hec(event=obj)
        print(f"Event sent, status {status}")

    reader.close()
    fp.close()


endpoint = os.getenv("MINIO_URL", "localhost:9000")
access_key = os.getenv("MINIO_ACCESS_KEY", "admin")
secret_key = os.getenv("MINIO_SECRET_KEY", "Password$")
compliancy_bucket = os.getenv("COMPLIANCY_BUCKET", "compliancy-bucket")

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
except Exception as e:
    print(f"Connection to {endpoint} failed!")
    sys.exit(1)

if compliancy_bucket not in buckets:
    raise Exception(f"Bucket {compliancy_bucket} not found")

# Process Objects in bucket

objects = client.list_objects(compliancy_bucket, prefix=bucket_prefix, recursive=True)
for obj in objects:
    print(obj.object_name)
    try:
        response = client.get_object(compliancy_bucket, obj.object_name)
        # Read data from response.
        items = response.read(decode_content=True)
        # Decode .gz
        lines = zlib.decompress(items, 15 + 32)
        # Process .ndjson
        process_ndjson(lines)

    finally:
        response.close()
        response.release_conn()
        
