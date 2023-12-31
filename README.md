# Datalake

Proof of concept architecture to segregate traffic from various customers
into dedicated indexes,
while avoiding saturation of the main Splunk instance.

Each customer is tagged.
Based on the tagging both the throughput and the destination are adjusted.

The troughput and the tagging is set per Unversal Forwarder class.

The traffic is segregated using ingest actions.

All customer indexes are using Smartstore to lower storage footprint.

For compliancy reasons all tarffic is also sent to a dedicated S3 bucket.

## Architecture

![Datalake Architecture](assets/datalake.png "Datalake Architecture")

## Startup / Shutdown

Copy `.env.template` into `.env` and fill the SPLUNK_PASSWORD
and MINIO_ROOT_PASSWORD values in the file.

Then launch the whole config:

```bash
make up
```

and to stop it:

```bash
make down
```

## Initialisation

All Splunk instances (so1, ds1, uf{0..2}) are initialised
using a dedicated `yml` config file.

Except the `ingest-action`. It is initilised using a sidecar container
because at this time of writing, the `yml` config  routing to an external
destination creates a syntax error.

## Restore Capability

### Schema

![Restore Architecture](assets/Data_Restore.png "Restore Architecture")

### Restore App

The Python Script managing the restore capability is `main.py`

It has no interactive capability at this moment.
