# Session-bus event layer — design

> Companion to [ADR 0012](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0012-session-bus-event-layer.md). Composes with [ADR 0006](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0006-multi-agent-human-concurrency-governance.md) (state) and [ADRs 0013](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0013-master-worktree-read-only-by-convention.md), [0015](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0015-smallest-change-on-shared-substrate.md), [0016](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0016-ref-ownership-preflight.md) (action discipline). Implementation tracked under Block 48N.

## Purpose

A low-latency, event-shaped, scope-tagged channel for agents (and humans-via-CLI) to broadcast intent and outcome to other concurrent sessions in the same clone. Bounded reader cost, zero between-turn token burn, durable-on-disk for post-hoc reconstruction.

## As-built (2026-08) — read this first

The sections below this one are the v1 *design*; the implementation diverged. What actually runs:

- **Storage:** `~/.claude/state/session-bus-<sha256-of-master-worktree-path, 12 hex>.jsonl` — one file, monthly rotation to `<file>-YYYY-MM`. Not daily files, not `~/.goat/`.
- **Writer:** `work bus warn|info|urgent <msg> [--to session:<id>|track:<name>] [--track <name>] [--force]`. No `--scope` token grammar — events carry free-text `msg` plus auto-captured `track`/`branch`/`cwd`/`host`/`session_id`. Rate-limit: identical (level, owner, msg) refused within 60 s.
- **Reader = delivery.** **Posting to the bus is not delivery; the hook is.** `.claude/hooks/session-bus-tail.sh`, wired in `.claude/settings.json` for two events:
  - `SessionStart` — catch-up: a brand-new session has no cursor, so it receives events from the last 24 h (`GOAT_BUS_CATCHUP_HOURS`) that arrived while it didn't exist.
  - `UserPromptSubmit` — incremental: events newer than the session's cursor (`~/.claude/state/session-bus-cursor-<session-id>`, a byte offset), then the cursor advances. Nothing is delivered twice.
- **Injection policy:** `urgent` + `warn` always inject; `info` capped to the 5 most recent (`GOAT_BUS_INFO_CAP`) with an omitted-count line; own events never inject; empty case emits nothing — zero token cost. There is no scope-match algorithm; level + addressing replaced it.
- **Directed messages:** msg text containing `TO session <id>` or `TO track <name>` always injects for the addressee (flagged `ADDRESSED TO THIS SESSION`), cap or no cap. Write it canonically with `--to session:<id>` / `--to track:<name>`.
- **Acknowledgement:** `work bus ack <ts> [--note ...]` looks up the event with that `ts`, emits an info event directed back at its sender with `"ref":"<ts>"`. Senders verify delivery with `work bus tail | grep '"ref":"<ts>"'`.
- **Subagents inherit nothing.** Hook context reaches the parent session only. A subagent that needs bus context gets its excerpt in the spawn prompt; its own emits carry the parent's session id.
- **Failure mode:** hook error or unwired settings degrades to the durable JSONL + manual `work bus tail` — exactly the write-only state this section exists to prevent. Tests: `.claude/hooks/tests/session-bus-tail-tests.sh` (hook) + `ops/work/bus_test.go`, `bus_ack_test.go`, `multi_session_bus_test.go` (CLI).

## Sender identity — fixed 2026-09-05, and what the broken history looks like

`busSessionID()` preferred `$CLAUDE_SESSION_ID` and fell back to `p<ppid>`.
Claude Code does not export `CLAUDE_SESSION_ID`; it exports
`CLAUDE_CODE_SESSION_ID`, and that value is the same uuid the delivery hook
reads from its stdin JSON. It also runs every Bash tool call in a fresh shell,
so the fallback minted a **new id on every emit** — measured on the operator
laptop, 157 events in one bus file carried ~155 distinct `p<pid>` ids.

Two behaviours were dead for as long as that held:

- **Own-event filtering.** The hook drops events whose `session_id` equals its
  own; no `p<pid>` ever did, so sessions were fed their own posts back.
- **`--to session:<id>`.** The id printed on an event belonged to one shell
  invocation, so the intended reader never matched it and never saw the
  `ADDRESSED TO THIS SESSION` flag. Only `warn`/`urgent` (which inject
  unconditionally) and `--to track:<name>` (matched off the `track/` branch)
  ever arrived — which is why bus history over-uses `warn`.

`busSessionID()` now reads `CLAUDE_SESSION_ID` then `CLAUDE_CODE_SESSION_ID`
before falling back; the hook's own fallback chain gained the same variable.
Events emitted before 2026-09-05 keep their one-shot ids: an old `p<pid>` in
the log is not an address.

## One bus per clone — a designed property that now cuts across the team

