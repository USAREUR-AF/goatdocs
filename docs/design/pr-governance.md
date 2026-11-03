# PR Governance — synthesis layer

| Field | Value |
|---|---|
| Status | Accepted (2026-05-05 — implementation under Block 66) |
| ADR anchors | [ADR 0109](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md) trunk-based · [ADR 1014](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1014-codex-pattern-adr-to-enforced-lint.md) codex pattern · [ADR 1015](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1015-code-review-discipline.md) code-review discipline |
| Companion docs | [`docs/design/code-review-process.md`](code-review-process.md) · [`docs/process/block-completion-checklist.md`](https://github.com/usareur-af/goatcore/blob/main/docs/process/block-completion-checklist.md) · [`docs/operations/branch-protection-rules.md`](../operations/branch-protection-rules.md) · [`docs/operations/tier-3-install-runbook.md`](../operations/tier-3-install-runbook.md) |
| Composes with | [ADR 1006](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1006-phase-gates.md) phase gates · [ADR 1008](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1008-soak-testing-discipline.md) soak · [ADR 1012](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1012-load-testing-discipline.md) load · [ADR 1013](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1013-continuous-architectural-chaos.md) chaos · [ADR 0006](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0006-multi-agent-human-concurrency-governance.md) work tracker · [ADR 1011](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1011-findings-register.md) findings register |

## TL;DR (for a layperson)

Pull-request governance — what gets checked when a contributor (human or
agent) opens a PR — is the daily-mechanics layer where every other
discipline (test, review, supply chain, work tracking) hits the wall.
This document synthesizes the design across three ADRs into one picture
so a new contributor reads one doc instead of reverse-engineering three.

The picture: **five tiers of CI gates run at PR open**, each tier
catching a different class of problem. Tier A (always-fast) catches
typos, lint errors, missing signed commits. Tier B (per-module tests)
catches code-level regressions. Tier C (heavier — soak / load / chaos)
catches what only shows up under sustained load. Tier D (supply chain)
catches malicious or accidental tamper of shipped binaries. Tier E
(block-completion review) catches the human-judgment things — does this
PR's tests fit the change-shape, are the docs in sync with the code.

The five tiers are designed so most PRs hit only A + B + the relevant
parts of E. Tier C runs on demand or scheduled crons, not every PR.
Tier D runs at release tagging, not every PR. Tier E is structurally
unavoidable but takes ~10 minutes per Block.

## TL;DR (for a sponsor)

PR governance is the engineering discipline that makes the codebase
auditable. Every change has a written description tied to an
implementation Block, every change runs through a multi-tier automated
test set before it can merge, and every Block of work gets a
human-readable review file before it's released. The cost is small (a
few minutes per PR for the author; a 10-minute review per Block).
The benefit is that any external assessor — government accreditation,
security audit, vendor due diligence — can pick up the repo cold and
trace what was changed, why, by whom, with what evidence.

## TL;DR (for SCA-R)

PR governance is anchored in three ADRs:

- [ADR 0109](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md) — trunk-based collaboration: signed commits, DCO sign-off, Conventional Commits, branch protection, merge queue at >3 active contributors.
- [ADR 1014](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1014-codex-pattern-adr-to-enforced-lint.md) — Codex pattern: each ADR with a mechanically-checkable decision declares its CI enforcement.
- [ADR 1015](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1015-code-review-discipline.md) — Code-review discipline: three-tier scaffold (author self-review / cross-review / PR review) on a single shared checklist.

