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


def render(data: dict) -> str:
    since, until = instant(data["since"]), instant(data["until"])
    org = data["org"]
    landed = [row for row in data["merged"] if row["onDefaultBranch"]]
    elsewhere = [row for row in data["merged"] if not row["onDefaultBranch"]]
    out = [
        f"# Weekly changelog, {span(since, until)} ({week_label(since)})",
        "",
        f"Every pull request merged in the public [{org}](https://github.com/{org}) repositories in this week, "
        "grouped by the kind of change its author named in the title. This page is generated on a schedule from "
        "pull request titles and is not edited by hand. It lists what merged and explains nothing: the "
        "[written entries](../INDEX.md) say what a change means for someone who runs or contributes to a goatnet.",
        "",
    ]
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
        for repo in sorted(single, key=str.lower):
            out += [f"### {repo}", ""] + [line(group) for group in single[repo]] + [""]
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
    out += [
        "---",
        "",
        f"Window: {data['since']} up to, not including, {data['until']} (UTC). Repositories read: "
        + ", ".join(data["repositories"]) + ".",
        "",
    ]
    return "\n".join(out)


def update_index(path: str, label: str, covers: str) -> None:
    """Add this week's row under the table header; a week already listed is left as it is."""
    header = [
        "# Weekly changelog",
        "",
        "One page a week, generated from pull request titles across the public repositories by "
        "`.github/changelog/weekly.py`. For what a change means for you, read the "
        "[written entries](../INDEX.md).",
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
    args = parser.parse_args()
    with open(args.data, encoding="utf-8") as handle:
        data = json.load(handle)
    since, until = instant(data["since"]), instant(data["until"])
    label = week_label(since)
    out = args.out or os.path.join("docs", "changelog", "weekly", f"{label}.md")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as handle:
        handle.write(render(data))
    if args.index:
        update_index(args.index, label, span(since, until))
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
