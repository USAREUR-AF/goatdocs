# SPDX-License-Identifier: Apache-2.0
"""Checks for the repository index: python3 -m unittest discover -s .github/repositories/tests"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import index  # noqa: E402


def repo(name, description="", archived=False):
    return {"name": name, "description": description, "isArchived": archived,
            "url": f"https://github.com/example/{name}"}


CONFIG = {
    "section": [
        {"title": "Core", "about": "The core.", "repositories": ["alpha", "soon"]},
        {"title": "Examples", "about": "Examples.", "repositories": ["hello-galaxy-beta"]},
    ],
    "planned": {"soon": "Coming."},
    "outside": {".github": "templates"},
}
REPOS = [repo("alpha", "The alpha."), repo("hello-galaxy-beta", "Hello Galaxy — beta steps."),
         repo(".github", "Templates")]


class Problems(unittest.TestCase):
    def test_clean(self):
        self.assertEqual(index.problems(CONFIG, REPOS), [])

    def test_new_public_repository_fails(self):
        found = index.problems(CONFIG, REPOS + [repo("gamma")])
        self.assertEqual(len(found), 1)
        self.assertIn("gamma is public and not in the index", found[0])

    def test_archived_repository_needs_no_section(self):
        self.assertEqual(index.problems(CONFIG, REPOS + [repo("old", archived=True)]), [])

    def test_named_repository_that_is_not_public_fails(self):
        found = index.problems(CONFIG, [r for r in REPOS if r["name"] != "alpha"])
        self.assertEqual(len(found), 1)
        self.assertIn("alpha (in 'Core') is not a public repository", found[0])

    def test_planned_repository_that_became_public_fails(self):
        found = index.problems(CONFIG, REPOS + [repo("soon", "Here now.")])
        self.assertEqual(found, ["soon is public now: remove its [planned] entry"])

    def test_repository_in_two_sections_fails(self):
        config = dict(CONFIG, section=CONFIG["section"] + [
            {"title": "Again", "about": "", "repositories": ["alpha"]}])
        self.assertIn("alpha is named in both 'Core' and 'Again'", index.problems(config, REPOS))


class Render(unittest.TestCase):
    def test_page(self):
        page = index.render(CONFIG, REPOS, "example")
        self.assertIn("- [alpha](https://github.com/example/alpha): The alpha.", page)
        self.assertIn("- **soon** (not public yet): Coming.", page)
        self.assertIn("- [hello-galaxy-beta](https://github.com/example/hello-galaxy-beta): beta steps.", page)
        self.assertIn("## Also in the organization", page)
        self.assertNotIn("## Archived", page)
        self.assertLess(page.index("## Core"), page.index("## Examples"))

    def test_archived_listed_apart(self):
        page = index.render(CONFIG, REPOS + [repo("old", "Old one.", archived=True)], "example")
        self.assertIn("## Archived", page)
        self.assertIn("- [old](https://github.com/example/old): Old one.", page)

    def test_same_input_same_page(self):
        self.assertEqual(index.render(CONFIG, REPOS, "example"), index.render(CONFIG, REPOS, "example"))

    def test_committed_sections_file_parses(self):
        config = index.load_sections()
        self.assertTrue(config["section"])
        for section in config["section"]:
            self.assertTrue(section["title"] and section["about"] and section["repositories"])


if __name__ == "__main__":
    unittest.main()
