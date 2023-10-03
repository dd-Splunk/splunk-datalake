#!/bin/bash

set +o history  

# Server
ALIAS=local
PROT=https

# Wait for Minio server to be up
# echo "Waiting for ${MINIO_SERVER} ..."
# until $(curl --output /dev/null -k --silent --head --fail ${PROT}://${MINIO_SERVER}:9000/minio/health/live ); do
#     printf '.'
#     sleep 1
# done
# echo "${MINIO_SERVER} is up." 

# Create alias to local minio
mc alias set --insecure ${ALIAS} ${PROT}://${MINIO_SERVER}:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}

# Create service account 
mc admin user --insecure  svcacct add       \
   --access-key "${AWS_ACCESS_KEY_ID}"      \
   --secret-key "${AWS_SECRET_ACCESS_KEY}"  \
   ${ALIAS} admin

# Create bucket 
mc mb --insecure ${ALIAS}/${MINIO_BUCKET}
mc mb --insecure ${ALIAS}/vol01

set -o history 
exit 0