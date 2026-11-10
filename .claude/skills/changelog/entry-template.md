# Changelog, <day> to <day> <Month> <year>: <the two changes that matter most>

<What is true now that was not before, in two or three sentences. No history, no counts.>

This entry covers the public [USAREUR-AF](https://github.com/USAREUR-AF) repositories, because a change in one usually lands with matching changes in others. It follows [the entry for <previous window>](<previous-entry>.md).

## In short

- **<The point, as a full sentence.>** <One more sentence if the reader needs it> ([section 1](#1-first-section-title)).
- **<Next point.>** ([section 2](#2-second-section-title)).
- **Not in `main` yet:** <what is in review and where> ([section N](#n-still-in-progress)).

## What to do

| If you | Do this | Why |
|---|---|---|
| <a kind of reader> | <a command, a version, a variable: something that can be typed or set> | <the rule or change behind it, with its ADR or pull request> |

## Who should read what

| If you | Read | Because |
|---|---|---|
| contribute code or documents | [1](#1-first-section-title) | <what changed for them> |
| run a goatnet | [2](#2-second-section-title) | <what changed for them> |

Each pull request's page names its author and any co-authors.

---

## 1. <First section title: the change, not the component>

<Two plain sentences a reader with no context understands. What is different, and for whom.>

![<The whole message of the figure in one sentence, usable with the image missing>](figures/<date>/<name>.svg)

| Change | What you see | PR |
|---|---|---|
| <the change, named> | <the effect, with the real file, command, variable or limit> | <repo> [#<n>](https://github.com/USAREUR-AF/<repo>/pull/<n>) (`<handle>` when from outside the maintainers) |

- **<A point that does not fit a table row.>** <Its detail> (<repo> [#<n>](https://github.com/USAREUR-AF/<repo>/pull/<n>)).

## 2. <Second section title>

<Two plain sentences.>

### <A sub-heading only when the section holds two different things>

**None of this is in `main`.** <Use this line, with the branch name and what brings it to `main`, above anything merged into an integration branch.>

## N. Still in progress

These areas are moving now. Status words are the ones the repositories use.

| Area | State | Watch |
|---|---|---|
| <area> | **<In review / Proposed / WIP / Open / Draft>**: <one line, with the gate if it is WIP> | <repo> [#<n>](https://github.com/USAREUR-AF/<repo>/pull/<n>) |

## About this entry

- **Window.** Pull requests merged from <start> to <end, UTC>, in the public USAREUR-AF repositories.
- **What "merged" means here.** A change is described as part of goat only when it merged into a repository's default branch. A pull request merged into any other branch is reported as in review.
- **The weekly listing.** [`weekly/`](weekly/INDEX.md) lists every merged pull request by kind, one page per ISO week, generated with no person or model in the loop. Written entries explain; the weekly listing is the complete record.
