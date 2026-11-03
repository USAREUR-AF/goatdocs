# Engineering Baseline — How goat Aligns With Industry Best Practice

> **Read this alongside [deliberate-deltas.md](deliberate-deltas.md).** That doc tells you what's bespoke and load-bearing-because-it's-different. This doc tells you what's standard and load-bearing-because-it's-done-well. Both views are equally important — emphasizing only the deltas creates the misread that "if it's not exotic, it must not matter." The reverse is closer to true: the bespoke choices only pay off because the unsurprising foundations underneath them are solid.
>
> If a topic appears in **neither** this doc nor [deliberate-deltas.md](deliberate-deltas.md), default behavior applies and the topic is not load-bearing for this project.

## How entries are structured

Each entry has three fields:

- **Practice** — what we do (and that we do it deliberately, not by accident).
- **Why** — the reason it's load-bearing here, even though it's standard everywhere.
- **Read more** — the canonical doc, ADR, or module.

Entries are grouped by layer, top-to-bottom: change management → infrastructure → secrets → network/TLS → OS → containers → database → observability → identity & access → defense in depth → operations → culture.

---

## 1. Change management & code provenance

### 1.1 Trunk-based, PR-gated, signed-commit git workflow

**Practice:** Branch off `main`, PR, automated tests, ≥1 review, then merge. No direct pushes to `main`. Commits cryptographically signed (SSH or GPG), DCO sign-off, Conventional Commits for PR titles, CODEOWNERS for cross-team review routing.

**Why:** Code provenance + change control are auditor expectations and a procurement-resilience baseline. Standard for any serious project.

**Read more:** [adr/0109-git-collaboration-trunk-based.md](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md), CONTRIBUTING.md.

### 1.2 ADR / design doc / runbook artifact separation

**Practice:** ADRs record decisions (the "why"); design docs describe systems (how they work today); runbooks describe operator tasks (what to do). Separate artifacts, separate locations under `docs/`.

**Why:** Each artifact decays at its own rate; bundling them produces stale or duplicated content.

