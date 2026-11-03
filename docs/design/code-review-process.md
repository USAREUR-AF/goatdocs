# Code-review process for completed blocks

| Field | Value |
|---|---|
| Status | Accepted (2026-05-05 — implementation under Block 50G) |
| ADR anchor | [`1015-code-review-discipline.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1015-code-review-discipline.md) |
| Companion checklist | [`docs/process/block-completion-checklist.md`](https://github.com/usareur-af/goatcore/blob/main/docs/process/block-completion-checklist.md) |
| Composes with | [ADR 0006](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0006-multi-agent-human-concurrency-governance.md) work tracker · ADR 0009 worker discipline · [ADR 1006](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1006-phase-gates.md) phase gates · [ADR 1008](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1008-soak-testing-discipline.md) soak · [ADR 1012](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1012-load-testing-discipline.md) load · [ADR 1013](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1013-continuous-architectural-chaos.md) chaos · [ADR 1014](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1014-codex-pattern-adr-to-enforced-lint.md) codex pattern · [ADR 0109](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md) trunk-based |

## TL;DR (for a layperson)

When we finish a block of work, we currently say "done" and move on. The
problem: two recent engineering-quality reviews each produced gaps that
*only the next reviewer caught*. The fix is a small standing process —
the author runs through a written checklist before declaring the work
released, and the checklist becomes a commit, not a verbal gesture. As
the project grows we add more eyes to that same checklist (a second
agent or human reviews it before promotion to production-bearing
branches; eventually it becomes the requirements list on a pull
request). Same checklist all the way; what changes is who runs it and
when.

## The gap this closes

The 2026-05-03 wave shipped Block 50A.2 with verdict criterion *"`go
test ./...` passes; any new leak fails the build."* That criterion is
existence-based ("does goleak appear?"), not fitness-based ("does the
goleak that appears actually cover the failure modes?"). A subsequent
review three days later found **three load-bearing Go services with
zero goleak coverage** (snitch, admit-audit, enrollment) — the original
verdict was technically met because every package that *had* tests had
goleak; the missing-tests-entirely category fell through.

The 2026-05-05 wave shipped three genuinely functional changes (snitch
URL-query auth removal + snitch install.sh fix + gatewatch graceful
shutdown) **with build + reasoning as the only verification.** No tests
were written, no checklist surfaced the gap before track release. The
gap is now Block 50F.

In both cases, the missing piece was the same: a checkpoint between
"track released" and "next-wave audit" that would have caught the gap
in-track. This document defines that checkpoint.

## Three tiers, one checklist

The same checklist threads three tiers. What changes is who runs it and
when. Adoption is staged: today we have Tier 1; Tier 2 lands when a
reviewing agent or human is regularly available; Tier 3 lands when the
branching-and-PR model in [ADR 0109](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md)
ships per-repo.

### Tier 1 — block-completion self-review (TODAY)

| Field | Value |
|---|---|
| Who runs it | The block author (agent or human) |
| When | After implementation lands; before the `work release` step |
| Output | A `docs/project/block-<name>-completion-review.md` artifact citing each checklist row with evidence |
| Discipline | The review is a *commit*, not a verbal gesture. **No review file = block not released.** |
| Reviewer authority | The author signs off on themselves. Tier 1 is honest self-assessment, not external validation. |

The Tier-1 author runs through the checklist row by row, attaching one
of: a file path + line number; a commit SHA; a test verdict
(green/red); a link to a finding (`F-NNN`); a measurement (`M-NNN`); a
soak evidence file; or — for a known gap — an explicit pointer to the
follow-on Block that owns the gap.

The output is a single Markdown file, committed alongside the release
commit. The review file is what the next-wave reviewer reads first.

The first published Tier-1 review is
`docs/project/block-50e-completion-review.md`
— the retroactive review of Block 50E, which is the demonstration that
validates the checklist catches what it should.

### Tier 2 — cross-agent / human review (NEXT)

| Field | Value |
|---|---|
| Who runs it | An independent reviewer (agent or human) — not the block author |
| When | After Tier 1 lands; before promotion to production-bearing branches or production deploy |
| Output | A `docs/project/block-<name>-cross-review.md` counter-review |
| Discipline | Either approves with citations or files findings + requests fixes. The Tier-2 review is also a commit. |
| Reviewer authority | Approving Tier 2 = "fit for production-bearing path." Rejecting = block stays released-with-fixes-pending. |

Tier 2 operates on Tier-1-released blocks and is gated to the same
checklist. The reviewer is not the author. For agent-only sessions, the
reviewer is a different agent invocation with no shared context to the
authoring session — independence by construction.

The Tier-2 reviewer's specific job is **to read the Tier-1 review file
critically**: did the author's evidence actually demonstrate what they
claimed? Are the known-gap pointers honest about scope? Did the
classification (functional vs edge-case vs test-only) match what
shipped?

Tier 2 ships on availability — it is **not** mandatory while only one
agent is on a block, but the Tier-1 review file MUST be structured to
make Tier 2 a quick read whenever a reviewer is available. Today's
posture: ship Tier 1 reviews; leave them stub-ready for Tier 2.

### Tier 3 — PR review (FUTURE)

| Field | Value |
|---|---|
| Who runs it | PR reviewer per CODEOWNERS + required-reviewers |
| When | At PR open; before merge to main |
| Output | The PR description (Tier 1 self-review fields) + approving review (Tier 2 review fields) |
| Discipline | The same checklist becomes a PR review template and the merge-blocking review surface |
| Gate | Branching-and-PR model in [ADR 0109](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md) shipped per-repo; CI gates listed below installed |

When the branching-and-PR model lands (per [ADR 0109](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md)
the trigger is repo-by-repo, with merge queues at >3 active
contributors per repo), the same checklist becomes:

- **PR description checklist** — author self-fills (this *is* the
  Tier-1 review)
- **PR review template** — reviewer fills (this *is* the Tier-2 review)
- **CI gates** — mechanical enforcement of the rows that can be
  mechanically checked (see "CI enforcement of the checklist" below)
- **CODEOWNERS routing** — automatic reviewer assignment per file
  pattern
- **Required reviewers** — at minimum 1; merge queue at >3 active
  contributors

The Tier-3 design is **declared now** so the Tier-1 + Tier-2 work today
naturally sets up for Tier-3 later. The checklist rows are written to
be mechanically checkable where possible, so the day-1 Tier-3 install
is mostly wiring.

## The shared checklist (summary)

Full checklist: [`docs/process/block-completion-checklist.md`](https://github.com/usareur-af/goatcore/blob/main/docs/process/block-completion-checklist.md).
Twelve rows, grouped into four sections:

### Section A — Closeout sweep
1. **Closeout-status row check** — every implementation-plan sub-task
   marked Done / Skipped / Carried-forward with citations (commit SHA
   or follow-on Block reference).
2. **Plan-vs-shipped truth-up** — if a sub-task shipped differently
   from the plan row, the plan row is updated to match what shipped
   (deviation note in the row body).

### Section B — Test fitness (the gap that bit us)
3. **Functional-vs-edge-case classification** — every change in the
   block is classified as functional / edge-case-hardening /
   error-surfacing / test-only / doc-only.
4. **Test coverage per category** — functional changes have a unit
   test that exercises the behavior change; edge-case-hardening has at
   minimum lint + build + (where applicable) goleak green; test-only
   changes self-validate.
5. **Known-gap filing for un-testable items** — if a functional change
   can't be unit-tested in this block (e.g. missing test substrate,
   needs docker-in-docker), an `F-NNN` finding is filed with explicit
   pointer to the follow-on Block.

   *Row 5.5 — Fail-loud on silent-failure modes (added 2026-05-08).*
   Every change that depends on a runtime invariant (config-file mode,
   bucket lifecycle, directory layout being present, allowlist
   non-emptiness, upstream default that we override) has either a
   fail-loud assertion or a structured drop/skip event. Catches the
   class of bug where "no log line said anything was wrong, the system
   just quietly stopped doing what we expected" — F-039 / F-050 / F-074
   / Block 22K.8 / F-075 are the reference instances. Pattern at
   CONTRIBUTING.md §"Fail-loud on silent-failure modes" so authors
   apply it during the work; the checklist row enforces it at release.

### Section C — Drift sweep
6. **Docs-vs-code grep sweep** — `grep` for stale references to
   renamed components / paths / hostnames; verify CLAUDE.md pointers
   match current source-of-truth locations.
7. **CLAUDE.md updates** — if the block moved a source-of-truth or
   added a load-bearing component, CLAUDE.md is updated in the same
   block (per the existing CLAUDE.md `UserPromptSubmit` reminder).
8. **ADR updates** — if architectural, ADR(s) authored or
   superseded; INDEX row added; per-tag sub-series carried.

### Section D — Evidence + hygiene
9. **Findings register** — any external-system gotcha discovered
   during the block becomes an `F-NNN`; INDEX row added.
10. **Measurements register** — any perf claim is backed by an `M-NNN`
    measurement; numbers without an `M-NNN` are explicitly framed as
    "preliminary" or "estimated."
11. **Validation-state tracker** — any soak run, probe, or env
    provisioning verdict updates `docs/project/validation-state.md`
    in the same block.
12. **Commit hygiene** — every commit carries a `[track: <name>]`
    trailer; commits use `git commit <path>` form to bypass the
    concurrent-staging window observed in Block 50E (`bf199f3`,
    `cccb67b`); GPG-signed; no skipped hooks.

## Composition with existing discipline

This process **does not replace** existing discipline ADRs. It
**operationalizes** them:

| Existing ADR | What it says | How the checklist integrates it |
|---|---|---|
| [1006 phase gates](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1006-phase-gates.md) | Pre-conditions for phase promotion | Section A row 1: phase-gate evidence cited per relevant sub-task |
| [1008 soak](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1008-soak-testing-discipline.md) | Required test class for stateful / replicated | Section B row 4: soak verdict cited for any stateful component |
| [1012 load](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1012-load-testing-discipline.md) | Required pre-prod measurement | Section B row 4 + Section D row 10: M-NNN cited for any perf claim |
| [1013 chaos](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1013-continuous-architectural-chaos.md) | Continuous architectural-invariant probing | Section A row 2 + Section C row 6: any new invariant gets a chaos probe row |
| [1014 codex pattern](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1014-codex-pattern-adr-to-enforced-lint.md) | ADR-to-enforced-lint | Tier-3 future: mechanical rows from the checklist become CI gates |
| [0006 work tracker](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0006-multi-agent-human-concurrency-governance.md) | Active-work tracker | Section D row 12: track trailer + path-form commits |
| 0009 worker discipline | Six worker mechanisms (fast/slow inchworm, hypothesis-first, etc.) | Section B row 3: classification step is the "two-hat refactoring discipline" check — function vs polish in the same commit |
| [0109 trunk-based](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md) | Trunk + signed commits + DCO + Conventional Commits | Tier-3 trigger: when ADR 0109's per-repo branching adoption fires, Tier 3 lands |

## CI enforcement of the checklist (Tier 3 day-1 install)

When Tier 3 is installed (gated on ADR 0109 per-repo branching
adoption), these checklist rows become mechanical CI gates:

| Checklist row | CI mechanism | Status |
|---|---|---|
| 1 — Closeout-status row check | `ops/work/work check-stale` extended to verify every Block sub-task in PR diff has a status update | Code-now (post-50G), wire-as-PR-gate later |
| 4 — Test coverage per category | `golangci-lint` with the strict `.golangci.yml` from Block 50A.3 + `goleak.VerifyTestMain` presence per package + `go test -race -count=1` | Already running per-PR via existing CI |
| 6 — Docs-vs-code drift | `ops/ci/check-claude-md-drift.sh` (NEW under [ADR 1014](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1014-codex-pattern-adr-to-enforced-lint.md) §3.4) | Future per ADR 1014 |
| 9 — Findings register | `ops/ci/check-findings-index.sh` — verify `ls docs/findings/F-*.md \| wc -l` matches INDEX row count (Block 50E.8 caught this once already) | Code-now |
| 10 — Measurements register | Same shape as 9 for `docs/measurements/` | Code-now |
| 11 — Validation-state tracker | Hard to mechanize without false positives — tier-3 review-time check, not CI | Manual at Tier 3 |
| 12 — Commit hygiene | `commit-msg` git hook checking for `[track:]` trailer + signed commit + Conventional Commits prefix | Today as `ops/work/git-hooks/pre-commit` (warn-not-block); promote to PR-block on Tier 3 |

The remaining rows (Section A row 1 + 2; Section B row 3; Section B
row 5; Section C rows 7 + 8) require human-or-agent judgment and stay
review-time.

## Adoption path

1. **Today (Block 50G):** Tier 1 ships. The checklist file lands.
   Block 50E gets a retroactive Tier-1 review at
   `docs/project/block-50e-completion-review.md`
   that demonstrates the checklist working. From this point forward,
   no `work release` without a Tier-1 review file.
2. **When a reviewing agent or human is available:** Tier 2 ships.
   Cross-reviews land alongside their Tier-1 counterparts. The first
   block to receive a Tier-2 review is **the Block 50G work itself**
   (the review process gets reviewed under itself — meta-discipline
   per ADR 0009 §6.5).
3. **When ADR 0109 per-repo branching lands:** Tier 3 ships per-repo.
   CI gates from the table above install at branching adoption.
   CODEOWNERS expands per the existing entry in
   implementation-plan.md "Human / external actions register".

## Open questions / future work

- **Cross-track review interaction.** The work tracker (ADR 0006)
  governs *concurrency* of who's editing what; this process governs
  *closure* of completed work. They compose cleanly today (every track
  needs a Tier-1 review at release; Tier 2 happens after release). Open
  question: when two related tracks complete near-simultaneously, do
  their reviews compose (single combined review) or stay independent
  (two reviews + a small "joint observations" file)? Default for now:
  independent reviews; combined only on explicit operator request.
- **Tier 2 reviewer-assignment policy.** When a reviewing agent is
  available but multiple are available, which agent reviews? Today's
  posture: any free reviewer; future: per-area expertise routing
  (Go/Rust split per [ADR 0112](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0112-tech-strategy-workload-shape-language-boundary.md);
  per-cluster captain assignment per Block 48).
- **Severity escalation.** A Tier-1 review that surfaces a Sev-1 gap
  (e.g. an un-tested functional change to security-critical code) —
  does the author block their own release pending fix, or is
  release-with-known-gap-and-fast-follow-Block still fair? Today:
  release-with-known-gap-and-fast-follow-Block IS fair (the goal is
  visibility, not blocking throughput); future: tighten if the
  fast-follow-Blocks aren't getting picked up promptly.
