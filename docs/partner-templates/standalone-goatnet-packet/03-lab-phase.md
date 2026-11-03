# 03 — Lab phase plan (CONUS)

This document walks you through standing up GOAT-Net at home station, week by week, from "decision made" through "operators trained, ready for Phase 2 planning."

Target elapsed time: **~6 weeks** with weekly concierge sync. Some weeks compress; some expand. Hardware lead time is the most likely scheduling driver.

## Pre-conditions before week 1

You can start week 1 once these are in place. Most of them are work you'd already do for any platform stand-up:

- [ ] Procurement order placed for Phase 1 hardware (02-procurement.md)
- [ ] AWS account (or equivalent cloud) provisioned
- [ ] Domain registered (`<your-unit>.<tld>` or sub-delegation)
- [ ] Cloudflare account (or equivalent DNS provider)
- [ ] Lab space allocated (rack, power, cooling, network drop)
- [ ] LAN segment defined (CIDR, gateway, internet uplink)
- [ ] Technical lead identified, has 0.5 FTE for 6 weeks
- [ ] 1-2 operators identified, available weeks 5-6 for training
- [ ] AO informed; not yet engaged in formal review
- [ ] Concierge engagement opened (see 06-asks-and-commitments.md)

If you're not sure about the network or LAN segment, that's fine — week 1 includes a 1-on-1 design call where we work through the per-site shape with you.

## Week 1 — Design + dependencies

**Goal:** All decisions made, all dependencies ordered, all reading done.

| Activity | Lead | Outcome |
|---|---|---|
| Design call — per-site shape (3-Orin vs single-Orin lab? FIPS at lab y/n? cloud provider?) | Tech lead + us | Decisions captured in your engagement notes |
| Network design — LAN CIDR, switch model, VRRP plan, transport | Tech lead | LAN diagram, IP plan |
| Cloud account hygiene — IAM, MFA, billing alerts | Tech lead | Account ready for Terraform |
| Domain DNS configured | Tech lead | NS records pointing at Cloudflare or chosen provider |
| Hardware shipped (procurement ordered week 0) | Procurement | Tracking numbers |
| Read 00-executive-overview.md + 01-what-you-get.md end-to-end | Tech lead, AO | Shared mental model |
| Skim relevant ADRs we send you | Tech lead | Familiarity with substrate decisions |

**Concierge load:** ~4-6 hours of sync calls + ~10-15 hours of async questions.

**Stuck-points typical at week 1:** cloud-provider choice (commercial vs GovCloud), TAA constraints surfacing late, network gear that doesn't support VRRP. We work through these together.

## Week 2 — Hardware receiving + bench setup

**Goal:** Hardware on the bench, OS installed, network reachable.

| Activity | Lead | Outcome |
|---|---|---|
| Hardware received and inventoried | Operator | Asset tags, serial numbers recorded |
| Initial OS install — Ubuntu 22.04 LTS Tegra (Orin) or 24.04 LTS (x86) | Operator | Hosts boot to Linux |
| LAN connected, switch configured, VLANs (if any) defined | Operator | Hosts ping each other on LAN |
| Initial passwords + SSH key setup | Operator | Operator can SSH into all hosts |
| Cloud account: AWS CLI configured, aws-vault profile set up | Tech lead | `aws sts get-caller-identity` works |
| Terraform installed locally on tech lead's workstation | Tech lead | `terraform version` works |
| Ansible installed locally on tech lead's workstation | Tech lead | `ansible --version` works |
| Repository cloned (we provide the URL — sanitization-clean version) | Tech lead | Local checkout |
| Direnv + secret-management baseline (`.envrc.local` template) | Tech lead | Secrets pattern in place; values to fill in week 3 |

**Concierge load:** ~2-3 hours of sync; ~5-10 hours of async.

**Stuck-points typical at week 2:** Tegra OS quirks (we have a runbook); BIOS/firmware updates that take longer than expected; disk geometry surprises (LUKS partitioning).

## Week 3 — Offline CA + relay tier

**Goal:** Your offline CA exists, your relays are deployed.

