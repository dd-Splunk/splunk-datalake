import os
import urllib3

urllib3.disable_warnings()

from datetime import date
from minio import Minio
from minio.error import S3Error

import zlib
import ndjson
import jsonlines


def stream_gzip_decompress(stream):
    dec = zlib.decompressobj(32 + zlib.MAX_WBITS)  # offset 32 to skip the header
    for chunk in stream:
        rv = dec.decompress(chunk)
        if rv:
            yield rv
    if dec.unused_data:
        # decompress and yield the remainder
        yield dec.flush()


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


# List buckets
buckets = client.list_buckets()

for bucket in buckets:
    print(bucket.name, bucket.creation_date)
    objects = client.list_objects(bucket.name, prefix=bucket_prefix, recursive=True)
    for obj in objects:
        print(obj.object_name)
        try:
            response = client.get_object(bucket.name, obj.object_name)
            # Read data from response.
            items = response.read(decode_content=True)
            lines = zlib.decompress(items, 15 + 32)
            print(lines)

        finally:
            response.close()
            response.release_conn()
        print("---")
