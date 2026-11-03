# CI discipline

| Field | Value |
|---|---|
| Status | Rules in force 2026-10-27; enforced by `ops/ci/check-workflow-discipline.py` (a `repo-guards` step) |
| Related | [ci-redundant-rebuild-guard](https://github.com/usareur-af/goatcore/blob/main/docs/design/ci-redundant-rebuild-guard.md) (image builds), [pr-governance](pr-governance.md) (gate tiers), [ADR 0109](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md) |

The repo runs about a thousand Actions jobs a day on a private plan where
every job is billed by the minute, rounded up. The cost of a check is the
runner start, not the script; a check that takes four seconds costs the same
minute as one that takes fifty. These rules keep the fleet of workflows
small, fast and quiet, and the lint keeps them true after the next hundred
pull requests.

## Rules

| # | Rule | Why | Enforced |
|---|---|---|---|
| R1 | Every job declares `timeout-minutes` | a hung job holds a runner for six hours | lint |
| R2 | Every pull_request / push workflow declares a `concurrency` group; PR groups cancel in progress, `main` never cancels | a superseded push is cancelled, not finished; the merge-commit run is the one recorded | lint (presence) |
| R3 | No schedule fires more than once an hour | a cron is a poll; a poll under an hour is a webhook that was never wired | lint |
| R4 | A pull_request workflow with no `paths:` filter is listed in `ops/ci/unfiltered-pr-workflows.txt` with its reason | the list is the complete set of "runs on every PR" and shrinks on purpose | lint |
| R5 | A guard is one checkout plus a script: it goes in `repo-guards.yml` (tree facts) or `pr-hygiene.yml` (PR facts), never its own workflow | the runner start is the cost; one job reports every guard, and a failure names the step | review |
| R6 | A guard does not run on `push` to `main`; a publisher (image, release, tag) does | a squash merge puts the reviewed diff on main unchanged | review |
| R7 | A workflow that builds or tests one component is path-filtered to that component and its workflow file | an unrelated PR does not pay for a build it cannot have broken | review |
| R8 | Scanning that GitHub manages (CodeQL) runs from a workflow in this repo, path-filtered, analysing only the languages and Go modules the push touched | a managed scan has no path filter and rebuilds 27 Go modules on a three-file PR | review |

What does **not** belong in a fold (R5): anything with a service container, a
matrix, a secret, or a build. Those need their own runner. `fleet-pins.yml`
runs a `cargo test` and `gym-registry.yml` renders four sites, so both stay
separate although both are unfiltered.

## What runs on every pull request

Eight workflows, listed in `ops/ci/unfiltered-pr-workflows.txt`. Everything
else starts only when its paths change. The two fold targets:

- `pr-hygiene.yml`, one job: base is `main`, Conventional Commits title, DCO
  on every commit, `[track:]` trailer on a `track/*` branch, no per-worktree
  artifact in the diff, staleness warning, advisory scope report.
- `repo-guards.yml`, one job: about seventy whole-tree scripts, including the
  Default-All->All scan (ADR 1185), environment and terraform coverage, ghcr
  namespace parity (ADR 1195), and the diff-scoped netbird users-table guard.

## Cadence of the scheduled workflows

| Workflow | Cadence | Reason |
|---|---|---|
| issue-track-pickup | hourly | HQ board moves have no webhook into this repo; issue events trigger it directly |
| ci-coverage-audit, warrant-expiry, relay-fleet-health, wg-cp0-mesh-reach | daily | audits of a day's changes |
| mgmt-host-bootstrap, snitch, ory-soak-smoke, rust-audit, trivy-advisory, netbird-dashboard-e2e | weekly | slow, no PR drives them |

## Folds

| Date | Into | From | Runs removed per PR sync |
|---|---|---|---|
| 2026-08-17 | repo-guards | 17 single-script workflows | 16 |
| 2026-09-08 | repo-guards | 14 more (track guard-cull) | 14 |
| 2026-10-27 | pr-hygiene | refuse-non-main-base, pr-title, dco, drift-check, pr-scope | 4 |
| 2026-10-27 | repo-guards | no-default-allow, env-coverage, registry-parity, netbird-user-sql | 4 |

## Adding a check

1. A tree fact: a step in `repo-guards.yml`. A PR fact: a step in
   `pr-hygiene.yml`. Name the step after the rule, not the script.
2. A build or test of one component: its own workflow, `paths:` to the
   component and the workflow file, `concurrency` with
   `cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}`,
   `timeout-minutes` on every job, `pull_request` only unless it publishes.
3. A schedule: hourly at most, and say in the file what is being polled and
   why no event covers it.
4. Run `python3 ops/ci/check-workflow-discipline.py` before pushing; it is
   what CI runs.
