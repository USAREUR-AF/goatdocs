---
name: splash-page
description: Build or revise a project's landing page on GitHub Pages in the house style, the shape of ziggity.dev: wordmark and terminal prompt, Star on GitHub, a copyable command, the real thing running in the first screen, measured numbers where the project has real ones, declarative sections, light and dark, checked in CI. Use whenever asked for a splash page, landing page, project page, showcase page, GitHub Pages site, "a page like ziggity" or "like our other repos" for a repository, including a repository created minutes ago; when a component inside a larger repository needs its own page (a goatdocs sub-page); and when an existing landing page needs a new section, a fix, or its numbers brought back in line with the tree.
---

# Splash page

A landing page sells a repository to someone who has never heard of it, in one screen, and
proves every claim it makes. The house pattern is live on every page `examples.md` lists, with
what each first screen shows; https://usareur-af.github.io/goatdocs/goat/splash-page/ shows
them side by side and was built with this skill. Read two of them before writing another.

This skill ships a skeleton (`templates/`), a scaffold script that lays it down without
overwriting anything, and the two checks every page passes: numbers against the tree, and
command boxes at 1440 and 390 px.

## 1. Own site or sub-page

| The project is | Page goes | Served at |
|---|---|---|
| its own public repository | `site/` in that repository, `.github/workflows/pages.yml` | `https://<owner>.github.io/<repo>/` |
| a component inside a larger repository (a service in goatstuff, a tool in goatcore) | goatdocs, `docs/goat/<slug>/index.html`, one self-contained file, linked from `docs/goat/index.html` | `https://usareur-af.github.io/goatdocs/goat/<slug>/` |
| a facet of something that already has a page (a decoder, a contributor guide) | a second page in the same `site/` (`contribute.html`, `decoder/`), listed in `PAGES` in `site/build.py` | beside its parent |
| a private repository | no public page unless the operator says the content is public; then a goatdocs sub-page that names only what is public | |

## 2. Lay down the skeleton

```bash
SK=<this skill's directory>
python3 -I "$SK/scaffold.py" site <repo-root> --name <repo> --repo USAREUR-AF/<repo> \
  --tagline "<one line>" --start "<the one command that shows it working>" --prompt "<prompt line>"
# or, for a goatdocs sub-page:
python3 -I "$SK/scaffold.py" subpage <goatdocs-root> --slug <slug> --name <name> --repo USAREUR-AF/<repo> ...
```

Every value not given stays a placeholder, and `site/build.py` refuses to pass until each one
is replaced in `index.html` and every file under `assets/`. The sub-page mode prints the three
goatdocs wiring edits (link from `docs/goat/index.html`, `exclude_docs` in `mkdocs.yml`, the
`fitcheck.py` line in `.github/workflows/pages.yml`).

## 3. The first screen

The first screen is the whole pitch. Above it, on every page, is the goat-tree strip: one line,
`<nav class="goat-tree">` with "← All goat pages" linking to
https://usareur-af.github.io/goatdocs/goat/pages/, the catalogue, so a reader exploring one page
can reach all of them. It is the body's first element after the skip link, in the template's
markup and CSS word for word; it takes its colors from the page, so it fits any palette. The
catalogue itself carries "↑ goat" in its place. Then, top to bottom, left column:

1. **Prompt line**: `>_ <a command that names what the stage shows>` with a blinking cursor.
2. **Wordmark**: the repository name in heavy monospace. One word where the name allows.
3. **Tagline**: one line in the accent color. What it does, with what.
4. **Lede**: two or three plain sentences, then stop.
5. **Buttons**: `Star on GitHub` (filled, with the star icon) first, then two or three of Quick start, README, the specification, a contributor page.
6. **Command box** with Copy: the one command that shows the project working from a clone.

Right column, **the stage**: the real thing working, taken from the tree and replayed. Never a
mock, never invented data. What each live page uses:

- a test vector replayed step by step with its own trace records (goat-processors)
- a real capture decoded byte by byte (open-billie, first-bite, goat-transformers)
- a session recorded against a running instance by `build.py` (saltlick, goat-client)
- the real program, built to WebAssembly or embedded (goatrodeo, goat-transformers)
- what crosses a boundary for one record (vendor-bridges, zagros-moon-pod)

The lines already in the HTML are the frame shown without JavaScript and with reduced motion:
pick the one frame that tells the story. `aria-label` on the stage says in full sentences
what the replay shows.

Behind the hero, faint (`.bgcode`, `aria-hidden`), a real file from the tree: a pack, a
config, a schema. At the bottom edge of the first screen, **the numbers strip**, only when the project has
numbers its reader would ask about (vectors that pass, binary size, startup time, formats it
converts), each with the command that measures it under it in small monospace. Up to four;
never padded to four. Never a count invented to fill the strip (pages in a list, groups,
template files, widths checked, numbers stated). A catalogue, an index or a page about a
tool has no strip. Leave the strip out rather than fill it.

## 4. Below the fold

Sections are `<section class="band">`, each with a declarative `h2` that states a claim
("Every decision is in the trace", "Seven engines check each other"), never a bare label
other than "What it is" and "Quick start". Usual order: What it is (three cards) → two or
three feature bands (prose with one real output, plus a figure) → status tiles if the
project has designed-not-built parts → Quick start → footer.

