#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Render the weekly changelog from collect.py's output. No model, no person.

    weekly.py week.json --out docs/changelog/weekly/2026-W45.md --index docs/changelog/weekly/INDEX.md

The page lists what merged, grouped by the kind of change its author declared
in the pull request title (Conventional Commits). It explains nothing: the
written entries in docs/changelog/ do that. Rules the page keeps:

  - No counts. The page says what changed, never how much.
  - One line for one change. The same change made in several repositories
    (one title, many pull requests) is one line naming every repository.
  - A pull request merged into a branch other than its repository's default
    branch is listed apart: it is not in the product yet.
  - The same input always renders the same page.
  - Every repository that was read is named, with where its changes are
    listed, so a reader can see that none was skipped.
  - A repository named in own-changelog.txt has a page of its own,
    docs/changelog/weekly/<repository>/<week>.md. The main page lists only its
    highlights and links to that page.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]

# (heading, one-line description). Order is the order on the page.
SECTIONS = [
    ("decisions", "Decisions", "Architecture decision records added or amended."),
    ("features", "New capabilities", "Pull requests their authors titled `feat`."),
    ("security", "Security", "Security fixes and dependency updates that answer an advisory."),
    ("fixes", "Fixes", "Pull requests titled `fix` or `perf`."),
    ("docs", "Documentation", "Pull requests titled `docs`, apart from decision records."),
    ("upkeep", "Build, CI, tests and dependencies", "Pull requests titled `ci`, `build`, `chore`, `test`, `refactor` or `style`."),
    ("other", "Other", "Pull requests whose title names no kind of change."),
]
SECURITY_WORDS = re.compile(r"\b(cve-\d|ghsa-|rustsec-|vulnerab|advisor(y|ies))", re.I)


HIGHLIGHT_LINES = 3


