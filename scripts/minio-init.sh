#!/bin/bash

set +o history

# Server
ALIAS=local
PROT=https

# Buckets
SMART_BUCKET=smart-bucket
COMPLIANCY_BUCKET=compliancy-bucket


# Create alias to local minio
mc alias set --insecure ${ALIAS} ${PROT}://${MINIO_SERVER}:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}

# Create service account
mc admin user --insecure  svcacct add       \
   --access-key "${AWS_ACCESS_KEY_ID}"      \
   --secret-key "${AWS_SECRET_ACCESS_KEY}"  \
   ${ALIAS} admin

# Create bucket
mc mb --insecure ${ALIAS}/${SMART_BUCKET}
mc mb --insecure ${ALIAS}/${COMPLIANCY_BUCKET}
mc policy --insecure public ${ALIAS}/s{SMART_BUCKET}
mc policy --insecure public ${ALIAS}/${COMPLIANCY_BUCKET}

set -o history
exit 0
