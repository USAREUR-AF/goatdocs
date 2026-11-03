# Branch protection rules — runbook

| Field | Value |
|---|---|
| Status | Authored 2026-05-05 (Block 66B.3); not yet flipped on |
| Anchors | [ADR 0109 trunk-based collaboration](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md) · [ADR 1015 code-review discipline](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1015-code-review-discipline.md) · [`docs/design/pr-governance.md`](../design/pr-governance.md) |
| Companion | [`docs/operations/tier-3-install-runbook.md`](tier-3-install-runbook.md) (the end-to-end operator runbook) · `ops/ci/branch-protection-readiness.sh` (pre-flight check) |

This document specifies the **rule set** to toggle, the **verification** at each step, and the **rollback** path. It does NOT cover when to flip on (that's the Tier-3 install runbook) or the underlying decisions (those are in the ADRs).

## §1 The rule set

When branch protection flips on for a repo, configure the following rules on `main`:

### Rule group A — author authenticity + commit hygiene

| Rule | GitHub setting | Why |
|---|---|---|
| Require signed commits | `Settings → Branches → main → Require signed commits` | ADR 0109: every commit on main is GPG-signed; rejects unsigned pushes |
| Require linear history (no merge commits) | `Require linear history` | Squash-merge per ADR 0109; rebases stay clean |
| Block direct push | `Restrict pushes that create matching branches: ON` (only allow via PR) | Forces PR flow |
| Require pull request before merging | `Require a pull request before merging: ON` | The Tier-3 entry point |
| Required approving reviews: 1 | `Required approving reviews: 1` (minimum) | ADR 0109; 2 for security-sensitive paths via CODEOWNERS |
| Dismiss stale reviews on new commit | `Dismiss stale pull request approvals when new commits are pushed` | Force re-review after fixup |
| Require review from CODEOWNERS | `Require review from Code Owners` | Auto-routes per `.github/CODEOWNERS` |
| Require resolution of conversations | `Require conversation resolution before merging` | No merge while threads are open |

### Rule group B — required CI status checks

| Check | Source | Tier |
|---|---|---|
| `lint-shell + lint-yaml` | [`ci.yml`](https://github.com/usareur-af/goatcore/blob/main/.github/workflows/ci.yml) | A |
| `compose-lint` | [`compose-lint.yml`](https://github.com/usareur-af/goatcore/blob/main/.github/workflows/compose-lint.yml) | A |
| `PR hygiene` (base, title, DCO, track trailer) | `pr-hygiene.yml` | A |
| `signal-server / unit` | [`signal-server.yml`](https://github.com/usareur-af/goatcore/blob/main/.github/workflows/signal-server.yml) | B |
| `mgmt-host-bootstrap / unit + integration` | [`mgmt-host-bootstrap.yml`](https://github.com/usareur-af/goatcore/blob/main/.github/workflows/mgmt-host-bootstrap.yml) | B |
| `time-hygiene / unit` | [`time-hygiene.yml`](https://github.com/usareur-af/goatcore/blob/main/.github/workflows/time-hygiene.yml) | B |
| `goat-relay-protocol / unit + conformance + fuzz-smoke` | [`goat-relay-protocol.yml`](https://github.com/usareur-af/goatcore/blob/main/.github/workflows/goat-relay-protocol.yml) | B |
| `netbird-mgmt / build` | [`netbird-mgmt.yml`](https://github.com/usareur-af/goatcore/blob/main/.github/workflows/netbird-mgmt.yml) | B |
| `postgres-spock / build` | [`postgres-spock.yml`](https://github.com/usareur-af/goatcore/blob/main/.github/workflows/postgres-spock.yml) | B |
| `ory-soak-smoke / smoke` | `ory-soak-smoke.yml` | B |
| `inchworm-test / shellcheck + unit` | `inchworm-test.yml` | B |
| `snitch / unit + integration` | [`snitch.yml`](https://github.com/usareur-af/goatcore/blob/main/.github/workflows/snitch.yml) | B (Block 66A.1) |
| `gatewatch / unit` | `gatewatch.yml` | B (Block 66A.2) |
| `admit-audit / unit` | `admit-audit.yml` | B (Block 66A.3) |
| `enrollment / unit` | [`enrollment.yml`](https://github.com/usareur-af/goatcore/blob/main/.github/workflows/enrollment.yml) | B (Block 66A.4) |

**Strict mode:** require branches to be up-to-date before merging (`Require branches to be up to date before merging: ON`). Forces rebase before merge button is available. Increases merge-time latency but ensures CI ran against the actual merge state.

### Rule group C — administrators

| Rule | Setting | Why |
|---|---|---|
| Include administrators | `Apply rules to administrators: ON` | No backdoor for owners; ADR 0109 means it for everyone |
| Allow force pushes | OFF | Never |
| Allow deletions | OFF | `main` is permanent |

### Rule group D — merge queue (activates at >3 active contributors)

ADR 0109 specifies a merge queue once the repo has >3 active contributors. Until then, leave merge queue OFF. When the trigger fires:

| Rule | Setting |
|---|---|
| Require merge queue | ON |
| Build concurrency | 5 (tune from there) |
| Maximum entries to merge | 5 |
| Maximum entries to build | 5 |
| Minimum entries to merge | 1 |
| Maximum minutes to wait for entries | 5 |
| Only merge non-failing pull requests | ON |

## §2 Step-by-step toggle order

Run `ops/ci/branch-protection-readiness.sh` first. It checks every required workflow + template + CODEOWNERS exists. Do not proceed if it reports red.

```bash
ops/ci/branch-protection-readiness.sh
# Expected: "Branch protection readiness: GREEN"
```

Then, in order:

1. **Toggle rule group A (author authenticity).** Test with: try to push an unsigned commit; expect rejection. Try direct push to main; expect rejection.
2. **Toggle rule group B status checks one at a time.** For each check, open a no-op PR, verify the check fires, verify the merge button is blocked until check is green. This catches typos in the required-check name (GitHub matches by exact job name).
3. **Toggle rule group C (administrators).** Confirm with a no-op admin push attempt — should reject.
4. **Leave rule group D (merge queue) OFF** until the >3-active-contributors trigger fires. Re-run this runbook when the trigger hits.
5. **Update the implementation-plan.md "Human / external actions register"** to record the date branch protection was flipped on.

## §3 Verification

After each rule group, verify:

```bash
# A — try to push unsigned (should reject)
git -c commit.gpgsign=false commit --allow-empty -m "test unsigned" && git push
# Expected: "(unsigned commits are not allowed on this protected branch)"

# A — try to push directly to main (should reject)
git push origin HEAD:main
# Expected: "(only PRs can update this branch)"

# B — open a no-op PR; check that all required checks appear in the PR's "Checks" tab
gh pr create --title "chore: branch-protection verification" --body "test" --draft

# B — verify each per-module workflow's path triggers fire correctly:
#   modify ops/snitch/* → snitch.yml fires
#   modify ops/gatewatch/* → gatewatch.yml fires
#   etc.
```

## §4 Rollback

If a rule causes operational pain (e.g. the strict-mode "branches up to date" rule blocks merges during a soak run, or a required check is flaky):

1. **Do not loosen rules silently.** Open an issue first, document the pain, decide whether to tune or roll back.
2. **Tune individual rules** (e.g. drop a flaky required check, mark it advisory pending fix) rather than disabling the whole rule group.
3. **If a rule needs full rollback**, do it via `Settings → Branches → main → Edit rule`. Document in the implementation-plan.md "Human / external actions register" with date + reason.
4. **Never disable signed-commits.** That's the load-bearing author-authenticity invariant. If GPG breaks for a contributor, fix their GPG, don't bypass the rule.

## §5 What this runbook does NOT cover

- **When to flip on** — that's [`tier-3-install-runbook.md`](tier-3-install-runbook.md). This runbook is the rule-set spec.
- **Per-repo timing** — branching adoption is per-repo per ADR 0109 (the trigger is repo-by-repo, with merge queues at >3 active contributors per repo). Most repos today don't meet that bar.
- **CODEOWNERS expansion** — initial scaffold lives at `.github/CODEOWNERS`; specific role/people expansion is tracked in the implementation-plan.md "Human / external actions register" as H-items.
- **Cross-repo coordination** — ADR 0109 §"Cross-repo coordination" handles sequenced merges + atomic flips via feature flag. Branch protection per-repo doesn't itself coordinate cross-repo; the contributor + CODEOWNERS handle that.

## §6 Open questions

- **Required-status-check name drift.** GitHub matches required checks by exact job name. If a workflow renames a job, the required-check rule silently doesn't fire. Today's mitigation: the readiness script pre-checks names. Future: extract job names from a single source-of-truth file (`docs/operations/required-checks.yml`?) that both branch-protection-rules.md and the readiness script consume.
- **Merge-queue tuning.** The numbers in §1 rule group D are starter values; tune from there based on per-PR CI duration distribution. Today's CI durations: Tier A ~3 min; Tier B per-module ~5-15 min. Merge queue is sequential by default; concurrency >1 means multiple PRs build against speculative merge states.
- **Bypass policy.** GitHub allows a bypass list ("these users can bypass branch protection"). Default: no bypasses. Open: should the offline-CA + LUKS-zeroize on-call have a bypass for emergency response? Probably no — emergency response goes through the policy engine, not main-branch direct-push.
