# Cluster worker execution environment

> **Status: design (v1 — Option I worktrees adopted; Options II + III named).** Authoritative source for the substrate's worker-execution-environment design. Anchored at [ADR 0011](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0011-cluster-worker-execution-environment.md). Operational steps live in the runbook at [`../operations/cluster-worker-worktree-runbook.md`](../operations/cluster-worker-worktree-runbook.md).

## Conclusion

The substrate spawns captain + worker agents. Each worker needs an isolated working tree, its own branch, and the ability to open a real PR against `main` (or `cluster/<name>` for Pattern B). Today's substrate has none of those by default — the operator runs Claude Code in VS Code against a single checkout. Three options exist; **Option I (local git worktrees) is the v1 default, available always**. Option II (GitHub Actions runner) is the named scale-out path for when the laptop ceiling binds. Option III (long-running cloud execution sandbox) is the queued upgrade for persistent / overnight execution.

Worktrees stay the substrate's primitive even when III lands — the cloud sandbox uses worktrees inside its own checkout. The decision between I and III is "where does this worker run physically," not "do we still use worktrees."

## Problem

Multi-agent execution against a single git checkout breaks four substrate properties simultaneously:

1. **Pattern A track-direct-to-main** becomes single-threaded — every worker fights for `.git/HEAD`. Stated parallelism is fictional.
2. **Pattern B cluster-integration branch** is unusable — there's no second checkout to integrate into.
3. **PR-gated merges** ([ADR 0109](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md)) become advisory — workers commit straight to `main` because that's the only branch checked out. Block 66 readiness is wasted at runtime.
4. **AI PR review tooling** (Block 48H) has nothing to review — there are no worker PRs.

The substrate works on paper; nothing is testing the paper claims because nothing actually opens PRs.

## Three options

| Option | Where workers physically run | Branch isolation | Cost shape | Fit for v1 |
|---|---|---|---|---|
| **(I) Local git worktrees** | Same laptop as operator, separate filesystem dirs at `../worktrees/<track-name>/` | Per-worker branch in shared `.git/` | Disk + CPU/RAM during run; zero infra cost | ✅ **v1 adopted** |
| **(II) GitHub Actions runner** | Ephemeral container on GitHub-hosted or self-hosted runner | Per-worker branch in fresh checkout per run | Runner minutes + Anthropic API spend × workers; API-key custody overhead | Named; deferred to Phase-3 scale-out |
| **(III) Long-running cloud execution sandbox** | Dedicated VM / Codespace / agent-host with its own persistent checkout | Per-worker branch in remote checkout | VM ~$50-200/mo + API spend; persistent state ops | Queued; planned migration under Block 48M |

Decision criteria for each:

- **(I) v1** — works for clusters of up to ~3-4 concurrent workers per laptop (operator-machine-specific). Always-available. Validates substrate against real-PR shape.
- **(II)** — adopt when laptop ceiling binds AND the work isn't sensitive to overnight pauses (CI-job-shaped work). Skip-step to (III) if overnight pause matters.
- **(III)** — adopt when (a) operator-laptop-sleep-pauses-execution becomes intolerable, OR (b) Phase-3 push at 6-10 concurrent workers needs persistent state, OR (c) clusters genuinely need long-lived VM resources (build caches, model weights, etc.).

## Option I — local git worktrees (v1)

### Mechanics

Per-track worktree:

```bash
# Captain provisions worker's worktree
git worktree add ../worktrees/<cluster>/<track-name> -b track/<cluster>/<track-name>

# Worker session is spawned with cwd=../worktrees/<cluster>/<track-name>
# Worker commits to its own branch (track/<cluster>/<track-name>)

# Worker (or captain on worker's behalf) opens PR
cd ../worktrees/<cluster>/<track-name>
gh pr create --base main --head track/<cluster>/<track-name> --title "..." --body "..."

# After PR merge, captain removes worktree
git worktree remove ../worktrees/<cluster>/<track-name>
```

`../worktrees/` lives outside the main repo dir to keep `git status` clean in the operator's mainline checkout. Convention: `../worktrees/<cluster-name>/<track-name>/` so the cluster grouping is visible in `ls`.

### Pattern A vs Pattern B with worktrees

**Pattern A (track-direct-to-main)** is the default. Each worker's branch is `track/<cluster>/<track-name>`; PRs target `main`; merge-queue serializes.

