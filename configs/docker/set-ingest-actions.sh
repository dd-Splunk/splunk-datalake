#!/bin/ash

echo "Create S3 Destination"

echo "Create Ruleset for sourcetype"

curl -k -u admin:$SPLUNK_PASSWORD --location 'https://so1:8089/services/data/ingest/rulesets' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'name=ruleset_heure' \
--data-urlencode 'sourcetype=heure' \
--data-urlencode 'rules=[]'

echo "Add rules"

curl -k -u admin:$SPLUNK_PASSWORD --location 'https://so1:8089/services/data/ingest/rulesets//ruleset_heure?output_mode=json' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode 'rules=[{"name":"r0","action":"set_index","expr":"\"cust0\"","cond":{"type":"eval","expr":"cust==\"customer-unlimited\""}},{"name":"r1","action":"set_index","expr":"\"cust1\"","cond":{"type":"eval","expr":"cust==\"customer-normal\""}},{"name":"r2","action":"set_index","expr":"\"cust2\"","cond":{"type":"eval","expr":"cust==\"customer-double\""}},{"name":"rroute","action":"route","clone":false,"dest":"rfs:minio,_splunk_","cond":{"type":"eval","expr":"true()"}}]'