The file key is the master worktree path, so two clones of this repo on one
machine are two mutually invisible coordination domains. That was
[ADR 0012](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0012-session-bus-event-layer.md)'s explicit choice, made when
a second clone meant a second piece of work.

It means something else when two clones are of the *same* repo and worked by
the *same* sessions: each clone has its own bus, so a session posting from one
reaches nobody working in the other.

Not changed here, because re-keying the bus is an ADR-level call with its own
consequences (a shared key merges genuinely separate work; a symlink hides
which clone an event came from). Until it is decided, a post that must reach
everyone is posted from each clone. Tracked as an open question below.

Delivery-contract narrative: [multi-agent-team-management.md](multi-agent-team-management.md) §6.4.8; decision trail: [ADR 0012](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0012-session-bus-event-layer.md) amendment 2026-08-11.

Operator/agent-facing usage — levels, addressing, etiquette, limits — is the
`/bus` skill at `.claude/skills/bus/SKILL.md`.

## State vs events — the load-bearing split

| Substrate | Cadence | Question it answers | Storage |
|---|---|---|---|
| `docs/project/active-work.yaml` (ADR 0006) | Minutes-to-hours; pickup / release / status-update | "Who picked up what track? What scope? What status?" | Tracked file in repo |
| Session-bus (this design) | Sub-second; per-action | "What is happening *right now*? What *just happened* I need to know about?" | Append-only JSONL outside repo |

Encoding events as state mutations on `active-work.yaml` is rejected: every typed line would become a coordination commit, downstream rebases would churn, and the file would lose its "stable index of who-holds-what" character. The bus is the missing fast lane.

## Storage layout

```
~/.goat/session-bus/
└── <clone-id>/                              # SHA-1 of the absolute path of the master worktree
    ├── 2026-05-06.jsonl                     # daily file; UTC date
    ├── 2026-05-07.jsonl
    ├── ...
    └── <session-id>.cursor                  # per-session reader cursor (last-seen ts)
```

- **`<clone-id>`** — `sha1(master-worktree-absolute-path)`. Different clones of the same repo on the same machine are independent coordination domains.
- **Daily JSONL files** — one append-only file per UTC day. Logrotate-equivalent cleanup keeps last 7 days local; older archived to per-clone tarball under `~/.goat/session-bus/<clone-id>/archive/`.
- **`<session-id>.cursor`** — single line, ISO-8601 UTC timestamp. Updated only after a successful read.

The path is deliberately outside the repo — gitignored even at the in-repo level — so bus contents never enter git history. Writes are atomic via single `O_APPEND` write per ADR 1009-style filesystem discipline.

## Event schema

One JSON object per line. Required fields:

```json
{
  "ts": "2026-05-06T05:18:00.123Z",
  "from": "session-A | bus-cli | hook | <free-string>",
  "sev": "info | warn | urgent",
  "scope": ["<token>", ...],
  "msg": "<one-line human-readable summary>"
}
```

Optional fields:

```json
{
  "ts": "...",
  "from": "...",
  "sev": "...",
  "scope": [...],
  "msg": "...",
  "worktree": "<absolute-path>",        // if action originated in a specific worktree
  "branch": "<refs/heads/...>",         // if action mutates a specific ref
  "intent": "before | after",           // before-action announcement vs after-action confirmation
  "duration_s": 30,                     // expected duration of the in-flight operation (for soft-locks)
  "ref_to": "<sha>",                    // for ref-mutating operations: target SHA
  "ref_from": "<sha>",                  // for ref-mutating operations: previous SHA
  "track": "<active-work-track-name>"   // optional cross-link to active-work.yaml
}
```

**Scope tokens** are flexible. Common forms:

| Token shape | Meaning | Match rule |
|---|---|---|
| `path:<glob>` | File or path glob | Match if any entry in the receiver's "touched paths" matches the glob |
| `track:<name>` | A named active-work track | Match if the receiver's session was spawned for this track |
| `branch:<ref>` | A git ref | Match if the receiver's worktree has this ref checked out |
| `worktree:<absolute-path>` | A specific worktree | Match if the receiver IS that worktree |
| `clone` | The whole clone | Always match |
| `master-worktree` | The master worktree specifically | Match if the receiver is the master worktree |

Scope tokens are an OR-set: a receiver matches the event if *any* of its touched paths/branches/tracks matches *any* token in the event's scope array.

## Sender API — `work bus` CLI

Three subcommands extend `ops/work/work`:

### `work bus warn|info|urgent --scope <tokens> --msg "..." [--intent before|after] [--duration-s N] [--branch REF] [--track NAME]`

Append a single event with the given severity. Scope tokens are comma-separated.

