import os
import urllib3

urllib3.disable_warnings()

from minio import Minio
from minio.error import S3Error

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

# List buckets
buckets = client.list_buckets()
print(buckets)

for bucket in buckets:
    print(bucket.name, bucket.creation_date)
    objects = client.list_objects(bucket.name, recursive=True)
    for obj in objects:
        print(obj.object_name)



