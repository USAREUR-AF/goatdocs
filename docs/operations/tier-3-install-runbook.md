# Tier-3 install runbook — flipping branch protection on per-repo

| Field | Value |
|---|---|
| Status | Authored 2026-05-05 (Block 66C.2); not yet executed on any repo |
| Anchors | [ADR 0109 trunk-based collaboration](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md) · [ADR 1015 code-review discipline](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1015-code-review-discipline.md) · [`docs/design/pr-governance.md`](../design/pr-governance.md) |
| Companion | [`docs/operations/branch-protection-rules.md`](branch-protection-rules.md) (rule-set spec) · `ops/ci/branch-protection-readiness.sh` (pre-flight check) |

This runbook is the **end-to-end operator runbook** for flipping Tier 3 of the code-review discipline on for a repository. ADR 1015 declares Tier 3 (PR review with CI gates) — this document is the operator's how-to for installing it.

## §0 When to run this runbook

Per ADR 0109, branching adoption is per-repo with merge queue at >3 active contributors. Trigger conditions for running this runbook on a repo:

| Trigger | Action |
|---|---|
| Repo grows to **3 active contributors** in the last 30 days | Run §1-§3 (basic branch protection); skip §4 (merge queue) |
| Repo grows to **>3 active contributors** in the last 30 days | Run §1-§4 in full |
| Repo is going **public** (OSS publication per Block 29) | Run §1-§3 even if <3 contributors — public repos must reject direct push |
| **Sponsor / external reviewer asks** for branch protection evidence | Run §1-§3 + document evidence in `docs/compliance/` |

For repos that don't meet any trigger today: don't run this runbook. Tier 1 (block-completion self-review per ADR 1015) is in effect; that's the operative discipline.

## §1 Pre-flight (before touching the GitHub UI)

### §1.1 Run the readiness script

```bash
cd /path/to/repo
ops/ci/branch-protection-readiness.sh
```

Expected output:

```
=== Branch protection readiness — pre-flight check ===
  PASS  ci.yml (lint-shell + lint-yaml)
  PASS  compose-lint.yml
  ...
Branch protection readiness: 39 pass, 0 fail
STATUS: GREEN — safe to flip branch protection per docs/operations/tier-3-install-runbook.md
```

If RED: **stop.** The script prints which artifact is missing. Author it before proceeding. The most common reasons:

- A required CI workflow file is missing → author it (Block 66A pattern)
- The PR template doesn't include the ADR 1015 fields → re-extend it (Block 66B.1)
- CODEOWNERS doesn't cover security-sensitive paths → fix (Block 66B.2)
- No `block-*-completion-review.md` files → at least one Block must be released under ADR 1015 first

### §1.2 Verify the workflows actually run on the repo

This step catches workflow-name typos before branch-protection rules require them. Open a no-op PR (e.g. fix a typo in a comment, or `chore: trigger CI`) and verify every workflow in the required-status-checks list of [`branch-protection-rules.md`](branch-protection-rules.md) §1 actually fires:

```bash
gh pr create --title "chore: branch-protection pre-flight" --body "verifying CI fires" --draft
gh pr checks <PR-number>
```

Expected: every required check appears in the output, even if some are SKIPPED (path-triggered). If a check is missing entirely, fix the workflow's `paths:` filter or trigger pattern before proceeding.

### §1.3 Verify pgp + DCO setup is current for all named contributors

Every active contributor needs a working GPG key and DCO sign-off configured. Branch protection will reject any contributor whose setup is broken.

```bash
# For each active contributor, verify their last commit is signed:
git log --show-signature -1 --author='<email>'
# Look for "Good signature from"

# Verify DCO sign-off:
git log -1 --pretty=%B --author='<email>' | grep "Signed-off-by:"
```

Per CONTRIBUTING.md §"Commits": every commit on `main` is signed; the DCO sign-off is required.

## §2 Toggle branch protection (the actual flip)

### §2.1 Open the GitHub branch protection settings

`Settings → Branches → Branch protection rules → Add rule` (or `Edit` if a rule already exists).

Branch name pattern: `main`

### §2.2 Apply rule group A (author authenticity)

Per [`branch-protection-rules.md`](branch-protection-rules.md) §1 rule group A:

- ☑ Require signed commits
- ☑ Require linear history
- ☑ Require a pull request before merging
- ☑ Required approving reviews: **1**
- ☑ Dismiss stale pull request approvals when new commits are pushed
- ☑ Require review from Code Owners
- ☑ Require conversation resolution before merging

Save. Verify by attempting an unsigned direct push from a sandbox clone:

```bash
git -c commit.gpgsign=false commit --allow-empty -m "test unsigned"
git push origin main
# Expected output: rejected, "(unsigned commits are not allowed on this protected branch)"
# Or: rejected, "(only PRs can update this branch)"
```

### §2.3 Apply rule group B (required CI status checks) ONE AT A TIME

This is the highest-risk step. GitHub matches required status checks by **exact job name** (not workflow file name); typos here silently cause the check to never block. Add them one at a time, verify the merge button blocks until each is green.

For each entry in [`branch-protection-rules.md`](branch-protection-rules.md) §1 rule group B:

