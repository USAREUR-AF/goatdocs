# Cluster worker worktree runbook (Option I substrate)

> **Purpose.** Operator-facing steps for spinning up + tearing down git worktrees that host cluster captain + worker agent execution. Authoritative design at [`../design/cluster-worker-execution-environment.md`](../design/cluster-worker-execution-environment.md). Anchored at [ADR 0011](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0011-cluster-worker-execution-environment.md).
>
> **When this runbook applies.** Any time a captain agent spawns workers and they need real PR isolation. Default substrate for clusters of up to ~3-4 concurrent workers. Beyond that, see [ADR 0011](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0011-cluster-worker-execution-environment.md) Trigger conditions for Option II / III.

## Pre-flight

Verify state before provisioning worktrees:

```bash
# 1. From mainline checkout — verify no uncommitted state on main
git status -s

# 2. Verify branch protection state (Block 66 readiness)
ops/ci/branch-protection-readiness.sh   # should report GREEN

# 3. Verify worktree dir doesn't already have stale entries
git worktree list
ls ../worktrees 2>/dev/null || echo "(no worktrees dir yet — fresh start)"

# 4. Verify gh CLI authenticated
gh auth status
```

Branch protection on `main` should be **enabled** for the pilot's duration per [ADR 0109](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md). If readiness reports GREEN but protection isn't flipped, follow the [Tier-3 install runbook](tier-3-install-runbook.md) before provisioning workers.

## Captain provisions a worker's worktree

For each track the captain assigns:

```bash
# Variables (captain fills per track)
CLUSTER=demogame-epic-wrath
TRACK=epic-wrath-pilot-schema   # or epic-wrath-pilot-research / epic-wrath-pilot-contracts / etc.

# Provision worktree
mkdir -p ../worktrees/${CLUSTER}
git worktree add ../worktrees/${CLUSTER}/${TRACK} -b track/${CLUSTER}/${TRACK}

# Verify
git worktree list | grep ${TRACK}
cd ../worktrees/${CLUSTER}/${TRACK} && git status && cd -
```

Cluster grouping (`../worktrees/<cluster>/<track>/`) keeps `ls` legible when multiple clusters run concurrently.

