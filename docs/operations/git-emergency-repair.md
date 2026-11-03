# Git emergency repair — when state gets borked despite the substrate

**Reactive only.** Nothing in this doc fires proactively. The repair tiers + dictator-election protocol activate only after **observable failure** is detected by an agent, captain, operator, or drift critic. Substrate runs in the green-path mode by default; this doc is what to do after a red event.

Scope: master worktree HEAD wrong, branches contaminated, local main diverged dangerously, multiple sessions in conflicting states, drift-induced damage that the post-checkout/pre-commit hooks didn't catch (e.g., `git reset --hard` slip-through, `git rebase` from drifted state, force-pushed branch lost via someone-else's rewrite).

Companion to: [ADR 0013](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0013-master-worktree-read-only-by-convention.md) + [ADR 0017](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0017-claude-code-session-isolation-pilot.md) + [ADR 0014](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0014-local-main-as-trunk-mirror-invariant.md). Substrate prevents most damage; this runbook is for when prevention fails.

---

## Default posture: the substrate works most of the time. This doc is for when it doesn't.

The bundle has five layers (mechanical hooks, autonomous deny list, role discipline, drift-critic, PR-time CI). Total residual ~1 in 5,000 to 1 in 50,000 actions per the Block 48O completion review. Eventually one will slip. **This doc is what to do then.**

Three escalation tiers, each cleaner than going beyond:

| Tier | Trigger | Authority | Recovery method |
|---|---|---|---|
| **Tier 1 — local-only repair** | Local damage; no force-push to origin yet; no other session affected | Whoever caused it (worker / captain / operator) | reflog + cherry-pick + reset to last-known-good local commit |
| **Tier 2 — substrate-wide pause** | Multi-session damage; uncertainty about which sessions are in which state; dirty cross-session state | Captain takeover (workers silenced) | Captain quiesces all workers; elects single repair-dictator; dictator repairs; declares all-clear |
| **Tier 3 — relinquish + restart from origin** | Local main diverged from origin/main in a way reflog can't recover; force-pushed branch lost | Operator + dictator | Hard reset to origin/main; treat all dirty work as lost; restart per substrate |

**Always try Tier 1 before Tier 2; always try Tier 2 before Tier 3.** Each tier's cost is real but bounded; don't skip down without trying up.

---

## Tier 1 — Local-only repair (most common)

### The reflog is your friend

Git keeps a per-clone log of every HEAD movement at `.git/logs/HEAD` (master) or `.git/worktrees/<name>/logs/HEAD` (per-session worktree). Default retention is 90 days. If you can name a state by reflog entry, you can get back to it.

```bash
git reflog               # current branch's reflog
git reflog show HEAD     # same
git reflog --all         # all refs (exhaustive)
```

### Preferred tactics, in order

**1. Preserve WIP using the existing primitives before any rewrite operation**

From inside the affected worktree:

```bash
git rev-parse HEAD                              # note the SHA — reflog also holds it 90 days
git tag wip/before-repair-$(date -u +%s) HEAD   # optional named ref if you don't trust the reflog
git commit -s -m "wip(<track>): preserve before repair"   # if there's uncommitted WIP, land it on the existing track branch
git push -u origin HEAD                         # belt-and-suspenders: get the commit off-host
```

`git stash` is forbidden by the PreToolUse destructive-git guard. `refs/stash` is a single repo-wide ref shared across every worktree and every concurrent session — another session can `git stash pop` and silently grab the bytes (the 2026-05-06 incident class). Use the existing primitives instead: the SHA + reflog + a tag form the recovery point; the `wip(<track>):` commit pattern (same one used by the `/handoff` skill, ADR 0839) is the cross-session-resumption primitive. No new branch type is needed.

**2. Cherry-pick lost commits onto a recovery branch**

If a `git checkout` on master accidentally landed commits on main that should have been on a feature branch:

