# Multi-agent team management — design

**Status:** SKELETON. Section headers + scope notes; an authoring agent fills in the actual design over Block 48B once the SOTA research at `../research/agent-team-management-sota-2026-05.md` is in.

**Purpose.** Take the chosen orchestration pattern from the research doc and turn it into goat's concrete substrate — what we build, what we change, what tooling extends, what discipline we adopt. ADR [`0007`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/INDEX.md) captures the decision; this doc captures the design.

**Scope.** Coordination layer for 6-10 parallel Claude-agent + human threads working against a single shared trunk with durable-artifact-driven knowledge transfer. Extends — does **not** replace — [ADR 0006](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0006-multi-agent-human-concurrency-governance.md). Out of scope: agent-evaluation tooling, observability beyond what `ops/work/` already exposes, the agent harness itself (Claude Code / Claude Agent SDK is the harness; we don't rebuild it).

**Audience.** Three readers per the [three-audience writing convention](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0003-three-audience-writing.md): the program orchestrator (the load-bearing human), a cluster-captain agent loading this doc as part of its bootstrap, and an SCA-R asking "how do you keep change-control coherent at multi-agent scale?"

---

## 1. Existing primitives — what we lean on

Inventory of the substrate that already works at 2-3 concurrent threads. Block 48 *extends*, doesn't replace:

- [ADR 0006](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0006-multi-agent-human-concurrency-governance.md) + `ops/work/` CLI — pickup / `[track:]` trailer / release.
- Block-clustering pattern — Block 17/18, Block 22, Block 33, Block 40-47 (security-ascent), etc.
- ADR sub-series tags — see [`../adr/INDEX.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/INDEX.md) §"Sub-series tags".
- Trunk-based + signed-commit + Conventional Commits ([ADR 0109](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md)).
- Single-source-of-truth doctrine — CLAUDE.md, [INDEX.md](https://github.com/usareur-af/goatcore/blob/main/docs/adr/INDEX.md), validation-state.md, findings + measurements registers.
- Soak / load / chaos discipline ([ADR 1008](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1008-soak-testing-discipline.md) / [1012](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1012-load-testing-discipline.md) / [1013](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1013-continuous-architectural-chaos.md)) — verifies cluster outputs hold up post-handoff.

What these don't yet cover at 6-10 threads — each is a §3 sub-section.

---

## 2. Hierarchy

The chosen hierarchy shape, three named tiers (or whatever the research doc lands on):

### 2.1 Program orchestrator
- Single entity (human + assistant pair). Owns: cross-cluster prioritization, decision-dedup arbitration, daily status review, scope-shape calls.
- Does NOT: write code in clusters it's orchestrating.
- Daily inputs: `work cluster status` rollup, `work decisions pending`, exceptional-events from clusters.

### 2.2 Cluster captain
- One per Block-cluster (or per ADR sub-series). Agent or human. Owns: decomposing the cluster into tracks, spawning workers, integrating outputs, surfacing decisions to program orchestrator.
- Loads: this design doc, the cluster's design doc, the cluster's section of implementation-plan.md, the captaincy template (TBD §6).
- Issues `work cluster register <name> --captain <agent_id> --scope <blocks>` at start; `work cluster release` at end.

### 2.3 Worker
- One per active track (sub-block). Agent or human. Owns: a single block of executable work end-to-end.
- Loads: a role-prompt (researcher / planner / implementer / reviewer / integrator) + the cluster captain's scope contract for the track.
- Picks up via `work pickup <track>`; commits with `[track:]` trailer; releases via `work release`.

### 2.4 Spawn rules
- Program → cluster: explicit registration; one captain per cluster.
- Cluster → worker: cluster captain spawns worker with role-prompt + scope contract.
- Worker → sub-worker: not allowed in v1 (avoid hierarchy creep). Workers that need help return to captain.

---

## 3. Interface contracts between clusters

How clusters that share substrate (e.g., Block 33 relay protocol used by Block 40 reproducible builds; security-ascent cluster's Block 47 reading every other cluster's invariants) coordinate without fratricide.

### 3.1 Cluster contract template
- **Cluster name:** ...
- **Outputs:** named artifacts (file paths / ADR numbers / Block stubs / library APIs) the cluster produces.
- **Inputs:** named artifacts the cluster reads from other clusters.
- **Verification:** how a downstream cluster verifies an upstream output is ready (file presence + ADR Accepted + soak-driver passing + measurement evidence).
- **Versioning:** how upstream signals breaking change to downstream.

### 3.2 Cross-cluster touchpoints registry
- Lives at `../project/active-work.yaml` under a new `cluster_contracts:` key (or sibling file).
- Each contract is one entry; contracts are Backlog / Proposed / Accepted in lockstep with the cluster's anchor ADR.

### 3.3 Shared-file conflict avoidance
- Files known to be shared across clusters (CLAUDE.md, INDEX.md, GLOSSARY.md, implementation-plan.md, MEMORY.md, validation-state.md): every edit goes through a `work file claim` (TBD §5) before touching.
- Other files: track-grain pickup is sufficient.

---

## 4. Decision-deduplication

When two threads independently raise the same architectural question.

### 4.1 Pending-decisions queue
- Captain or worker that hits an unresolved architectural question writes an entry to `work decisions pending` (new command).
- Program orchestrator scans the queue daily; arbitrates or consolidates duplicates.

### 4.2 Debate-then-judge for design-shape questions
- Two captains independently sketch a candidate design; program orchestrator (with optional debate-judge agent) picks one, OR directs a synthesis.
- Decision lands as a single ADR; loser's branch deleted; lessons captured as feedback memory if they're durable.

### 4.3 Anti-pattern: parallel ADR drafting
- Hard rule: an ADR number cannot be claimed by two threads. The pending-decisions queue is the dedup layer; ADR numbers are not assigned until the program orchestrator resolves the dedupe.

---

## 5. `ops/work/` CLI extensions

New commands and schema additions. Implemented in Block 48C.

### 5.1 Cluster commands
- `work cluster register <name> --captain <agent_id> --scope <blocks> [--contracts <contract_id,...>]`
- `work cluster status <name>` — rollup: tracks under cluster + each track's status + blockers.
- `work cluster release <name>`

### 5.2 Role commands
- `work role list`
- `work role load <name>` — emits the role-prompt to stdout for an agent harness to inject as system prompt.

### 5.3 File-claim commands
- `work file claim <path> --until <eta> [--track <name>]`
- `work file release <path>`
- Pre-commit hook warns on commits to claimed files by non-claimant.

### 5.4 Decision-queue commands
- `work decisions submit <title> --cluster <name> [--summary <text>]`
- `work decisions list`
- `work decisions resolve <id> --as-adr <number> | --as-duplicate <id> | --as-deferred`

### 5.5 Schema additions to `active-work.yaml`
- `clusters:` map (name → captain, scope, contracts, started_at, status).
- `pending_decisions:` list.
- `file_claims:` list.

---

## 6. Role-prompt registry

Each role lives at `ops/work/roles/<role>.md` as a Markdown file with a known shape:

### 6.1 Roles in v1
- `cluster-captain` — decomposes cluster into tracks, spawns workers, integrates.
- `researcher` — produces SOTA artifact / survey / spike code; outputs are durable docs.
- `planner` — produces Block stub / sub-block tables; outputs feed implementation-plan.md.
- `implementer` — produces code + tests; outputs are PRs.
- `reviewer` — consumes a worker's output, returns approve / change-request / blocked.
- `integrator` — merges worker outputs into a cluster deliverable; owns the final commit-and-PR.

### 6.2 Captaincy template + per-cluster kickoff memo
- **Captaincy role-prompt** — one file at `ops/work/roles/captaincy-template.md`. Loaded by every captain at session start. Contains: kickoff prompt, decision-tree references, role-prompt registry pointers, status-rollup format. CONSTANT across all captains; cluster-specific content does NOT live here.
- **Per-cluster kickoff memo** — one file per cluster at `../project/cluster-kickoffs/<cluster-name>.md`, filled from `../project/cluster-kickoffs/TEMPLATE.md` at cluster spawn. Contains: cluster identity, scope contract, deliverables, dependencies (incl. H-actions), worker spawn plan, **cluster-specific routing table** (named identities per §6.5b), operational rules, mechanism specifics, pre-flight gate checklist, done criteria, decision log, companion artifacts. **Cluster work does NOT begin until the captain runs the §9 pre-flight gate checklist and every box checks.** Index of all spawned clusters at `../project/cluster-kickoffs/INDEX.md`.
- **Captain reads BOTH at session start.** Role-prompt provides the constants; kickoff memo provides the specifics. Together they replace what would otherwise be a multi-doc-scrolling-and-re-deriving exercise on every session.

### 6.3 Inheritance
- Every role-prompt inherits CLAUDE.md by reference (not copy) — the captain or worker's harness loads CLAUDE.md as project instructions, then the role-prompt as additional system context.

### 6.4 Worker-discipline mechanisms — load-bearing on every role-prompt

Every role-prompt (captain + all worker roles) loads this set of five mechanisms at boot. These exist to catch the specific failure modes that destroy autonomous multi-agent work — drift, theatrical productivity, hypothesis-theater, abandoned mainlines, plausible-but-ungrounded synthesis — without suppressing the good behaviors agents naturally exhibit. **Composed deliberately to interact** rather than stack (each mechanism's failure mode is caught by another).

#### 6.4.0 Deploying a shared role is a WRITE nobody reports

Session isolation protects the *repo*. It does not protect the *host*. Two
sessions on separate worktrees can deploy the same Ansible role to the same
machine minutes apart, and each render silently drops whatever settings the
other's tree did not carry — because role rendering is whole-file and **no
Ansible run reports what it removed**. `changed=1` says the file differs, not
which direction, so the play output of a run that deleted another operator's
live configuration is indistinguishable from one that added its own.

Two rules follow, and the second is the one that is easy to get wrong:

- **A deploy is a pickup-worthy write.** Read-only exploration does not need a
  track; putting a file on a shared production host does. Check `work list`
  before deploying a role, not before editing it.
- **Carrying the other session's variables is not enough.** A role change can
  live in the template too. Reconciling only the `group_vars` half looks like
  success and drops the rest — that is precisely how the second repair attempt
  in F-410 left every cert mint failing. Deploy from a tree carrying every
  merged change to that role, which after anything merges means from `main`.

#### 6.4.1 Fast/slow inchworm (anchor mechanism)

Two motions taken in sequence, never collapsed into one:
- **Fast move** — a narrow probe or fix that produces a definitive answer to a specific question. Throwaway quality acceptable; speed is the priority. ~5-30 min cycle. Output: a specific yes/no to a specific question, not a production artifact.
- **Slow move** — durable codification of what the fast move learned. Production quality; hours-to-days cycle. Output: an ADR, role, finding, test — something the next contributor reads instead of re-deriving.

**Hard rule:** never use a long playbook run / full soak / production-shape mechanism as the *validation step* for a hypothesis. The validation is the smallest possible probe; the production-shape mechanism comes later as the codification, when we know what we're codifying.

**Anti-patterns the inchworm forbids** (verbatim from `tech-strategy.md` §"The fast/slow inchworm"):
- Comprehensive solution to an unmeasured problem (full Ansible role for an issue we don't yet understand).
- "Fast move" that becomes permanent (throwaway probe script ends up running in production untracked).
- Slow move with no fast move first (production-quality code against an unvalidated hypothesis).
- Slow move skipped entirely ("I figured it out — moving on").

**Canonical capture:** `docs/design/tech-strategy.md` §"The fast/slow inchworm — workflow discipline that makes the principles operationally feasible." That doc is authoritative; this section is the substrate-elevation pointer. **Role-prompts MUST cross-reference the tech-strategy.md section** so workers load the full empirical motivation, not just the rule.

**Operational tell at the reviewer-role gate:** any commit that is the validation step for a hypothesis AND is not a small probe is suspect. Reviewer asks: "what was the fast move? what did it tell us? where's the slow move codifying it?"

#### 6.4.2 Hypothesis-first with falsifiability gate

Before any fix attempt: state the hypothesis. The hypothesis must predict an *observable*. After the attempt: was the predicted observable observed?

**Acceptable:** "If I add this field, the next request will return header X instead of Y."
**Not acceptable:** "I think this fixes the bug" / "this should work" / "let me try X."

Reviewer-role gate rejects PRs that ship without a falsifiable predicted-vs-observed pair in the commit message or PR description. Catches plausible-sounding-but-ungrounded synthesis — the most expensive Opus failure mode.

**Composes with inchworm:** the *fast move* IS the falsifiability check. Predict observable → run probe → observe → answer is yes/no. The two mechanisms reinforce each other.

#### 6.4.3 Progress-shape spin-detection

Halt criterion based on **whether the hypothesis space is narrowing across attempts**, NOT time elapsed and NOT attempt count.

At each checkpoint (typically per-attempt or per-N-tool-calls), worker answers: *"what's narrower in my understanding now than at the previous checkpoint?"* If the answer is "nothing" — automatic halt + reassess. Three attempts that each disprove a distinct hypothesis is healthy progress; ten attempts that permute the same approach is a halt signal at attempt 4.

**Why time and attempt-count fail:** time penalizes legitimate slow progress on hard problems; attempt-count misses spinning-fast-without-progress. Progress-shape gets at the actual signal.

**Reassessment shape on halt:** re-read the original task; write down what's been tried; write down what's known now that wasn't known at start; write down a fresh hypothesis OR escalate to captain with "I'm stuck and here's why."

#### 6.4.4 Minimal-surface preference (preserves healthy laziness)

Before any non-trivial implementation: *check for the smallest possible change that solves the problem*. Mandatory pre-flight question: **"Have you considered a config change?"** Then: existing primitive? One-line fix? Refactor of a single function? Module creation requires explicit justification — *why won't a smaller change suffice?*

This mechanism *preserves* healthy laziness — the engineer's most valuable instinct, the one that finds the config-line change before building a module. Module creation defaults to NOT happening unless the worker can articulate why a smaller change can't.

**Operational tell:** any PR creating new modules, files, or abstractions without a one-paragraph justification of "why not a smaller change" is rejected at the reviewer-role gate.

#### 6.4.5 Mainline tenacity (anti-theater discipline)

When the critical mainline path is the right path AND minimal-surface preference (§6.4.4) has confirmed no simpler path exists, **stay on the mainline.** Do not pivot to peripheral changes that *look like productivity* (add some logging and hope; refactor a side-thing while the bug remains; rename things to seem busy).

When the mainline is hard, bring **fresh creative rigor** to the same problem — not the same approach repeated, and not avoidance.

**Distinguish:**
- *"This is hard"* → deserves more rigor (mainline tenacity invoked).
- *"This is wrong"* → deserves a deliberate pivot, with the new path's correctness named explicitly.

**Decision tree when stuck:**
1. **Minimal-surface check first** (§6.4.4) — cheap; healthy laziness gets first turn.
2. **Mainline-validity check** (if minimal-surface yields nothing) — does succeeding on the current path actually solve the user's ask? If no → pivot deliberately, name *why* the original framing was wrong.
3. **Mainline tenacity** (if mainline is validated correct) — bring fresh creative rigor; do not theater-pivot.

**Operational tells the reviewer-role flags as theater (auto-reject):**
- Diff modifies files unrelated to the named hypothesis.
- Worker generated logging / instrumentation without naming what observable it would disambiguate.
- Refactor or rename in the same PR as the bug fix (real fixes are diff-minimal; theater fixes spread).
- Hypothesis abandoned without disconfirmation evidence in the commit message.
- Adding features while the assigned bug remains unfixed.

**Composes with all five others:** inchworm gives you the fast probe to validate the mainline IS right (not theater); hypothesis-first ensures the rigor reapplied is grounded; spin-detection catches when "tenacity" has degraded into bashing; minimal-surface prevents over-engineering when the right answer was small all along; two-hat refactoring discipline (§6.4.6) keeps the diff-minimality property of real fixes enforceable at commit time, not just culturally hoped-for.

#### 6.4.6 Two-hat refactoring discipline

At any commit boundary, the worker is wearing exactly one of two hats: **refactoring** (restructure code; behavior unchanged; tests pass before and after where they exist) or **adding-feature** (change behavior; new capability or bug fix). **Never both in the same commit.** The two hats are interleaved in time — Beck's *make the change easy, then make the easy change* — but each commit is single-hat.

**Why this is load-bearing for autonomous workers specifically:** an LLM worker's natural failure mode is to "tidy as I go" — the diff mixes a rename with a logic change with a small refactor with the actual fix. The result is *structurally unreviewable*: the captain / reviewer cannot tell which lines preserved behavior and which changed it. Revert granularity is lost. The fix gets shipped but the silently-introduced behavior change goes undiagnosed for weeks.

**Hard rule.** If a worker decides mid-task that adjacent code needs cleanup, the cleanup is a separate commit, ideally landing **before** the feature commit (preparatory refactor, per Beck). Stage the refactor → run tests / smoke → commit → stage the feature change → commit.

**Anti-patterns the reviewer-role flags as auto-reject:**
- Commit message conjunction: "refactor X and fix Y" / "cleanup and add Z."
- Diff modifies a function's outputs AND moves code blocks with no semantic change.
- Tests changed in the same commit as a refactor (if behavior preserved, why did the test change?).
- "While I'm here" diffs touching unrelated files under a single fix label.
- New abstraction landing in the same commit as the second caller of it (rule-of-three violation — wait for the third).

**Composes with §6.4.5 mainline tenacity.** §6.4.5 already flags "refactor or rename in the same PR as the bug fix" as theater; §6.4.6 elevates that anti-pattern to a positive discipline — name the hat at commit time, never mix.

**Composes with §6.4.4 minimal-surface preference.** A refactor *to enable a feature* must justify itself the same way a new module would: was the smaller change considered? Preparatory refactor is acceptable when the feature commit would otherwise be unreviewably large; refactor-for-its-own-sake during a feature task is rejected.

**Composes with §6.4.1 inchworm.** The fast move asks "does this hypothesis hold?" The slow move codifies. Refactoring discipline determines *how* the slow move lands: the codification commit is feature-hat; any cleanup that makes the codification possible is a separate refactor-hat commit landing first.

**Canonical reference:** `docs/design/tech-strategy.md` §"Refactoring discipline — two hats, never both at once" carries the full theory (Fowler's definition, Beck's two-hat principle, Metz's rule of three, Henney on read-vs-write asymmetry). **Role-prompts MUST cross-reference that section** so workers load the full theory, not just the rule.

#### 6.4.7 Late-context vigilance (interim mechanism)

Captain-side check for the worker-degradation pattern empirically observed at ≥~70% context fill: passive complaints about scope; instruction-drop relative to earlier in the session; hedging on tasks the worker handled cleanly before; sloppy diff hygiene (missing trailers, stale doc cross-references, dropped sub-tasks); suggestions to "continue tomorrow" on work the worker would have completed cleanly mid-session. Built-in auto-compaction is the existing mitigation and is sometimes — empirically — insufficient.

**Honor-system convention** (no automation; complements existing tooling):

- **Worker self-flag.** Late in a session (≥ ~70% context by self-assessment, or after auto-compaction has fired once), worker adds `[ctx-state: stretched]` to the commit trailer alongside `[track: ...]`. Default state is omitted (warm). Trailer convention extended in [ADR 0006](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0006-multi-agent-human-concurrency-governance.md) §"Commit-message linkage."
- **Captain routing.** PRs / commits with `[ctx-state: stretched]` route to a differentiated-review path — captain reviews with extra scrutiny for the tells above. Captain may rotate the worker out mid-session if tells are present, rather than fighting through degraded output. The replacement session starts with a captain-prepared handoff packet (track scope + recent commits + open question), preserving substantive state at the cost of warm cache.
- **Captain proactive option.** On long-running single-worker tracks (>~4 hours), captain may schedule a worker rotation regardless of `[ctx-state]` self-report — costs handoff overhead, buys reset of accumulated drift.

**Why interim, not load-bearing.** Both halves rely on self-report (worker correctly flagging stretched state) and captain attention (noticing tells in review). Both faculties are exactly what context-fill degrades — so this mechanism is **not** clear-net-positive in isolation. It ships as a vocabulary + routing convention so the eventual pilot has a baseline to measure against. Does not graduate to a load-bearing §6.4 mechanism without the Block 48K pilot harness yielding evidence per §6.5 net-positive rule.

**Composes with §6.4.3 progress-shape spin-detection.** Spin-detection catches stuck-on-problem; late-context vigilance catches degraded-faculties on a problem the worker would have handled fine earlier. Distinct signals; both can fire on the same track.

**Composes with [ADR 0006](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0006-multi-agent-human-concurrency-governance.md) opt-in coordination.** Stretched flag is opt-in; absence is normal. No commits are blocked. Honor-system, additive — fits the existing pre-commit-warns-not-blocks posture.

#### 6.4.8 Bus delivery contract — posting is not delivery; the hook is

The session bus ([ADR 0012](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0012-session-bus-event-layer.md), `ops/work/work bus`) was write-only in practice for its first three months: sessions posted claims / handoffs / context, but no session ever *received* a message unless the operator noticed it and pasted it in by hand (observed 2026-08-11: a directed hand-off message sat unread until manually relayed). The structural fix, live since track `bus-delivery-hook`:

**The contract.** Posting an event to the bus is durable *record*, not delivery. **Delivery happens when the reader session's `.claude/hooks/session-bus-tail.sh` hook fires** — at `SessionStart` (catch-up on events that arrived while the session didn't exist, bounded to the last 24 h) and on every `UserPromptSubmit` (incremental since the session's per-session cursor). A sender who needs *confirmation* of delivery uses `work bus ack <ts>` from the receiving side, which emits an info event directed back at the sender.

**Injection policy** (token-cost-bounded by construction): `urgent` + `warn` always inject; `info` is capped to the N most recent (default 5, `GOAT_BUS_INFO_CAP`) with an omitted-count line; the empty case emits nothing and costs zero tokens. The cursor advances on every fire, so nothing is injected twice.

**Directed messages.** A message whose text contains `TO session <id>` or `TO track <name>` is always injected for the addressed session/track, cap or no cap, and is flagged `(ADDRESSED TO THIS SESSION)`. Emit canonically with `work bus info|warn|urgent --to session:<id>` or `--to track:<name>` (the CLI writes the canonical `TO session <id>: ` prefix). Session ids are visible in every injected event and in `work bus tail` output.

**Subagents inherit nothing.** Hook context lands in the parent session only — a spawned subagent never sees the bus. The parent is the delivery point; a subagent that needs bus context must be handed the relevant excerpt in its spawn prompt. Symmetrically, a subagent's `work bus` emits are attributed to the parent's session id.

**Failure mode is the pre-fix status quo:** if the hook errors or isn't wired, events still land durably in the JSONL; coordination degrades to manual `work bus tail`. Regression fixture: `.claude/hooks/tests/session-bus-tail-tests.sh`.

**Sender identity was broken until 2026-09-05, which changes how to read bus history.** `work bus` stamped `p<ppid>` whenever `$CLAUDE_SESSION_ID` was unset — and Claude Code exports `CLAUDE_CODE_SESSION_ID` instead, while running every Bash tool call in a fresh shell. The id therefore changed on every emit (157 events in one bus file, ~155 distinct ids), so own-event filtering never matched and `--to session:<id>` never reached its addressee. Only `warn`/`urgent` and `--to track:<name>` landed, which is why the history over-uses `warn`. Fixed in `busSessionID()` + the hook's fallback chain; ids minted before that date are not addresses. Measured detail: [session-bus.md](session-bus.md) §"Sender identity".

**The bus is keyed per clone, and the two goat clones are the same repo.** All of one measured day's traffic sat on the mirror clone's bus while the primary clone's carried 22 events; a session posting from the primary reached nobody. Open question in [session-bus.md](session-bus.md); until it is settled, a post that must reach everyone is posted from each clone.

**Agent-facing usage** — which level to pick, how to address, what is worth posting, the 2 KB and 60 s limits — is the `/bus` skill (`.claude/skills/bus/SKILL.md`).

### 6.5a Boundary classification — what work agents pick up vs human-only

Naive "agents do everything; ask for help when stuck" degenerates. Stoic-pushing-through and cargo-cult escalation are both fail modes. The substrate classifies work BEFORE pickup into one of three eligibility tiers, with bias-toward-asking when unclear.

**Eligibility tiers:**
- `agent-eligible` — worker can pick up and execute end-to-end.
- `captain-eligible` — captain handles directly (no worker delegation).
- `human-only` — agents do not pick up; routes to a designated human per §6.5b.

**Seven classes of human-only work** (any one of these classifies a track as `human-only`):

| Class | What | Examples in goat | Routing default |
|---|---|---|---|
| **C1 — Strategy / values / policy judgment** | Tradeoff calls where the *decision* (not just analysis) requires human authority | Block prioritization; scope-shape calls; "ship X or Y first" | Program orchestrator |
| **C2 — Cross-organizational / interpersonal** | Trust, relationship, accountability that doesn't transfer to an agent | Partner federations; vendor procurement; contractor engagement | Human relationship-owner |
| **C3 — Hardware / physical-world / one-shot ops** | Cannot be delegated; agent prepares procedure, human executes | YubiKey ceremonies; on-site work; power-cycle; NVMe swap | On-site team / designated operator |
| **C4 — Novel / unprecedented architectural calls** | No prior art; multiple valid approaches; hard-to-reverse | First-time subsystem touch; new partner integration; new substrate decision | Program orchestrator + domain expert |
| **C5 — High-blast-radius / hard-to-reverse** | Already covered by system-prompt safety rules; in autonomous teams the bar is *higher* | Production push; force-push to main; credential rotation; partner-facing email | Program orchestrator (always) |
| **C6 — Senior-engineer-judgment problems** | Depth + calibrated intuition the agent can scaffold but not replace | 30-year-old OS assumption violations; logs that fit no pattern; bug reports contradicting docs | Designated tech lead |
| **C7 — Trust / security / compliance signature** | Even when agent articulates the right answer, the *signature* needs to be human | Offline CA touch; secret exposure; accreditation posture; compliance review | Security/compliance reviewer |

**Pre-pickup classification** is the captain's first action on a new track. New field in `active-work.yaml`: `eligibility: agent | captain | human-only` + `class: <none|C1..C7>`. **Default when unclear: `human-only`** — bias toward asking, not toward acting. Mis-classification is caught by:
- Worker hitting an in-flight escalation trigger (the work was actually class-N, not agent-eligible).
- Reviewer-role catching scope outside agent-eligibility at PR time.
- Captain spot-checking the classification rubric weekly; tracking false-positive rate (work classified human-only that an agent could have handled) and false-negative rate (work classified agent-eligible that landed sub-optimally) to refine the rubric over time. **Rubric refinement IS the load-bearing pilot validation — see §6.5d.**

**In-flight escalation triggers** (when a track crosses a boundary that wasn't obvious at pickup):
- Three consecutive halts under §6.4.3 progress-shape spin-detection — strong signal it's class C4 or C6.
- A single-line fix would change a load-bearing invariant — class C1.
- Natural diff exceeds threshold of cross-cluster touch — class C4.
- Worker about to make a decision that names a value/policy choice — class C1.
- Work hits a class-C7 surface (offline CA, secrets, compliance) — automatic halt.
- **Cost-budget tripwire** (carefully scoped): if estimated cost exceeded by ≥3× AND progress-shape detection has fired ≥2 times in this track, escalate by *cost-of-continuing*, not by time elapsed. Three soak-runs of "let me just try one more thing" is the autonomous version of cloud-burn loop.

**Pushback affordance** (often forgotten — not gatekeeping): agents must also be willing to push back on humans who hand them work that's miscategorized. *"I think this is human-only because X; before I proceed, can you confirm or reclassify?"* The bidirectional flow prevents the human from accidentally treating the agent as a yes-machine for class-C1/C2/C4/C6/C7 work. Distinct from `feedback_no_gatekeeping.md` (which forbids unwarranted gatekeeping on already-decided shipping calls); pushback on miscategorization is praised, not penalized.

### 6.5b Routing-to-right-human table

The right human is rarely "the program orchestrator." Cluster-captain role-prompt knows the routing table:

| Class | Right human | Pager severity | Interactive medium |
|---|---|---|---|
| C1 strategy/values | Program orchestrator | sev-2 | GitHub Issue |
| C2 cross-org | Relationship-owner | sev-3 | GitHub Issue (or directly external comm) |
| C3 hardware/physical | On-site team | sev-1 | Matrix room (real-time coordination) |
| C4 novel architectural | Program orchestrator + domain expert | sev-2 | GitHub Issue (often spawn Claude Code session for deep diagnostic) |
| C5 high-blast-radius | Program orchestrator | sev-1 + PagerDuty if available | GitHub Issue |
| C6 senior-engineer judgment | Designated tech lead | sev-2 | GitHub Issue |
| C7 trust/security/compliance | Security/compliance reviewer | sev-1 | GitHub Issue + audit-log entry (Block 17D) |

Specific human-id assignments per role are a §11.5 EXTERNAL ACTION — only humans can decide who plays each role for goat's organizational reality.

### 6.5c Escalation interaction medium — pager + interactive layers

Two distinct concerns; do not collapse them. Pager has different requirements than interactive medium.

**Pager layer (asynchronous attention-getting):**

| Severity | Triggers | Recommended pager | Why |
|---|---|---|---|
| **sev-1 (≤1 min response)** | Class-C5 about-to-be-destructive; class-C7 trust/security; production-incident-class | **Matrix priority-room with mobile push** (Element on phone) — sovereign, already deployed per [ADR 0812](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0812-per-site-matrix.md). **Optional PagerDuty escalation** for after-hours / degraded-connectivity coverage if the org already pays for it | Matrix is sovereign; PagerDuty's SMS + voice fallback is the differentiator for genuinely degraded data conditions |
| **sev-2 (≤30 min response, in-hours)** | Class-C4 architectural; class-C6 senior-judgment; class-C1 strategy in-hours | **Matrix room @-mention** in per-cluster room | Discriminates from sev-1 by room (different push profile); doesn't wake at 3am |
| **sev-3 (hours-acceptable)** | Class-C2 cross-org; class-C1 batch; routine | **GitHub @-mention** on the escalation issue + Matrix daily-batch summary | Lower-friction; in-band with the work |

**Sovereign sev-1 alternative:** **ntfy** (free, self-hosted, supports topics + priority + mobile push via FCM/APNS) layered on top of Matrix — covers most cases without PagerDuty's seat cost. ntfy is IP-push only (no SMS/voice fallback); for genuinely-degraded-connectivity scenarios PagerDuty's premium is the differentiator. **Recommendation: Matrix Element push + ntfy as defaults; PagerDuty as optional add-on for after-hours/degraded coverage. Operate ntfy and PagerDuty as peers, not fallbacks** — see `failure-isolation.md` §9 for the SRE-pager equivalent of this peer pattern.

**Interactive medium — GitHub Issue with structured "Escalation" template:**

- **Title:** `[escalation/<class>] <track-name> — <one-line question>`
- **Body:** structured packet (Question / What I know / What I've ruled out / What I'd lean toward / What I need from you).
- **Assignee:** routed-to human per §6.5b table.
- **Linked from:** `active-work.yaml` track row with `escalation_issue: <github-issue-url>` field.
- **Pinned in:** the cluster integration branch's PR description (if Pattern B per §10).
- **Resolution:** human responds in thread → agent updates packet with resolution + closes with link to commit / ADR / PR / re-classification artifact.

**Why GitHub Issues over alternatives** (Matrix room thread / Slack / direct Claude Code session / email / custom UI): in-band with work; persistent + searchable; threaded; markdown + code blocks; @-mention routing; auto-links to PRs by number; visible to all agents on cluster (prevents repeat-escalation); mobile GitHub app push. Reject Slack on Block-30 sanitization grounds (third-party diff exposure same concern as CodeRabbit); reject custom UI on minimal-surface preference.

**Composing the two layers — the pager → interactive flow:**

1. Agent hits escalation trigger.
2. Agent opens GitHub Issue with structured escalation packet → assigned to routed-to human.
3. Agent posts to Matrix at the right severity tier with one-line summary + link to the GitHub Issue (and to ntfy topic if sev-1).
4. Human's mobile gets push (Element / ntfy app / PagerDuty if wired). Human reads the Matrix one-liner or ntfy notification, taps through to the GitHub Issue for full context.
5. Human responds in the GitHub Issue thread (rich diagnostic conversation).
6. Issue resolution links to the durable artifact (commit / ADR / PR / re-classification).

GitHub does the persistence + rich interaction; Matrix and ntfy do the urgency + push fidelity. Each tool plays to its strength.

### 6.5d Pilot-validate the rubric (load-bearing per §6.5)

Per the §6.5 net-positive governance rule: the seven-class classification rubric is **tactical/observational** — failure modes shift as Claude model behavior shifts. **Pilot the rubric specifically:** track classification accuracy (false-positive rate where work was classified human-only but agent could've handled; false-negative rate where work was classified agent-eligible but should've been human-only). Adjust weekly until rates stabilize. The rubric is the *substrate's most likely drift surface* — refresh on the same 6-month cadence as other tactical claims per `../research/agent-team-management-sota-2026-05.md` §0.

---

### 6.5 Net-positive-only governance rule (meta — load-bearing)

**No mechanism ships from theory; all ship from evidence.**

Every governance mechanism in this substrate must demonstrate clear-net-positive in pilot before adoption. *(benefit of catching the failure mode it targets) − (overhead it adds + good behavior it suppresses + new failure modes it introduces) > 0 over the mechanism's full lifecycle.* Equilibrium and negative outcomes are forbidden, even when the mechanism "feels responsible."

**Pilot methodology** — same shape as goat's soak / load / chaos discipline applied to substrate itself:

1. Run a cluster pilot WITHOUT the mechanism. Capture observed failure modes by name with evidence (commit traces, time-to-deliverable, captain interventions needed).
2. Add ONE mechanism. Run another cluster pilot. Measure differential:
   - Did the named failure mode reduce?
   - Did good behavior or net work-output suffer?
   - Were any new failure modes introduced?
3. Adopt only when differential is clear-net-positive across **2+ pilots**.

**Pilot-validate watchlist (mechanisms NOT yet adopted; must clear the bar before shipping):**
- **Pre-mortem-on-spawn with prediction-tracking.** Captain → worker spawn contract includes a one-line pre-mortem ("if this fails, the most likely failure mode is X"). At task completion, did the predicted failure mode actually occur? **Drop if predictions consistently don't match outcomes** (becomes checkbox theater). **Adopt if matches** (earning its keep).
- **Captain-side intervention triggers.** Net-positive only if the captain brings *fresh information* (broader context, different angle, cross-worker awareness). Track intervention outcomes; **drop if >80% of interventions are no-op "keep going carefully"** (delegation theater); **adopt if interventions consistently produce concrete redirection** (genuine signal).
- **Context-fill behavioral degradation tripwire.** Three variants pilot-tested against a no-risk known-good-end-state problemset of appropriate complexity: (a) **default** — auto-compaction only, no behavioral signal; (b) **proactive** — rotate worker at fixed context-fill threshold regardless of behavior; (c) **reactive** — captain rotates on tells per §6.4.7 (instruction-drop, passive complaints, sloppy diff hygiene). Per Block 48K. **Drop if the harness shows default is sufficient** (auto-compaction handles the regime); **adopt the variant with clearest differential** if proactive or reactive net-positive. Interim §6.4.7 ships ahead of pilot to give the harness a vocabulary baseline; this watchlist entry resolves at pilot verdict.

**The "config-line change" test as a first-class invariant.** Any proposed mechanism that would suppress an agent's instinct to look for a single-line fix instead of building a module is **automatically rejected**. Healthy laziness preserved by construction.

**Mechanisms explicitly DROPPED at this design** (do not re-propose without new evidence):
- **Time-budget tripwires** — wrong metric. Time penalizes legitimate slow-progress on hard problems and misses spinning-fast-without-progress. Replaced by §6.4.3 progress-shape spin-detection.
- **LLM-judge laziness-detector** — heaviest mechanism, weakest evidence base, biggest risk of false-positives suppressing healthy behavior. Don't adopt without pilot data showing it catches real drift more than it kills real work.

---

## 7. Status aggregation

How the program orchestrator sees what's happening across 6-10 threads.

### 7.1 Daily rollup
- `work cluster status --all` runs once daily; output is shape-stable Markdown.
- Posted to a fresh entry in `docs/reports/daily-status/<YYYY-MM-DD>.md`.

### 7.2 Exception escalation
- Captains push exceptions to the program orchestrator out-of-band — failed soak, unresolvable decision, scope re-shape proposal. New `work exception submit` command.

### 7.3 Health metrics
- Per-cluster: % sub-blocks complete, average track age, exception count last 7 days, soak-pass rate.
- Threshold for "cluster needs attention" is named in the ADR.

---

## 8. Conflict-resolution protocol

What happens when two tracks legitimately need to touch the same file outside the file-claim window.

### 8.1 Three classes
- **Trivial overlap** (different sections of same file) — second mover rebases over first; pre-commit hook flags both tracks for review.
- **Semantic overlap** (different changes to same section) — both tracks pause, captains synthesize, single PR lands; merge conflict resolved at write time, not at git-merge time.
- **Decision conflict** (the change implies different architectural calls) — escalated to program orchestrator via decision-queue (§4).

### 8.2 Pre-commit hook extension
- Existing hook from ADR 0006 warns on missing `[track:]` trailer.
- Extended: warn when a commit touches a file claimed by a different track; warn when a commit touches a known-shared file without a fresh `work file claim`.

---

## 9. Failure modes + watchlist

- **Captain capacity collapse** — captain agent's context bloats with worker outputs; mitigation is structured-deliverable handoff (workers submit final-form artifacts only, not raw exploration).
- **Decision-queue starvation** — program orchestrator misses a daily review; mitigation is `work decisions list --stale 24h` automation + isitup tile.
- **Role drift** — workers operating outside their role profile; mitigation is reviewer-role gate before every PR.
- **Substrate gold-plating** — temptation to keep refining the substrate instead of doing actual work; mitigation is hard 9-11 day budget on Block 48 + ban on substrate changes during month 1 except via emergency-decision path.

---

## 10. Branching strategy + git tier mapping

Foundation stays **trunk-based per [ADR 0109](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md)** — single `main`, signed-commit, squash-merge, conventional commits, CODEOWNERS-routed review, merge queue once the team passes the >3-active-contributor threshold. Block 48 layers a per-cluster integration-branch pattern on top, scoped tightly so we don't pay the merge-complexity cost where it isn't needed.

### 10.1 Two-pattern model

**Pattern A — Track branch direct to `main` (default).** Worker creates `track/<track-name>` (matches the `[track:]` trailer name from ADR 0006), commits, opens PR direct to `main`. Captain reviews; merge queue handles the merge. Same shape we run today. **Use when:** track is short (≤ 3 days, ≤ 2 PRs).

**Pattern B — Cluster integration branch `cluster/<name>`.** Captain creates the long-lived integration branch at cluster kickoff. Workers PR into the cluster branch (`track/<...> → cluster/<name>`). Captain integrates worker outputs in the cluster branch. Captain PRs `cluster/<name> → main` as a single coherent landing per cluster milestone. **Use only when BOTH:** cluster has ≥ 4 concurrent worker tracks AND scope is multi-week (> 2 weeks).

The two-pattern model maps the substrate hierarchy (program orchestrator / cluster captain / worker) onto the git tier (`main` / `cluster/<name>` / `track/<...>`). Three substrate tiers, three git tiers — clean correspondence.

### 10.2 Cluster-eligibility decision

| Cluster | Pattern | Rationale |
|---|---|---|
| Block 17/18 closeouts | **B (cluster branch)** | 7+ sub-blocks, multi-week, multi-captain potential |
| Block 21 Ory wire-up | A (track branches) | 3 sub-blocks (21C / 21D / 21F), each clean unit |
| Block 22A-F silent plane | A (track branches) | 6 sub-blocks but each is a clean PR |
| Block 27 wide events | **B (cluster branch)** | 5 sub-blocks (27A spike + 27B-E), schema reservations span PRs |
| Block 28 WASM | A (track branches) | 6 sub-blocks but sequential, not concurrent |
| Block 33 relay | **B (cluster branch)** | Multi-week + protocol changes span many PRs (already in-flight pattern) |
| Block 35 video | **B (cluster branch)** | 4 spikes + ADR + storage work; multi-week |
| Block 36 / 37 / 38 | A (track branches) | Each is one substantial PR, not a cluster |
| Block 39 netbird-watch | A (track branches) | Small scope |
| Security-ascent (40-47) | A (track branches) | Each block is a clean unit, sub-blocks PR independently |

Borderline calls are A by default (B has real cost; only opt in when the gain is clear).

### 10.3 Branch-protection rules

- **`main`** — required: signed-commit, ≥ 1 CODEOWNER review, all required checks pass, conventional-commit title, linear history (squash-merge only).
- **`cluster/<name>`** — required: signed-commit, captain review (single approver OK since captain owns the cluster), CI passes; **NOT** required: full CODEOWNER review (that happens at the `cluster/<name> → main` PR).
- **`track/<track-name>`** — no branch protection; track-level discipline lives in `[track:]` commit trailers.

### 10.4 CODEOWNERS extension

CODEOWNERS gains per-cluster captain assignments at cluster kickoff. Pattern: `# cluster/<name>` section header followed by path globs that route to the cluster captain's GitHub identity. When the captain is an agent, it routes to a designated human reviewer who owns the captain's output. **Per-cluster captain identity is a §11.5 EXTERNAL ACTION before scale-out.**

### 10.5 Tradeoffs explicitly named

- Cluster branches add merge complexity (rebase or merge from `main` periodically; conflicts surface at integration time, not at track-PR time).
- Cluster branches delay external-visibility into work-in-progress (a downstream consumer won't see the cluster-branch state until it lands on `main`).
- Cluster branches enable atomic cluster milestones (a coherent feature set lands together rather than as 7 sequential PRs).
- Trade is worth it for ≥ 4-worker multi-week clusters; not worth it for short clean clusters.

---

## 11. AI PR review tooling layering

Three signal classes, do not stack overlapping ones.

### 11.1 Signal-class layering

**Class 1 — Semantic / project-context-aware review.** Tool: **Claude Code `/ultrareview`**. Loads CLAUDE.md + reads ADRs + understands the architecture; multi-agent under the hood (program orchestrator runs multiple critic agents); deepest signal class. Per-PR human-triggered; per-session billed against existing Anthropic account. **No third-party diff exposure** — same trust boundary as our regular Claude Code use.

**Class 2 — Per-PR automated nit / security-pattern / style check.** Tool: **CodeRabbit OR GitHub Copilot review — pick exactly one.** They overlap ~70% (line-level nits, common security patterns, style); stacking just drowns signal. Both fire as a GitHub PR check on every push.

**Class 3 — Worker self-review at PR creation.** No external tool — implemented via the reviewer role-prompt in [§6 role-prompt registry](#6-role-prompt-registry). Worker swaps to reviewer role before opening PR; runs structural + invariant checks; surfaces issues to itself; only opens PR when reviewer-role is satisfied. Cheapest signal class because it catches issues before any other reviewer sees them.

### 11.2 Tool selection: CodeRabbit vs Copilot

**Recommendation: CodeRabbit.** Reasons: better OSS posture (matches goat's go-open direction); more configurable noise thresholds (we'll need this — 6-10 parallel PRs at moderate review-noise levels would drown the program orchestrator); per-PR cost model is friendlier than per-seat; AST-grep-style custom rule engine fits goat's invariant-heavy style.

**Copilot is the fallback if** the team is already paying for Copilot seats and the marginal cost of Copilot review is zero, OR a future GitHub Enterprise mandate forces Copilot adoption.

**Hard rule: never both.** Track + reject any PR that runs both — it's the AI-review version of `say(thing); say(same_thing)`.

### 11.3 Block-30-sanitization gate (CRITICAL)

**Hold all external AI PR review (Class 2) until Block 30 public-surface sanitization completes.** Both CodeRabbit and Copilot send PR diffs to third-party services; both cache / index those diffs externally. Goat's tree currently contains:

- Personal email addresses.
- Mesh and LAN IP addresses.
- Deployment-specific references that scope the deployment.
- AWS account names.

Sending these to a third-party reviewer today — even with the reviewer's "we don't store" / "we don't train on" claims — leaves us with cached external copies of sensitive references. **Block 30 is queued in the Phase-3 push (month 1-2) anyway**; AI review tooling activates after Block 30 lands, not before. Class 1 (`/ultrareview`) is fine pre-Block-30 (same trust boundary as regular Claude Code).

### 11.4 Operational rules

- **Tune noise threshold aggressively.** First week of CodeRabbit operation will surface ~10× the comments we want. Triage: anything not actionable on the first PR triggers a noise-threshold tightening.
- **Required check vs advisory.** Class 2 starts as **advisory** (PR can merge with red Class-2 check) for the first 2 weeks; promotes to **required** only after false-positive rate stabilizes < 5%.
- **No Class-2 reviews of cluster-internal PRs.** `track/<name> → cluster/<name>` PRs use Class 1 (captain `/ultrareview`) + Class 3 (worker self-review) only. Class 2 fires only on `cluster/<name> → main` and `track/<name> → main`. Reduces external-API spend ~3-5×.

### 11.5 EXTERNAL ACTIONS REQUIRED — humans must take these (cannot be done by Claude)

> ⚠️ **Pinned for human pickup.** These items block §11.1 Class 2 activation. Mirror in `../project/implementation-plan.md` §"Human / external actions register."

1. **Block 30 public-surface sanitization** — tracked as Block 30 in the implementation plan. Decision-and-execute owned by the human program orchestrator; gate is "tree contains no personal email / mesh IPs / deployment-specific references that scope the deployment."
2. **CodeRabbit (or Copilot) account procurement** — paid account with billing setup. Recommended: CodeRabbit per §11.2. Create the account, configure org-level access to the goat repos, save credential to AWS Secrets Manager OR 1Password (not committed). **Approximate cost:** CodeRabbit Pro ~$24/dev/mo (5-10 devs ≈ $120-240/mo); Copilot per-seat ~$10-19/mo. Both have free tiers but they don't include the rule engine / custom config we need.
3. **GitHub OAuth grant + integration** — install the chosen review tool's GitHub App on the goat org, scope to the relevant repos. Configure as advisory PR check initially.
4. **GitHub branch protection rules update** — apply §10.3 protection rules to `main` and the `cluster/*` pattern. Currently only `main` is protected.
5. **CODEOWNERS expansion** — add per-cluster sections per §10.4 at cluster kickoff. First cluster (Block 17/18 closeouts or Block 33) needs the first cluster section.
6. **GitHub merge queue enable** — per ADR 0109, merge queue activates when active-contributor count crosses 3. With 6-10 parallel agent threads, the threshold is crossed by definition. **Enable merge queue on `main` before scale-out**.
7. **Anthropic seat / billing capacity check** — 6-10 parallel agent threads at sustained scale will multiply API spend ~6-10×. Confirm billing capacity before scale-out. (Not a procurement item; a capacity-confirmation item.)

### 11.6 Tradeoffs explicitly named

- Class 1 `/ultrareview` is per-PR human-triggered today; not on every PR by default. **Tradeoff:** depth-of-review vs always-on coverage. We accept this — Class 2 covers the always-on case.
- Class 2 sends diffs externally. **Tradeoff:** automated coverage vs third-party data exposure. Block 30 gate addresses this.
- Class 3 worker self-review is cheap but biased — the same agent that wrote the code also reviews it. **Tradeoff:** speed vs independence. Mitigated by Class 1 + Class 2 catching the cases self-review misses.

---

## 12. Out of scope, deliberately

- Specific agent harness — Claude Code / Claude Agent SDK is the harness; this doc operates at the layer above.
- Multi-tenant agent platforms — single-org single-trunk for now; cross-org coordination is a Phase 4+ question.
- Replacing ADR 0006 — this design extends 0006; the byte-level pickup-track-release pattern stays.
- Inventing a multi-agent benchmark — we run real work, not a benchmark.
- Stacking multiple AI PR review tools — explicit anti-pattern per §11.2.

---

## 13. Companion artifacts

- ADR: [`../adr/0007-multi-agent-orchestration-hierarchy.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/INDEX.md) — records the hierarchy / interface-contract / decision-dedup / role decisions.
- ADR: [`../adr/0008-cluster-branching-and-ai-review-tooling.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/INDEX.md) — records the §10 + §11 decisions specifically.
- Research: `../research/agent-team-management-sota-2026-05.md` — grounds the chosen pattern.
- Implementation: `../project/implementation-plan.md` Block 48 — execution.
- Cadence: `../project/implementation-plan.md` §"Two-month execution cadence — Phase-3 push" — what the substrate enables.
- Concurrency primitives: [ADR 0006](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0006-multi-agent-human-concurrency-governance.md) (extends) + [ADR 0109](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md) (trunk-based git).

---

## 14. Continuous-handoff baton pattern

Cross-session continuity layer. Composes with the §1 primitives + ADR 0017 session-isolation pilot. Full rationale + cost-benefit math + alternatives at [ADR 0839](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0839-continuous-handoff-baton.md).

### 14.1 The gap it closes

ADR 0017 + Block 48O give us **byte-level** continuity — worktree + branch + commits + active-work.yaml row + memory files + session bus all survive a session boundary. What does NOT survive is **in-head** state: TodoWrite list, working hypothesis, ruled-out paths, "stuck on" blocker, intent behind uncommitted diffs.

This matters when sessions end abruptly: account hits a weekly cap, autonomous worker halts on a permission boundary, laptop reboots, operator clears context, IDE crashes. Today the gap is closed by a manual ~5-10 min operator re-brief on the next session. The pattern below drops that to ~30s-2 min without paying always-on cost.

### 14.2 Why not quota-aware

Claude Code does not expose any programmatic signal for daily / weekly / monthly subscription quota approach. No CLI command, no env var, no quota hook event. We considered building a "trigger handoff at 95% of cap" mechanism; not feasible today. If Anthropic ever exposes a quota hook, it slots in as an additional trigger without changing the rest of the pattern.

### 14.3 Cost model — why not always-on

Handoffs are rare under normal use (~1-2 per quarter). Saving 10 min per handoff = 10-20 min/quarter benefit. Maintaining a per-tool-use artifact at ~30s × ~200 commits/quarter = 100 min/quarter cost. **5-10× net negative.**

The artifact tier that pays is one fired at natural state-loss moments, not per tool-use.

### 14.4 The five composing pieces

1. **Commit-message-as-baton (zero-cost layer).** Every commit body on a tracked branch carries why + what changed + what's next. Mostly already-existing discipline. Pre-commit hook gains a soft warning (not block) on missing forward-pointer on tracked branches.
2. **`/handoff` skill** at `../../.claude/skills/handoff/SKILL.md` — project-installed at `.claude/skills/handoff/` so every Claude Code session that opens the repo gets `/handoff` automatically (no per-user install). Captures TodoWrite + active hypothesis + ruled-out paths + next concrete step + WIP files into a `wip(<track>): handoff baton` commit. Updates active-work.yaml track note with sha + timestamp. Idempotent no-op on clean tree with forward-pointing last commit.
3. **PreCompact hook** at `../../.claude/hooks/precompact-handoff.sh`. `matcher=auto|manual`. Fires nudge before context compaction (the strongest available "state about to be summarized" signal). Skips silently when no track + no WIP.
4. **SessionEnd hook** at `../../.claude/hooks/session-end-handoff.sh`. Last-chance write before session terminates. Catches abrupt ends (quota shutdown, IDE crash, `/quit`).
5. **Stop hook with throttle + WIP-check** at `../../.claude/hooks/stop-handoff-throttle.sh`. Gated on (active track) AND (WIP exists) AND (last handoff > 30 min ago). Cheap when nothing's happening; catches steady-state drift between explicit invocations.

Plus a **self-discipline memory rule** at [`../../ops/scripts/feedback-memory-hooks/feedback_handoff_at_pause_points.md`](https://github.com/usareur-af/goatcore/blob/main/ops/scripts/feedback-memory-hooks/feedback_handoff_at_pause_points.md) instructing agents to fire `/handoff` proactively at natural pause points without waiting for a hook nudge.

### 14.5 Why state-loss-coincident triggers work without a quota signal

Events where in-head state is *actually* lost have substantial overlap with quota approaches:

- Auto-compaction fires when the context window is near full → long sessions trigger it → long sessions are also the ones most likely to bump weekly caps.
- Session end fires on every termination → including quota-hit shutdowns.
- Stop-with-WIP catches the residual cases mid-session.

The triggers don't *know* they're correlated with quota; they fire when state is about to be lost regardless of cause. Quota-driven shutdown is one cause among several; the trigger set covers all uniformly.

### 14.6 Reversibility

Each piece independently revertable: delete the skill, remove the hooks from `.claude/settings.json`, delete the memory rule. Pre-commit warning revert by undoing the ADR-driven change. Pattern leaves no orphan substrate.

### 14.7 Pilot evaluation criteria

Promote ADR 0839 Proposed → Accepted after **two of three signals** turn net-positive across three real cross-session resumes: (a) cold-start time delta ≥3 min reduction, (b) zero "tried this and failed before" cycles in the new agent's first 10 actions, (c) hook-nudge action rate 50-80% (too high = nagging on no-WIP; too low = missing real WIP).

Three resumes is the minimum sample. If telemetry is inconclusive, the pattern stays Proposed and the sample window extends.
