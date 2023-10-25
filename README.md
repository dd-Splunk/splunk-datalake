# Datalake

Proof of concept architecture to segregate traffic from various customers.

Each customer is tagged. Based on the tagging both the throughput and the destination are adjusted.

The troughput and the tagging is set per Unversal Forwarder class.

The traffic is segregated using ingest actions.

All customer indexes are using Smartstore to lower storage footprint.

## Architecture

![Datalake Architecture](assets/datalake.png "Datalake Architecture")

## Startup / Shutdown

To launch the whole config:

```bash
make up
```

and to stop it:

```bash
make down
```

## Initialisation

All Splunk instances (so1, ds1, uf{0..2}) are initialised using a dedicated `yml` config file.

Except the `ingest-action`. It is initilised using a sidecar container because at this time of writing,
 the `yml` config  routing to an external destination creates a syntax error.