```bash
# Identify the commits via reflog
git reflog show main | head -10
# e.g., output shows commits a468192 + b486c36 landed on main

# Reset main back to where it should be
git checkout main
git reset --hard <last-good-sha-on-main>      # CAREFUL — destructive

# Cherry-pick the stranded commits onto their proper branch
git checkout -b track/<correct-name>
git cherry-pick a468192 b486c36
```

The 2026-05-08 zenoh-bump incident was repaired this way. ~30 min for two stranded commits.

**3. `git reset --hard <reflog-entry>` to back out a recent destructive op**

If the last operation was `git reset --hard` from a wrong cwd:

```bash
git reflog show HEAD | head -10
# e.g., HEAD@{2}: <correct previous state>
git reset --hard HEAD@{2}
```

Reflog persists across resets (it logs the reset itself), so you can reset back from a bad reset.

**4. `git fsck --lost-found` for orphaned commits**

When a branch is deleted before its commits are merged, the commits become unreachable. Git's GC runs after 90 days but until then they're in the object store:

```bash
git fsck --lost-found 2>&1 | grep "dangling commit"
git show <dangling-sha>  # inspect each
git cherry-pick <dangling-sha>  # rescue if useful
```

**5. `git push origin <local-branch>` from a known-good local clone**

If the remote ref was force-overwritten by a bad push and your local clone has the good state:

```bash
# Don't pull. Don't fetch. Push from the local clone that's still clean.
git push origin <branch>:<branch>
# Or if the local refs were also clobbered, use a backup clone if you have one.
```

### Tier 1 anti-patterns (don't)

- ❌ `git push --force` to "fix" a branch — usually makes it worse; force-push is the most-common cause of needing this runbook
- ❌ `rm -rf .git/` and `git init` — nukes all reflog, all branches, all history; absolute last resort
- ❌ Using `git stash` at all — `refs/stash` is repo-global across worktrees and sessions; another session can pop your WIP without consent (the 2026-05-06 incident class). The PreToolUse destructive-git guard refuses stash mutations. Use the existing primitives instead: worktree isolation, `wip(<track>):` commit on your track branch, reflog, tag.
- ❌ Editing `.git/logs/HEAD` or `.git/HEAD` by hand — hand-tweaking ref state breaks consistency assumptions

---

## Tier 2 — Substrate-wide pause + captain-elected dictator

### When to escalate to Tier 2

