# UI Kit — Console

An opinionated reconstruction of the **operator console** described in the project's README:

> "A **catalog** lists every system on the bus, everything it publishes, and
> what shape the data is in — a phone book for the whole network, keyed by
> what each system does rather than by who built it. A **data common
> operating picture** is a live, system-by-system view of who is talking to
> whom right now."

**This UI does not exist in the source repo.** The codebase is Rust + Go +
Ansible; there is no frontend checked in anywhere. Treat this kit as a
*proposal in the project's design language* — useful for mocking the
catalog and the operator's status surface, not as a recovery of an existing
product.

## What's in the kit

```
ui_kits/console/
├── README.md         this file
├── index.html        full clickable surface
├── TopBar.jsx        56px top bar — logo, sector, search, command-K, status
├── SideNav.jsx       left rail — catalog / topology / enrollment / audit
├── CatalogTable.jsx  the peer-and-publication table (main view)
├── PeerDetail.jsx    right-side drawer with peer KV + identity + traffic
├── ChipDot.jsx       status chip (online/degraded/offline/enrolling/exp)
├── Icon.jsx          inline Lucide-style SVG icons
└── data.js           fake mesh data — peers + publications
```

## Interactions covered

- **Tab nav** between Catalog / Topology / Enrollment / Audit
- **Row select** on the peer table opens the right-hand peer drawer
- **Filter pill** narrows the table by status
- **⌘K command palette** opens a recall surface (mocked)
- **Sector switcher** in the top bar (mocked)

Everything else is static cosmetic.
