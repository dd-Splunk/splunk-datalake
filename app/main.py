import logging
import sys
from datetime import datetime

from .classes import Archive, Destination
from .config import archive, destination

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


def restore_objects(
    onThatDay: datetime, archive: Archive, destination: Destination
) -> None:
    if onThatDay > datetime.now():
        logging.error(f"Restoring from {onThatDay} is not allowed")
        sys
        exit(1)
    if not archive.check_connectivity:
        logging.error(f"Archive host {archive.host} unreachable!")
        sys.exit(1)
    if not archive.check_compliancy_bucket:
        logging.error(f"Bucket {archive.compliancy_bucket} not found")
        sys.exit(1)
    if not destination.check_connectivity:
        logging.error(f"Destination host {destination.host} unreachable!")
        sys.exit(1)

    # Process ndjson.gz Objects in bucket
    objects = archive.list_objects(onThatDay)

    for obj in objects:
        logging.info(obj.object_name)
        # Decode .gz
        lines = archive.get_lines(obj.object_name)
        # send ndjson ( multi lines )
        status = destination.sendMultiLines(lines)
        logging.info(f"Event sent, status {status}")

    return None


if __name__ == "__main__":
    # Select a given day
    onThatDay = datetime(2023, 12, 1)
    # Restore that day from archive to destination
    restore_objects(onThatDay, archive, destination)
