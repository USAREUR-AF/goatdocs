# Cross-track commit sweep handling

When work for one `active-work` track gets
accidentally swept into a commit authored under a different track's
`[track: ...]` trailer, **do not rewrite history.** Annotate forward.

## Rule

Once a commit lands on `main`, its `[track: ...]` trailer is immutable.
Rewriting (rebase, amend, force-push) trades a small audit gap for a
larger one — silent history mutation breaks signed-commit verification,
invalidates downstream clones, and makes the original mistake harder to
learn from. The audit trail is more valuable than a tidy trailer.

## Annotation convention

Add a follow-up empty commit on `main` whose message carries:

- A `[sweep-of: <sha>]` trailer pointing at the offending commit.
- A per-file ownership list naming the correct track for each file
  the original commit shouldn't have touched.
- The trailer for the **annotating** commit's own track (typically
  whichever track is doing the bookkeeping).

Example shape:

```text
chore(work): annotate cross-track sweep in 6c9b171

Files swept under track foo that belong to track bar:
  - path/to/file-a   (track: bar)
  - path/to/file-b   (track: bar)

[sweep-of: 6c9b171]
[track: cross-track-commit-sweep-policy]
Signed-off-by: ...
```

`git commit --allow-empty` is fine — the body IS the artifact.

## active-work.yaml linkage

Both the originating track and the receiving track add a `commits_swept`
entry pointing at the original commit + the annotation commit. This
makes the bookkeeping queryable from either side.

## Going-forward mitigation

Stage explicitly. `git add -A` and `git add .` are how sweeps happen.
Prefer `git add -- <pathspec>`, then `git diff --cached --stat` before
every `git commit` — if the file list doesn't match the track scope,
unstage and split.

A pre-commit hook that warns on cross-scope staging is separate work
(not yet shipped); for now this is honor-system, like the rest of the
[ADR 0006](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0006-multi-agent-human-concurrency-governance.md)
trailer discipline.
