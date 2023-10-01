#!/bin/sh

HOST=so1

# echo "Wait for Splunk availability"
# until [ "`docker inspect -f {{.State.Health.Status}} ${HOST}`"=="healthy" ]; do
#     sleep 1;
# done;
# echo  "Splunk is up."

curl -v -k -u admin:${SPLUNK_PASSWORD} https://${HOST}:8089/services/data/ingest/rfsdestinations \
-d name=${INGEST_ACTION_DESTINATION} \
-d path=s3://${INGEST_ACTION_BUCKET}/ \
-d remote.s3.access_key=${INGEST_ACTION_AK} \
-d remote.s3.secret_key=${INGEST_ACTION_SK} \
-d remote.s3.endpoint=https://${INGEST_ACTION_DESTINATION}
