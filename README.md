# Datalake

## Compress

```bash
tar --disable-copyfile -czf unlimited-speed.spl unlimited-speed
```

## Check UF speed

```bash
sudo /opt/splunkforwarder/bin/splunk btool limits list thruput --debug
```

## Add so1 to uf

```bash
sudo /opt/splunkforwarder/bin/splunk add forward-server so1:9997 -auth admin:Password$
```

## Secure Minio

Follow [this](https://min.io/docs/minio/linux/operations/network-encryption.html) setup from Mino docs.
Use `certgen -host minio` from [CertGen](https://github.com/minio/certgen#install)
and put `private.key` and `public.crt` in `./certs/` directory

## To Do

- [x] Apps to throttle UF
- [x] Secure Minio
- [x] Configure S3 as destination
- [ ] Create Tiered Index types
- [ ] Configure SmartStore
- [ ] Set Up Ingest actions for each source
- [ ] Generate Data for each UF
- [ ] etc ..

## References

- Smartstore [configuration](https://blog.arcusdata.io/minio-and-splunk)
- Tag traffic [GDI](https://community.splunk.com/t5/Getting-Data-In/Universal-Forwarder-Tag-or-add-identifier-to-data-to-distinguish/m-p/475448)

## Sample generator

```bash
echo "Il est: `date`" >> ~splunk/heure.log
```

## Ingest Action Ruleset

## Destination

Must add to `/opt/splunk/etc/system/local/outputs.conf`

```ini
[rfs]
sslVerifyServerCert = false
partitionBy = day, sourcetype
```

### props.conf

```ini
[heure]
RULESET-ruleset_heure = _rule:ruleset_heure:route:eval:rxdtogbq
RULESET_DESC-ruleset_heure =
```

### transforms.conf

```ini
[_rule:ruleset_heure:route:eval:rxdtogbq]
INGEST_EVAL = 'pd:_destinationKey'=if((true()), "rfs:minio", 'pd:_destinationKey')
STOP_PROCESSING_IF = NOT isnull('pd:_destinationKey') AND 'pd:_destinationKey' != "" AND (isnull('pd:_doRouteClone') OR 'pd:_doRouteClone' == "")
```

## Tagging inputs

See community [blog](https://community.splunk.com/t5/Getting-Data-In/Universal-Forwarder-Tag-or-add-identifier-to-data-to-distinguish/m-p/475448)

## Create dummy data

index=_internal | head 10 | summaryindex spool=t uselb=t addtime=t index="cust0"

## Roll the buckets

docker compose exec -it so1 /opt/splunk/bin/splunk _internal call /data/indexes/cust0/roll-hot-buckets -auth admin:Password$

## Check the rolling

index=_internal component=HotBucketRoller

## Check the upload to Smartstore

index=_internal component=CacheManager TERM(action=upload)
