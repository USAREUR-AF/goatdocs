#!/usr/bin/env python3
# Build a custom pandoc reference.docx that doesn't read as a pandoc auto-doc.
# Serif body (Georgia), dark headings, left-aligned title.
#
# Usage: make-reference-docx.py <output-path>

import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

HEADING_BLUE = "0F4761"  # Office default accent1 color pandoc emits on headings


def rewrite_theme(path: Path) -> None:
    text = path.read_text()
    text = re.sub(
        r'(<a:majorFont>\s*<a:latin[^/]*?)typeface="[^"]*"',
        r'\1typeface="Georgia"',
        text,
    )
    text = re.sub(
        r'(<a:minorFont>\s*<a:latin[^/]*?)typeface="[^"]*"',
        r'\1typeface="Georgia"',
        text,
    )
    path.write_text(text)


def rewrite_styles(path: Path) -> None:
    text = path.read_text()
    # Drop the blue accent color from every heading that inherits it.
    text = re.sub(
        r'<w:color w:val="' + HEADING_BLUE + r'"[^/]*/>',
        '<w:color w:val="1A1A1A"/>',
        text,
    )
    # Title style: left-align instead of centered.
    text = re.sub(
        r'(<w:style w:type="paragraph" w:styleId="Title">.*?)<w:jc w:val="center" />',
        r'\1<w:jc w:val="left" />',
        text,
        count=1,
        flags=re.DOTALL,
    )
    path.write_text(text)


def build(output: Path) -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        default_ref = tmp / "default.docx"
        subprocess.run(
            ["pandoc", "--print-default-data-file", "reference.docx"],
            stdout=default_ref.open("wb"),
            check=True,
        )

        extracted = tmp / "extracted"
        extracted.mkdir()
        with zipfile.ZipFile(default_ref) as zf:
            zf.extractall(extracted)

        rewrite_theme(extracted / "word" / "theme" / "theme1.xml")
        rewrite_styles(extracted / "word" / "styles.xml")

        output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zf:
            for p in sorted(extracted.rglob("*")):
                if p.is_file():
                    zf.write(p, p.relative_to(extracted))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: make-reference-docx.py <output-path>")
    build(Path(sys.argv[1]))
    print(f"wrote {sys.argv[1]}")