| Activity | Lead | Outcome |
|---|---|---|
| YubiKey-PIV ceremony — generate offline CA root inside YubiKey slot 9c | Tech lead | CA root exists; private key never touches host disk |
| Backup YubiKey ceremony (per the same protocol) | Tech lead | 1-of-N backup stored offsite or in safe |
| `ca-init --mode prod` run; root cert published | Tech lead | Public root cert at known path |
| Relay tier Terraform applied | Tech lead | 3 relay VPSes running in 3 regions |
| Relay tier Ansible applied (haproxy ingress dispatch + rathole tunnels + STUN + relay binary) | Tech lead | Relays operational; DNS round-robin resolves |
| Relay smoke test — TLS handshake succeeds from external workstation | Tech lead | Relays reachable |
| `wg-cp0` outer wrap deployed on each relay | Tech lead | Silent control plane substrate in place |

**Concierge load:** ~3-4 hours of sync (the YubiKey ceremony is sensitive; we walk through it live).

**Stuck-points typical at week 3:** YubiKey firmware version (need 5.7+ for Ed25519 PIV); cloud-region TAA restrictions; cloud-provider quota limits on instance types.

## Week 4 — First site bringup

**Goal:** Your three mgmt-hosts come up running GOAT-Net. Or, if you chose single-Orin lab, your one mgmt-host comes up.

| Activity | Lead | Outcome |
|---|---|---|
| LUKS-encrypt NVMe drives on each mgmt-host | Operator | Data partitions encrypted |
| FIDO2 + LUKS keyslot enrollment (multiple modes per Block 65) | Operator | Auto-unseal keypath in place |
| `seed-ssh-key.sh` for each mgmt-host | Tech lead | Operator pubkey on each host |
| `mgmt-host-baseline.yml` Ansible play | Tech lead | OS baselined, hostname set, reboot if needed |
| `mgmt-host-luks.yml` Ansible play | Tech lead | LUKS volumes mounted at known paths |
| Bootstrap bundle generation — first peer's bundle | Tech lead | Signed CBOR bundle exists |
| `site-bootstrap.yml -e site_id=<your-site>` Ansible play (first run) | Tech lead | Mgmt-plane stack up: Postgres + signal-server + netbird-mgmt + Caddy/Traefik + identity stack |
| First peer enrollment via bundle | Operator | First peer (your tech lead's laptop, probably) is on the mesh |
| Smoke tests — mesh reachable, services healthy, observability dashboards green | Operator | Reference observability board shows green |
| Optional: 4th host as obs-host C (full three-Orin) | Operator | Observability + storage + utility tier |

**Concierge load:** ~8-12 hours of sync (week 4 is the densest week).

**Stuck-points typical at week 4:** Postgres init script timing; Spock extension load order; Traefik certificate issuance; the first bundle's signature verification (matching the offline CA's root cert correctly).

By the end of week 4, you have a working GOAT-Net site at home station, with your tech lead enrolled as the first peer.

## Week 5 — Apps + operators

**Goal:** At least one of your apps runs on GOAT-Net. Operators start hands-on.

| Activity | Lead | Outcome |
|---|---|---|
| Pick first app to run on GOAT-Net (TAK federation, sensor ingest, dashboard, custom) | Tech lead | App identified |
| Deploy first app — Ansible role or docker-compose, your choice | Operator + Tech lead | App running, reachable from mesh peers |
| Enroll 5-10 more peers (operator workstations, lab Orins, etc.) | Operator | Mesh has population; peer-to-peer paths exercised |
| Operator runbook walkthrough — daily checks, alerts, common stuck-points | Operator + us | Operator can describe how to read the dashboard, what alerts mean, what to do when something breaks |
| Operator tooling walkthrough — the `goat` CLI, the live fabric dashboard, the identity view, the inspection surfaces | Operator + us | Operator can answer "is the fabric healthy", "who is this peer", and "what can it reach" without asking us |
| Backup verification — run `pgbackrest stanza-create` + first backup | Operator | Backup working; test restore on a separate host |
| Audit log integrity check | Operator | First daily check succeeds |
| Continuous chaos probes (subset) — run a partition probe in lab | Operator + us | Substrate behaves correctly under partition |

