# UI Kit — Brief

A slide-deck shell for **briefs and decks** authored in the GOAT-Net design
system. The source repo ships its own deck (`docs/briefs/zenoh-in-goat-net-brief.html`,
preserved at `raw/zenoh-brief.html`) in a paper-warm, serif aesthetic; this
kit is the **tactical-console restatement** of that surface, in line with the
rest of this system.

## What's in the kit

```
ui_kits/brief/
├── README.md
├── deck-stage.js    deck shell — 1280×720 scaling, keyboard nav, slide counter
├── brief.css        slide layouts: title, section, two-col, stat, quote, code
└── index.html       a 9-slide brief restating "How GOAT-Net uses Zenoh"
```

The deck shell auto-scales to any viewport, handles ←/→ navigation, supports
right-click → print-to-PDF, and posts slide-index changes to the parent
frame for speaker-notes sync.

## Slide-type patterns

Each slide is a `<section>` child of `<deck-stage>` with one of these classes:

| Class | Purpose |
|---|---|
| `slide slide--title` | Cover. Mark + headline + one-line subtitle. |
| `slide slide--section` | Section break. Eyebrow + statement. Green top strip. |
| `slide slide--two-col` | Diagram or panel on the left, bullets/copy on the right. |
| `slide slide--stat` | One big number, one short caption. For "10 systems → 45 conversations." |
| `slide slide--quote` | Pull quote + attribution. |
| `slide slide--code` | Code or shell specimen, full-width. |

Slides are written as plain HTML — no JSX. This is intentional: it keeps
slide content directly editable in-browser, which is how decks usually get
revised. The shared system tokens from `colors_and_type.css` carry the
brand; per-slide styles live in `brief.css`.
