# Datalake

## Architecture

![Datalake Architecture](assets/datalake.png "Datalake Architecture")

## Compress

```bash
tar --disable-copyfile -czf unlimited-speed.spl unlimited-speed
```

## Check UF speed

```bash
sudo /opt/splunkforwarder/bin/splunk btool limits list thruput --debug
```

## Secure Minio

Follow [this](https://min.io/docs/minio/linux/operations/network-encryption.html) setup from Mino docs.
Use `certgen -host minio` from [CertGen](https://github.com/minio/certgen#install)
and put `private.key` and `public.crt` in `./certs/` directory

## To Do

- [x] Apps to throttle UF
- [x] Generate Data for each UF
- [x] Secure Minio
- [x] Configure S3 as smartstore destination
- [x] Create Tiered Index types
- [x] Configure SmartStore for each indexes
- [x] Harmonize uf* docker compose setup
- [x] Review `outputs.conf` in `forward-to-so1`
- [ ] Create app DataLake
- [x] Define sourcetype `heure`

- [ ] Create Viz with count by `cust` and count by individual uf

- [x] Set Up Ingest actions for each customer
- [x] Use yml to configure forward-server on uf*
- [ ] Use yml to deploy apps on ds1 instead of environment variables
- [ ] etc ..

## References

- Smartstore [configuration](https://blog.arcusdata.io/minio-and-splunk)
- Tag traffic [GDI](https://community.splunk.com/t5/Getting-Data-In/Universal-Forwarder-Tag-or-add-identifier-to-data-to-distinguish/m-p/475448)

## Sample generator

```bash
echo "Il est: `date`" >> ~splunk/heure.log
```

## Ingest Action Ruleset

### Troubleshoot

```bash
index="_internal" sourcetype="splunkd" (ERROR OR WARN) RfsOutputProcessor OR S3Client
```

## Tagging inputs

See community [blog](https://community.splunk.com/t5/Getting-Data-In/Universal-Forwarder-Tag-or-add-identifier-to-data-to-distinguish/m-p/475448)

## Create dummy data

```bash
index=_internal | head 10 | summaryindex spool=t uselb=t addtime=t index="cust0"
```

## Roll the buckets

```bash
docker compose exec -it so1 /opt/splunk/bin/splunk _internal call /data/indexes/cust0/roll-hot-buckets -auth admin:Password$
```

## Check the rolling

```bash
index=_internal component=HotBucketRoller
```

## Check the upload to Smartstore

```bash
index=_internal component=CacheManager TERM(action=upload)
```
