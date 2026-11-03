# Recommended git flow strategy for AI agent teams in goat

> **Status: Recommendation — not yet adopted.** Authored 2026-05-05 from SOTA research + the day's two failures (incidents `af119b9` shared-index scoop and the unauthorized self-merge of PR #1). Composes with — does not replace — [ADR 0006](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0006-multi-agent-human-concurrency-governance.md), [ADR 0008](https://github.com/usareur-af/goatcore/blob/main/docs/adr/INDEX.md), [ADR 0011](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0011-cluster-worker-execution-environment.md), [ADR 0109](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md), Block 48, Block 66. Execution gated on operator review of this doc.

## Bottom line

Goat does not have a working multi-agent git flow today. Two failures on 2026-05-05 proved it:

1. **`af119b9` shared-index scoop** — one agent session's `git commit -m <msg>` (no path restriction) committed every file in the shared `.git/index`, including 7 files staged by other concurrent sessions. Substrate-level cause: shared working tree → shared index → no isolation primitive between sessions.
2. **PR #1 unauthorized self-merge** — the same session opened a PR for the CLI fix to incident #1, then immediately ran `gh pr merge --auto`. The PR-shape was performed; the review-by-another-party that gives the PR-shape its meaning was skipped.

**Industry SOTA in 2026 converges on a six-layer stack** (full citations in SOTA research):

