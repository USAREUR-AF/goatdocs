"""Render each scene alone: one HTML per scene with the page's css, then PNGs at 1120 and 464 wide,
light and dark, with headless Chrome.   python3 scenes/preview.py [scene ...]"""
import importlib, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); PAGE = os.path.dirname(HERE)
sys.path.insert(0, HERE)
CHROME = os.environ.get("CHROME", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
OUT = os.path.join(HERE, "preview"); os.makedirs(OUT, exist_ok=True)
ALL = ["layers", "path", "air_gap", "custody", "boundary", "self_documenting"]


def css(theme="light"):
    # the page follows the reader's system theme; a preview must show each theme whatever this machine is set to
    sub = "all" if theme == "dark" else "not all"
    return _css().replace("(prefers-color-scheme: dark)", sub)


def _css():
    return "".join(open(os.path.join(d, n)).read() for d, n in
                   ((PAGE, "extra.css"), (PAGE, "figs.css"), (PAGE, "extra-tail.css"), (HERE, "scenes.css")))


def shot(html_path, png, w, h, dark):
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={w},{h}", f"--screenshot={png}"]
    if dark: cmd.append("--force-dark-mode")
    subprocess.run(cmd + ["file://" + html_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)


def main(names):
    for n in names:
        m = importlib.import_module(n)
        figs = []
        for kind, w in (("wide", 1120), ("narrow", 464)):
            fn = getattr(m, "figure_" + kind, None)
            if not fn: continue
            parts = fn() if isinstance(fn(), list) else [fn()]
            for k, svg in enumerate(parts):
                svg = svg.replace('class="viz narrow"', 'class="viz"').replace('class="viz wide"', 'class="viz"')
                hgt = int(float(svg.split('viewBox="0 0 ')[1].split('"')[0].split()[1])) + 2
                for theme in ("light", "dark"):
                    p = os.path.join(OUT, f"{n}-{kind}{k if len(parts) > 1 else ''}-{theme}.html")
                    open(p, "w").write(f"<meta charset=utf-8><style>{css(theme)}</style><body style='margin:0;background:var(--paper)'><div style='width:{w}px'>{svg}</div></body>")
                    png = p[:-5] + ".png"; shot(p, png, w, hgt, False); figs.append(png)
        p = os.path.join(OUT, f"{n}-scene.html")
        open(p, "w").write(f"<meta charset=utf-8><meta name=viewport content='width=device-width'><style>{css('dark')}</style><body>{m.html()}</body>")
        if os.environ.get("SCENE_SHOTS"):
            for w, h in ((1440, 1700), (390, 3000)):
                png = p[:-5] + f"-{w}.png"; shot(p, png, w, h, False); figs.append(png)
        print(n, len(figs), "images")


if __name__ == "__main__":
    main(sys.argv[1:] or ALL)
