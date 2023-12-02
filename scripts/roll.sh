#!/bin/bash
for i in {0..2}
do
    echo "Rolling cust${i}"
    docker compose exec -it so1 /opt/splunk/bin/splunk _internal call /data/indexes/cust${i}/roll-hot-buckets -auth admin:Password$
done