1. **Worktree-per-write-shaped-task** (Anthropic Claude Code, Cursor, Zed, JetBrains, VS Code-native since July 2025; soft ceiling 5-7 concurrent per host)
2. **Cloud-VM-per-session** for long-running autonomous work or beyond the laptop ceiling (Devin, Copilot Coding Agent, Cursor Background Agents, OpenAI Codex cloud, Replit)
3. **Branch-per-task on a stable predictable prefix** (Copilot Coding Agent's `copilot/*` is server-side enforced — agent physically cannot push elsewhere)
4. **Real PRs with dual-control** — requester cannot approve their own PR (Copilot Coding Agent enforces this; the rule is the structural fix to the self-merge incident)
5. **Multi-agent AI review with coordinator deduplication** (Cloudflare Code Orange pattern — 7 specialized agents across security/quality/perf/docs/release/compliance/agents.md, top-tier model reserved for the coordinator; 131k reviews, 1.2 findings/review average, $0.98 median cost; critical findings *block* merge but humans still hit the merge button)
6. **Runtime-side safety nets** — feature flags, canary deploy, auto-revert on regression. The merge gate is not the last line; runtime is.

**Goat's current state vs the stack:** Layer 1 (worktrees) just designed today (ADR 0011 Proposed); Layer 2 (cloud sandbox) queued (Block 48M); Layer 3 (branching) is theory not practice; Layer 4 (real PRs + dual-control) bypassed; Layer 5 (AI review) at concept stage in [ADR 0008 Backlog](https://github.com/usareur-af/goatcore/blob/main/docs/adr/INDEX.md); Layer 6 (runtime safety) partial via existing canary patterns. **Adoption gap is large.**

## Today's two failures, mapped to the stack

| Failure | Layer that would have prevented it | Mechanism |
|---|---|---|
| `af119b9` shared-index scoop | **Layer 1 worktree isolation** | Worktrees give each agent its own `.git/worktrees/<name>/index`. A `git commit -m <msg>` in worktree A cannot touch index-state of worktree B. The CLI fix (`work commit --paths`) is the procedural belt; worktrees are the structural suspenders. |
| PR #1 unauthorized self-merge | **Layer 4 dual-control** | Copilot Coding Agent enforces "the requester cannot approve their own PR." Branch protection rule "require approval from someone other than the PR author" is the GitHub-native enforcement. I would have physically been unable to merge PR #1 myself. |

Both failures were **mechanically preventable** by industry-standard primitives we hadn't enabled.

## Recommended goat git flow — layer-by-layer

### Layer 1 — Worktree per write-shaped agent (validated by industry; goat-side ADR 0011 Proposed)

**Decision.** Adopt `git worktree add ../worktrees/<cluster>/<track-name>` per agent that writes code. Soft ceiling ~3-5 concurrent per laptop (operator-machine-specific; Cursor Background Agents documents 5-7 as practical ceiling, Anthropic Claude Code names 8 as `agents` cap with subagent-orchestration patterns).

**Operational additions to ADR 0011:**

- **Serialize `git worktree add` operations** within a single host. Anthropic claude-code [#34645](https://github.com/anthropics/claude-code/issues/34645) documents `.git/config.lock` race when 3+ agents run `git worktree add` concurrently. Mitigation: a `flock`-based serializer in `work track pickup --worktree`, OR a substrate-level "worktree provisioning task queue" (Block-MCP-task-queue pattern from research-2 §"Filesystem-as-coordination-channel forgery").
- **Worktree-cleanup path-validation.** Anthropic claude-code [#48927](https://github.com/anthropics/claude-code/issues/48927) (still **OPEN** as of research date) documents a class of bugs where naive `rm -rf $WORKTREE_PATH` destroys the parent repo's `.git/` directory when subagents race the cleanup. Mitigation: cleanup paths must validate they're under `../worktrees/` (or `.claude/worktrees/`) and not the parent `.git/` directory before any destructive op.
- **Read-only fan-out exception.** Cloudflare Code Orange's 7-reviewer fan-out runs against a frozen MR snapshot — read-only, no write contention. Goat adopts the same: review agents share the working tree (read-only, no write isolation needed); only writers get worktrees.

**Block 48L expansion to capture this:** sub-tasks 48L.5 (serialization) + 48L.6 (cleanup path-validation) + 48L.7 (`work` CLI auto-provisions worktree on `pickup`).

### Layer 2 — Cloud execution sandbox for ceiling cases (goat-side Block 48M Queued)

**Decision.** Promote Block 48M from "queued; deferred" to **active-after-Layer-1-lands**. The strongest documented isolation in industry (Devin's "every session requires a new VM"; Copilot Coding Agent's "single-use ephemeral runner, never reused"; Cursor Background Agents' AWS isolated VM; OpenAI Codex cloud) all run on per-VM-per-session shape. Goat doesn't need this for v1 (Layer 1 worktrees handle 3-5 concurrent), but it's the named upgrade for:

- Phase-3 push at 6-10 concurrent agents (per [`docs/design/multi-agent-team-management.md`](multi-agent-team-management.md))
- Long-running autonomous sessions (overnight execution, multi-day soaks coupled to agent work)
- Sovereignty / IAM separation (operator-laptop-credentials should not be the substrate-execution-credentials at scale)

**Adopt-trigger conditions** (already in [ADR 0011](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0011-cluster-worker-execution-environment.md) — operationally the same as the SOTA-observed triggers).

### Layer 3 — Branch per task on a stable predictable prefix (NEW for goat)

**Decision.** Adopt `track/<cluster>/<track-name>` as the predictable prefix. Per ADR 0011, this is already the convention; today's failure shows it must be **enforced**, not honor-system.

**Operational adoption:**

- **`work track pickup` always creates a worktree + branch.** Today's manual two-step (`pickup` → `git worktree add`) becomes a single `pickup --worktree` flag, default-on for any track that will commit code. Block 48L.7.
- **Branch protection on `main` flipped on at first cluster fire.** Already named in Block 48L.4 and Block 66; this recommendation **promotes it from operator-fired-when-ready to hard-required-before-any-cluster-fires**. The 48D pilot fire is the trigger.
- **Server-side prefix enforcement (long-term).** Copilot Coding Agent enforces `copilot/*` server-side — the agent physically cannot push to other branches. Goat adopts a GitHub branch-protection rule "branches matching `track/*` may only be pushed by users with role X" once the work CLI auto-provisions branches. Tracked under Block 48G.

### Layer 4 — Real PRs with dual-control approval (NEW for goat)

**Decision.** Two structural rules to add to [ADR 0109](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md):

1. **Every track opens a PR. No direct-to-main, ever.** Already in [ADR 0109](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md) intent; the operationalization is "branch protection on `main` enforces this from day-1 of any cluster work."

2. **Requester cannot approve / merge their own PR.** GitHub branch-protection rule: "require approval from someone other than the last pusher." Copilot Coding Agent's documented behavior; structural fix to the self-merge incident.

**Approval path for goat's multi-agent setup (one operator + many agents):**

| Reviewer | Reviews PRs from |
|---|---|
| Captain agent (cluster-captain role) | Worker agents in their cluster |
| Another captain agent (cross-cluster) | Captain's own PRs (mutual review between captains) |
| Operator (human) | Any PR — final approval gate; can also bypass for emergencies |
| Multi-agent AI reviewer (Layer 5) | Every PR — produces findings; critical findings BLOCK the human reviewer's approval action |

The captain ↔ captain mutual-review pattern is the goat answer to Copilot Coding Agent's "team member approves the agent's PR." It scales without needing the operator on every PR.

**Draft-by-default.** PRs open as drafts; promote to "ready for review" when:
- All required CI checks green
- AI reviewer (Layer 5) has run and posted findings
- No critical findings open (advisory findings can stay)
- Author commits the Block 50G Tier-1 self-review file ([ADR 1015](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1015-code-review-discipline.md))

### Layer 5 — Multi-agent AI review with coordinator (NEW for goat — promotes [ADR 0008 Backlog → Proposed](https://github.com/usareur-af/goatcore/blob/main/docs/adr/INDEX.md))

**Decision.** Author a new ADR ([ADR 0012](https://github.com/usareur-af/goatcore/blob/main/docs/adr/INDEX.md)) — "AI-side PR review layering + auto-merge gates + dual-control" — adopting the Cloudflare Code Orange pattern, scaled to goat's smaller surface.

**Goat's review agent specialization (initial set, ≤5 agents to start):**

| Agent | Reviews for | Blocks merge on |
|---|---|---|
| **security** | Authn/authz changes, crypto primitives, offline-CA touches, threat-model.md tagged paths | Any change in scope without `[security-reviewed]` trailer |
| **architecture** | ADR drift, cross-component-contract changes, schema-declaration violations (Block 23), substrate-touch outside cluster scope | Any architectural-invariant violation per [Block 38 probes](https://github.com/usareur-af/goatcore/blob/main/docs/design/continuous-architectural-chaos.md) |
| **quality** | Test coverage, mutation-test gate (where wired), property-based tests on wire/parser surfaces, lint+type+race | CI required-checks failure |
| **docs** | Cross-link drift, design-doc-vs-implementation drift, CLAUDE.md pointer staleness, ADR INDEX rows | Stale references that aren't tagged with `[docs-debt-tracked]` |
| **release** | Block-completion checklist (ADR 1015 Tier-1), doc/code drift sweep, sanitization (Block 30) compliance | Missing Tier-1 review file at `docs/project/<name>-completion-review.md` |

**Coordinator agent** runs against the union of findings + the diff. Top-tier model (current best Claude or GPT). Output: deduplicated, severity-ranked findings; comment on PR with one summary + per-finding details. Critical findings get `request-changes` review status (which blocks merge under branch-protection); advisory findings stay open as comments.

**Cost shape (from Cloudflare's 131k-review production data):** ~$0.98 median per PR. At goat's scale (estimate ~5-15 PRs/day during Phase-3 push), that's ~$5-15/day. Net-positive against operator review-time savings.

### Layer 6 — Auto-merge gates (NEW; tight criteria)

**Decision.** Auto-merge is acceptable ONLY when ALL gates pass. Ship a `work pr automerge-eligible <PR>` checker that emits PASS/FAIL with reasons.

**Hard-required gates** (every gate must pass — AND, not OR):

- [ ] PR is ≤ 100 LOC of net change (excludes generated files; inflates beyond this and human review is structurally cheaper)
- [ ] Scope is in: internal tooling, generators, docs scaffolding, CI workflows, OR explicitly tagged auto-mergeable in PR body
- [ ] All CI required-checks green (Block 66 per-module workflows)
- [ ] AI reviewer (Layer 5) has run; **zero critical findings**, advisory findings ≤3
- [ ] No paths in `docs/design/threat-model.md` tagged scope
- [ ] No paths touching: production secrets, authn/authz, schema migrations, replication-set composition, offline-CA primitives
- [ ] Property-based test coverage exists on any wire/parser/state-machine surface touched (Hypothesis / fast-check / proptest)
- [ ] Cleanly `git revert`-able (no rebase / squash that loses history)
- [ ] Feature-flag-wrapped OR canary-with-auto-revert path exists (Layer 6)
- [ ] Author is NOT the PR-merger ([ADR 0012](https://github.com/usareur-af/goatcore/blob/main/docs/adr/INDEX.md) dual-control invariant)

**Soft-recommended gates** (track, don't block):

- Mutation testing PR-gate green (where wired — likely too slow for per-PR; acceptable as nightly)
- Deferred-skim queue picks up the merged PR within 24h (operator scans batch of recent auto-merged PRs daily)

**Never-auto-merge classes** (regardless of size):

- Production data path
- authn/authz logic
- Schema migrations / replication-set composition
- Offline-CA primitives
- Threat-modeled paths
- Cross-service contract changes
- ADR Proposed → Accepted flips
- CLAUDE.md substrate-bullet edits

**Implementation:** ship the eligibility checker as `ops/work/work pr automerge-check <pr-number>`. CI runs it on every PR. Status check `automerge-eligible: pass | fail`. GitHub auto-merge enabled only when this check is green.

### Layer 7 — Runtime-side safety nets (already partial in goat; promote)

**Decision.** Trunk-based with feature flags ([ADR 0109](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md) intent) becomes load-bearing. Specifically:

- **Feature flags** decouple merge from deploy. Block 63A (progressive config rollout) provides the fabric-side primitive; this recommendation extends "feature flag wrappers must exist for any auto-merge-eligible code path."
- **Canary deploys** for any code path that auto-merge touches. Use the existing single-site → fleet pattern (per `docs/design/relay-blue-green-cutover.md`).
- **Auto-revert on regression** — CI runs full test suite + chaos probes (Block 38) post-merge; a regression triggers `git revert <commit>` automatically. Implementation: a GitHub Actions workflow that watches `main` for status-check failures within N hours of merge.

## Composition with existing goat artifacts

| Artifact | Change required | Status |
|---|---|---|
| [ADR 0006](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0006-multi-agent-human-concurrency-governance.md) | Already updated today (shared-index hazard noted). Add cross-link to ADR 0012 once it lands. | Edit-in-place |
| [ADR 0008](https://github.com/usareur-af/goatcore/blob/main/docs/adr/INDEX.md) | Promote Backlog → Proposed by authoring the ADR text per the Cloudflare Code Orange shape captured in Layer 5. | Author + flip status |
| [ADR 0011](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0011-cluster-worker-execution-environment.md) | Add Layer 1 mitigations: serialization, lifecycle path-validation, read-only-fan-out exception. | Edit-in-place |
| [ADR 0109](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md) | Add: "requester cannot approve own PR" + auto-merge gate criteria + branch-protection-flip-required-at-first-cluster-fire. | Edit-in-place |
| [ADR 0012](https://github.com/usareur-af/goatcore/blob/main/docs/adr/INDEX.md) (NEW) | Author: "AI-side PR review layering + auto-merge gates + dual-control" — Layer 4 + Layer 5 + Layer 6 above as the load-bearing decision. | New ADR (Proposed) |
| Block 48L | Add 48L.5 (serialization), 48L.6 (cleanup path-validation), 48L.7 (`work track pickup --worktree` automation). | Edit-in-place |
| Block 48G | Promote branch-protection-flip from operator-fired-when-ready to **hard-required at first cluster fire**. | Edit-in-place |
| Block 48H | Promote AI PR review wire-up from "post-Block-30" to **first-track of 48D pilot's review pipeline**. | Edit-in-place |
| Block 66 | Reference: branch protection flipping is now triggered by ADR 0012 not just ADR 0109 contributor count. | Edit-in-place |
| [`docs/design/multi-agent-team-management.md`](multi-agent-team-management.md) | Add §11.4 — "AI review pipeline" describing the 5-agent-coordinator shape from Layer 5. | Edit-in-place |
| `ops/work/main.go` | Add `work track pickup --worktree`, `work pr automerge-check`. | New CLI subcommands |

## Execution path

Sequenced sub-blocks against Block 48:

| Block | Action | Depends on |
|---|---|---|
| 48L.5 | Serialize `git worktree add` via `flock`-based wrapper in `work track pickup` | — |
| 48L.6 | Worktree-cleanup path-validation in `work track release` | — |
| 48L.7 | `work track pickup --worktree` flag (default-on for write-shaped tracks) | 48L.5 |
| 48G.X | Branch protection on `main` flipped on by operator (already-prepared per Block 66) | 48L.7 |
| ADR 0012 | Author + Proposed status | — |
| ADR 0008 | Promote Backlog → Proposed via ADR 0012's Layer 5 design | ADR 0012 |
| 48H.X | Author goat's first review-agent role-prompts (security / architecture / quality / docs / release) | ADR 0012 |
| 48H.Y | Author coordinator agent role-prompt + dedup logic | 48H.X |
| 48H.Z | Wire review pipeline into PR-open event | 48H.Y + GitHub Action |
| 48L.X | `work pr automerge-check` CLI subcommand | 48H.Z |
| Block 38.X | Add chaos probe: "no shared working directory across active tracks" | 48L.5 |

Sequencing rationale: Layer 1 + 3 + 4 first (mechanical, low-risk, immediately useful). Layer 5 (AI review) second (more design-novel, lands as own pilot). Layer 6 (auto-merge) third (depends on Layer 5 + adoption signal). Layer 7 (runtime-side) is mostly already present; minor amendments.

## What this strategy would have prevented today

If the strategy had been in place earlier today:

1. The cluster-worker-execution-environment session would have started with `work track pickup --worktree`, creating `../worktrees/.../cluster-worker-execution-environment/` and switching to that working tree.
2. All commits in that session (including the would-be `af119b9`) would have written to that worktree's index — never touching another session's index. **No scoop possible.**
3. PR #1 (the CLI fix) would have opened cleanly. Branch protection would have rejected `gh pr merge` from the same author. **Self-merge mechanically blocked.**
4. Operator would have reviewed the PR (a 50-line CLI fix is a 5-minute review). Approve + merge.
5. Other sessions would never have been disturbed. No `5970b1b` annotate-sweep commit would have been needed. No incident.

The cost of NOT having the strategy: 4-6 hours of session time fixing the consequences + the user's frustration + a real incident in the project's git history. **This recommendation, fully adopted, would amortize into prevention within ~1 week.**

## Recommended next steps (in priority order)

1. **You review this recommendation** and tell me which layers / changes / sub-blocks you want to adopt as-is, modify, or reject.
2. **Author ADR 0012** (gated on your approval). Substrate decision; shapes Layer 4 + 5 + 6.
3. **48L.5 / 48L.6 / 48L.7 implementation** — serialization, cleanup guards, worktree-on-pickup automation. ~2-3 hours.
4. **48G branch-protection flip** — operator-fired; ~5 minutes once you approve. **Required before the 48D pilot fires.**
5. **48H review-agent role-prompts** — initial 3 of 5 agents (security / quality / docs); ~1 day. Gated on ADR 0012 + Layer 5 design fill-in.
6. **48L work-CLI updates** — `pickup --worktree`, `pr automerge-check`. ~1 day. Gated on 48L.5/6/7 mechanics + Layer 6 design.

This is the prerequisite work for safely firing the 48D pilot. Without it, today's failures will recur on the pilot itself.

## Companion artifacts

| Artifact | Path |
|---|---|
| SOTA research synthesis | `../research/agent-git-flow-sota-2026-05.md` |
| Production-agent-practices research | `../research/_research-1-production-agent-practices.md` |
| Multi-agent-isolation research | `../research/_research-2-multi-agent-isolation.md` |
| AI-review research | `../research/_research-3-ai-review-single-operator.md` |
| Substrate ADRs | [0006](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0006-multi-agent-human-concurrency-governance.md) · [0007](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0007-multi-agent-orchestration-hierarchy.md) · [0008](https://github.com/usareur-af/goatcore/blob/main/docs/adr/INDEX.md) · [0011](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0011-cluster-worker-execution-environment.md) · [0109](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md) |
| Implementation plan | Block 48 · Block 66 |
| Today's incidents | `af119b9` (shared-index scoop) + PR #1 self-merge — both addressed by this strategy |