def own_changelog() -> list[str]:
    """Repositories that have their own weekly page (see own-changelog.txt)."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "own-changelog.txt")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as handle:
        return [text.strip() for text in handle if text.strip() and not text.startswith("#")]


def only(data: dict, keep) -> dict:
    """The same window with only the repositories `keep` accepts."""
    return {**data,
            "repositories": [name for name in data["repositories"] if keep(name)],
            "merged": [row for row in data["merged"] if keep(row["repo"])],
            "open": [row for row in data["open"] if keep(row["repo"])],
            "releases": [row for row in data["releases"] if keep(row["repo"])]}


def has_changes(data: dict, repo: str) -> bool:
    since, until = instant(data["since"]), instant(data["until"])
    return (any(row["repo"] == repo for row in data["merged"])
            or any(row["repo"] == repo for row in data["releases"])
            or any(row["repo"] == repo and since <= instant(row["createdAt"]) < until for row in data["open"]))


def highlights(data: dict, repo: str) -> list[str]:
    """A few lines for the main page: releases, then security, then new capabilities."""
    notes = [f"released [{cell(release['tag'])}]({release['url']})"
             for release in data["releases"] if release["repo"] == repo]
    landed = [row for row in data["merged"] if row["repo"] == repo and row["onDefaultBranch"]]
    for key in ("security", "features"):
        for row in landed:
            if section_of(row) == key:
                marker = " **(breaking)**" if row["breaking"] else ""
                notes.append(f"{cell(row['text'])}{marker} [#{row['number']}]({row['url']})")
    if not notes:
        return ["fixes, documentation or upkeep only"] if landed else ["work opened or in review, nothing merged"]
    shown = notes[:HIGHLIGHT_LINES]
    return shown + (["more on its page"] if len(notes) > HIGHLIGHT_LINES else [])


def instant(value: str) -> dt.datetime:
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(dt.timezone.utc)


def day(moment: dt.datetime) -> str:
    return f"{moment.day} {MONTHS[moment.month - 1]} {moment.year}"


def span(since: dt.datetime, until: dt.datetime) -> str:
    """The window as inclusive days: [2 Nov 00:00, 9 Nov 00:00) reads 2 to 8 November 2026."""
    last = until - dt.timedelta(seconds=1)
    if (since.year, since.month) == (last.year, last.month):
        return f"{since.day} to {last.day} {MONTHS[last.month - 1]} {last.year}"
    if since.year == last.year:
        return f"{since.day} {MONTHS[since.month - 1]} to {last.day} {MONTHS[last.month - 1]} {last.year}"
    return f"{day(since)} to {day(last)}"


def week_label(since: dt.datetime) -> str:
    year, week, _ = since.isocalendar()
    return f"{year}-W{week:02d}"


def section_of(row: dict) -> str:
    kind, scope, title = row["type"], row["scope"].lower(), row["title"]
    if kind == "docs" and scope == "adr":
        return "decisions"
    if scope == "security" or SECURITY_WORDS.search(title):
        return "security"
    if kind == "feat":
        return "features"
    if kind in ("fix", "perf"):
        return "fixes"
    if kind == "docs":
        return "docs"
    if kind in ("ci", "build", "chore", "test", "refactor", "style", "revert"):
        return "upkeep"
    return "other"


def cell(text: str) -> str:
    """Text safe inside a Markdown list item or table cell."""
    return text.replace("|", "\\|").replace("<", "&lt;").replace(">", "&gt;").strip()


def link(row: dict) -> str:
    return f"{row['repo']} [#{row['number']}]({row['url']})"


def merge_siblings(rows: list[dict]) -> list[list[dict]]:
    """Group pull requests that carry one title: the same change in several repositories."""
    groups: dict[str, list[dict]] = {}
    for row in rows:
        groups.setdefault(row["title"].strip().lower(), []).append(row)
    ordered = sorted(groups.values(), key=lambda group: (len(group) == 1, group[0]["repo"].lower(),
                                                        group[0]["scope"].lower(), group[0]["number"]))
    return ordered


def line(group: list[dict]) -> str:
    first = group[0]
    lead = f"**{cell(first['scope'])}**: " if first["scope"] else ""
    marker = " **(breaking)**" if any(row["breaking"] for row in group) else ""
    text = cell(first["text"])
    if len(group) == 1:
        return f"- {lead}{text}{marker}. {link(first)}"
    links = ", ".join(link(row) for row in sorted(group, key=lambda row: row["repo"].lower()))
    return f"- {lead}{text}{marker}. In every one of: {links}"


def render(data: dict, own: list[str] | None = None, repo: str | None = None) -> str:
    """The main page, or with `repo` the page of one repository that has its own changelog."""
    full = data
    own = [name for name in (own or []) if name in full["repositories"]]
    if repo:
        data = only(full, lambda name: name == repo)
    else:
        data = only(full, lambda name: name not in own)
    since, until = instant(data["since"]), instant(data["until"])
    org = data["org"]
    landed = [row for row in data["merged"] if row["onDefaultBranch"]]
    elsewhere = [row for row in data["merged"] if not row["onDefaultBranch"]]
    label = week_label(since)
    if repo:
        out = [
            f"# {repo}: weekly changelog, {span(since, until)} ({label})",
            "",
            f"Every pull request merged in [{org}/{repo}](https://github.com/{org}/{repo}) in this week, grouped "
            "by the kind of change its author named in the title. This page is generated on a schedule from pull "
            "request titles and is not edited by hand. The other public repositories are on the "
            f"[main weekly page](../{label}.md).",
            "",
        ]
    else:
        out = [
            f"# Weekly changelog, {span(since, until)} ({label})",
            "",
            f"Every pull request merged in the public [{org}](https://github.com/{org}) repositories in this week, "
            "grouped by the kind of change its author named in the title. This page is generated on a schedule from "
            "pull request titles and is not edited by hand. It lists what merged and explains nothing: the "
            "[written entries](../INDEX.md) say what a change means for someone who runs or contributes to a goatnet.",
            "",
        ]
        changed = [name for name in own if has_changes(full, name)]
        if changed:
            out += [
                "## Repositories with their own changelog",
                "",
                "These repositories do not build from goatcore. Each has its own page for the week; only "
                "releases, security fixes and new capabilities are noted here.",
                "",
            ]
            for name in sorted(changed, key=str.lower):
                out.append(f"- **[{name}]({name}/{label}.md)**: " + "; ".join(highlights(full, name)) + ".")
            out.append("")
    if data["releases"]:
        out += ["## Releases", "", "| Repository | Release | Published |", "|---|---|---|"]
        for release in data["releases"]:
            flag = " (pre-release)" if release["prerelease"] else ""
            out.append(f"| {release['repo']} | [{cell(release['tag'])}]({release['url']}){flag} | "
                       f"{day(instant(release['publishedAt']))} |")
        out.append("")
    by_section: dict[str, list[dict]] = {}
    for row in landed:
        by_section.setdefault(section_of(row), []).append(row)
    for key, heading, about in SECTIONS:
        rows = by_section.get(key)
        if not rows:
            continue
        out += [f"## {heading}", "", about, ""]
        groups = merge_siblings(rows)
        shared = [group for group in groups if len(group) > 1]
        single: dict[str, list[list[dict]]] = {}
        for group in groups:
            if len(group) == 1:
                single.setdefault(group[0]["repo"], []).append(group)
        if shared:
            out += ["### In several repositories", ""] + [line(group) for group in shared] + [""]
        for name in sorted(single, key=str.lower):
            out += [f"### {name}", ""] + [line(group) for group in single[name]] + [""]
    if not landed:
        out += ["No pull request merged to a default branch in this week.", ""]
    if elsewhere:
        out += [
            "## Merged into a branch that is not the default branch",
            "",
            "These pull requests merged into an integration or stacked branch. They are not in the product "
            "until that branch itself merges.",
            "",
            "| Repository | Into branch | Change |",
            "|---|---|---|",
        ]
        for row in sorted(elsewhere, key=lambda row: (row["repo"].lower(), row["base"], row["number"])):
            out.append(f"| {row['repo']} | `{cell(row['base'])}` | {cell(row['title'])} "
                       f"[#{row['number']}]({row['url']}) |")
        out.append("")
    opened = [row for row in data["open"] if since <= instant(row["createdAt"]) < until]
    if opened:
        out += [
            "## Opened this week and still open",
            "",
            "Work in review when this page was generated. A draft is marked.",
            "",
        ]
        groups = merge_siblings(opened)
        for group in groups:
            first = group[0]
            draft = " (draft)" if all(row["draft"] for row in group) else ""
            if len(group) == 1:
                out.append(f"- {cell(first['title'])}{draft}. {link(first)}")
            else:
                links = ", ".join(link(row) for row in sorted(group, key=lambda row: row["repo"].lower()))
                out.append(f"- {cell(first['title'])}{draft}. In every one of: {links}")
        out.append("")
    if repo:
        out += ["---", "", f"Window: {data['since']} up to, not including, {data['until']} (UTC).", ""]
        return "\n".join(out)
    out += [
        "## Repositories read",
        "",
        "Every public repository that is not archived was read for this week.",
        "",
        "| Repository | This week |",
        "|---|---|",
    ]
    for name in full["repositories"]:
        if name in own:
            where = f"[its own page]({name}/{label}.md)" if has_changes(full, name) else "nothing merged or opened"
        else:
            where = "listed on this page" if has_changes(full, name) else "nothing merged or opened"
        out.append(f"| {name} | {where} |")
    out += ["", "---", "", f"Window: {data['since']} up to, not including, {data['until']} (UTC).", ""]
    return "\n".join(out)


def update_index(path: str, label: str, covers: str, repo: str | None = None) -> None:
    """Add this week's row under the table header; a week already listed is left as it is."""
    if repo:
        header = [
            f"# {repo}: weekly changelog",
            "",
            f"One page for each week in which {repo} changed, generated from its pull request titles by "
            "`.github/changelog/weekly.py`. The other public repositories are on the "
            "[main weekly pages](../INDEX.md).",
            "",
            "| Week | Covers |",
            "|---|---|",
        ]
    else:
        header = [
            "# Weekly changelog",
            "",
            "One page a week, generated from pull request titles across the public repositories by "
            "`.github/changelog/weekly.py`. A repository that does not build from goatcore has its own pages "
            "in a folder beside these, and each week's page links to them. For what a change means for you, "
            "read the [written entries](../INDEX.md).",
            "",
            "| Week | Covers |",
            "|---|---|",
        ]
    rows: list[str] = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as handle:
            rows = [text.rstrip("\n") for text in handle if text.startswith("| [")]
    row = f"| [{label}]({label}.md) | {covers} |"
    if not any(existing.startswith(f"| [{label}]") for existing in rows):
        rows.append(row)
    rows.sort(reverse=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(header + rows) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("data", help="JSON written by collect.py")
    parser.add_argument("--out", help="page to write (default: docs/changelog/weekly/<year>-W<week>.md)")
    parser.add_argument("--index", help="index page to add this week's row to")
    parser.add_argument("--written", help="file to list every page and index written, one path per line")
    args = parser.parse_args()
    with open(args.data, encoding="utf-8") as handle:
        data = json.load(handle)
    since, until = instant(data["since"]), instant(data["until"])
    label = week_label(since)
    out = args.out or os.path.join("docs", "changelog", "weekly", f"{label}.md")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    own = own_changelog()
    written = [out]
    with open(out, "w", encoding="utf-8") as handle:
        handle.write(render(data, own))
    if args.index:
        update_index(args.index, label, span(since, until))
        written.append(args.index)
    for repo in own:
        if repo not in data["repositories"] or not has_changes(data, repo):
            continue
        folder = os.path.join(os.path.dirname(out) or ".", repo)
        os.makedirs(folder, exist_ok=True)
        page = os.path.join(folder, f"{label}.md")
        with open(page, "w", encoding="utf-8") as handle:
            handle.write(render(data, own, repo=repo))
        written.append(page)
        if args.index:
            index = os.path.join(folder, "INDEX.md")
            update_index(index, label, span(since, until), repo=repo)
            written.append(index)
    if args.written:
        with open(args.written, "w", encoding="utf-8") as handle:
            handle.write("\n".join(written) + "\n")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
