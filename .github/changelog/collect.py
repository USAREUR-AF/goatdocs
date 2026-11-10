#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Collect what changed in every public repository of an organization.

One collector feeds both kinds of changelog: the weekly listing that
weekly.py renders with no person or model in the loop, and the written
entries a person (or their coding agent) authors from the same facts.

    collect.py --week last --out week.json
    collect.py --week 2026-W45 --out week.json
    collect.py --since 2026-11-08T12:00:00Z --bodies --cited-in docs/changelog/*.md --out window.json

It reads through the GitHub CLI (`gh`), so it uses whatever token `gh` has:
GH_TOKEN in a workflow, your own login on a laptop. Only public repositories
are read, so a changelog can never describe a private one. A repository whose
id is in left-out.txt is skipped: the leak gate refuses its name here.

What it records, per window [since, until):
  merged    every merged pull request, with its base branch and whether that
            base is the repository's default branch. A pull request merged
            into any other branch is not in the product yet.
  open      every open pull request, with its draft flag.
  releases  every release published in the window.
  cited     with --cited-in, whether an earlier entry already links the pull
            request, so a new entry does not repeat it.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys

TITLE = re.compile(r"^(?P<type>[a-z]+)(?:\((?P<scope>[^)]+)\))?(?P<bang>!)?:\s*(?P<text>.+)$")
PULL_LINK = re.compile(r"github\.com/(?P<org>[\w.-]+)/(?P<repo>[\w.-]+)/pull/(?P<number>\d+)")


def left_out() -> set[str]:
    """Ids of repositories the changelog never names (see left-out.txt)."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "left-out.txt")
    if not os.path.exists(path):
        return set()
    with open(path, encoding="utf-8") as handle:
        return {text.strip() for text in handle if text.strip() and not text.startswith("#")}


def repo_id(name: str) -> str:
    return hashlib.sha256(name.lower().encode("utf-8")).hexdigest()[:12]


def gh(*args: str) -> object:
    """Run one gh command and return its parsed JSON output."""
    run = subprocess.run(["gh", *args], capture_output=True, text=True)
    if run.returncode != 0:
        raise SystemExit(f"collect: gh {' '.join(args[:4])} failed: {run.stderr.strip()}")
    return json.loads(run.stdout or "null")


def instant(value: str) -> dt.datetime:
    """Parse a date or an ISO instant as UTC."""
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        value += "T00:00:00Z"
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(dt.timezone.utc)


def stamp(moment: dt.datetime) -> str:
    return moment.strftime("%Y-%m-%dT%H:%M:%SZ")


def week_window(value: str, now: dt.datetime | None = None) -> tuple[dt.datetime, dt.datetime]:
    """An ISO week as [Monday 00:00 UTC, next Monday 00:00 UTC). "last" is the last full week."""
    if value == "last":
        now = now or dt.datetime.now(dt.timezone.utc)
        this_monday = (now - dt.timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        start = this_monday - dt.timedelta(days=7)
    else:
        found = re.fullmatch(r"(\d{4})-W(\d{2})", value)
        if not found:
            raise SystemExit("collect: --week takes 'last' or a week such as 2026-W45")
        start = dt.datetime.fromisocalendar(int(found[1]), int(found[2]), 1).replace(tzinfo=dt.timezone.utc)
    return start, start + dt.timedelta(days=7)


def parse_title(title: str) -> dict:
    """Split a Conventional Commits title; an unparsed title keeps its text."""
    found = TITLE.match(title.strip())
    if not found:
        return {"type": "", "scope": "", "breaking": False, "text": title.strip()}
    return {
        "type": found["type"],
        "scope": found["scope"] or "",
        "breaking": bool(found["bang"]),
        "text": found["text"].strip(),
    }


def cited_pulls(org: str, paths: list[str]) -> set[tuple[str, int]]:
    cited: set[tuple[str, int]] = set()
    for path in paths:
        with open(path, encoding="utf-8") as handle:
            for found in PULL_LINK.finditer(handle.read()):
                if found["org"].lower() == org.lower():
                    cited.add((found["repo"], int(found["number"])))
    return cited


def collect(org: str, since: dt.datetime, until: dt.datetime, bodies: bool, cited: set) -> dict:
    repos = gh("repo", "list", org, "--visibility", "public", "--no-archived", "--limit", "500",
               "--json", "name,defaultBranchRef")
    skip = left_out()
    repos = sorted((repo for repo in repos if repo_id(repo["name"]) not in skip), key=lambda repo: repo["name"].lower())
    fields = "number,title,author,mergedAt,baseRefName,url" + (",body" if bodies else "")
    merged, still_open, releases = [], [], []
    for repo in repos:
        name = repo["name"]
        default = (repo.get("defaultBranchRef") or {}).get("name") or "main"
        slug = f"{org}/{name}"
        window = f"merged:{stamp(since)}..{stamp(until)}"
        for pull in gh("pr", "list", "-R", slug, "--state", "merged", "--limit", "1000",
                       "--search", window, "--json", fields):
            when = instant(pull["mergedAt"])
            if not since <= when < until:
                continue
            row = {
                "repo": name,
                "number": pull["number"],
                "title": pull["title"],
                "author": (pull.get("author") or {}).get("login", ""),
                "mergedAt": stamp(when),
                "base": pull["baseRefName"],
                "onDefaultBranch": pull["baseRefName"] == default,
                "url": pull["url"],
                "cited": (name, pull["number"]) in cited,
                **parse_title(pull["title"]),
            }
            if bodies:
                row["body"] = pull.get("body") or ""
            merged.append(row)
        for pull in gh("pr", "list", "-R", slug, "--state", "open", "--limit", "1000",
                       "--json", "number,title,author,createdAt,isDraft,baseRefName,url"):
            still_open.append({
                "repo": name,
                "number": pull["number"],
                "title": pull["title"],
                "author": (pull.get("author") or {}).get("login", ""),
                "createdAt": pull["createdAt"],
                "draft": pull["isDraft"],
                "base": pull["baseRefName"],
                "onDefaultBranch": pull["baseRefName"] == default,
                "url": pull["url"],
                **parse_title(pull["title"]),
            })
        for release in gh("api", f"repos/{slug}/releases?per_page=100") or []:
            published = release.get("published_at")
            if release.get("draft") or not published:
                continue
            if since <= instant(published) < until:
                releases.append({
                    "repo": name,
                    "tag": release["tag_name"],
                    "name": release.get("name") or release["tag_name"],
                    "publishedAt": published,
                    "prerelease": bool(release.get("prerelease")),
                    "url": release["html_url"],
                })
    merged.sort(key=lambda row: (row["repo"].lower(), row["number"]))
    still_open.sort(key=lambda row: (row["repo"].lower(), row["number"]))
    releases.sort(key=lambda row: (row["repo"].lower(), row["publishedAt"]))
    return {
        "org": org,
        "since": stamp(since),
        "until": stamp(until),
        "repositories": [repo["name"] for repo in repos],
        "merged": merged,
        "open": still_open,
        "releases": releases,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--org", default="USAREUR-AF")
    parser.add_argument("--week", help="'last' (the last full ISO week) or a week such as 2026-W45")
    parser.add_argument("--since", help="start of the window (date or ISO instant, UTC), inclusive")
    parser.add_argument("--until", help="end of the window, exclusive (default: now)")
    parser.add_argument("--bodies", action="store_true", help="include each merged pull request's description")
    parser.add_argument("--cited-in", nargs="*", default=[], metavar="FILE",
                        help="earlier entries; a pull request they link is marked cited")
    parser.add_argument("--out", default="-", help="output file (default: standard output)")
    args = parser.parse_args()
    if bool(args.week) == bool(args.since):
        raise SystemExit("collect: give exactly one of --week and --since")
    if args.week:
        since, until = week_window(args.week)
    else:
        since = instant(args.since)
        until = instant(args.until) if args.until else dt.datetime.now(dt.timezone.utc)
    if until <= since:
        raise SystemExit("collect: --until must be after --since")
    data = collect(args.org, since, until, args.bodies, cited_pulls(args.org, args.cited_in))
    text = json.dumps(data, indent=1, ensure_ascii=False) + "\n"
    if args.out == "-":
        sys.stdout.write(text)
    else:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