**Pattern B (cluster-integration branch)** layers on top: captain creates `cluster/<name>` from `main` first; each worker branches from `cluster/<name>` instead of `main`; PRs target `cluster/<name>`; captain merges `cluster/<name>` to `main` once cluster milestone lands. Per [ADR 0008 (Backlog)](https://github.com/usareur-af/goatcore/blob/main/docs/adr/INDEX.md), Pattern B is the choice for clusters with >4 concurrent workers OR strong cross-track integration risk.

### Operator session vs worker sessions

The operator's interactive Claude Code session in VS Code stays on `main` (or whatever working branch the operator is on). **Workers run in `../worktrees/*` siblings** spawned via the Claude Code SDK or sub-agent invocation. The captain agent typically runs as a sub-agent within the operator's session, switching worktrees as needed via `cd` or per-tool `cwd` parameters; workers run in their own sub-agent sessions with sticky `cwd` to their assigned worktree.

The operator's mainline checkout is never blocked by worker activity. Worktrees share `.git/objects/` so disk usage is minimal; `.git/worktrees/<name>/HEAD` is per-worktree.

### Captain's responsibilities for worktree lifecycle

| Phase | Captain action |
|---|---|
| Track pickup | `git worktree add` for the track; record path in cluster status |
| Worker spawn | Spawn worker session with `cwd=<worktree>`; pass track name + role-prompt |
| Mid-flight integration | Cherry-pick / rebase / merge as needed; conflicts handled in worktree, not on `main` |
| PR open | Worker opens PR; captain reviews; CI gates apply |
| Track release | After PR merge, `git worktree remove` + `git worktree prune` |
| Cluster status rollup | `git worktree list` is part of `work cluster status <name>` output |

### Concurrency ceiling

~3-4 concurrent active workers per laptop is the soft ceiling. Operator-machine-specific. Beyond that ceiling, signals appear:

- Worktrees building / testing in parallel cause CPU thrashing.
- Memory pressure (each worker session = ~500MB-1GB).
- Operator's interactive session lags.
- Worktree `git status` slows (indexer contention).

When binding: upgrade to Option II or III. **The ceiling is not a substrate property** — Phase-3 substrate intent is 6-10 concurrent workers, which exceeds Option I's ceiling by definition. Block 48M (Option III migration) is the named landing pad.

### Shared-state hazards

Worktrees isolate git state but NOT non-git state. Concrete hazards:

- **Shared dev database** — two workers running migrations against the same `postgres-spock-test` fixture step on each other. Mitigation: worker-specific docker-compose project name (`COMPOSE_PROJECT_NAME=epic-wrath-pilot-schema`) per worktree.
- **Shared docker network names** — two `goat-relay-bench` envs collide. Mitigation: unique compose project names per worktree.
- **Shared cloud resources** — Terraform state file lock contention if two workers `terraform apply` against the same backend. Mitigation: per-worker terraform workspaces, OR substrate-touch discipline (per demogame-epic-wrath kickoff §2) keeps workers off `terraform/` by default.
- **Shared local ports** — two workers trying to bind `:8080`. Mitigation: per-worker port assignment via env var.

The kickoff memo §7 cluster-specific operational rules carry the per-cluster shared-state hazard inventory; captains check before spawning concurrent workers.

### PR-gate enforcement during pilots

The 48D pilot (and every subsequent pilot) MUST run with branch protection enabled on `main` for the duration of the pilot. Per [ADR 0109](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md), branch protection is gated on the >3-active-contributor threshold; running a pilot with 1 captain + 3 workers + operator = 5 active contributors trivially trips that threshold for the pilot's duration.

Block 66 readiness script reports GREEN (39/0); the operator just hasn't flipped the toggle. Pilot fire is the explicit trigger to flip it on. Post-pilot, branch protection stays on (the substrate keeps tripping the threshold whenever any cluster is active).

## Option II — GitHub Actions runner (deferred scale-out)

Named for completeness; full design deferred to its own decision moment.

Shape:

- Captain triggers a `workflow_dispatch` workflow per worker with input parameters (track name, role-prompt, scope).
- Workflow runs Claude Code SDK against an Anthropic API key stored in repo secrets (or fetched from a self-hosted-runner-side secret manager).
- Worker session executes inside the runner; commits to a feature branch; opens PR via `gh pr create` (runner has GitHub token by construction).
- After PR merge, branch is deleted; runner is ephemeral, no cleanup needed.

Adopt-trigger:

- Operator observes laptop ceiling binding (per Option I "Concurrency ceiling" signals).
- Phase-3 push exceeds Option I capacity but operator-laptop-sleep-pause is acceptable for the work-class.
- AI-review-tooling work (Block 48H) wants to run agents on PR-open events from the same runner substrate.

Skip-trigger (go straight to III):

- Workers need persistent state across runs (build caches measured in tens of GB, model weights, downloaded datasets).
- Overnight execution matters (operator wants to fire 10 cluster-pilots on Friday afternoon and read results Monday).
- Anthropic API key custody risk in CI is unacceptable for the operator's threat model.

Defer-cost: relatively low (worktrees keep working in the meantime). Not gating for the 48D pilot.

## Option III — long-running cloud execution sandbox (queued)

Queued under Block 48M. Full design lands when the trigger conditions fire.

Sketch shape (subject to refinement at design time):

- Dedicated VM (or Codespace, or AWS-managed agent-runner — substrate-choice deferred to design).
- Persistent checkout at `/home/runner/repo/`; worktrees provisioned inside the VM exactly as Option I, just remote.
- Captain runs in the VM (likely as a long-running tmux / systemd-managed process) and spawns workers locally inside the VM.
- Operator's role becomes "remotely tail captain status + approve at decision points" rather than "host the captain on the laptop."
- Cleanup discipline: VM is reset / nuked at cluster milestone landing; persistent state bound to substrate-essential dirs only (build caches, model weights — explicitly NOT working-tree state, which lives in git).

Adopt-trigger (any one):

- Operator-laptop-sleep-pauses-execution becomes intolerable for ≥1 cluster (e.g., a 30-day soak tightly coupled to multi-agent work).
- Phase-3 push at 6-10 concurrent workers needs persistent state.
- Sovereignty / IAM separation between operator-laptop-credentials and substrate-execution-credentials becomes load-bearing (e.g., the operator no longer wants to host long-running Anthropic API calls on the personal laptop).

Cost shape sketch: VM ~$50-200/mo (depending on shape) + Anthropic API spend (same as Option II) + minor Terraform/Ansible to provision and tear down. Sovereign single-VPS is the cheapest landing; Codespace is faster to spin up but has cost-control risk.

Block 48M tracks this as a named-but-not-active sub-block under Block 48; design lands when triggered.

## Composition with substrate ADRs

| Concern | Source |
|---|---|
| Captain ↔ worker hierarchy | [ADR 0007](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0007-multi-agent-orchestration-hierarchy.md) |
| Concurrency governance + track lifecycle | [ADR 0006](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0006-multi-agent-human-concurrency-governance.md) |
| Branching pattern (A track-direct vs B integration-branch) | [ADR 0008 (Backlog)](https://github.com/usareur-af/goatcore/blob/main/docs/adr/INDEX.md) |
| PR-gated trunk-based development | [ADR 0109](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md) |
| Worker discipline mechanisms (six rules + net-positive) | ADR 0009 |
| Boundary classification + escalation | [ADR 0010](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0010-boundary-classification-escalation-and-medium.md) |
| **Worker execution environment (this doc + ADR 0011)** | New |

This decision is independent of the others — Option I works regardless of Pattern A vs B, regardless of worker-discipline mechanism choices, regardless of escalation routing. It's the *physical-execution-substrate* layer.

## Open questions

1. **`work` CLI automation of worktree provisioning?** Today the captain runs `git worktree add` manually. A `work track pickup --worktree` or `work cluster spawn-worker --track <name>` flag could automate. Defer to Block 48L follow-on; mechanical convention land first.
2. **Shared dev-database orchestration.** Per-worker docker-compose project name is the v1 convention; long-term we may want a substrate-managed fixture allocator. Not load-bearing for the pilot.
3. **Terraform state isolation.** v1 default = workers don't touch terraform; if a future cluster genuinely needs Terraform, we add per-worker workspaces. Not load-bearing today.
4. **Devcontainer per worker?** Considered; deferred. Useful if worker toolchains diverge from main; not the case for demogame-epic-wrath pilot.

## Companion artifacts

| Artifact | Path |
|---|---|
| Anchoring ADR | [`../adr/0011-cluster-worker-execution-environment.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0011-cluster-worker-execution-environment.md) |
| Operator runbook (worktree provisioning + lifecycle + cleanup) | [`../operations/cluster-worker-worktree-runbook.md`](../operations/cluster-worker-worktree-runbook.md) |
| Substrate design doc (parent) | [`./multi-agent-team-management.md`](multi-agent-team-management.md) |
| Implementation tracking | `../project/implementation-plan.md` Block 48L (Option I worktrees) + Block 48M (Option III cloud sandbox, queued) |
| Pilot kickoff memo (first cluster to use this) | `../project/cluster-kickoffs/demogame-epic-wrath.md` §9 pre-flight gate |
| Substrate ADRs | [`../adr/0006-multi-agent-human-concurrency-governance.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0006-multi-agent-human-concurrency-governance.md), [`../adr/0007-multi-agent-orchestration-hierarchy.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0007-multi-agent-orchestration-hierarchy.md), [`../adr/INDEX.md` ADR 0008 (Backlog)](https://github.com/usareur-af/goatcore/blob/main/docs/adr/INDEX.md), [`../adr/0109-git-collaboration-trunk-based.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md) |
| PR governance preparedness | [`./pr-governance.md`](pr-governance.md) (Block 66) |
