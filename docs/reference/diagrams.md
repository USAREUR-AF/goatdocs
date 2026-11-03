# Diagrams

ASCII diagrams maintained in three formats:
- **Markdown** — for rendering in GitHub/VS Code markdown preview
- **Google Docs** — for pasting into Google Docs after "clear formatting"
- **Code block** — for rendering as monospace in any context

---

## Double-Encryption Inspection Problem

### Markdown version

```
┌─────────────────────────────────────┐
│  Satellite link encryption          │  ← The satellite operator can decrypt this layer
│  ┌───────────────────────────────┐  │
│  │  WireGuard tunnel encryption  │←---- Only the peers can decrypt this
│  │  ┌─────────────────────────┐  │  │
│  │  │  Actual mission traffic │←------- Invisible to everyone else
│  │  └─────────────────────────┘  │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Google Docs version (paste, then clear formatting)

┌──────────────────────────────-─┐
│  Satellite link encryption                                      │  ← The satellite operator can decrypt this layer
│  ┌────────────────────────┐             │
│  │  WireGuard tunnel encryption              │←------------- Only the peers can decrypt this
│  │  ┌──────────────────┐         │             │
│  │  │  Actual mission traffic            │←---------------------- Invisible to everyone else
│  │  └──────────────────┘         │             │
│  └────────────────────────┘             │
└────────────────────────────────┘

### Code block version

    ┌─────────────────────────────────────┐
    │  Satellite link encryption          │  ← The satellite operator can decrypt this layer
    │  ┌───────────────────────────────┐  │
    │  │  WireGuard tunnel encryption  │←---- Only the peers can decrypt this
    │  │  ┌─────────────────────────┐  │  │
    │  │  │  Actual mission traffic │←------- Invisible to everyone else
    │  │  └─────────────────────────┘  │  │
    │  └───────────────────────────────┘  │
    └─────────────────────────────────────┘

---

## WireGuard Mesh Overlay Architecture

### Markdown version

```
┌─────────────────────────────────────────────────┐
│              WireGuard Mesh Overlay              │
│         (identity-based, encrypted, P2P)         │
└──────────┬──────────┬──────────┬────────────────┘
           │          │          │
    ┌──────▼───┐ ┌────▼────┐ ┌──▼──────────────┐
    │ Satcom   │ │ 5G/LTE  │ │ HaLow / LoRa    │
    │ (WAN     │ │ (WAN or │ │ (local tactical  │
    │ backhaul)│ │  local) │ │  mesh, 1-10km)   │
    └──────────┘ └─────────┘ └─────────────────┘
    Connects sites   Either     Connects nodes
    to each other              within a site
```

### Google Docs version (paste, then clear formatting)

┌─────────────────────────────────┐
│              WireGuard Mesh Overlay                              │
│         (identity-based, encrypted, P2P)                        │
└──────┬────────--┬───────-─┬────-----┘
                  │                       │                      │
   ┌──-──▼───┐ ┌───▼────┐ ┌──▼───────┐
   │ Satcom            │ │ 5G/LTE         │ │ HaLow / LoRa    │
   │ (WAN            │ │ (WAN or        │ │ (local tactical      │
   │ backhaul)      │ │  local)            │ │  mesh, 1-10km)  │
   └──────-──┘ └─────────┘ └───---──────┘
     Connects sites         Either               Connects nodes
      to each other                                    within a site

### Code block version

    ┌─────────────────────────────────────────────────┐
    │              WireGuard Mesh Overlay              │
    │         (identity-based, encrypted, P2P)         │
    └──────────┬──────────┬──────────┬────────────────┘
               │          │          │
        ┌──────▼───┐ ┌────▼────┐ ┌──▼──────────────┐
        │ Satcom   │ │ 5G/LTE  │ │ HaLow / LoRa    │
        │ (WAN     │ │ (WAN or │ │ (local tactical  │
        │ backhaul)│ │  local) │ │  mesh, 1-10km)   │
        └──────────┘ └─────────┘ └─────────────────┘
        Connects sites   Either     Connects nodes
        to each other              within a site
