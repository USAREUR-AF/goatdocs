#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check a written changelog entry against what actually merged.

    collect.py --since <end of the previous entry> --bodies --cited-in docs/changelog/2*.md --out window.json
    check.py docs/changelog/2026-11-10-example.md window.json

Fails (exit 1) when the entry:
  - reports activity volume ("142 pull requests", "74 commits"): an entry
    says what changed, never how much;
  - links a pull request that is neither merged in the window, merged before
    it, nor open: a wrong number;
  - uses a figure that does not stand alone (see figure.py).

Prints, for the author to act on:
  - every pull request the entry links that merged into a branch other than
    the default branch. Each must be described as in review, not as part of
    the product;
  - every pull request merged in the window that the entry does not link.
    Link it, or leave it to the weekly listing on purpose.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys

import figure

PULL = re.compile(r"github\.com/(?P<org>[\w.-]+)/(?P<repo>[\w.-]+)/pull/(?P<number>\d+)")
VOLUME = re.compile(r"\b\d[\d,]*\s+(merged\s+)?(pull requests|prs|commits|changes merged|contributors)\b", re.I)


def exists(org: str, repo: str, number: int) -> bool:
    run = subprocess.run(["gh", "api", f"repos/{org}/{repo}/pulls/{number}", "--jq", ".number"],
                         capture_output=True, text=True)
    return run.returncode == 0


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__, file=sys.stderr)
        return 2
    entry, data_path = sys.argv[1], sys.argv[2]
    with open(entry, encoding="utf-8") as handle:
        text = handle.read()
    with open(data_path, encoding="utf-8") as handle:
        data = json.load(handle)
    org = data["org"]
    merged = {(row["repo"], row["number"]): row for row in data["merged"]}
    still_open = {(row["repo"], row["number"]) for row in data["open"]}
    linked = {(found["repo"], int(found["number"])) for found in PULL.finditer(text)
              if found["org"].lower() == org.lower()}
    failed = False

    for number, line in enumerate(text.splitlines(), 1):
        if VOLUME.search(line):
            print(f"FAIL {entry}:{number}: activity volume: {VOLUME.search(line).group(0)!r}")
            failed = True
    for repo, number in sorted(linked - set(merged) - still_open):
        if not exists(org, repo, number):
            print(f"FAIL {repo}#{number}: no such pull request")
            failed = True
    if figure.check(entry):
        failed = True

    apart = sorted(key for key in linked & set(merged) if not merged[key]["onDefaultBranch"])
    if apart:
        print("\nLinked, but merged into a branch that is not the default branch. Describe each as in review:")
        for key in apart:
            print(f"  {key[0]}#{key[1]} -> {merged[key]['base']}: {merged[key]['title']}")
    unlinked = sorted(key for key, row in merged.items() if key not in linked and not row.get("cited"))
    if unlinked:
        print("\nMerged in the window and not linked. Link it, or leave it to the weekly listing on purpose:")
        for key in unlinked:
            print(f"  {key[0]}#{key[1]}: {merged[key]['title']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