**Read more:** [adr/0005-decision-log-vs-design-doc.md](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0005-decision-log-vs-design-doc.md), [adr/INDEX.md](https://github.com/usareur-af/goatcore/blob/main/docs/adr/INDEX.md), [docs/INDEX.md](../INDEX.md).

### 1.3 Code review on every change

**Practice:** Required ≥1 reviewer before merge. CODEOWNERS routes review for cross-team areas. No solo-merging load-bearing changes.

**Why:** Catches bugs, distributes context, enforces conventions.

**Read more:** [adr/0109-git-collaboration-trunk-based.md](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md).

### 1.4 CI on every PR

**Practice:** Linting, type-checking, tests, schema validation, and pin-regression checks run automatically per PR. Required to pass before merge.

**Why:** Surface regressions before they reach `main`. Cheaper to catch in CI than in a soak.

**Read more:** [.github/workflows/](https://github.com/usareur-af/goatcore/tree/main/.github/workflows), [adr/0703-pinned-digests-and-pin-regression-ci.md](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0703-pinned-digests-and-pin-regression-ci.md).

---

## 2. Infrastructure as code

### 2.1 Everything is Terraform or Ansible — no hand-deploys

**Practice:** Cloud infrastructure in Terraform (`terraform/`). Host configuration in Ansible (`ops/ansible/`). No hand-edited servers. No "I'll just SSH in and fix it." If it's not in git, it didn't happen — the next reconciliation will overwrite anything that is not.

**Why:** Reproducibility, drift control, change auditability.

**Read more:** onboarding/01-concepts.md, CLAUDE.md §"Running Ansible".

### 2.2 Idempotent playbooks

**Practice:** Every Ansible playbook can be re-run safely. Tasks check current state and skip when already converged. Setup scripts check for existing artifacts before creating them.

**Why:** Operators must be able to re-run any playbook without fear. Drift is fixed by re-running, not by hand.

**Read more:** onboarding/01-concepts.md §"Idempotence".

### 2.3 Inventory-driven environment separation

**Practice:** Dev, pre-merge and prod environments are separated by Ansible inventory, not by separate playbooks. The same playbooks run against any env.

**Why:** Identical tooling across environments means a fix validated in dev is a fix that ships to prod with no transformation.

**Read more:** collaborator-overview.md §"Dev / Prod Parity".

### 2.4 Mainstream cloud providers (AWS, Cloudflare)

**Practice:** AWS for the transit-layer cloud; Cloudflare for public DNS. Both are mainstream, well-documented, well-audited, well-tooled providers.

**Why:** Boring infrastructure choices reduce cognitive surface area for new contributors and reduce vendor risk. Exotic providers earn their place only with a load-bearing reason.

**Read more:** [terraform/](https://github.com/usareur-af/goatcore/tree/main/terraform).

---

## 3. Secrets & credentials

### 3.1 Secrets out of repo — runtime resolution only

**Practice:** No plaintext secrets in committed files or on-disk generated files. Secrets resolved at runtime from env vars, AWS Secrets Manager, or Ansible vault.

**Why:** A leaked secret in git history is permanent.

**Read more:** CLAUDE.md §"Credentials".

### 3.2 direnv for local env, aws-vault for AWS creds

**Practice:** `.envrc` checked in (no secrets). `.envrc.local` gitignored (secrets, mirrored in 1Password). AWS credentials in OS keychain via aws-vault, never in env files.

**Why:** Keychain-backed credentials don't appear in env dumps, shell history, or core files.

**Read more:** onboarding/02-toolchain.md, CLAUDE.md §"Credentials".

### 3.3 Per-region / per-purpose secret scoping

**Practice:** Each VPS region has its own AWS Secrets Manager entries; each purpose (relay creds, bridge creds, etc.) is a separate entry rather than one mega-secret.

**Why:** Blast-radius containment. Compromise of one secret does not cascade.

**Read more:** [terraform/modules/relay/](https://github.com/usareur-af/goatcore/tree/main/terraform/modules/relay).

---

## 4. Network & TLS

### 4.1 HTTPS everywhere via Let's Encrypt DNS-01

**Practice:** All HTTP services terminate TLS at Traefik. ACME DNS-01 challenge through the Cloudflare API. Auto-renewal.

**Why:** Standard TLS-everywhere posture. DNS-01 lets us issue certs for non-public hostnames (`*.netbird.legacy.example`) without exposing port 80.

**Read more:** hosting-services.md, service-onboarding-plan.md.

### 4.2 DNSSEC enabled

**Practice:** Cloudflare signs the `legacy.example` zone; the DS record is registered at Route 53.

**Why:** Standard zone-integrity posture. Prevents DNS spoofing of the public enrollment hostnames.

**Read more:** CLAUDE.md §"Fresh Deployment Checklist".

### 4.3 SSH closed by default; admin via SSM or mesh

**Practice:** Port 22 closed on all VPS instances. Admin access via AWS SSM Session Manager (relay + bridge) or SSH-over-mesh-IP (bridge + mgmt-hosts only). Temporarily opening SSH for a specific IP is a Terraform change.

**Why:** Reduce attack surface. SSM has IAM-gated audit logs; mesh-IP access is gated on prior enrollment.

**Read more:** CLAUDE.md §"VPS Shell Access".

### 4.4 Reverse proxy at the edge

**Practice:** Traefik terminates TLS and routes by hostname. Application services do not face the network directly.

**Why:** One place to enforce TLS, one place to enforce headers, one place to add ForwardAuth or rate limiting.

**Read more:** hosting-services.md.

### 4.5 Network segmentation via security groups

**Practice:** Per-role AWS security groups, default-deny ingress, narrow allow-rules per port and source.

**Why:** Standard cloud network segmentation. The blast radius of a compromised host is bounded at the SG.

**Read more:** [terraform/modules/relay/](https://github.com/usareur-af/goatcore/tree/main/terraform/modules/relay), [terraform/modules/bridge/](https://github.com/usareur-af/goatcore/tree/main/terraform/modules/bridge).

---

## 5. Operating system

### 5.1 Ubuntu LTS — boring, well-supported, mainstream

**Practice:** Ubuntu 24.04 LTS on x86, Ubuntu-for-Tegra 22.04 LTS on Orin. Standard apt for package management.

**Why:** LTS releases get five years of security updates. Boring distros have the largest operator pool and the deepest tooling ecosystem.

**Read more:** os-baseline-and-luks.md, [orin-os-decision.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/orin-os-decision.md).

### 5.2 systemd unit wrappers around Compose stacks

**Practice:** Docker Compose stacks are wrapped by systemd units so they start at boot, restart on failure, and log through journald with standard rotation.

**Why:** Standard Linux service-management discipline. Don't reinvent process supervision.

**Read more:** container-orchestration.md.

### 5.3 chrony for NTP

**Practice:** chrony as the per-host NTP client. Standard config, standard packages.

**Why:** chrony is the modern Linux default and the standard choice for NTP. (The multi-source strategy and the admit-audit gate are deltas — chrony itself is vanilla.)

**Read more:** [ntp-strategy.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/ntp-strategy.md).

---

## 6. Containers

### 6.1 Pinned container digests / SHAs — no `latest`

**Practice:** Every container reference pins a specific tag plus digest (or a SHA-tagged build). CI catches regressions to floating tags.

**Why:** Standard reproducibility discipline. `latest` is a recipe for "works on my machine."

**Read more:** [adr/0703-pinned-digests-and-pin-regression-ci.md](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0703-pinned-digests-and-pin-regression-ci.md).

### 6.2 Health checks and restart policies on every service

**Practice:** Compose `healthcheck` defined per service. `restart: unless-stopped` or stricter. Application-level `/health` endpoints for HTTP services.

**Why:** Standard container-ops discipline. Lets the orchestrator surface real failure rather than guessing from process exit codes.

**Read more:** hosting-services.md.

### 6.3 Drop unnecessary capabilities, no privileged containers

**Practice:** Containers run as the least-privileged user that works. `cap_drop: [ALL]` followed by narrow `cap_add` where needed. No `privileged: true` unless explicitly required and documented.

**Why:** Standard container-hardening posture. A compromised container's blast radius stays bounded.

**Read more:** os-supply-chain-security.md.

### 6.4 A memory ceiling on every container

**Practice:** Every compose service declares `deploy.resources.limits.memory`. Size it at four times the container's measured seven-day peak working set, floor 512M; a container with no measurement yet gets the floor and is re-sized once it has one. CI (`ops/ci/check-compose-memory-limits.sh`) refuses a service that declares a container and no ceiling; files that predate the rule sit in `ops/ci/compose-memory-limits.allow`, which only shrinks.

**Why:** A sweep of one management host found most containers running with no limit at all while the limits that did exist summed to more than physical RAM, so they were per-service guards applied unevenly, not a plan. An unbounded leak in any unlimited container would consume the host's free memory before any cgroup intervened, and take the identity plane with it. Four times peak is loose on purpose: the ceiling exists to bound the first failure, not to tune steady state, and a limit that kills a healthy container is worse than none.

**Read more:** [ops/ci/check-compose-memory-limits.sh](https://github.com/usareur-af/goatcore/blob/main/ops/ci/check-compose-memory-limits.sh) · [ADR 1168](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1168-self-hosted-paging-and-automatic-oncall-enrolment.md) (the sweep that found it).

---

## 7. Database

### 7.1 PostgreSQL 16 — current LTS-equivalent, no fork

**Practice:** Stock PG 16 from the upstream apt repo. Spock layers on top as an extension; we don't run a forked Postgres.

**Why:** Standard SQL, standard tooling, standard recovery procedures. Boring database = predictable behavior.

**Read more:** ha-multi-site.md, pg-spock-security.md.

### 7.2 WAL archiving via pgBackRest

**Practice:** Continuous WAL archiving plus scheduled full and differential backups via pgBackRest. The tool itself is standard; the per-site paired-stanza topology is the delta.

**Why:** WAL archiving lets us do PITR within the local repo. Standard PG backup hygiene.

**Read more:** [pgbackrest.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/pgbackrest.md).

### 7.3 Restore drills, not "we have backups"

**Practice:** pgBackRest restore is exercised against the smoke-test env (`pgbackrest-wave18`). The restore command path is the same in dev and prod.

**Why:** Untested backups are not backups.

**Read more:** pgbackrest-wave18-validation.md.

### 7.4 No ORM in our own Go code

**Practice:** Raw SQL via sqlx / pgx in services we author. SQL is checked in, reviewable, and visible in slow-query logs.

**Why:** ORMs hide the query plan. At our scale and complexity, the cost of debugging hidden behavior outweighs the convenience.

**Read more:** [adr/0413-no-orm-in-our-go-code.md](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0413-no-orm-in-our-go-code.md).

---

## 8. Observability

### 8.1 Prometheus + Alertmanager + standard exporters

**Practice:** Prometheus scrapes node_exporter, pg_exporter, chrony_exporter, and per-service custom metrics. Alertmanager routes to email, Matrix (`#policy-alerts:<site>...`), and the isitup status widget.

**Why:** Industry-standard metrics stack. Vast ecosystem of dashboards and alert rules to draw from.

**Read more:** [ops/monitoring/](https://github.com/usareur-af/goatcore/tree/main/ops/monitoring).

### 8.2 Structured logs to journald

**Practice:** Services log JSON or key=value to stdout, captured by journald via the systemd unit, rotated and queryable via journalctl.

**Why:** No custom logging stack needed for the volume we run. Querying by unit, host, time range, and JSON field is built in.

**Read more:** N/A (standard journald usage).

### 8.3 Status page + per-service health endpoints

**Practice:** Every service exposes `/health`. The isitup status page checks every 5 minutes and stores 30-day history. Auto-discovers services from the registry.

**Why:** Operators get one page that answers "what's broken right now?" without per-service knowledge.

**Read more:** ops/status/, hosting-services.md.

---

## 9. Identity & access

### 9.1 SSH keys, no passwords

**Practice:** SSH password auth disabled. Public-key auth only. Personal SSH keys live on user laptops, never on shared systems.

**Why:** Standard SSH hardening.

**Read more:** [terraform/modules/relay/](https://github.com/usareur-af/goatcore/tree/main/terraform/modules/relay) (sshd config).

### 9.2 GitHub 2FA required for org members

**Practice:** Two-factor auth enforced on GitHub org membership.

**Why:** Source-control hardening — a phished password is not enough to push to `main` even if branch protection is misconfigured.

**Read more:** GitHub org settings (operator-only).

### 9.3 Read-only by default; escalation requires intent

**Practice:** AWS access starts read-only. Write actions require explicit `aws-vault exec --no-session` invocation. Operators do not stay in write mode.

**Why:** Limits the blast radius of an absent-minded mistake.

**Read more:** CLAUDE.md §"AWS".

---

## 10. Defense in depth

### 10.1 LUKS at rest on every host that holds data

**Practice:** Full-disk encryption on all mgmt-hosts, x86 mini-PCs, and Orins. Key custody via TPM 2.0 (x86) or OP-TEE (Orin) where feasible.

**Why:** Standard data-at-rest protection. A stolen drive is useless without the unsealed key.

**Read more:** os-baseline-and-luks.md.

### 10.2 Fail-closed firewall posture

**Practice:** nftables default-deny on Router-A/B. Every allow is explicit and documented. (The five-tier cascade is a delta — the default-deny posture itself is standard.)

**Why:** Standard network-hardening. New services do not get egress by accident.

**Read more:** [egress-proxy.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/egress-proxy.md).

### 10.3 auditd + standard system auditing

**Practice:** auditd captures syscall-level audit events on every host. Logs ship to the integrity tier.

**Why:** Standard host-audit discipline. Provides the syscall trail when investigating an incident.

**Read more:** implementation-plan.md Block 18G.

### 10.4 Continuous vulnerability scanning

**Target practice:** Trivy and grype scan container images and host packages, with findings feeding the remediation queue. Currently, a non-blocking Trivy advisory workflow scans the checkout and a curated set of published images on relevant PRs, weekly, and on manual dispatch. It does not gate image builds or scan deployed hosts; grype and host config-drift scanning are not implemented. See ADR 0704 for current status and Block 18H for the broader target.

**Why:** Standard vuln-management discipline. The continuous-scan posture is standard; the open-source-EDR stack underneath is the delta.

**Read more:** implementation-plan.md Block 18H.

---

## 11. Operations

### 11.1 Runbooks for every load-bearing operator task

**Practice:** Every recurring task (peer enrollment, TAK setup, troubleshooting, deploy, backup restore, key rotation, DR) has a runbook in `docs/operations/`.

**Why:** New operators are not blocked on tribal knowledge. Standard ops-knowledge discipline.

**Read more:** [docs/operations/](../operations/).

### 11.2 Phase-gated rollouts with explicit gate criteria

**Practice:** Phases (1, 2, 2D, 3, etc.) have written gate criteria. Phase advancement requires the gate to be met — not "we feel ready."

**Why:** Forces honest assessment before scope expansion. Standard staged-rollout discipline.

**Read more:** project/roadmap.md, project/implementation-plan.md, [adr/0509-phase-2-gate-criteria.md](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0509-phase-2-gate-criteria.md).

### 11.3 Dev / prod parity

**Practice:** The dev cloud envs and the sovereign prod sites run the same containers, the same Ansible roles, and the same Terraform module patterns. The only difference is the inventory file.

**Why:** A fix validated in dev is a fix that ships to prod with no transformation. Standard continuous-delivery discipline.

**Read more:** collaborator-overview.md §"Dev / Prod Parity".

### 11.4 Cost discipline on cloud envs

**Practice:** Every cloud env has explicit teardown criteria. Non-prod resources are sized for the smallest box that exercises the test (e.g. t3.nano fleets for cgnat-validation).

**Why:** Unbounded envs become surprise bills.

**Read more:** cloud-env-lifecycle.md.

---

## 12. Engineering culture

### 12.1 Right tool for the job

**Practice:** Go for control-plane services and HTTP APIs. Python for Ansible + scripts + ad-hoc data work. TypeScript for browser SPAs and small UI work. Rust for new data-services / high-perf network work. Terraform + Ansible for infra.

**Why:** Match the tool to the workload, not to fashion. Polyglot stacks are fine when each language is doing what it's best at.

**Read more:** tech-strategy.md.

### 12.2 Boring tech where possible

**Practice:** Postgres, Compose, Ubuntu LTS, chrony, nftables, systemd, Traefik, Prometheus — boring, mainstream, well-understood. Exotic choices require a load-bearing reason and an ADR.

**Why:** Boring tech has the deepest tooling, the largest operator pool, and the longest survival horizon. Novelty has a tax — pay it only when the bespoke option is actually doing work.

**Read more:** tech-strategy.md.

### 12.3 "If it's not in git, it didn't happen"

**Practice:** No hand-edited config on a server. Every change goes through PR → Ansible / Terraform → re-run. The next reconciliation will overwrite anything edited by hand.

**Why:** Standard immutable-infra discipline. Hand-edits decay; git history doesn't.

**Read more:** onboarding/README.md §"The golden rule", onboarding/01-concepts.md.

---

## How this doc evolves

When we adopt a new standard practice that is load-bearing here, add an entry. When something we used to do drifts away from standard, either bring it back to standard (preferred) or move the entry to [deliberate-deltas.md](deliberate-deltas.md) and explain why the divergence is justified.

This doc is intentionally not exhaustive — it covers the load-bearing practices, not every habit. If a topic is in neither this doc nor [deliberate-deltas.md](deliberate-deltas.md), default behavior applies and the topic is not load-bearing for this project.

## Where to start reading

If you're new, read in this order:

1. collaborator-overview.md — architecture end-state and sovereignty split.
2. **[deliberate-deltas.md](deliberate-deltas.md) and this doc together** — what's bespoke, what's standard. Together they're the complete picture for a new collaborator.
3. architecture.md — detailed architecture, diagrams, phase plan.
4. [wireguard-netbird-primer.md](wireguard-netbird-primer.md) — what WG / Netbird actually do under the hood.