1. Add it to "Status checks that are required."
2. Save.
3. Open the no-op PR from §1.2.
4. Verify the merge button is blocked until that check is green.
5. Verify the check name matches what's actually firing (the GitHub UI shows the firing check name; copy that exact string).

Also enable: ☑ Require branches to be up to date before merging (strict mode).

### §2.4 Apply rule group C (administrators)

- ☑ Apply rules to administrators
- ☐ Allow force pushes (DO NOT enable)
- ☐ Allow deletions (DO NOT enable)

Save. Verify by attempting an admin direct push (if you have admin access on a sandbox account):

```bash
git push origin main
# Expected: rejected even with admin
```

### §2.5 SKIP rule group D (merge queue)

Unless you're at the >3 active contributors threshold, leave merge queue OFF. If you ARE at the threshold, see §4 below.

## §3 Post-flip verification

### §3.1 Smoke test the full PR flow

Open a real (non-draft) PR with a small change. Walk through every gate manually:

- ✓ PR template renders correctly with the ADR 1015 fields
- ✓ CODEOWNERS auto-requests review
- ✓ All required CI checks fire
- ✓ Merge button is blocked until checks green + review approved
- ✓ Squash-merge produces a clean main-branch commit
- ✓ Track trailer (`[track: <name>]`) is preserved through the squash

### §3.2 Update the implementation-plan.md "Human / external actions register"

Add a row recording the date branch protection flipped on, the repo name, and the rule groups applied. Format per existing H-item entries.

### §3.3 Update CONTRIBUTING.md if needed

If this is the first repo to flip Tier 3 on, update CONTRIBUTING.md §"Pull requests" to reflect that PRs are now required (not optional). If subsequent repos, no doc change needed.

### §3.4 Notify active contributors

For active-contributor channels (Matrix room, Slack, etc.), post a one-line announcement:

> Branch protection now active on `<repo>:main`. Direct push is rejected; please use PRs. See [docs/design/pr-governance.md](../design/pr-governance.md) for the full picture.

## §4 Merge queue (only at >3 active contributors)

When the trigger fires (>3 active contributors per ADR 0109), enable the merge queue per [`branch-protection-rules.md`](branch-protection-rules.md) §1 rule group D:

- ☑ Require merge queue
- Build concurrency: 5
- Maximum entries to merge: 5
- Maximum entries to build: 5
- Minimum entries to merge: 1
- Maximum minutes to wait for entries: 5
- ☑ Only merge non-failing pull requests

Verify with two simultaneous PRs:

1. Open PR-A and PR-B with conflicting changes to the same file.
2. Both pass CI individually.
3. Both authors hit "merge."
4. Verify GitHub puts them in the merge queue (visible at `Merge queue` tab).
5. PR-A merges first; PR-B's speculative-merge build fails; PR-B is requeued behind PR-A's actual merge state.

## §5 Rollback

If a rule causes operational pain after flipping:

1. **Do NOT loosen rules silently.** Open an issue documenting the pain.
2. **Tune individual rules** rather than disabling whole rule groups. The strict-mode "branches up to date" rule is the most common pain point during multi-PR weeks; it can be relaxed without dropping the other rules.
3. **Required-status-check name drift** is the second most common: a workflow renames a job, the required-check rule silently doesn't match. Mitigation: re-run `branch-protection-readiness.sh` on a regular cadence (weekly cron candidate).
4. **Never disable signed-commits.** That's the load-bearing author-authenticity invariant.
5. **Document any rollback in implementation-plan.md "Human / external actions register"** with date + reason.

## §6 What this runbook does NOT cover

- **The rule-set spec** — see [`branch-protection-rules.md`](branch-protection-rules.md). This runbook tells you when + how to toggle; that doc tells you what rules.
- **Cross-repo coordination** — see [ADR 0109 §"Cross-repo coordination"](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0109-git-collaboration-trunk-based.md). This runbook is per-repo.
- **CODEOWNERS expansion** — initial scaffold lives at `.github/CODEOWNERS`; specific role/people expansion is tracked in implementation-plan.md "Human / external actions register" as H-items.
- **Tier-1 / Tier-2 review discipline** — see [`docs/design/code-review-process.md`](../design/code-review-process.md). Tier 3 is the PR-time install of an existing discipline; the discipline itself doesn't change at flip time.
- **Block 63C codex retrofit** — five mechanical rules become CI gates per [ADR 1014](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1014-codex-pattern-adr-to-enforced-lint.md). When those land, add them to the required-status-checks list per §2.3.
- **Block 40 supply-chain signing** — cosign / SLSA L4 / Rekor wire to release tags, not PR. They're not in the per-PR required-status-checks list.

## §7 Open questions

- **Per-repo trigger automation.** Today the >3 active contributors trigger is operator-judgment. Future: a `gh-active-contributors` script that checks the trigger condition automatically and posts to a channel when it fires.
- **Cross-repo branch-protection consistency.** When goat flips Tier 3 on but a sibling repo doesn't, contributors hit different friction in each repo. Open: do we batch flip all sibling repos at once, or accept asymmetry?
- **Bypass policy.** Default: no bypasses. Open: emergency response (offline-CA + LUKS-zeroize on-call) — bypass or always-via-policy-engine? Probably always-via-policy-engine; the bypass surface is itself a security risk.
