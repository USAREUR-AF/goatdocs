# Built with

goat is assembled from open-source projects. This page names the ones goat runs, builds on or ships, with each project's licence and what goat uses it for. Paths are in [goatcore](https://github.com/usareur-af/goatcore) unless marked goatstuff.

The licence-tier posture and the attribution and source-availability record are goatcore's [THIRD_PARTY_LICENSES.md](https://github.com/usareur-af/goatcore/blob/main/THIRD_PARTY_LICENSES.md). Where this page and that file differ, that file governs licence obligations; this page is the thank-you.

## Networking and data fabric

| Project | Licence | What goat uses it for | Where |
|---|---|---|---|
| [Eclipse Zenoh](https://zenoh.io/) | EPL-2.0 or Apache-2.0 | The data fabric: the `zenohd` router on every site and the client library in goat's Rust services. goat builds `zenohd` 1.9.0 with a post-quantum TLS provider | `ops/zenoh/pqc-image/`, `ops/ansible/roles/zenoh/` |
| [NetBird](https://netbird.io/) | BSD-3-Clause (client); AGPL-3.0 (management, signal, relay) | The mesh control plane (management server, dashboard) and the agent on every host; goat runs a patched management build | `ops/netbird/`, `ops/ansible/roles/netbird-mgmt/`, `netbird-dashboard/`, `netbird-client-pin/` |
| [WireGuard](https://www.wireguard.com/) | GPL-2.0 (kernel module, wireguard-tools) | Encrypted tunnels between peers, the outer control-plane tunnel, and peering links | `ops/ansible/roles/wireguard-kmod/`, `wg-cp0-server/`, `goat-peering-wg/` |
| [Rosenpass](https://rosenpass.eu/) | MIT or Apache-2.0 | Post-quantum key exchange for WireGuard; built, off by default | `ops/ansible/group_vars/all.yml` |
| [CoreDNS](https://coredns.io/) | Apache-2.0 | Name resolution inside the mesh and on site LANs | `ops/ansible/roles/mesh-coredns/`, `lan-coredns/` |
| [Traefik](https://traefik.io/traefik/) | MIT | TLS reverse proxy in front of each host's web surfaces | `ops/ansible/roles/traefik/`, `obs-traefik/` |
| [nginx](https://nginx.org/) | BSD-2-Clause | Static sites and the client-certificate proxy for smart-card sign-in | `ops/ansible/roles/goat-docs/`, `goat-get/`, `icam-mtls-proxy/` |
| [coturn](https://github.com/coturn/coturn) | BSD-3-Clause | TURN relay for peers that cannot connect directly | `ops/ansible/roles/coturn/` |
| [keepalived](https://www.keepalived.org/) | GPL-2.0 | Virtual-IP failover between a site's management hosts | `ops/ansible/roles/keepalived-mgmt/` |

## Identity and access

| Project | Licence | What goat uses it for | Where |
|---|---|---|---|
| [Ory Kratos](https://www.ory.sh/kratos/) | Apache-2.0 | Identity and sign-in for people | `ops/ansible/roles/ory/`, `operator-idp-kratos/` |
| [Ory Hydra](https://www.ory.sh/hydra/) | Apache-2.0 | OAuth 2.0 and OpenID Connect provider for every web surface | `ops/ansible/roles/ory/`, `operator-idp-hydra/` |
| [Ory Kratos self-service UI (Node)](https://github.com/ory/kratos-selfservice-ui-node) | Apache-2.0 | The sign-in and consent pages; goat applies five patches | `ops/ory-consent/` |
| [SPIFFE / SPIRE](https://spiffe.io/) | Apache-2.0 | Workload identity: short-lived certificates for services | `ops/ansible/roles/spire/`, `goat-peering-spire/` |
| [OAuth2 Proxy](https://oauth2-proxy.github.io/oauth2-proxy/) | MIT | OpenID Connect sign-in in front of web surfaces that have none | `ops/ansible/roles/oauth2-proxy-*/` |
| [Keycloak](https://www.keycloak.org/) | Apache-2.0 | Broker for smart-card (CAC/PIV) sign-in; off by default | `ops/ansible/roles/icam-keycloak-cac/` |
| [OpenBao](https://openbao.org/) | MPL-2.0 | One of the selectable secret stores for operator tooling | `ops/scripts/with-secrets`, `ops/scripts/secrets-session` |

## Data, storage and backup

| Project | Licence | What goat uses it for | Where |
|---|---|---|---|
| [PostgreSQL](https://www.postgresql.org/) | PostgreSQL License | The database behind the mesh control plane, identity, the portal and the admin console | `ops/postgres/`, `ops/ansible/roles/operator-idp-postgres/` |
| [pgEdge Spock](https://github.com/pgEdge/spock) | PostgreSQL License | Multi-master replication between sites | `ops/postgres/spock/Dockerfile` |
| [pgBackRest](https://pgbackrest.org/) | MIT | PostgreSQL backup and restore | `ops/ansible/roles/pgbackrest/` |
| [MinIO](https://min.io/) | AGPL-3.0 | S3-compatible object store for the audit log | `ops/ansible/roles/minio/` |
| [Distribution (registry)](https://distribution.github.io/distribution/) | Apache-2.0 | Site-local container image mirror | `ops/ansible/roles/docker-registry-mirror/` |

## Observability and time

| Project | Licence | What goat uses it for | Where |
|---|---|---|---|
| [Prometheus](https://prometheus.io/), Alertmanager, node_exporter, blackbox_exporter, postgres_exporter | Apache-2.0 | Metrics collection, probes and alerting | `ops/ansible/roles/observability/`, `obs-host/`, `node-exporter/` |
| [Grafana](https://grafana.com/oss/grafana/) | AGPL-3.0 | Dashboards | `ops/compose/goat-obs/`, `ops/ansible/roles/obs-host/` |
| [cAdvisor](https://github.com/google/cadvisor) | Apache-2.0 | Per-container resource metrics | `ops/ansible/roles/obs-host/` |
| [process-exporter](https://github.com/ncabatoff/process-exporter) | MIT | Per-process metrics | `ops/ansible/obs.yml` |
| [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/) | Apache-2.0 | Receiving OTLP from goat services and forwarding it to OpenObserve | `ops/ansible/roles/otel-collector/` |
| [Vector](https://vector.dev/) | MPL-2.0 | Shipping host logs to the object store | `ops/ansible/roles/goat-logship/` |
| [chrony](https://chrony-project.org/) | GPL-2.0 | Clock synchronisation on every host | `ops/ansible/roles/ntp-hygiene/` |

## Hosts, disks and deployment

| Project | Licence | What goat uses it for | Where |
|---|---|---|---|
| [Ubuntu](https://ubuntu.com/) | Free software, mixed licences | Host operating system (24.04 LTS) | `ops/ansible/` |
| [Ansible](https://www.ansible.com/) (ansible-core) | GPL-3.0 | Every host's configuration and every deployment | `ops/ansible/` |
| [Docker Engine / Moby](https://mobyproject.org/) | Apache-2.0 | Container runtime on every host | `ops/ansible/roles/docker-engine/` |
| [Tang](https://github.com/latchset/tang) and [Clevis](https://github.com/latchset/clevis) | GPL-3.0 | Unlocking LUKS-encrypted disks at boot when the host is on its own network | `ops/ansible/roles/tang-server/`, `luks-unlock/` |
| [Dropbear](https://matt.ucc.asn.au/dropbear/dropbear.html) | MIT | SSH in the initramfs, to enter a disk passphrase remotely | `ops/ansible/roles/dropbear-initramfs/` |
| [apt-cacher-ng](https://www.unix-ag.uni-kl.de/~bloch/acng/) | BSD-style | Site-local package cache | `ops/ansible/roles/apt-cacher-ng/` |
| [Mailpit](https://mailpit.axllent.org/) | MIT | Mail sink for test and stand-up runs | `ops/ansible/roles/smtp-sink/` |
| Terraform providers [hashicorp/aws](https://github.com/hashicorp/terraform-provider-aws) and [cloudflare/cloudflare](https://github.com/cloudflare/terraform-provider-cloudflare) | MPL-2.0 | Cloud relay hosts and public DNS records | `terraform/modules/` |

## Container base images

| Project | Licence | What goat uses it for | Where |
|---|---|---|---|
| [Distroless](https://github.com/GoogleContainerTools/distroless) | Apache-2.0 | Minimal runtime images for Go services | `signal-server/Dockerfile`, `ops/admit-audit/Dockerfile` |
| [Debian](https://www.debian.org/), [Alpine Linux](https://alpinelinux.org/) | Free software, mixed licences | Build stages and a few runtime images | Dockerfiles under `ops/` |

## Languages and libraries

| Project | Licence | What goat uses it for |
|---|---|---|
| [Rust](https://www.rust-lang.org/) | MIT or Apache-2.0 | The `goat` and `goatbuilder` CLIs, the relay, the fabric services and health publishers |
| [Tokio](https://tokio.rs/) | MIT | Async runtime for every Rust service |
| [rustls](https://github.com/rustls/rustls) | Apache-2.0, ISC or MIT | TLS in Rust services and in `zenohd` |
| [AWS-LC](https://github.com/aws/aws-lc) and [aws-lc-rs](https://github.com/aws/aws-lc-rs) | Apache-2.0 and ISC | The cryptographic library and post-quantum key exchange behind rustls |
| [quinn](https://github.com/quinn-rs/quinn) | MIT or Apache-2.0 | QUIC in the relay |
| [serde](https://serde.rs/), [clap](https://github.com/clap-rs/clap), [axum](https://github.com/tokio-rs/axum), [tracing](https://github.com/tokio-rs/tracing), [prost](https://github.com/tokio-rs/prost), [RustCrypto](https://github.com/RustCrypto) | MIT and/or Apache-2.0 | Serialisation, command lines, HTTP services, logging, protobuf, signatures |
| [Project Fluent](https://projectfluent.org/) (`fluent`, `i18n-embed`) | Apache-2.0 or MIT | Translated CLI messages and error explanations |
| [Go](https://go.dev/) | BSD-3-Clause | The identity console, portal, enrolment, signal server, probes and test harnesses |
| [pgx](https://github.com/jackc/pgx) | MIT | PostgreSQL driver for the Go services |
| [Prometheus Go client](https://github.com/prometheus/client_golang) | Apache-2.0 | Metrics from the Go services |
| [OpenTelemetry Go](https://github.com/open-telemetry/opentelemetry-go) | Apache-2.0 | Tracing from the Go services |
| [age](https://github.com/FiloSottile/age) | BSD-3-Clause | Keeping the enrolment CA's private key encrypted at rest |
| [piv-go](https://github.com/go-piv/piv-go) | Apache-2.0 | Signing enrolment certificates with a YubiKey-held CA |
| [facebook/time](https://github.com/facebook/time) | Apache-2.0 | Reading chronyd's state for the time-health checks |
| [cobra](https://github.com/spf13/cobra), [gRPC-Go](https://github.com/grpc/grpc-go), [modernc SQLite](https://gitlab.com/cznic/sqlite) | Apache-2.0, Apache-2.0, BSD-3-Clause | Command lines, RPC, embedded storage |
| [Playwright](https://playwright.dev/) | Apache-2.0 | Browser end-to-end tests of the web surfaces |

## In goatstuff

| Project | Licence | What goat uses it for | Where (goatstuff) |
|---|---|---|---|
| [MediaMTX](https://github.com/bluenviron/mediamtx) | MIT | Video stream server for the video fabric | `ops/ansible/roles/mediamtx/` |
| [OpenObserve](https://openobserve.ai/) | AGPL-3.0 | Wide-event search over observability data | `ops/ansible/roles/openobserve/` |
| [Caddy](https://caddyserver.com/) | Apache-2.0 | Web server for the trust sandbox | `ops/serve/trust-sandbox/deploy/` |
| [Apache Guacamole](https://guacamole.apache.org/) (`guacd`) | Apache-2.0 | Remote desktop gateway in the herd surface | `ops/ansible/roles/herd/` |
| [D3](https://d3js.org/) | ISC | The panoscope graph view | `ops/panoscope/frontend/` |

## Adding a project

A pull request that adds a dependency goat runs or ships adds its row here and its licence row in goatcore's `THIRD_PARTY_LICENSES.md`.
