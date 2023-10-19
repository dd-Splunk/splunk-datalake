# Datalake

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
./scripts/roll.sh
```

## Check the rolling

```bash
index=_internal component=HotBucketRoller
```

## Check the upload to Smartstore

```bash
index=_internal component=CacheManager TERM(action=upload)
```
