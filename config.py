import os
from dataclasses import dataclass

config_file_location = "configs/splunk/app.conf"


@dataclass
class Archive:
    endpoint: str
    access_key: str
    secret_key: str
    compliancy_bucket: str


config = Archive(
    os.getenv("MINIO_URL", "localhost:9000"),
    os.getenv("MINIO_ACCESS_KEY", "admin"),
    os.getenv("MINIO_SECRET_KEY", "Password$"),
    os.getenv("COMPLIANCY_BUCKET", "compliancy-bucket"),
)
