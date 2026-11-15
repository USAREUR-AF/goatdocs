# SPDX-License-Identifier: Apache-2.0
"""Checks for the weekly changelog: python3 -m unittest discover -s .github/changelog/tests"""
import datetime as dt
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import collect  # noqa: E402
import propose  # noqa: E402
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


OWN = {**DATA, "repositories": ["alpha", "beta", "gamma", "quiet"],
       "merged": DATA["merged"] + [
           pull("gamma", 1, "feat(capture): read a second sensor"),
           pull("gamma", 2, "fix(audit): keep the last line"),
           pull("gamma", 3, "feat(release): gate by label"),
           pull("gamma", 4, "feat(ui): a status page"),
           pull("gamma", 5, "fix(deps): bump a crate (RUSTSEC-2026-0382)"),
       ],
       "releases": DATA["releases"] + [
           {"repo": "gamma", "tag": "v0.3.0", "name": "v0.3.0", "publishedAt": "2026-11-06T09:00:00Z",
            "prerelease": False, "url": "https://github.com/example/gamma/releases/tag/v0.3.0"}]}


class OwnChangelog(unittest.TestCase):
    def setUp(self):
        self.main = weekly.render(OWN, ["gamma", "quiet", "not-a-repository"])
        self.gamma = weekly.render(OWN, ["gamma", "quiet"], repo="gamma")

    def test_the_main_page_gives_highlights_and_a_link_not_the_list(self):
        self.assertIn("## Repositories with their own changelog", self.main)
        self.assertIn("**[gamma](gamma/2026-W45.md)**", self.main)
        self.assertIn("released [v0.3.0]", self.main)
        self.assertNotIn("keep the last line", self.main)
        self.assertNotIn("example/gamma/pull/2", self.main)

    def test_highlights_are_few_and_say_when_there_are_more(self):
        line = next(text for text in self.main.splitlines() if text.startswith("- **[gamma]"))
        self.assertIn("more on its page", line)
        self.assertNotIn("a status page", line)

    def test_its_own_page_lists_only_its_pull_requests(self):
        self.assertTrue(self.gamma.startswith("# gamma: weekly changelog, 2 to 8 November 2026 (2026-W45)"))
        self.assertIn("keep the last line", self.gamma)
        self.assertIn("(../2026-W45.md)", self.gamma)
        self.assertNotIn("example/alpha/", self.gamma)

    def test_every_repository_read_is_named_with_where_it_is_listed(self):
        table = self.main.split("## Repositories read")[1]
        for name in OWN["repositories"]:
            self.assertIn(f"| {name} |", table)
        self.assertIn("| alpha | listed on this page |", table)
        self.assertIn("| gamma | [its own page](gamma/2026-W45.md) |", table)
        self.assertIn("| quiet | nothing merged or opened |", table)

    def test_with_no_list_every_repository_stays_on_the_main_page(self):
        page = weekly.render(OWN)
        self.assertIn("keep the last line", page)
        self.assertNotIn("Repositories with their own changelog", page)

    def test_the_listed_repositories_are_read_from_the_file(self):
        self.assertEqual(weekly.own_changelog(), sorted(weekly.own_changelog(), key=str.lower))
        self.assertTrue(all(re.fullmatch(r"[A-Za-z0-9._-]+", name) for name in weekly.own_changelog()))


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


class MergeOnGreen(unittest.TestCase):
    def checks(self, *buckets):
        return [{"name": f"check-{i}", "bucket": bucket} for i, bucket in enumerate(buckets)]

    def test_green_needs_every_check_passed_or_skipped(self):
        self.assertEqual(propose.verdict(self.checks("pass", "pass", "skipping", "pass"), 4), "green")

    def test_a_pending_check_waits(self):
        self.assertEqual(propose.verdict(self.checks("pass", "pass", "pass", "pending"), 4), "waiting")

    def test_too_few_checks_wait_even_when_all_passed(self):
        self.assertEqual(propose.verdict(self.checks("pass", "pass"), 4), "waiting")
        self.assertEqual(propose.verdict([], 4), "waiting")

    def test_a_failed_or_cancelled_check_never_merges(self):
        self.assertEqual(propose.verdict(self.checks("pass", "fail", "pass", "pending"), 4), "failed")
        self.assertEqual(propose.verdict(self.checks("pass", "cancel", "pass", "pass"), 4), "failed")


if __name__ == "__main__":
    unittest.main()