```
work bus warn --scope path:docs/project/active-work.yaml,master-worktree --msg "actively editing for next 5 min" --intent before --duration-s 300
work bus info --scope branch:refs/heads/main --msg "rebase complete" --intent after --branch refs/heads/main --ref-from 4218363 --ref-to 535cb5b
work bus urgent --scope clone --msg "PR #2 about to merge; pause pushes for 5 min" --duration-s 300
```

Atomic single-write append. Returns 0 on success.

### `work bus tail [--since <iso8601>] [--scope <tokens>]`

Read events newer than the given cursor (or this session's recorded cursor if `--since` omitted). Optionally filter by scope (used for ad-hoc operator queries; the hook does its own filtering).

Output: one JSON object per line. Doesn't advance the cursor (that's the hook's job).

### `work bus cursor [show | reset | set <iso8601>]`

Inspect or manipulate the current session's cursor.

### Failure modes

- Bus directory missing → CLI auto-creates on first write.
- Disk full → write fails loudly; CLI returns non-zero; no partial line.
- Cursor file corrupt → `cursor show` returns "uninitialized"; next hook read treats as "from beginning of today's file."
- Concurrent writes → POSIX-guarantees `O_APPEND` write atomicity for writes under PIPE_BUF (4096 bytes). Events larger than 4 KiB are out of scope.

## Reader — UserPromptSubmit hook

`.claude/hooks/session-bus-tail.sh` is invoked by Claude Code on every UserPromptSubmit event. Its job:

1. Resolve `<clone-id>` from `pwd` walking upward to find the master worktree (`git rev-parse --git-common-dir` then resolve to the master path).
2. Resolve `<session-id>` from `$CLAUDE_SESSION_ID` (provided by harness) or fall back to `$$` (process group).
3. Read this session's cursor (`<clone-id>/<session-id>.cursor`); default to start-of-today if missing.
4. Tail today's JSONL file (and optionally yesterday's if cursor is older than today) for entries newer than cursor.
5. For each entry: compute scope-overlap against this session's *touched-set* (current branch, current worktree path, paths modified or added in the last N=10 commits on the current branch, paths in `git status` output).
6. Emit injection-eligible entries to stdout in a fixed system-reminder format. Update cursor to the timestamp of the last processed entry.

**Scope-overlap algorithm.**

```
def matches(event, session):
    if event.sev == "urgent": return True
    for token in event.scope:
        if token == "clone": return True
        if token == "master-worktree" and session.is_master(): return True
        if token.startswith("worktree:") and token.value == session.worktree_path: return True
        if token.startswith("branch:") and token.value == session.current_branch: return True
        if token.startswith("track:") and token.value == session.track_name: return True
        if token.startswith("path:"):
            for touched in session.touched_paths:
                if fnmatch(touched, token.value): return True
    if event.sev == "info": return False  # exact-only matches handled above
    if event.sev == "warn":
        # loose match: parent dir, sibling track, ancestor commit
        for token in event.scope:
            if token.startswith("path:"):
                for touched in session.touched_paths:
                    if loose_match(touched, token.value): return True
        return False
    return False
```

`loose_match` for `warn`:
- Parent-dir match: `path:docs/design/foo.md` matches a touched path of `docs/design/`.
- Sibling-track in same cluster (when both events and session carry track tags): cluster prefix matches.
- Ancestor-ref: `branch:foo` matches if `foo` is an ancestor of session's current branch (via `git merge-base --is-ancestor`).

**Injection format** — one entry becomes a single system-reminder block:

```
SESSION-BUS [warn] from session-B at 2026-05-06T05:18:00Z
scope: path:docs/project/active-work.yaml, master-worktree
intent: before; duration: 300s
msg: actively editing for next 5 min
```

Multiple entries become multiple blocks, oldest first. Hook output is concatenated and Claude Code displays as system-reminder context for the next turn.

**Bounded cost.** Hook script is bash + jq, runs in ~10-50 ms typical. No outbound network. No daemon. Hook fires once per UserPromptSubmit which the operator was already going to submit.

**Failure mode.** If the hook errors out, the session continues without the warning — the event is still durably in the JSONL and any other session that's reading the bus sees it.

## ntfy integration for `urgent` tier

When `work bus urgent` is invoked, the CLI additionally:

1. Reads `~/.goat/session-bus/<clone-id>/ntfy.conf` for the per-clone ntfy endpoint URL + topic. (One-time operator setup.)
2. POSTs the event message + scope summary to the ntfy topic.
3. Per-site ntfy substrate is the same one used by Block 48J alertmanager-ntfy bridge (CLAUDE.md §"Boundary classification + escalation triggers + escalation medium") so operator gets pages on phone via existing infra.

