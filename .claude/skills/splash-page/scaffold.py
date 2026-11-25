#!/usr/bin/env python3
"""Lay down the house landing-page skeleton. Standard library only. Never overwrites.

  scaffold.py site    <repo-root> --name N --repo OWNER/REPO [--tagline T] [--start CMD] [--prompt P]
  scaffold.py subpage <goatdocs-root> --slug S --name N --repo OWNER/REPO [--tagline T] [--start CMD] [--prompt P]

site     writes <repo-root>/site/ (index.html, assets/, build.py, fitcheck.py, README.md,
         .gitignore) and <repo-root>/.github/workflows/pages.yml.
subpage  writes <goatdocs-root>/docs/goat/<slug>/index.html as ONE self-contained file
         (styles and script inline, icon as a data URL) and a README.md beside it, then
         prints the three wiring edits goatdocs needs.

Any value not given stays a placeholder; site/build.py refuses to pass until every
placeholder is replaced.
"""
import argparse
import os
import shutil
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(HERE, "templates")


def fill(text, a):
    url = f"https://github.com/{a.repo}"
    for k, v in {
        "NAME": a.name, "TAGLINE": a.tagline or "REPLACE: one line, what it does, with what",
        "REPO_URL": url, "START_COMMAND": a.start or "REPLACE: the one command that shows it working",
        "PROMPT": a.prompt or "REPLACE: a short command line that names what the first screen shows",
        "BGCODE": "REPLACE: a real file from the tree",
    }.items():
        text = text.replace("{{" + k + "}}", v)
    return text


def show(path):
    return os.path.relpath(path)


def write(path, text):
    if os.path.exists(path):
        sys.exit(f"scaffold: {show(path)} exists; not overwriting")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)
    print("wrote", show(path))


def read(*p):
    with open(os.path.join(T, *p)) as f:
        return f.read()


def site(a):
    root = os.path.abspath(a.root)
    for d, _, files in os.walk(os.path.join(T, "site")):
        for name in files:
            src = os.path.join(d, name)
            rel = os.path.relpath(src, os.path.join(T, "site"))
            dst = os.path.join(root, "site", rel)
            if name.endswith((".html", ".md")):
                write(dst, fill(read("site", rel), a))
            else:
                if os.path.exists(dst):
                    sys.exit(f"scaffold: {show(dst)} exists; not overwriting")
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copyfile(src, dst)
                print("wrote", show(dst))
    write(os.path.join(root, ".github", "workflows", "pages.yml"), read("pages.yml"))
    print("\nnext: replace every placeholder, then  python3 -I site/build.py")


def subpage(a):
    root = os.path.abspath(a.root)
    page = fill(read("site", "index.html"), a)
    css, js = read("site", "assets", "site.css"), read("site", "assets", "site.js")
    icon = "data:image/svg+xml," + urllib.parse.quote(read("site", "assets", "icon.svg").strip(), safe="=:/ '")
    page = page.replace('<link rel="stylesheet" href="assets/site.css">', "<style>\n" + css + "</style>")
    page = page.replace('<script src="assets/site.js" defer></script>', "<script>\n" + js + "</script>")
    page = page.replace('href="assets/icon.svg"', f'href="{icon}"').replace('src="assets/icon.svg"', f'src="{icon}"')
    page = page.replace('<a class="gh" href=', '<a href="../">goat</a>\n      <a class="gh" href=', 1)
    d = os.path.join(root, "docs", "goat", a.slug)
    write(os.path.join(d, "index.html"), page)
    write(os.path.join(d, "README.md"),
          f"# {a.name} landing page\n\n`index.html` is one self-contained file, served at "
          f"`goat/{a.slug}/` by goatdocs Pages. Images beside it are its captures, light and dark.\n"
          "Every number on it names the command that measures it.\n")
    print(f"""
next, in goatdocs:
  1. docs/goat/index.html: link goat/{a.slug}/ from the card that names its repository, and from the footer.
  2. mkdocs.yml exclude_docs: add  goat/{a.slug}/README.md
  3. .github/workflows/pages.yml: append  goat/{a.slug}/index.html  to the fitcheck.py line.
then replace every placeholder (grep -n 'REPLACE\\|{{{{' docs/goat/{a.slug}/index.html prints none) and run
  python .github/pages/fitcheck.py site goat/{a.slug}/index.html   after  mkdocs build""")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("mode", choices=["site", "subpage"])
    p.add_argument("root")
    p.add_argument("--name", required=True)
    p.add_argument("--repo", required=True, help="OWNER/REPO the Star button points at")
    p.add_argument("--slug")
    p.add_argument("--tagline")
    p.add_argument("--start")
    p.add_argument("--prompt")
    a = p.parse_args()
    if a.mode == "subpage" and not a.slug:
        p.error("subpage needs --slug")
    (site if a.mode == "site" else subpage)(a)


if __name__ == "__main__":
    main()
