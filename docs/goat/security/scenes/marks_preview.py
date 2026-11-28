"""Render the scene marks side by side, light and dark, at the size the icon grid shows them."""
import importlib, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import preview
names = ["timing", "layers", "path", "air_gap", "custody", "boundary", "self_documenting", "grade"]
cells = "".join(f'<div style="display:inline-block;margin:18px;text-align:center;font:13px var(--sans);color:var(--quiet)">{importlib.import_module(n).mark()}<br>{n}</div>' for n in names)
for theme in ("light", "dark"):
    p = os.path.join(preview.OUT, f"marks-{theme}.html")
    open(p, "w").write(f"<meta charset=utf-8><style>{preview.css(theme)}</style><body style='margin:0;background:var(--paper)'>{cells}</body>")
    preview.shot(p, p[:-5] + ".png", 1000, 150, False)
