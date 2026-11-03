# Multi-agent substrate — install + first dogfood (operator runbook)

This runbook covers the **two operator-fired actions** required to deploy the multi-agent substrate, and the first Pattern-2 dogfood (zenoh 1.9 bump). Total operator time: ~5 min for review, ~30 sec for install, then operator-talks-to-Claude as normal.

ADR anchor: [ADR 0017 Claude Code session-isolation pilot](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0017-claude-code-session-isolation-pilot.md)

---

## Action 1 — Review + merge the substrate (one-time, ~5 min)

The substrate ships as a feature branch on origin: `track/multi-agent-substrate-export`. Eight commits, ~1900 lines across ~30 files:

```
54e7bb9 test+fix(multi-agent-substrate): cross-session integration tests + cwd-discipline edge cases — caught real bus-path divergence bug
896655e test(multi-agent-substrate): comprehensive session-bus test coverage (Block 48N.2 hardening)
ec227bf feat(multi-agent-substrate): Block 48N session-bus + remediation runbook + 48O closeout
4c410de feat(multi-agent-substrate): cwd anti-drift discipline + drift-critic role + PR-time hygiene check
c52fb67 refactor(multi-agent-substrate): iso enter is the primary entry path for VSCode-launched sessions
900a536 docs(multi-agent-substrate): ADR 0013 amendment + ADR 0017 + Block 48O + export stub + pilot data + CLAUDE.md pointer
d350938 feat(multi-agent-substrate): session-isolation pilot — hooks + launcher + /iso skill + work CLI metadata + autonomous mode
+ 8th: feedback_auto_iso_enter_on_track_shaped_tasks memory hook + Makefile auto-install
```

Merge via your normal PR flow. Don't `git checkout` the branch on master worktree first — the post-checkout hook (which lands as part of this merge) is designed to refuse exactly that.

---

## Action 2 — Install (one-time, ~30 sec)

After the PR merges to `main`:

```bash
cd ~/src/github.com/usareur-af/goatcore   # your master worktree
git pull origin main                          # fast-forward; no checkout drama
make multi-agent-substrate-install
```

That single Make target installs:

- **Master-worktree git hooks** at `.git/hooks/{post-checkout,pre-commit}`. The post-checkout hook refuses HEAD off main; pre-commit refuses commits when off-main; both inert in child worktrees. Reverts include working tree (per the spike report).
- **`/iso` slash command** at `~/.claude/skills/iso/SKILL.md`, a symlink to `ops/scripts/iso.skill.md`. Per-user, available to every Claude Code session.
- **Two memory hooks** at `~/.claude/projects/<repo-prefix>/memory/`:
  - `feedback_master_worktree_readonly.md` — discipline reflex against master mutation
  - `feedback_auto_iso_enter_on_track_shaped_tasks.md` — agent self-spawns `/iso enter` on track-shaped tasks; operator never has to ask
- **Session-bus state directory** at `~/.claude/state/`. Per-repo bus file fingerprinted by master worktree path.

