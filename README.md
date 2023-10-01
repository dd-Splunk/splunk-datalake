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

Follow [this](https://min.io/docs/minio/linux/operations/network-encryption.html) setup from Mino docs. \
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
