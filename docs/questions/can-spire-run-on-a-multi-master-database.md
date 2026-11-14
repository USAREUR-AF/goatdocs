# Can SPIRE run on a multi-master database?

It depends on how the database replicates. A SPIRE server keeps its registration entries and attested nodes in a SQL datastore, and it tolerates a clustered SQL backend. A synchronous multi-master cluster, where a write is committed on every member before it is acknowledged, should work, because every SPIRE server reads the same state. Asynchronous multi-master replication that resolves conflicts by last write wins should be expected to break SPIRE: two servers can each accept a write that the other has not seen, and the conflict rule then discards one of them without telling either server.

## The alternative: two independent servers

If the goal is a SPIRE deployment that survives the loss of a server or a site, a shared database is not the only way to get it. The SPIFFE blog post [The Bottom Turtle That Heals Itself](https://spiffe.io/blog/2026-07-19-bottom-turtle-ha-architecture/) describes two fully independent SPIRE servers that together form one trust domain:

- Each server has its own hardware, its own local datastore (SQLite on its own disk) and its own certificate authority. There is no replication link and no clustered database.
- Both servers load the same registration entries from the same declarative manifests. They do not coordinate with each other.
- `spire-ha-agent` runs on each workload node, connects to both servers, and presents one Workload API socket. Workloads receive both servers' trust bundles as one bundle, and a request for an identity goes to whichever server answers.

The post gives the reasoning: replicas that share one datastore and one certificate authority can fail together, and a clustered database needs certificates from some other authority. The post also reports that the `spire-ha-agent` README describes the agent as early in development and not yet production-ready.

## How goat handles it

goat does not run SPIRE on multi-master replication.

- One SPIRE server runs on one management host per deployment (built). Its datastore is a `spire` database in that site's Postgres.
- goat replicates other databases between sites with Spock, whose default conflict rule is last write wins. The `spire` database is outside that replication set, by design.
- The server's CA private key is on local disk and not in the database. A play stages an encrypted copy of it on the passive nodes, and a runbook promotes a passive node when the active one is lost, so the trust domain survives.
- A SPIRE trust domain per site, so that a site cut off from the others keeps issuing identities, is recorded in ADR 1164 (status: Proposed; not built).

## Read more

- [Island mode, multi-writer: which stores replicate and how](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/island-mode-multi-writer.md)
- [ADR 1164: a SPIRE trust domain per site](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1164-per-site-spire-trust-domains.md)
- [Promoting the passive node to SPIRE server](https://github.com/USAREUR-AF/goatcore/blob/main/docs/operations/spire-failover-promotion.md)
- [Federated trust model](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/federated-trust-model.md)
