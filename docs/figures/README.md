# Figures

`make-figures.py` redraws diagrams from the design system's library (`docs/design-system/assets/diagrams/`) as self-contained SVG files, in a light and a dark variant for a `<picture>` element. The library's diagrams take their stroke and fill from the page's stylesheet, so they cannot be shown through an `<img>` on their own. The redraw reads the source diagram's title, labels and systems, and uses the colors in `docs/design-system/colors_and_type.css`.

```sh
python3 -I docs/figures/make-figures.py           # write the SVG files
python3 -I docs/figures/make-figures.py --check   # exit 1 if a committed file is out of date
```

| Figure | Shows | Source |
|---|---|---|
| `identity-at-the-boundary` | systems on one shared bus inside the private, encrypted network, each attached through an identity check; a system with no identity is refused | `docs/design-system/assets/diagrams/06-fits-into-goat-net.svg` |

## Checks

Each figure was rendered in headless Chromium as an `<img>` at 830 px and 400 px wide in both themes and inspected. Text is at least 13 units on an 880-unit canvas.
