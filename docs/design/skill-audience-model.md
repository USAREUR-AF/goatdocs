# Skill audience model — who a skill serves, and where its human guide lives

**Status:** adopted [ADR 1174](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1174-skill-audience-and-human-guides.md). Enforced by `ops/ci/check-skill-audience.py`.

Skills (`​.claude/skills/<name>/SKILL.md`) are written for an agent — a trigger and an execution recipe. Some skills describe work a person also does or supervises; most operational ones do. This doc is the pattern that decides where a human counterpart belongs, and keeps that counterpart from becoming a second source of truth.

## The two failures this prevents

- **Effort in the wrong place.** A skill that only choreographs the agent's own workflow — worktree toggling, the close-out protocol, bus messaging — gains nothing from a human companion. Writing one is noise.
- **Docs that drift.** Copying a skill's steps into a "human version" creates a second "THE procedure" that rots the moment the first changes. That is a direct violation of doctrine **P1: one source of truth**.

## The model

### 1. Every skill declares an `audience`

One frontmatter field, two values:

```yaml
---
name: env-door
description: ...
audience: both        # ai | both
---
```

- `audience: ai` — the skill only choreographs the agent's own process. No human counterpart.
- `audience: both` — the skill wraps a real-world capability a person can perform or must supervise. It gains a `GUIDE.md`.

**The discriminator, applied per skill:** *would a person ever do this, or need to understand it to oversee it?* Yes → `both`. Only-the-agent-runs-it → `ai`. The question is what scales; there is no list to maintain.

Current classification:

| audience | skills |
|---|---|
| `ai` | `iso`, `closeout`, `bus`, `design-work`, `handoff`, `inchworm`, `claude-md-frugality` |
| `both` | `env-door`, `fastlane`, `goatnet-standup`, `graduate`, `goat-cli`, `record` |

### 2. The `GUIDE.md` points at the canon, never copies it

A `both` skill gains a `GUIDE.md` beside its `SKILL.md`. The guide is a doorway, not a document. Nearly every capability already has a canonical home — a runbook in `docs/operations/` or a design doc in `docs/design/`. That stays the one source:

- **Canon already exists → the guide is a thin pointer.** A sentence of human orientation and a link. `goatnet-standup`'s guide points at [`goatnet-standup.md`](https://github.com/usareur-af/goatcore/blob/main/docs/operations/goatnet-standup.md); it does not restate it.
- **No canon yet → write it once, then point.** Author the human how-to in one place and link it. The content lives in exactly one place regardless.

**The invariant:** `SKILL.md` and `GUIDE.md` are both thin wrappers over one canonical doc. A guide that duplicates the runbook instead of linking it is the anti-pattern this model exists to stop.

### 3. Three artifacts, named the Diátaxis way

[Diátaxis](https://diataxis.fr) is the documentation framework most of the open-source world uses. It separates *reference / explanation* (what a thing is and why) from *how-to / tutorial* (doing a task). Naming our three artifacts by it makes the layout legible to any developer:

| Artifact | Audience | Diátaxis role | Holds |
|---|---|---|---|
| `docs/design/*.md`, ADRs, runbooks | both, indirectly | Reference + Explanation | What the thing is and why. The single source. |
| `SKILL.md` | agent | How-to (automation) | When to fire, and the steps the agent runs. Points at the canon. |
| `GUIDE.md` | human | How-to / Tutorial | How a person does or supervises the task. Usually just a link to the runbook. |

The learning-oriented *tutorial* quadrant is where the **gym** (ADR 1132) already lives — per-role lanes that assemble these task guides into a curriculum. Guides publish through the gym, reusing its hosting and outside-reader gate, rather than a parallel site.

## Enforcement

`ops/ci/check-skill-audience.py` (wired in `.github/workflows/docs-guards.yml`) fails the build when:

- a `SKILL.md` has no `audience`, or a value other than `ai` / `both`; or
- a `both` skill has no `GUIDE.md`.

Absence surfaces instead of hiding — doctrine P2 / P8 applied to docs.

## Where each guide points

| Skill | Guide is… | Canonical target |
|---|---|---|
| `goatnet-standup` | a pointer | [`docs/operations/goatnet-standup.md`](https://github.com/usareur-af/goatcore/blob/main/docs/operations/goatnet-standup.md) |
| `env-door` | a pointer | [`docs/design/env-doors.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/env-doors.md) |
| `graduate` | a pointer | [`docs/design/release-graduation.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/release-graduation.md) |
| `goat-cli` | a pointer | `docs/design/goat-cli.md` + the CLI `--help` |
| `fastlane` | a pointer | [ADR 1127](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1127-fastlane-urgent-fleet-wide-delivery.md) |
| `record` | a pointer | [ADR 1011](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1011-findings-register.md) + the register conventions |

## Related

- [ADR 1174](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1174-skill-audience-and-human-guides.md) — the decision.
- [ADR 1132](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1132-goat-gym-training-surface.md) — the gym, the publish path for guides.
- [Diátaxis](https://diataxis.fr) — the external framework the naming follows.
