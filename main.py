import io
import logging
import sys
from datetime import datetime

import jsonlines

from classes import Archive, Destination
from config import archive, destination

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

    # Process Objects in bucket
    objects = archive.list_objects(onThatDay)

    for obj in objects:
        logging.info(obj.object_name)

        lines = archive.get_lines(obj.object_name)
        # Extract individual log lines
        fp = io.BytesIO(lines)  # readable file-like object
        events = jsonlines.Reader(fp)
        for event in events:
            status = destination.sendEvent(event)
            logging.debug(f"Event sent, status {status}")

        events.close()
        fp.close()

    return None


if __name__ == "__main__":
    # Select a given day
    onThatDay = datetime(2023, 12, 1)
    # Restore from archive to destination
    restore_objects(onThatDay, archive, destination)