**Pattern B (cluster-integration branch) variant:** if the cluster uses Pattern B per [ADR 0008 (Backlog)](https://github.com/usareur-af/goatcore/blob/main/docs/adr/INDEX.md), the captain creates the integration branch first:

```bash
git checkout main && git pull
git checkout -b cluster/${CLUSTER}
git push -u origin cluster/${CLUSTER}

# Then per-worker worktrees branch from cluster/<name>:
git worktree add ../worktrees/${CLUSTER}/${TRACK} -b track/${CLUSTER}/${TRACK} cluster/${CLUSTER}
```

## Captain spawns a worker session in the worktree

The worker is a Claude Code SDK session (or sub-agent invocation) with `cwd` set to the worktree path. The captain typically passes:

- `cwd`: the worktree path (`../worktrees/<cluster>/<track>/`)
- Role-prompt file: `ops/work/roles/<role>.md` (researcher / planner / implementer / reviewer / integrator)
- Track scope: copied from the cluster kickoff memo §5 worker-spawn-plan
- Track name: for `[track:]` trailer injection on commits

The worker session does its work entirely within the worktree dir. It commits to its own branch (`track/<cluster>/<track>`), runs tests there, opens its PR there.

**Per-worker docker-compose isolation** (if the worker uses any compose-based fixture):

```bash
# In the worker's worktree
export COMPOSE_PROJECT_NAME=${TRACK}
docker compose up -d
# ... worker work ...
docker compose down
```

Project name is the load-bearing isolation primitive — without it, two workers running compose-based fixtures collide.

**Per-worker port assignments** (if multiple workers bind local ports):

```bash
# Convention: each track's PORT_BASE allocated by captain at spawn time
export PORT_BASE=18000   # captain assigns per-track non-overlapping range
```

## Worker opens a PR

After the worker has committed its deliverables on its branch:

```bash
# In the worktree
cd ../worktrees/${CLUSTER}/${TRACK}

# Push branch
git push -u origin track/${CLUSTER}/${TRACK}

# Open PR
gh pr create \
  --base main \
  --head track/${CLUSTER}/${TRACK} \
  --title "feat(${CLUSTER}): ${TRACK} — <summary>" \
  --body "$(cat <<'EOF'
## Summary
<1-3 bullets>

## Test plan
<bulleted markdown checklist>

## Cluster context
- Cluster: demogame-epic-wrath (48D pilot)
- Kickoff memo: docs/project/cluster-kickoffs/demogame-epic-wrath.md
- Track: ${TRACK}
EOF
)"
```

For Pattern B variant, `--base cluster/${CLUSTER}` instead of `--base main`.

## Captain integrates + cleans up

After the PR merges (via merge queue if enabled, otherwise direct merge):

```bash
# From mainline checkout
git fetch && git checkout main && git pull

# Remove the worktree
git worktree remove ../worktrees/${CLUSTER}/${TRACK}

# Verify
git worktree list   # track's row should be gone
```

If the worktree has uncommitted state and you intentionally want to discard it:

```bash
git worktree remove --force ../worktrees/${CLUSTER}/${TRACK}
```

(Don't `--force` reflexively — uncommitted state is a signal the worker isn't done yet. Verify with the captain.)

## Cluster status rollup includes worktree state

`work cluster status <name>` should reflect:

- Active tracks (one per worktree)
- Stale worktrees (worktree exists but its branch is merged + deleted upstream)
- Disk usage for `../worktrees/<cluster>/`

Manual equivalent until automated:

```bash
git worktree list
git worktree prune --verbose   # removes stale .git/worktrees/* entries
du -sh ../worktrees/${CLUSTER}/
```

`git worktree prune` is safe — it only removes git's internal record of worktrees that have been deleted from the filesystem. The branches themselves are not touched.

## Cleanup at cluster release

When the captain releases the cluster:

```bash
# Remove all worktrees for the cluster
for dir in ../worktrees/${CLUSTER}/*/; do
  git worktree remove "${dir}"
done

# Optionally remove the cluster's worktree dir
rmdir ../worktrees/${CLUSTER}

# Prune any stale entries
git worktree prune --verbose
```

Branches for merged tracks are typically auto-deleted by the merge queue (or manually via `git push origin --delete track/<cluster>/<track>`).

## Common failure modes

| Symptom | Cause | Fix |
|---|---|---|
| `fatal: '../worktrees/<...>' already exists` | Stale worktree from a prior run | `git worktree remove --force <path>` if state is discardable; otherwise investigate |
| `error: 'track/<...>' is already checked out at '../worktrees/<...>'` | Two workers assigned the same branch | Use unique track names per worker; per [ADR 0006](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0006-multi-agent-human-concurrency-governance.md) work-tracker should have caught this |
| Worker's `git status` shows mainline files as modified | Worker session has wrong `cwd` (still pointing at mainline checkout) | Re-spawn worker with correct `cwd` parameter |
| `gh pr create` fails "no commits between main and track/..." | Worker hasn't committed yet, or commits are on the wrong branch | Verify `git log` in the worktree |
| Two workers' `docker compose up` fail with port-in-use | Per-worker `COMPOSE_PROJECT_NAME` not set OR port allocation collision | Set unique project name per worker; assign per-worker `PORT_BASE` |
| Operator's mainline `git status` is clean but disk is full | Worktree dirs accumulating | `du -sh ../worktrees/*` to find offenders; `git worktree remove` |
| Worker's branch went stale during long-running pilot | Mainline moved while worker was busy | Captain `git rebase main` in the worktree before the worker opens PR |

## When this runbook stops fitting

If any of these are true, escalate per [ADR 0011](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0011-cluster-worker-execution-environment.md) Trigger conditions for revisit:

- Laptop CPU/memory thrashing during normal cluster runs (>3-4 concurrent workers binding the operator's machine).
- Workers need to run while operator's laptop is asleep / off.
- Phase-3 push at 6-10 concurrent workers across multiple clusters.
- Worker toolchain requirements diverge enough that per-worker venv/asdf hacks aren't sustainable.

The named upgrades are Option II (GitHub Actions) and Option III (cloud execution sandbox); see the design doc for adoption-trigger detail. Block 48M is the named landing pad for Option III.

## Companion artifacts

| Artifact | Path |
|---|---|
| Authoritative design | [`../design/cluster-worker-execution-environment.md`](../design/cluster-worker-execution-environment.md) |
| Anchoring ADR | [`../adr/0011-cluster-worker-execution-environment.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0011-cluster-worker-execution-environment.md) |
| First-cluster pilot kickoff memo | `../project/cluster-kickoffs/demogame-epic-wrath.md` |
| PR governance preparedness | [`../design/pr-governance.md`](../design/pr-governance.md) (Block 66) |
| Tier-3 install runbook (branch protection flip) | [`./tier-3-install-runbook.md`](tier-3-install-runbook.md) |
| Branch-protection readiness script | `../../ops/ci/branch-protection-readiness.sh` |