If the ntfy POST fails, the bus event still lands in the JSONL — the push is best-effort, the durable record is the file.

## Per-clone initialization

Operator (or automation) runs once per clone:

```
mkdir -p ~/.goat/session-bus/$(sha1sum <<< "$(pwd)" | cut -c1-12)
cp .claude/hooks/session-bus-tail.sh.example .claude/hooks/session-bus-tail.sh
chmod +x .claude/hooks/session-bus-tail.sh
# Optional: configure ntfy push for `urgent` tier
echo '{"url":"https://ntfy.<site>.netbird.legacy.example","topic":"goat-bus"}' > ~/.goat/session-bus/<clone-id>/ntfy.conf
```

Make target `make session-bus-init` automates the above.

## Pilot harness — Block 48N.5

Per the net-positive principle in CLAUDE.md: "no mechanism ships from theory; all ship from evidence; pilot WITHOUT, pilot WITH, measure differential, adopt only when net-positive."

**Pilot design.** Two-week pilot (≥10 multi-session work-days):
- WITHOUT bus: continue operations as today.
- WITH bus: enable hook, train operator on `work bus warn` for ref-mutating ops + master-worktree edits.

**Measurements.**

| Metric | WITHOUT baseline | WITH target |
|---|---|---|
| Cross-session disruption incidents (defined: any event where one session's action causes another session to lose work, get stale view, or have to re-do an operation) | Track count over 10-day window | Reduction ≥50% |
| Operator-noticed false-positive injections (warning that didn't apply) | n/a | <2 per day per session |
| Hook latency p95 | n/a | <100 ms |
| Storage growth | n/a | <10 MB / clone / month |
| Operator survey "did the bus catch something I'd have missed?" | n/a | ≥1 yes per week |

**Promotion criteria** to flip [ADR 0012](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0012-session-bus-event-layer.md) Status from Proposed to Accepted:
- Disruption incidents reduced.
- Latency + storage targets met.
- ≥2 operator-confirmed catches.

**Demotion criteria** (revert if):
- False-positive injection rate >5/day per session (signal-to-noise breakdown).
- Hook misfire rate >10% (correctness gap in scope-match algorithm).
- Operator reports the bus is creating MORE friction than it removes (subjective; operator final word).

## Composition with surrounding ADRs

| ADR | How this design composes |
|---|---|
| 0006 (concurrency governance) | Bus is the events-layer complement to active-work.yaml's state-layer. |
| 0011 (worker execution environment) | Per-session worktrees are the natural unit for bus event scoping (`worktree:` token). |
| 0013 (master-worktree read-only) | Soft-lock convention IS a bus warning; bus is the signaling substrate. |
| 0015 (smallest-change-on-shared-substrate) | Bus surfaces alternatives the agent considered + skipped, not just the action taken. |
| 0016 (ref-ownership pre-flight) | Pre-flight check emits bus events on both PASS (info) and FAIL (warn) paths. |

## Out-of-scope for v1 (named for completeness)

- Cross-clone or cross-machine federation. Per-clone scoping is sufficient.
- Reply threads / two-way conversation. Use `active-work.yaml` track-status-update for async.
- Per-event ack tracking. The bus is fire-and-forget; durability is in the JSONL.
- Operator-facing dashboard / TUI. `work bus tail` from a terminal is enough at v1.
- Schema versioning beyond a top-level `schema:` field. Add when format breaks.

## Open questions for pilot

1. Is the daily-JSONL-file the right rotation cadence, or hourly under high-event-rate sessions? Pilot will measure event volume.
2. Should the hook also inject events on agent-internal tool calls (not just UserPromptSubmit)? Probably not — would burn tokens between operator turns. Leave for follow-on if pilot evidence supports.
3. What's the right behavior when the bus directory doesn't exist? Currently auto-create on write; could fail loudly. Pilot operator preference will decide.
4. Should `work bus urgent` also write to the existing `docs/project/active-work.yaml` as a sticky banner? Probably not — would re-conflate state and events. Leave separate.
5. **Should the bus key stay the clone, when two clones are the same repo?** (See "One bus per clone" above.) Candidate keys: the origin remote's repo, an explicit per-team id, or keeping the clone key and teaching sessions to post twice. Whichever wins has to keep an event's originating clone legible, because deploys and worktrees differ between them.

## References

- [ADR 0012](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0012-session-bus-event-layer.md) — the decision
- [ADR 0006](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0006-multi-agent-human-concurrency-governance.md) — concurrency governance state-layer
- [ADR 0010](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0010-boundary-classification-escalation-and-medium.md) — escalation medium (ntfy integration target)
- Block 48J — alertmanager-ntfy bridge (substrate this design rides)
- Block 48N — implementation tracking for this work
