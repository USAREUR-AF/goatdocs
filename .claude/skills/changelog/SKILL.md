---
name: changelog
description: Write a goat changelog entry, the page that tells people who run or contribute to a goatnet what changed and what to do about it. Use whenever asked for a changelog, release notes, a "what changed since" summary, a community update, or the next entry after the last one; when asked to improve or review an entry; and when the weekly generated listing needs changing. Covers every public repository of the organization as one body of work, the entry's fixed shape (short notes first, then detail), figures, the checks an entry must pass, and the weekly listing that is generated with no model.
---

# Changelog

Two things live in `docs/changelog/`, and they do different jobs.

| | Written entry | Weekly listing |
|---|---|---|
| File | `docs/changelog/<date>-<slug>.md` | `docs/changelog/weekly/<year>-W<week>.md` |
| Made by | a person or their coding agent, with this skill | `.github/workflows/changelog-weekly.yml`, every Monday, no model |
| Says | what changed, what it means for the reader, what to do | every merged pull request, by kind, from its title |
| Complete? | no: it selects and explains | yes: it is the record |

This skill is for the written entry. The last section covers the weekly listing.

## The reader

Someone who runs a goatnet, federates with one, or contributes code, and who was not watching the repositories. They want three answers, in this order: what changed, does it affect me, what do I do. They are not helped by how much work was done.

## Rules that decide everything else

1. **All public repositories, one story.** A change in goatcore usually lands with matching changes in goatstuff, goatrodeo, the hello-galaxy repositories and others. Collect every public repository of the organization, and organize the entry by what changed, never by repository.
2. **Start where the last entry stopped.** The window opens when the previous entry was written and closes now. A pull request the previous entry already links is not repeated.
3. **Merged means merged into the default branch.** A pull request merged into an integration or stacked branch is not part of goat yet. Describe it as in review, name the branch, and say what brings it to `main`. `collect.py` records the base branch of every pull request for this reason.
4. **No activity volume.** No counts of pull requests, commits or contributors, no tiles of totals, no charts of volume. A number appears only when it is a fact about the product (a limit, a port, a version, a measured time).
5. **Short notes first, detail underneath.** The top of the entry must be enough for a reader who stops there. Every section opens with two plain sentences, then the specifics.
6. **Name the real thing.** A file path, a command, a variable, an ADR number, a version, and a link to the pull request. Never "the config" or "some fixes".
7. **Status words mean what the repositories mean:** built, measured, designed, proposed, WIP (with its gate), in review, open. A proposed ADR is proposed. Something not built is stated as designed.
8. **Nothing of a real deployment.** The leak gate refuses hostnames, domains, addresses, people, places and organizations of any real goatnet. Describe the maintainers' own environments only as "the maintainers' environments". Use the example goatnet `zagros`.
9. **Credit by handle, on the change.** Name a contributor by GitHub handle next to their pull request. Do not write a thanks section.
10. **The leak gate decides what may be named, and a changelog never exempts a line.** `oss-allow` is not for changelogs. When the gate refuses a name that is public by the project's own act (a public repository's name, a contributor's handle), an owner takes it off the private scan list; until then leave the handle out, and skip a repository whose name is refused by adding its id to `.github/changelog/left-out.txt`. When the gate refuses anything else, the entry is naming something of a real deployment: rename or remove it.

## Steps

### 1. Collect

```bash
python3 .github/changelog/collect.py \
  --since <when the previous entry was written, UTC> \
  --bodies --cited-in docs/changelog/2*.md \
  --out /tmp/window.json
```

Read the titles first, then the descriptions of the pull requests that change behavior. Read open pull requests too: they are the "still in progress" section. Check each release the window published (`releases` in the output).

### 2. Find the story before writing

Sort the pull requests into what changed for the reader. Typical groups: contributing rules, the tools and their releases, federation, deploying and secrets, a first goatnet, security fixes, the smaller repositories. Then answer in one sentence each:

- What are the two or three changes a reader must know? Those are the title and the lead.
- What must a reader **do**? Each answer is a row of the "What to do" table: a command to run, a version to install, a variable to set. If nothing requires action, say so in one line and omit the table.
- What looks finished and is not? That goes under "Still in progress".

### 3. Write, in this shape

Copy [`entry-template.md`](entry-template.md). The parts, in order:

