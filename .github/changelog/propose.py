#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Open a pull request that carries files written in this checkout.

    propose.py --branch changelog/weekly-2026-W45 \
        --title "docs(changelog): weekly changelog 2026-W45" --body-file body.md \
        docs/changelog/weekly/2026-W45.md docs/changelog/weekly/INDEX.md

The commit is made through the GitHub API (createCommitOnBranch), so GitHub
signs it and the pull request passes the verified-commits check. Nothing is
committed with git, and no signing key is needed in the workflow.

It does nothing, and exits 0, when every file already has this content on the
default branch, or when a pull request for the branch is already open.

Where the organization does not let a workflow open a pull request, it opens
an issue that carries the link an owner clicks to open it.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys


def gh(*args: str, check: bool = True, stdin: str | None = None) -> subprocess.CompletedProcess:
    run = subprocess.run(["gh", *args], capture_output=True, text=True, input=stdin)
    if check and run.returncode != 0:
        raise SystemExit(f"propose: gh {' '.join(args[:3])} failed: {run.stderr.strip()}")
    return run


def remote_text(repo: str, path: str, ref: str) -> str | None:
    run = gh("api", f"repos/{repo}/contents/{path}?ref={ref}", "-H", "Accept: application/vnd.github.raw", check=False)
    return run.stdout if run.returncode == 0 else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"), help="owner/name")
    parser.add_argument("--branch", required=True)
    parser.add_argument("--title", required=True, help="commit headline and pull request title")
    parser.add_argument("--body-file", required=True)
    parser.add_argument("--signoff", default=os.environ.get("CHANGELOG_SIGNOFF", ""),
                        help="'Name <email>' for the DCO Signed-off-by line")
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()
    if not args.repo:
        raise SystemExit("propose: --repo or GITHUB_REPOSITORY is required")

    default = json.loads(gh("api", f"repos/{args.repo}").stdout)["default_branch"]
    changed = []
    for path in args.files:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        if remote_text(args.repo, path, default) != text:
            changed.append((path, text))
    if not changed:
        print("propose: the default branch already has this content; nothing to do")
        return 0
    open_pulls = json.loads(gh("pr", "list", "-R", args.repo, "--head", args.branch, "--state", "open",
                               "--json", "number").stdout)
    if open_pulls:
        print(f"propose: pull request #{open_pulls[0]['number']} for {args.branch} is already open; nothing to do")
        return 0

    head = json.loads(gh("api", f"repos/{args.repo}/git/ref/heads/{default}").stdout)["object"]["sha"]
    made = gh("api", "-X", "POST", f"repos/{args.repo}/git/refs", "-f", f"ref=refs/heads/{args.branch}",
              "-f", f"sha={head}", check=False)
    if made.returncode != 0 and "Reference already exists" not in made.stderr:
        raise SystemExit(f"propose: could not create {args.branch}: {made.stderr.strip()}")
    if made.returncode != 0:
        head = json.loads(gh("api", f"repos/{args.repo}/git/ref/heads/{args.branch}").stdout)["object"]["sha"]

    message = {"headline": args.title}
    if args.signoff:
        message["body"] = f"Signed-off-by: {args.signoff}"
    query = ("mutation($input: CreateCommitOnBranchInput!) "
             "{ createCommitOnBranch(input: $input) { commit { oid url } } }")
    payload = {
        "query": query,
        "variables": {"input": {
            "branch": {"repositoryNameWithOwner": args.repo, "branchName": args.branch},
            "expectedHeadOid": head,
            "message": message,
            "fileChanges": {"additions": [
                {"path": path, "contents": base64.b64encode(text.encode("utf-8")).decode("ascii")}
                for path, text in changed
            ]},
        }},
    }
    commit = json.loads(gh("api", "graphql", "--input", "-", stdin=json.dumps(payload)).stdout)
    if commit.get("errors"):
        raise SystemExit(f"propose: the commit was refused: {commit['errors']}")
    print("propose: committed", commit["data"]["createCommitOnBranch"]["commit"]["url"])

    pull = gh("pr", "create", "-R", args.repo, "--base", default, "--head", args.branch,
              "--title", args.title, "--body-file", args.body_file, check=False)
    if pull.returncode == 0:
        print("propose: opened", pull.stdout.strip())
        return 0
    # The organization may not let a workflow open a pull request. The branch and its signed
    # commit exist, so hand an owner the link: a pull request a person opens also starts the
    # required checks, which one opened by the workflow's own token does not.
    print("propose: could not open the pull request:", pull.stderr.strip())
    compare = f"https://github.com/{args.repo}/compare/{default}...{args.branch}?expand=1"
    with open(args.body_file, encoding="utf-8") as handle:
        body = handle.read()
    body = (f"The branch `{args.branch}` holds this change, committed and signed through the GitHub API. "
            f"This workflow is not allowed to open the pull request, so an owner opens it:\n\n{compare}\n\n"
            "Close this issue when the pull request is open.\n\n---\n\n" + body)
    issue = gh("issue", "create", "-R", args.repo, "--title", args.title, "--body", body, check=False)
    if issue.returncode == 0:
        print("propose: opened an issue with the link:", issue.stdout.strip())
        return 0
    print("propose: could not open an issue either:", issue.stderr.strip())
    print("propose: open the pull request by hand:", compare)
    return 1


if __name__ == "__main__":
    sys.exit(main())