Optionally — only if you want to run `claude-session` from a CLI terminal (most operators don't, since `/iso enter` from inside Claude Code does the same thing):

```bash
ln -s $(pwd)/ops/scripts/claude-session ~/bin/claude-session
```

That's it. **You will never run these install commands again on this clone.**

---

## Verify the install

```bash
ls -la .git/hooks/post-checkout .git/hooks/pre-commit
ls -l ~/.claude/skills/iso/SKILL.md
ls ~/.claude/state/session-bus-*.jsonl 2>/dev/null  # may not exist until first emit
ls ~/.claude/projects/*$(basename $(pwd))*/memory/feedback_*.md 2>/dev/null
```

All four should return paths. If the memory-dir line returns nothing, that's because Claude Code hasn't initialized the per-repo memory dir yet — start one Claude Code session in this repo, then re-run `make multi-agent-substrate-memory-install`.

Quick functional check:

```bash
# From master worktree, attempt to checkout a sibling branch — hook should refuse
git checkout -b test-substrate-installation 2>&1 | head -3
# Expected: "master-guard: master HEAD must stay on main; reverted HEAD + working tree."
# Confirm we're back on main:
git branch --show-current   # → main
```

---

## First dogfood — Pattern-2 zenoh 1.9 bump (operator types one task)

Open VSCode at the master worktree. Start a new Claude Code session. Type:

```
do the zenoh 1.9 bump. handoff baton is the latest wip(zenoh-1.9-bump): commit on track/zenoh-1.9-bump (pushed to origin).
```

That's the entire operator action — the operator captured their dirty files via the `/handoff` skill (ADR 0839) which created a `wip(zenoh-1.9-bump): handoff baton` commit on the track branch and pushed it. The agent will (per the auto-`/iso enter` memory hook):

1. Recognize the task as multi-commit / multi-hour
2. Run `/iso enter --autonomous zenoh-1.9-bump` itself — provisions `.claude/worktrees/zenoh-1.9-bump/` on `track/zenoh-1.9-bump`, registers the track, switches operating directory, copies overnight allowlist
3. The worktree already has the baton commit on the branch (it's the tip of `track/zenoh-1.9-bump`). The baton's commit message tells the agent the TodoWrite list + active hypothesis + ruled-out paths + next step + WIP files to resume from. Do NOT use `git stash pop` — `refs/stash` is repo-global and another concurrent session can pop the bytes; the PreToolUse destructive-git guard refuses stash mutations.
4. Source adapt → cargo build → cargo test → commit → push → `gh pr create`
5. `ops/work/work release zenoh-1.9-bump` when done
6. Report back to operator with PR URL

If the agent hits a permission boundary at any point (autonomous mode), it follows the halt protocol from `ops/work/roles/autonomous-worker.md`: write F-NNN finding, emit `work bus warn` event, push branch with halt-state marker, stop. Operator wakes up to a halt-state PR, reviews the finding, decides on resume or rescope.

---

## Capture pilot evidence

Append a row to `docs/reports/cluster-pilot-data.md` with the run shape per the template there. Three signals:

- **Operator-intervention rate**: how many times the operator manually intervened in git state (target: 0)
- **Time-to-PR**: from "do the zenoh bump" to PR opened (informational; not a hard target for single-track work)
- **Worker green-rate**: not applicable for Pattern 2 (single-track)

Plus free-form `notes:` capturing any drift, halt, friction, or surprise.

After 2-3 Pattern-2 runs across varied work shapes, ADR 0017 promotes Proposed → Accepted (or rolls back per signal). Block 48O completion review Section D defines the criteria.

---

## When something goes wrong

The substrate has five layers of defense:

1. Mechanical hooks (master HEAD invariant)
2. Autonomous deny list (cloud + destructive ops blocked)
3. Agent role discipline (cwd-anchor, halt-on-boundary)
4. Drift-critic role (manual scan via `ops/scripts/drift-scan.sh <track>`)
5. PR-time CI gate (the track-discipline steps of `pr-hygiene.yml`, on PR open)

If state still gets borked despite all five, **DO NOT** patch on top. Open [`docs/operations/git-emergency-repair.md`](git-emergency-repair.md) and follow the Tier-1 → Tier-2 → Tier-3 escalation. Tier 2 includes the captain-elected dictator + REPAIR-MODE bus protocol for substrate-wide pause.

---

## Pre-push gate — `make pr-readiness   # operates on the CURRENT branch (no args)` (Block 48Q)

Before every `git push` / `gh pr create` from a feature-branch worktree, run:

```bash
make pr-readiness   # operates on the CURRENT branch (no args)
```

Hard-fails (exit 1) on five mechanically-checkable failure modes:

1. **Stale base** — branch's merge-base with `origin/main` is more than 50 commits behind (configurable via `PR_READINESS_MAX_BEHIND=N`).
2. **Orphan-resurrection** — any ahead-commit's SHA matches the HEAD of a recently-merged-and-deleted branch on origin (this is the PR #6 case).
3. **Runaway diff** — diff vs `origin/main` exceeds 50 files OR 5000 lines (overrides via `PR_READINESS_MAX_FILES` / `PR_READINESS_MAX_LINES` for legitimate bulk changes).
4. **Dirty working tree** — uncommitted or untracked files.
5. **Missing DCO** — any ahead-commit lacks `Signed-off-by:` trailer.

Composes with the `pr-hygiene.yml` CI gate (which runs post-push on PR open) — `pr-readiness` catches the same class of problems BEFORE the push.

## Cleanup-on-release (Block 48Q)

`work release <track>` now auto-removes the per-session worktree for tracks with `mode: worktree`. Refuses if cwd is inside the worktree (cd out first). Refuses if the worktree has uncommitted changes — force-remove via `git worktree remove --force <path>` or skip via `work release <track> --keep-worktree` for follow-on work.

Shape: finish work in your child worktree, commit, push (or direct-commit on main if appropriate), `cd` to master worktree, run `work release <track>`. Track row migrates to `recently_completed`; local worktree dir disappears in the same step.

## Uninstall

Reversible per ADR 0017:

```bash
make multi-agent-substrate-uninstall
```

Removes hooks + skill + memory hook. Bus state directory is preserved (forensic value). Per-worktree `.iso-mode.env` files are preserved (use `git worktree remove` for full cleanup).

---

## What this is NOT

- Not a substitute for code review on PRs (still required per ADR 1015)
- Not a replacement for branch protection on `main` (per ADR 0109; complementary)
- Not zero-defect — see Block 48O completion review §"Honest assessment of gaps"
- Not cross-machine — the bus is single-machine; out of scope for goat's pattern

## Decision-point + rollback

Pilot evaluation criteria + rollback procedure live in [ADR 0017](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0017-claude-code-session-isolation-pilot.md) §"Rollback procedure" + §"Pilot evaluation criteria." 2+ runs net-negative on any signal triggers per-piece rollback via `make multi-agent-substrate-uninstall` + cherry-pick rollback of the offending piece.
