# Worktree hygiene — keeping per-session worktrees bounded

Per-session isolation (ADR 0013, ADR 0017) gives every track its own worktree
at `.claude/worktrees/<name>`. That isolation is the point — but worktrees are
full working-tree copies (~3,900 files each), and they accumulate. On
2026-05-28 the working set had reached **51 worktrees**; the steady-state
target is **5–10**. This doc covers why they pile up and how
`ops/scripts/worktree-reap.sh` keeps the set bounded.

## Why they accumulate

`work release` already tears down a track's worktree via `cleanupWorktree()`
(Block 48Q, `ops/work/main.go`). It is necessary but not sufficient:

1. **Release is often skipped.** A PR squash-merges and the work is done, but
   nobody runs `work release <track>`. The merge does nothing to the local
   worktree, so it orphans. The bulk of the 51 were merged-PR worktrees still
   on disk.
2. **Ad-hoc worktrees bypass the track system.** One-line `image-bump-<sha>`,
   `pin-bump-*`, deploy-shim, and detached-HEAD worktrees get created by hand,
   never registered as tracks. `work release` never knows they exist. (Most of
   these shouldn't be worktrees at all — see *complexity budget* below.)
3. **F-118 orphans.** Release ran, but the track metadata recorded
   `mode != "worktree"` (e.g. pickup invoked from the master cwd), so
   auto-cleanup skipped with only a stderr warning nobody acted on.
4. **No reaper.** Nothing periodically detected merged/closed/idle worktrees
   and reclaimed them, so orphans lived until a human noticed the pile.
5. **Recurrence.** Orphaned admin entries can re-materialize their working
   tree on later git operations, so a one-off manual `rm` doesn't stay clean.

## The safety contract

The hazard when reclaiming a worktree is destroying work that exists **only**
locally — unpushed commits or an uncommitted working tree. The reaper removes a
worktree only when its work is preserved elsewhere:

- merged into `origin/main`, proven either way: `git cherry` (patch-id based,
  so single-commit squashes and rebases don't produce false positives — the
  same technique `work release` uses), **or** a **merged PR whose head SHA
  equals the branch tip** (via `gh`, when available). The second proof exists
  because git-cherry cannot see a *multi-commit* branch that was squash-merged
  — the squashed commit's patch-id matches no individual commit, so every
  commit reads unmerged and the worktree HOLDs forever (the 2026-07-08 sweep
  found 10 of 16 provably-merged worktrees invisible this way). Tip == merged
  PR head means everything local was in exactly what merged. **Or**
- already pushed to `origin/<branch>` and not ahead, **or**
- pushed by the reaper itself (it commits a `wip:` snapshot first if the tree
  is dirty), **then** removed.

A full local working-tree copy is expensive; a remote branch ref is cheap.
Preserve the work on the remote, then drop the local copy. This is exactly the
manual procedure run during the 51→3 cleanup, mechanized.

## `worktree-reap.sh`

Dry-run by default; the ACTION column is literally what `--apply` will do under
the current flags.

| ACTION | Meaning |
|---|---|
| `REAP` | merged to `origin/main` and clean, or a stale admin entry (dir gone), or a detached HEAD already in `origin/main`. Work is in main — remove worktree + delete local branch. |
| `PUSH+REAP` | unmerged local commits and/or dirty tree, **and** idle beyond `--idle-days`. Push to `origin` (wip snapshot if dirty), then remove. |
| `HOLD` | safe but retained — unmerged-yet-pushed, or local work not idle enough. Shown, not touched. |
| `KEEP` | never touched — the worktree you're standing in, or (with `--skip-open-prs`) a worktree with an open PR. |

```bash
ops/scripts/worktree-reap.sh                       # dry-run plan
ops/scripts/worktree-reap.sh --apply               # reap merged + stale only (safe default)
ops/scripts/worktree-reap.sh --apply --idle-days 14 --skip-open-prs
                                                   # also reclaim idle (>14d) safe/local-only
                                                   # worktrees, pushing them to origin first,
                                                   # while protecting live PRs
```

Idle-gating is deliberate: a clean, pushed worktree for an **open PR** is safe
on the remote but still actively in use, so a bare `--apply` never touches it.
Only `--idle-days N` reclaims live-but-safe worktrees, and `--skip-open-prs`
(needs `gh`) protects PR worktrees even when idle.

> Note: bare `grep` is shadowed by a shell-function shim in this environment
> (it execs the claude binary in subshells and silently kills loops). The
> script uses `command grep` throughout; any new repo script that loops over
> git output must do the same.

## How it composes — not a replacement

- **`work release`** (`cleanupWorktree`) is the happy-path teardown at the
  moment a track is released. Keep using it.
- **`worktree-reap.sh`** is the periodic backstop sweep that catches everything
  release missed — skipped releases, ad-hoc worktrees, F-118 orphans. Run it
  when the set grows past ~10, or on a weekly cadence, or from `iso exit`.

## Known gaps

- **No cross-session liveness check.** Both the reaper and `cleanupWorktree`
  protect only the *current* session's cwd. In a multi-agent run, a `--apply`
  from one session can `git worktree remove --force` a worktree another live
  session is mid-task in. Observed concretely: during the live 51→3 reap a
  sibling session removed a worktree between this reaper's dry-run and
  `--apply` (no data lost — the branch was merged — but proof of the race).
  Mitigation today is idle-gating + `--skip-open-prs`; a proper fix consults
  the `work` track registry (is there an active, non-paused track for this
  worktree?) or a heartbeat before reaping a worktree the session doesn't own.
- **Release path doesn't push-before-drop.** `cleanupWorktree` uses a
  non-`--force` `git worktree remove` and does not push first, so it fails on a
  dirty tree and cannot preserve local-only work. The reaper covers that gap
  today; folding the push-before-drop logic back into the release path is a
  future refinement.

## Prevention, not just cleanup

The cheapest worktree is the one never created. Per the complexity budget
(ADR 1016) and process-weight discipline, **one-line image/pin bumps and
throwaway deploy checkouts should not get a full worktree** — edit on a short
branch from master, or batch them. Reserve worktrees for multi-commit,
multi-hour, or cross-session track work (ADR 0006). The reaper bounds the set;
not spawning disposable worktrees keeps it small in the first place.