- Multiple per-session worktrees show inconsistent git state (their branches are mid-rewrite, dirty in ways their owner didn't expect)
- A push went out that contains commits from drifted state, and other sessions have already pulled
- The substrate itself (active-work.yaml, ops/work tooling) is affected
- Tier 1 attempts made the state worse (3 retries deep, branching into chaos)
- More than two sessions are simultaneously trying to repair → Tier 2 forces single-authority

### Phase A — silence workers immediately

The first action is **stop all in-flight worker actions**. Workers under autonomous mode will continue executing if not stopped. Issue the silence command on the session-bus:

```bash
ops/work/work bus urgent "REPAIR-MODE engaged. All workers HALT immediately. Captains take over per docs/operations/git-emergency-repair.md Tier 2."
```

The UserPromptSubmit hook (`.claude/hooks/session-bus-tail.sh`) injects this on the next prompt for every active session in the repo. Workers that read it MUST:

1. Stop current work mid-action (do not finish the current task)
2. Mark the track blocked so the dictator can see scope: `ops/work/work update <track> --status "blocked:repair-mode-quiesce"`
3. Any uncommitted state in your worktree stays there — the worktree is the isolation, the dictator is not touching arbitrary worker worktrees. If you want a durable handoff point so a different session can resume your track post-clear, run the `/handoff` skill (ADR 0839) — it captures a `wip(<track>): handoff baton` commit on your track branch.
4. Wait for `bus info "REPAIR-MODE-CLEAR"` before resuming.

(Do NOT `git stash` — repo-global ref, cross-session collision; the PreToolUse destructive-git guard refuses it.)

Workers that ignore this signal go on the watchlist for autonomous-mode demotion — silence-and-wait is the discipline.

### Phase B — captains take over

With workers silenced, captains are the only acting agents. Each cluster captain:

1. Reads the bus event stream from the moment the urgent fired backward to identify scope of damage
2. Reports their cluster's git state to the bus: `ops/work/work bus warn "captain <id>: cluster <name> state — branches: ... worktrees: ... last-known-good-sha: ..."`
3. Does NOT touch master or other clusters' state — captains are coordinating peers, not repairing yet

### Phase C — captains elect a single dictator

The captains coordinate via the bus to elect ONE dictator. Election rules:

- **Default**: the operator picks. If the operator is the one who notices the breakage, they assign.
- **Otherwise**: the captain whose cluster is LEAST affected by the damage takes the dictator role (least to lose if the repair has side effects). If unclear, the captain who first surfaced the breakage to the bus.
- **Election emits an event**: `ops/work/work bus urgent "DICTATOR ELECTED: <captain-id> for repair window starting <ts>; all other captains acknowledge with bus info"`

Captains acknowledge via `ops/work/work bus info "<id> acknowledges DICTATOR <captain-id>; standing down for repair window"`. If a captain doesn't acknowledge within 5 minutes, the operator is notified for manual override.

### Phase D — dictator performs repair

The elected dictator has **sole write authority** during the repair window. Other captains (and silenced workers) DO NOT touch git state. The dictator works through Tier 1 tactics in their own per-session worktree (or master worktree if they need to repair main itself), publishing each step to the bus:

```bash
ops/work/work bus info "DICTATOR <id> step 1: tagged current HEAD as wip/before-repair-<ts> as recovery point..."
ops/work/work bus info "DICTATOR <id> step 2: identified stranded commits a468192 b486c36 in reflog..."
ops/work/work bus info "DICTATOR <id> step 3: cherry-picking onto recovery branch track/repair-2026-05-08..."
```

Every step gets a bus event so an operator (or a future drift critic) can reconstruct the repair sequence post-hoc.

### Phase E — dictator declares all-clear with notes

When repair is complete, dictator emits:

```bash
ops/work/work bus urgent "REPAIR-MODE-CLEAR. Damage scope: <summary>. Repair tactics: <summary>. State now: <summary>. Affected tracks: <list>. Resumption guidance: <per-track guidance>."
```

The all-clear notes are mandatory — without them, captains have no basis to know what was actually repaired vs deferred. The notes also become a finding (`F-NNN-<repair-incident-name>.md`) for the durable register.

### Phase F — captains resume; workers reactivate per-track

Captains read the all-clear, decide per-track whether to:

- Resume from quiesce-stash (most cases)
- Discard quiesce-stash and re-do work (if the repair invalidated in-progress state)
- Halt the track until human intervention (if the repair couldn't restore the precondition)

Captain emits per-track reactivation events: `ops/work/work bus info "captain <id>: resuming track <name>; workers may reactivate"`. Workers under that captain MAY then unstash + continue.

---

## Tier 3 — Relinquish + restart from origin

### When to escalate to Tier 3

- Tier 2 dictator concludes that state cannot be reconciled without losing work
- `origin/main` has moved in ways that make local main impossible to fast-forward
- Reflog GC has aged out (>90 days since the last-known-good state)
- The `.git` directory is corrupted (object store inconsistency)
- Multiple force-pushed branches were rewritten by external actors

### The relinquish protocol

**Accept that some work will be lost.** This is the cost of escalating to Tier 3. Salvage what you can:

```bash
# 1. Push every track branch that hasn't been pushed yet, from each worktree
for wt in .claude/worktrees/*/; do
  cd "$wt" || continue
  git push -u origin HEAD || true  # best-effort
  cd -
done

# 2. Capture every track/* branch + any wip/* tags from every worktree
#    (replaces the old stash-list capture; stash is banned. track/* branches
#    are the units of work; wip/* tags, if any, are recovery points.)
for wt in .claude/worktrees/*/; do
  cd "$wt" || continue
  git for-each-ref --format='%(refname:short) %(objectname:short) %(committerdate:iso) %(subject)' \
    refs/heads/track/ refs/tags/wip/ > /tmp/refs-$(basename "$wt") || true
  cd -
done

# 3. Capture reflog from master + every worktree
git reflog > /tmp/reflog-master
for wt in .claude/worktrees/*/; do
  cd "$wt" || continue
  git reflog > /tmp/reflog-$(basename "$wt")
  cd -
done
```

These artifacts go into a Tier-3 finding for forensic record.

### The hard reset

```bash
# WARN: destructive. Only after Tier 1 + Tier 2 have failed.

# Master worktree: hard reset to origin/main
cd <master-worktree-path>
git fetch origin main --quiet
git reset --hard origin/main

# Each per-session worktree: nuke + recreate from origin
for wt in .claude/worktrees/*/; do
  name=$(basename "$wt")
  cd <master-worktree-path>
  git worktree remove --force "$wt"
  git worktree add ".claude/worktrees/${name}" -b "track/${name}" origin/main
done
```

After this, every clone is at origin's state. All in-progress local work that wasn't pushed in the relinquish step is **lost**.

### Restart from substrate

After a Tier 3 reset:

1. Re-install hooks: `make multi-agent-substrate-install`
2. Re-create per-session worktrees as needed (operator decides which tracks resume)
3. File a `F-NNN-tier3-relinquish-<date>.md` finding documenting what was lost + why Tier 1+2 didn't suffice
4. Update `docs/reports/cluster-pilot-data.md` with a verdict for the affected runs
5. If the failure mode that caused this is novel, queue a Block 48P/48Q/48R/48S subtask to add prevention

---

## Authority + tactics summary

| Situation | Authority | First tactic | Second tactic | Last resort |
|---|---|---|---|---|
| Local single-session damage | Whoever caused it | Note SHA + tag + reflog + `git reset --hard <good-sha>` | `git fsck --lost-found` + cherry-pick | Tier 2 |
| Multi-session damage | Captains via bus election | Quiesce workers + report state | Elect dictator + repair window | Tier 3 |
| origin/main diverged unrecoverably | Operator + dictator | Push every salvageable branch | Capture reflog + stash list | Tier 3 hard reset |
| `.git` directory corrupted | Operator | Restore from `.git` backup if available | Re-clone from origin (=Tier 3) | Re-clone from origin |

## Drill cadence

- **Tier 1 drill** quarterly — engineer deliberately drifts in a per-session worktree, recovers via reflog. Drill outcome posted to `cluster-pilot-data.md`.
- **Tier 2 drill** semi-annually — operator triggers a synthetic incident; captains run the silence-elect-repair-clear protocol against a synthetic worktree corruption. Tabletop format acceptable.
- **Tier 3 drill** annually — operator hard-resets a throwaway clone, walks through full restart-from-origin recovery. Wet drill required (no tabletop).

Drill failures are F-NNN findings, not embarrassments. Each drill that uncovers a tactic-gap improves the substrate.

## Bus event reference

```
bus urgent "REPAIR-MODE engaged"            — silence all workers
bus info   "captain <id>: cluster state ..." — captain reports situational state
bus urgent "DICTATOR ELECTED: <id> ..."     — election outcome
bus info   "<id> acknowledges DICTATOR ..."  — captain stand-down
bus info   "DICTATOR step N: ..."           — repair sequence
bus urgent "REPAIR-MODE-CLEAR ..."          — all-clear with notes
bus info   "captain <id>: resuming track ... workers may reactivate"
```

Use exactly these strings — drift critics, post-incident scans, and future automated tooling parse them.
