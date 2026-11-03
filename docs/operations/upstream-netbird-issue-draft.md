# Upstream issue draft — netbirdio/netbird

**Status:** Draft, ready to file. Created 2026-04-29 from M-001/M-002/M-005/M-006 RCA evidence.

The text below is intended to be copy-pasted (with light editing) into a new issue at https://github.com/netbirdio/netbird/issues. Two related questions worth raising upstream as a single issue or as two linked issues. Use the goat project lead's GitHub account to file.

---

## Suggested title

> Relay protocol selection: daemon defaults to WebSocket even when relay supports QUIC; per-pair throughput caps at ~25 Mbps with 76% of relay process time in Go runtime futex/scheduler

## Body

We've been doing a load-test campaign on a self-hosted netbird deployment (v0.70.0 daemon + v0.70.0 relay, official `netbirdio/relay:latest` image, t3.micro relay VPS, two peer-pairs behind separate AWS NAT Gateways forcing relay routing) and surfaced two related observations that we'd like to raise upstream. Both are reproducible; full evidence below.

### 1. Daemon picks WebSocket exclusively even when QUIC is available

The relay binary listens for **both** WebSocket (TCP) and QUIC (UDP) on the same port (`:33073`):

```
relay/server/listener/quic/listener.go:39: QUIC server listening on address: :33073
relay/server/listener/ws/listener.go:44:   WS server listening address: :33073
```

The netbird daemon binary contains the `quic-go` library (verified via `strings | grep quic-go`). Yet across every peer connection we observed, **100% of relay connections are WebSocket; 0% are QUIC**. Every entry in the relay log is `WS client connected from <ip>`, none are `QUIC client connected from <ip>`.

**Questions for the maintainers:**

- Why does the daemon prefer WebSocket over QUIC when both are available?
- Is there a config field, env var, or CLI flag to express a protocol preference? `netbird up --help` shows none; we found `QUIC_GO_DISABLE_GSO` and `QUIC_GO_DISABLE_ECN` (quic-go library tunables), but nothing controlling daemon-side protocol selection.
- Would maintainers consider exposing a relay-protocol-selection interface (env var, config field, or CLI flag) so operators can choose their preferred transport? A `prefer_quic` toggle would let deployments take advantage of QUIC's congestion-control and HOL-blocking-resistance properties where the network supports UDP.

We'd be happy to send a PR if there's appetite — please point us at the protocol-selection codepath if so.

### 2. Per-pair throughput caps at ~25 Mbps with 76% of CPU time in Go runtime overhead

iperf3-over-WireGuard between two peers forced into the relay path consistently caps at ~25-30 Mbps single-flow, regardless of:

- Peer hardware (also tested with bigger peer instances; same ceiling)
- Linux TCP receive/send buffer sizes (`tcp_rmem`/`tcp_wmem` tuned to 16 MB on peers — only ~10% improvement)
- Docker / docker-proxy presence (extracted relay binary, ran natively on host with `--network=host` equivalent — single-flow throughput **identical** to containerized)
- Kernel `rmem_max` (`strace -c` shows ZERO `setsockopt` calls — relay relies on Linux TCP autotuning, doesn't cap itself)
- Multi-flow concurrency (4-stream collapses to ~22 Mbps total, 16-stream collapses to ~10 Mbps total — the inverse of expected behavior)

`strace -c -f -p <relay-pid>` for a 20-second window during sustained load shows:

| Syscall | Calls | Time (s) | % of time |
|---|---|---|---|
| **futex** | 16,697 | 13.53 | **51.82%** |
| **nanosleep** | 51,581 | 6.33 | **24.26%** |
| write | 140,320 | 3.65 | 13.96% |
| read | 88,565 | 1.59 | 6.08% |
| epoll_pwait | 42,860 | 0.99 | 3.78% |

**76% of the relay process's measured CPU time is in `futex` + `nanosleep`** — Go runtime mutex contention and scheduler park/unpark. Only ~24% is actual network I/O syscalls. Relay process CPU peaked at 33% on the 2-vCPU instance — not CPU-bound at the processor level.

We confirmed inter-thread futex contention is part of the picture by sweeping `GOMAXPROCS`:

| `GOMAXPROCS` | Single-flow Mbps |
|---|---|
| 1 | **36.6** |
| 2 (default on 2 vCPU) | 27-30 |
| 4 | 34.7 |

**Setting `GOMAXPROCS=1` on a 2-vCPU relay yields ~25% improvement** — collapses to a single OS thread, eliminates inter-thread futex traffic.

**Questions for the maintainers:**

- Is the per-pair ~25 Mbps ceiling expected? It's roughly 13× lower than direct TCP between the same hosts (which sustains 330 Mbps single-flow / 1 Gbps 4-parallel).
- Has the `GOMAXPROCS=1` improvement been observed by others, and is it documented anywhere we missed?
- Would the project consider documenting expected per-pair relay throughput as a function of relay instance shape, so operators can plan capacity for sustained-bandwidth workloads (peer-to-peer video, file transfer through relay, etc.)?
- Is there interest in upstream contributions toward batched-syscall I/O (`recvmmsg`/`sendmmsg`) or `kTLS` offload, which our profiling suggests would help the 24% I/O slice?

### Reproducer

Full RCA evidence in our project repo:

- Throughput measurements: M-001, M-002, M-005, M-006 (linked from `docs/measurements/INDEX.md`)
- Findings derived: F-014 (engineering quality), F-015 (TCP-over-TCP HOL hypothesis on WS path), F-016 (daemon picks WS), F-017 (Go runtime overhead dominates) — `docs/findings/INDEX.md`
- Operations runbook: `docs/operations/relay-throughput-ceiling.md`
- ADR: `docs/adr/1012-load-testing-discipline.md` (the framework that produced these measurements)

(URLs to be filled in when filing — point at the relevant commit SHAs in the github.com/usareur-af/goatcore repo at the time of filing.)

### Context

goat is a sovereign tactical-edge data-fabric project that uses self-hosted netbird as its mesh substrate. We're operating within the project's scope envelope (600/3000/6000 peers fleet-wide) but are planning for video / sensor-stream workloads that will exceed the per-pair ceiling. We're not asking for an architectural rewrite of the relay (we have a path to do that ourselves if we have to — see `docs/findings/F-017-...`); we ARE asking for visibility into protocol selection so we can choose deliberately, and clarity on whether the throughput ceiling is expected.

Happy to share more detail or do additional reproduction work. Thanks for the project!

---

## Filing checklist

- [ ] Verify links to the goat repo resolve (after filing, may need to update SHAs)
- [ ] Decide whether to file as one issue or two (protocol selection + throughput ceiling are distinct asks)
- [ ] Include version info: daemon v0.70.0, relay image `netbirdio/relay:latest` (digest TBD at time of filing), Linux 6.17.0 / Ubuntu 24.04 on relay
- [ ] Cross-link the issue back from F-016 and F-017 once filed (status update on each)
- [ ] If maintainers don't respond within 30 days, the upstream-conversation step is "done" for our records — document the silence and proceed with the rewrite per Block 33