Implementation is staged across Blocks 50/63C/66/40. **Block 66 (this design doc's home) covers per-module CI workflow gap closure + PR contract artifacts + branch-protection rules runbook + pre-flight readiness check.** Block 63C ships the Codex retrofit. Block 40 ships supply-chain signing. Block 50 was the per-component test fitness work.

## §1 The five-tier CI test pyramid

Every PR runs through tiers A and B. Tiers C, D, E run on a schedule that depends on the change.

### Tier A — Always-run, fast (~3-5 min budget per PR)

Static checks + commit-hygiene gates. A PR that fails any Tier-A gate cannot proceed to Tier B.

| Gate | Purpose | Workflow |
|---|---|---|
| `make lint-shell` (shellcheck) | Bash regressions | [`ci.yml`](https://github.com/usareur-af/goatcore/blob/main/.github/workflows/ci.yml) |
| `make lint-yaml` (yamllint) | YAML config + cloud-init | [`ci.yml`](https://github.com/usareur-af/goatcore/blob/main/.github/workflows/ci.yml) |
| Compose-file lint | docker-compose semantic check | [`compose-lint.yml`](https://github.com/usareur-af/goatcore/blob/main/.github/workflows/compose-lint.yml) |
| DCO sign-off | every commit signed-off | `pr-hygiene.yml` |
| Conventional Commits PR title | machine-parseable PR title | `pr-hygiene.yml` |
| Signed commits (GPG) | author authenticity | branch protection per ADR 0109 |
| `[track:]` trailer check | commit ↔ active-work-tracker linkage | `ops/work/git-hooks/pre-commit` (warn-not-block today; block once Block 66 lands) |

Promised at Tier-3 install (per ADR 1014 + Block 63C):

| Gate | Promised mechanism |
|---|---|
| Strict `golangci-lint` (Block 50A.3) | per-Go-module |
| `gitleaks` secrets scan | new workflow per Block 63C.2 |
| `goleak.VerifyTestMain` presence per package | custom `golangci-lint` rule per Block 63C.2 |
| `http.Server` timeouts presence in handler files | `ops/ci/check-http-timeouts.sh` per Block 63C.2 |
| `no-ORM` rule (ADR 0413) | custom `golangci-lint` rule per Block 63C.2 |
| Schema-declaration mandatory ([ADR 0512](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0512-rapid-adaptation-with-ai.md)) | schema-enforcer CI dry-run per Block 63C.2 |
| F-NNN INDEX row-count = file-count | `ops/ci/check-findings-index.sh` |
| M-NNN INDEX coverage | analogue script |
| `cargo clippy` strict | per Rust crate |
| `cargo audit` | Rust dep vulnerability scan |

### Tier B — Per-module unit + integration tests, path-triggered

Each load-bearing module owns a workflow that runs on PRs touching its paths. The workflow runs `go test ./... -race -count=1` (or `cargo test --release` for Rust crates) plus module-specific extras (testcontainers integration tests gated by `-tags=integration`, fuzz smoke, conformance fixtures).

#### Module → workflow contract (Block 66 closes the gaps marked **NEW**)

| Module | Workflow | Status |
|---|---|---|
| `signal-server` | [`signal-server.yml`](https://github.com/usareur-af/goatcore/blob/main/.github/workflows/signal-server.yml) | Wired |
| `mgmt-host-bootstrap` | [`mgmt-host-bootstrap.yml`](https://github.com/usareur-af/goatcore/blob/main/.github/workflows/mgmt-host-bootstrap.yml) | Wired (testcontainers) |
| `time-hygiene` | [`time-hygiene.yml`](https://github.com/usareur-af/goatcore/blob/main/.github/workflows/time-hygiene.yml) | Wired |
| `goat-relay-protocol` | [`goat-relay-protocol.yml`](https://github.com/usareur-af/goatcore/blob/main/.github/workflows/goat-relay-protocol.yml) | Wired (conformance + fuzz) |
| `netbird-mgmt` | [`netbird-mgmt.yml`](https://github.com/usareur-af/goatcore/blob/main/.github/workflows/netbird-mgmt.yml) | Wired |
| `postgres-spock` | [`postgres-spock.yml`](https://github.com/usareur-af/goatcore/blob/main/.github/workflows/postgres-spock.yml) | Wired |
| `ory-soak` | `ory-soak-smoke.yml` | Wired |
| `inchworm` | `inchworm-test.yml` | Wired |
| **`snitch`** | **[`snitch.yml`](https://github.com/usareur-af/goatcore/blob/main/.github/workflows/snitch.yml)** | **NEW (Block 66A.1)** |
| **`gatewatch`** | **`gatewatch.yml`** | **NEW (Block 66A.2)** |
| **`admit-audit`** | **`admit-audit.yml`** | **NEW (Block 66A.3)** |
| **`enrollment`** | **[`enrollment.yml`](https://github.com/usareur-af/goatcore/blob/main/.github/workflows/enrollment.yml)** | **NEW (Block 66A.4)** |
| **`id-console`** | **[`goat-id-console.yml`](https://github.com/usareur-af/goatcore/blob/main/.github/workflows/goat-id-console.yml)** | **NEW (GH #191)** |
| `goat-relay` (Rust binary) | (deferred per Block 66A.5) | Plan-row only |
| `zenoh-plugins/audit-logger` | (deferred per Block 66A.6) | Plan-row only |

Per-module workflow contract (every module workflow MUST):

1. Run `go test ./... -race -count=1` (or `cargo test --release`) on every PR touching the module's paths.
2. Run the strict `golangci-lint` (Block 50A.3) or `cargo clippy -- -D warnings`.
3. Verify `goleak.VerifyTestMain` presence in every package that has tests.
4. Run integration tests when `-tags=integration` paths are touched (or testcontainers paths).
5. Cache the toolchain across runs (Go 1.25 / Rust 1.x / docker layers).
6. Pin third-party action versions by SHA (supply chain hygiene per ADR 0110/0111).

### Tier C — Heavier gates (pre-merge, not per-commit)

Per ADRs 1008 (soak) / 1012 (load) / 1013 (chaos) / 1006 (phase gates):

| Class | When | Status today | Owner Block |
|---|---|---|---|
| **Soak smoke (5 min)** | per-PR for stateful components on image-pin bumps | ory-soak-smoke wired; Spock-related ones ad-hoc | Block 66E (deferred) extends to Spock / signal-server / netbird-mgmt |
| **Soak validation (2 h)** | pre-promotion to a phase | manual today; codified per ADR 1008 | — |
| **Soak canonical (72 h)** | Phase-gate stateful components | manual; Wave 3 §3.1 shape | — |
| **Load smoke** | per-PR for performance-critical paths | scaffolded for goat-relay; per-PR not wired | Future Block — wires criterion regression smoke |
| **Load full** | pre-prod for any load-bearing component | manual; ADR 1012 "no measured ceiling = no production-ready claim" | — |
| **Continuous architectural chaos** | post-merge, not per-PR | designed; not yet built | Block 38 |
| **Combined-failure matrix** | pre-Phase-cutover | manual; named scenarios C3-01..C3-08 | Block 55 |
| **Scale validation (Floor/Target/Stretch)** | gating for Phase-3 cutover | scaffold; CGNAT validation env pattern | Block 54 |
| **Red Team adversarial** | quarterly | manual program | Block 55 (b) |

### Tier D — Supply chain + signing

Per Block 40 (security ascent — reproducible builds + SLSA L4 + Rekor + cosign), Block 50B.5 (cosign), Block 13C (Chainguard-first), Block 18H (Trivy + grype):

| Gate | When | Status | Owner Block |
|---|---|---|---|
| Cosign-signed binaries | every release tag | pending | Block 50B.5 + Block 40 |
| SLSA L4 attestation | every release | deferred | Block 40 |
| Binary transparency log (Rekor) | every release | deferred | Block 40 |
| SBOM generation + sign | every release | partial via image build | Block 40 |
| Trivy advisory scan | Relevant PRs, weekly, or manual dispatch | Implemented; non-blocking scan of checkout + curated published images. Does not scan each image build. | Trivy advisory workflow |
| Trivy / grype build gates | per-image-build | Planned; built images are not gated, and grype is not wired into CI. | Block 18H |
| License audit (CI-as-service) | weekly cron + per-PR | spec'd; not built | License-audit follow-on |

### Tier E — Block-completion review (ADR 1015)

| Sub-tier | When | Mechanism |
|---|---|---|
| Tier 1 self-review | before `work release` | `docs/project/block-<name>-completion-review.md` committed; `work release` warns if missing |
| Tier 2 cross-review | after Tier 1, before promotion | independent reviewer writes `block-<name>-cross-review.md`; ships on availability |
| Tier 3 PR review | at PR open | PR description = Tier-1 fields; approving review = Tier-2 fields; CODEOWNERS routing; merge queue at >3 contributors |

When Tier 3 (PR review) installs, the existing checklist becomes the **PR description template** (author self-fills) + the **PR review template** (reviewer fills). The mechanical rows of the checklist (closeout-status sweep, F-NNN/M-NNN INDEX consistency, commit hygiene) graduate to CI gates per Tier A above.

## §2 Branch-protection readiness criteria

Before flipping branch protection on for a repo, all of these MUST be true:

1. Every load-bearing module has a Tier-B workflow that runs on PRs touching its paths (Block 66A closes today's gap).
2. The required-status-checks list is finalized — at minimum the Tier-A gates (lint/DCO/PR-title/signed-commits) plus all Tier-B per-module workflows that apply to the changed paths.
3. The PR template (`.github/PULL_REQUEST_TEMPLATE.md`) is in place and aligned with ADR 1015 Tier-1 review fields (Block 66B.1).
4. CODEOWNERS routing is in place and assigns at least one reviewer for security-sensitive paths (Block 66B.2).
5. The branch-protection rules runbook is written and verifies cleanly on a dry-run (Block 66B.3).
6. The pre-flight readiness script (`ops/ci/branch-protection-readiness.sh`, Block 66C.1) reports green.
7. At least one Block has been completed under the new ADR 1015 discipline with a Tier-1 review file committed (currently: Block 50E retrospective + Block 50FG self-review + this Block's review).

## §3 Per-PR contract from the contributor's perspective

When a contributor (human or agent) opens a PR, this is what happens:

1. **At PR open** — GitHub renders the PR description from `.github/PULL_REQUEST_TEMPLATE.md`. The contributor fills in the Tier-1 review fields: closeout-status sweep, functional-vs-edge-case classification, test coverage per category, drift-sweep evidence, known-gap filings, commit-hygiene self-attestation. They link to their committed `docs/project/block-<name>-completion-review.md`.
2. **Tier A gates fire immediately.** Lint, DCO, PR title, signed commits, secrets scan, INDEX-consistency checks. ~3-5 min budget.
3. **Tier B gates fire on path triggers.** Per-module workflows for any module whose paths are in the diff. ~5-15 min budget per module.
4. **Tier C gates run on demand.** A label like `run-soak` or `run-load` triggers the relevant workflow. Most PRs don't need them.
5. **Tier D gates run at release tag, not PR.** Cosign, SLSA, Rekor wire to the release flow.
6. **Tier E review** — the PR description is the Tier-1 review file's content. CODEOWNERS auto-requests reviewers from the security-sensitive-path list. Required reviewers approve. Merge queue (if active) batches PRs.
7. **Merge.** Squash-and-merge per ADR 0109; signed merge commit; conventional title; new commit lands on main with `[track:]` trailer preserved.
8. **Post-merge** — Tier C scheduled crons (continuous architectural chaos, license audit) eventually exercise the new code in their windows.

## §4 What an agent contributor adds to the picture

For an agent (vs human) contributor, two extra invariants apply:

- **Active-work tracker pickup is mandatory** before code changes start (per ADR 0006). An agent that skips `work pickup` and starts editing files immediately is a discipline violation.
- **Path-form commit discipline** — the concurrent-staging race observed in Block 50E (`bf199f3`, `cccb67b`) bit because `git add` + `git commit` captured whatever else was in the index when another agent staged concurrently. Use `git commit <path>` form instead, or `git add <new-files-only>` followed by `git commit <all-paths>` for new + modified files. The block-completion checklist Section D Row 12 codifies this.

When Tier 3 lands and PRs replace direct-to-main pushes, both invariants stay — they apply at the commit level, not the merge level.

## §5 Coordination with existing Blocks

Block 66 does not absorb the work in adjacent Blocks. It coordinates:

- **Block 63C Codex retrofit** — adds the five mechanical rules to CI. Block 66 lands the per-module workflows where those rules execute.
- **Block 40 Security-ascent (cosign + SLSA L4 + Rekor)** — wires Tier D supply-chain signing into the release flow. Block 66 doesn't ship Tier D itself.
- **Block 50F.4 Broader shellcheck coverage** — extends shellcheck across `ops/**/*.sh`. Block 66 ensures `make lint-shell` runs in CI; coverage extension is its own block.
- **Block 50F.5 install.sh end-to-end integration test** — needs docker-in-docker substrate. Block 66 covers everything else for snitch's CI surface; this gap waits.

## §6 Open questions

- **Merge-queue trigger.** ADR 0109 says merge queue activates at >3 active contributors per repo. Block 66 doesn't pre-install merge queue — it ships when the trigger fires. Open: who decides "3 active contributors" — operator, automation, or implicit per-repo activity threshold?
- ~~**CODEOWNERS expansion timing.** The Block 66B.2 scaffold uses `@goat-maintainer` placeholders. Expansion to specific people/roles requires the human-actions register entries to be filled. Do we block branching adoption on full expansion, or accept "scaffold + expand-as-needed"?~~ **CLOSED 2026-08-19** ([ADR 0109](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md) amendment). Expand-as-needed lost: the scaffold left 874 of 7,640 tracked files (11.4%) approvable by exactly one person, and because GitHub forbids self-approval, those paths were unmergeable whenever that person was the author — the gate was satisfiable only by admin bypass. Expansion routes to five role teams (maintainers / platform / software / product / data) rather than to named accounts, so the file states the role and org team membership states the people.
- **Cross-repo PR coordination.** A change spanning goat + goat-bond + future siblings needs sequenced merges. ADR 0109 §"Cross-repo coordination" addresses this; Block 66 doesn't add new tooling. Open: do we want a `gh-pr-link` helper for the multi-repo case, or accept manual coordination at today's scale?