Footer, always: Repository · Apache License 2.0 · Security policy, then "Portions written by
U.S. Federal government employees within the scope of their employment are in the public
domain in the United States. Part of goat." linked to goatcore.

## 5. Rules the checks enforce

| Rule | Enforced by |
|---|---|
| Every number is in `data-measure="<key>"` and `MEASURES` in `site/build.py` computes the same text from the tree; `site/README.md` says how each is measured | `build.py` |
| Every `<pre>` is `data-box="command"` (shows whole at any width, wraps at spaces, each line a `<span class="ln">`, long tokens in `<span class="w">`) or `data-box="output"` (fits at 1440 px) | `fitcheck.py` |
| The page never scrolls sideways at 1440 or 390 px | `fitcheck.py` |
| No placeholder survives | `build.py` |
| The goat-tree strip is on the page and links to the catalogue | goatdocs `docs/goat/pages/collect.py` records it from each live page; `build.py --check` fails while any page lacks it |
| Figures and captures are copied from the tree into `assets/from-tree/` (git-ignored), never committed twice | `build.py` `FROM_TREE` |
| A status tile shows the least-built status (Built, Written, Designed) of what it names, read from the file the README is written from | `build.py` (copy `check_agentic` from goat-processors `site/build.py`) |

The workflow runs the checks on every pull request that touches the page or anything it
measures. Put every measured path in both `paths:` lists of `pages.yml`, so a change that
moves a number fails before the merge.

## 6. Rules no script catches

- **One static page.** No framework, no build step beyond copying, no external request, no web font, no analytics, no tracking.
- **Its own metaphor.** The first line of `site.css` names it, taken from what the project does (a plotting table, a laid rope, a field map), and the palette and background follow it. Every page keeps the roles in the token block, light and dark through `prefers-color-scheme`, text contrast 4.5:1 and marks 3:1 in both.
- **Figures** are fixed-layout SVG drawn by code in the tree, light and dark, checked at real size; never Graphviz or auto-layout. Load the `visualization` skill, if the session has it, before drawing one. In a figure of forces, tracks or units, red means hostile: no red, orange, yellow or purple for status; show state by pattern and grey.
- **Voice**: short declarative sentences, American spelling, no idioms, no exclamation marks, no superlatives ("blazing", "powerful", "seamless"). Name the real thing: path, command, format, version. State what is built as built and what is designed as designed.
- **No activity volume.** No stars, commits, contributors, downloads or "trusted by".
- **Nothing of a real deployment.** No goatnet name, host, address, person, place or unit. Use the example goatnet `zagros`, `example.test` addresses and documentation ranges (198.51.100.0/24). Screenshots are taken with example data.
- **Motion** has a purpose (the replay, the cursor) and stops with `prefers-reduced-motion`.

## 7. Check it, then ship it

1. `python3 -I site/build.py` passes (needs Chrome; `$CHROME` or the macOS app).
2. Look at it: serve `site/`, screenshot at 1440 and 390 px in light and dark, and read every screenshot. In headless Chrome a narrow window may be clamped; load the page in a 390 px iframe to see the true phone width.
3. Read the text cold: `sed 's/<[^>]*>/ /g' site/index.html | tr -s ' ' | fold -s -w 160`.
4. Run the repository's leak gate on the diff before any push to a public repository.
5. Branch, signed DCO commit (`git commit -S -s`), pull request, merge on zero failing checks.
6. **Owner actions, confirmed with the operator first** because they publish: Settings → Pages → Source "GitHub Actions" (`gh api -X POST repos/<owner>/<repo>/pages -f build_type=workflow`), then the repository's website field (`gh repo edit <owner>/<repo> --homepage https://<owner>.github.io/<repo>/`). Until Pages is set, the workflow checks the page and skips the deploy with a notice.
7. Link the page from the README's first lines and, for a goat repository, from `docs/goat/index.html` in goatdocs.

## Where this skill lives

The source is goatdocs `.claude/skills/splash-page/`. The goatdocs site publishes a one-file
plugin catalogue, `https://usareur-af.github.io/goatdocs/claude/marketplace.json` (source: goatdocs `docs/claude/marketplace.json`).
Its plugin `goat-skills` is the folder `.claude/` of goatdocs, fetched on its own
(`git-subdir`), about 100 KB; nobody clones goatdocs to get it. Install once per person and the
skill is present in every repository, including one that has no files yet:

```
/plugin install goat-skills --marketplace https://usareur-af.github.io/goatdocs/claude/marketplace.json
```

A repository can ask for it on its own: its `.claude/settings.json` carries

```json
{
  "extraKnownMarketplaces": { "goat": { "source": { "source": "url", "url": "https://usareur-af.github.io/goatdocs/claude/marketplace.json" } } },
  "enabledPlugins": { "goat-skills@goat": true }
}
```

and Claude Code offers the install to anyone who opens it. Add that block when scaffolding a
page into a repository that has no `.claude/settings.json`, or merge it into one that does.
Never copy this skill into another repository; a copy drifts.