**Concierge load:** ~4-6 hours of sync; lots of async during operator hands-on.

**Stuck-points typical at week 5:** app integration with mesh DNS (your app may assume direct IP routing); TAK-shim configuration if running TAK; backup-restore on a non-canonical host.

## Week 6 — Operations baseline + Phase 2 planning

**Goal:** You're operating GOAT-Net independently. You have a written plan for Phase 2.

| Activity | Lead | Outcome |
|---|---|---|
| Independent stand-up rehearsal — operator stands up a fresh lab site from clean hardware in ≤1 day with no concierge support | Operator | "If we lose this site, we can rebuild it in a day" — proven |
| Drift-check sweep — what's deployed differs from documentation? | Tech lead | Closeout list |
| Phase 2 design call — division HQs? Brigade CPs? Transport? Drill cadence? | Tech lead + us | Phase 2 plan draft |
| Phase 2 procurement plan | Procurement officer + Tech lead | Hardware order, transport plan |
| AO formal engagement begins — show them the deployment, walk through compliance posture | Tech lead + AO | AO has a mental model; ATO journey starts |
| Concierge engagement transition — to "as-needed" instead of weekly sync | Tech lead + us | Reduced cadence; you have our number |

**Concierge load:** ~3-4 hours of sync; mostly transition.

By the end of week 6, you have:

- A working GOAT-Net lab at home station
- Operators trained, including on the operator CLI and inspection surfaces
- One+ of your apps running on it
- A backup + restore proven
- A Phase 2 plan
- AO engaged

## What can go wrong (and what we do about it)

| Risk | Likelihood | Mitigation |
|---|---|---|
| Hardware doesn't arrive on time | High | Use AWS EC2 mgmt-hosts as evaluation stand-in; switch to Orin/Karbon when arrives |
| YubiKey 5.7+ firmware not available in your supply chain | Low | We have a 5-operator dev-mode fallback |
| Cloud account constraints (TAA, GovCloud quirks) | Medium | We surface in week 1 design call; some unknowns will emerge |
| Tech lead loses time to higher-priority work | Medium | We can pause + resume; concierge engagement is flexible |
| AO has unexpected concerns | Medium | We support compliance-posture conversation; you own the AO relationship |
| App integration is harder than expected | Medium | Most apps need ~half-day per integration; some need more |
| Substrate bug surfaces in your environment | Low-medium | Treat as F-NNN finding; we fix in flight; you may be the first to find it |

## Definition of done — Phase 1

You're done with Phase 1 when:

- [ ] Lab site is operational; observability green
- [ ] Tech lead has stood up a fresh site from clean hardware in ≤1 day independently
- [ ] At least one of your apps runs on GOAT-Net
- [ ] Operators have completed runbook walkthrough; can describe daily checks
- [ ] Backup-restore proven on a separate host
- [ ] Phase 2 plan draft exists
- [ ] AO has reviewed compliance posture (informally; formal ATO comes later)
- [ ] You have a written list of what's open / blocked / next

If any of these are not true, Phase 1 isn't done. We'd rather extend Phase 1 by 1-2 weeks than push you to Phase 2 with a half-baked lab.

## What's the bare minimum if 6 weeks is too long?

If you have 2-3 weeks, not 6, the compressed shape is:

- Week 1: Design + procurement + cloud + read packet (compressed; go-faster path means we accept more open questions)
- Week 2: Hardware on bench + offline CA + relay tier + first mgmt-host
- Week 3: First peer enrolled + first app running + operator handoff

Tradeoffs of compressed Phase 1:

- No drift-check sweep
- Operators less trained
- AO not yet engaged
- Less time for substrate to settle / for surprises to surface
- Phase 2 planning happens during Phase 2 instead of before it

The compressed shape is real, but you carry more risk into Phase 2. We recommend the 6-week shape unless your timeline is firm.
