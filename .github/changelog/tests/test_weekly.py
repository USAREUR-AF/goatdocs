# SPDX-License-Identifier: Apache-2.0
"""Checks for the weekly changelog: python3 -m unittest discover -s .github/changelog/tests"""
import datetime as dt
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import collect  # noqa: E402
import weekly  # noqa: E402


def pull(repo, number, title, base="main", default=True):
    return {"repo": repo, "number": number, "title": title, "author": "someone",
            "mergedAt": "2026-11-03T10:00:00Z", "base": base, "onDefaultBranch": default,
            "url": f"https://github.com/example/{repo}/pull/{number}", "cited": False,
            **collect.parse_title(title)}


DATA = {
    "org": "example", "since": "2026-11-02T00:00:00Z", "until": "2026-11-09T00:00:00Z",
    "repositories": ["alpha", "beta"],
    "merged": [
        pull("alpha", 1, "feat(relay): cap subscriptions per peer"),
        pull("alpha", 2, "docs(adr): 1300 every site runs every surface"),
        pull("alpha", 3, "fix(deps): rustls-webpki 0.103.16 (RUSTSEC-2026-0382)"),
        pull("alpha", 4, "docs(licensing): state the licence"),
        pull("beta", 9, "docs(licensing): state the licence"),
        pull("alpha", 5, "feat(federation)!: one command", base="integration/x", default=False),
        pull("beta", 7, "Tidy the README | and <tables>"),
    ],
    "open": [{"repo": "beta", "number": 8, "title": "ci: pin actions", "author": "someone",
              "createdAt": "2026-11-04T00:00:00Z", "draft": True, "base": "main", "onDefaultBranch": True,
              "url": "https://github.com/example/beta/pull/8", **collect.parse_title("ci: pin actions")}],
    "releases": [{"repo": "alpha", "tag": "v1.2.0", "name": "v1.2.0", "publishedAt": "2026-11-05T09:00:00Z",
                  "prerelease": False, "url": "https://github.com/example/alpha/releases/tag/v1.2.0"}],
}


class Weekly(unittest.TestCase):
    def setUp(self):
        self.page = weekly.render(DATA)

    def test_title_names_the_inclusive_days_and_the_week(self):
        self.assertIn("# Weekly changelog, 2 to 8 November 2026 (2026-W45)", self.page)

    def test_each_kind_of_change_has_its_section(self):
        for heading in ("## Releases", "## Decisions", "## New capabilities", "## Security",
                        "## Documentation", "## Other", "## Opened this week and still open"):
            self.assertIn(heading, self.page)

    def test_an_advisory_fix_is_security_and_an_adr_is_a_decision(self):
        security = self.page.split("## Security")[1].split("\n## ")[0]
        self.assertIn("RUSTSEC-2026-0382", security)
        decisions = self.page.split("## Decisions")[1].split("\n## ")[0]
        self.assertIn("1300 every site runs every surface", decisions)

    def test_one_title_in_two_repositories_is_one_line(self):
        self.assertEqual(self.page.count("state the licence"), 1)
        self.assertIn("alpha [#4]", self.page)
        self.assertIn("beta [#9]", self.page)

    def test_a_merge_into_another_branch_is_listed_apart(self):
        features = self.page.split("## New capabilities")[1].split("\n## ")[0]
        self.assertNotIn("one command", features)
        apart = self.page.split("## Merged into a branch that is not the default branch")[1]
        self.assertIn("`integration/x`", apart)

    def test_the_page_states_no_counts(self):
        prose = [text for text in self.page.splitlines() if not text.startswith(("- ", "| ", "#", "Window:"))]
        self.assertFalse([text for text in prose if re.search(r"\b\d+ (pull requests|commits|changes|repositories)\b", text)])

    def test_table_and_markup_characters_are_escaped(self):
        self.assertIn("Tidy the README \\| and &lt;tables&gt;", self.page)

    def test_the_same_input_renders_the_same_page(self):
        self.assertEqual(self.page, weekly.render(DATA))


class Windows(unittest.TestCase):
    def test_last_is_the_last_full_iso_week(self):
        now = dt.datetime(2026, 11, 10, 5, 0, tzinfo=dt.timezone.utc)  # a Tuesday
        since, until = collect.week_window("last", now)
        self.assertEqual((collect.stamp(since), collect.stamp(until)), ("2026-11-02T00:00:00Z", "2026-11-09T00:00:00Z"))

    def test_a_named_week(self):
        since, _ = collect.week_window("2026-W45")
        self.assertEqual(collect.stamp(since), "2026-11-02T00:00:00Z")

    def test_titles_parse(self):
        self.assertEqual(collect.parse_title("feat(x)!: do it")["breaking"], True)
        self.assertEqual(collect.parse_title("No type here")["type"], "")


if __name__ == "__main__":
    unittest.main()