| Part | What it holds | Limit |
|---|---|---|
| Title | `# Changelog, <d> to <d> <Month> <year>: <the two changes that matter most>` | one line |
| Lead | What is true now that was not before. Then one sentence naming the repositories covered and linking the previous entry | two short paragraphs |
| In short | One bullet per change a reader must know, each starting with the point in bold and ending with a link to its section | 5 to 8 bullets |
| What to do | `If you` / `Do this` / `Why`. Exact commands and variables | only real actions |
| Who should read what | `If you` / `Read` / `Because`, by role | 4 to 6 rows |
| Numbered sections | One per group. Two plain sentences, then a figure if it explains a mechanism, then a table of changes with their pull requests | as many as the story needs |
| Still in progress | `Area` / `State` / `Watch`: what is in review, proposed, WIP or open | a table |
| About this entry | The window, what "merged" means here, the weekly listing | a short list |

Sentences are short and literal. American spelling. No idioms. State the design as it is, never the order in which it was worked out.

### 4. Figures

A figure earns its place when it shows a mechanism or a state that a table cannot: an order of steps, a before and after, what crosses a boundary, where something is on its way to `main`. Never a count, a volume or a decoration. Most entries need two to four.

For each figure, write two sentences before drawing:

1. **The finding, as the title:** "A release travels one hop unless its owner says otherwise", never "Release transit".
2. **The whole message, as the alt text:** one sentence a reader could use with the image missing.

Then:

- Draw it as an SVG whose shapes use the classes in `.github/changelog/figure.css` (the goat design system's colors, light and dark, every pair checked for contrast). No literal colors. Text at least 13 units. Nothing overlapping, nothing clipped. If your session has a measured figure toolkit or a visualization skill, build with it; do not use Mermaid.
- Make it stand alone: `python3 .github/changelog/figure.py wrap drawing.svg docs/changelog/figures/<date>/<name>.svg`. This embeds the styles, a background, a `<title>` and a `<desc>`, so the file reads the same on GitHub, on the docs site and in a page.
- Put it in the entry as `![<the whole message>](figures/<date>/<name>.svg)`, directly under the two plain sentences it supports.
- Look at every figure rendered, in light and in dark, before you commit. A figure nobody looked at is not finished.

### 5. Check

```bash
python3 .github/changelog/check.py docs/changelog/<entry>.md /tmp/window.json
```

It fails on activity volume, on a link to a pull request that does not exist, and on a figure that does not stand alone. It prints two lists to act on: linked pull requests that merged into a branch other than the default branch (each must read as in review), and merged pull requests the entry does not link (link each, or leave it to the weekly listing on purpose: repeated housekeeping across repositories usually belongs there).

Then read the entry from the top as someone who was not there:

- Does the "In short" list alone tell a reader what changed?
- Does every "What to do" row give something that can be typed or set?
- Does each section's first two sentences make sense with no other context?
- Is every status word true today? Open the ADR or design document and read its status line.
- Is any claim taken from a pull request description that you did not confirm in the repository? Confirm it or cut it.

### 6. Publish

- Add a row to `docs/changelog/INDEX.md`: the file, and one line naming the window and the main changes.
- One pull request, title `docs(changelog): <window>, <the main change>`. Every commit signed off and signed.
- Before pushing, run the documentation checks from a goatcore checkout beside this one (`AGENTS.md`, "Before you push").
- If a page version is wanted for sharing, build it from the same Markdown and the same figure files, so the two never disagree.

## The weekly listing

`.github/workflows/changelog-weekly.yml` runs every Monday at 06:17 UTC. It reads every public repository for the last full ISO week, renders `docs/changelog/weekly/<year>-W<week>.md`, and opens a pull request that adds it. No model takes part, and nobody edits the page.

| File | Job |
|---|---|
| `.github/changelog/collect.py` | reads the repositories through `gh`; the same collector this skill uses |
| `.github/changelog/weekly.py` | renders the page from pull request titles; the same input always gives the same page |
| `.github/changelog/propose.py` | commits through the GitHub API, so GitHub signs the commit, and opens the pull request |
| `.github/changelog/tests/` | `python3 -m unittest discover -s .github/changelog/tests` |

To generate a week by hand: Actions, `changelog-weekly`, Run workflow, with a week such as `2026-W45`. Locally:

```bash
python3 .github/changelog/collect.py --week 2026-W45 --out /tmp/week.json
python3 .github/changelog/weekly.py /tmp/week.json --index docs/changelog/weekly/INDEX.md
```

The listing groups by the kind of change the author named in the title, so it is only as good as the titles. To change how the listing reads, change `weekly.py` and its tests, then run the workflow again for the week. Never hand-edit a generated page.
