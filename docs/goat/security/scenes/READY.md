# Scenes ready to wire in

Each module exposes `html()`, `figure_wide()`, `figure_narrow()`, `mark()` and `ALT`. `html()` returns the whole
section in the page's own classes, with both figure variants already inside it. Add the rules in `scenes.css`
to the page's css. Render any scene alone with `python3 scenes/preview.py <name>` (PNGs in `scenes/preview/`).

| Scene | File | Section id | Status words used | Notes |
|---|---|---|---|---|
| Three layers around every message (the onion) | `layers.py` | `layers` | in use (mesh tunnel; data fabric link; grant encryption where an owner turns it on); designed (a standardized post-quantum key exchange for the mesh tunnel) | Grant encryption graded "in use" on the operator's correction of 28 Nov: decision record 1208 (Accepted) and the pinned key service; records 1094 and 1106 still read Proposed in the tree |
| Sealed once, and closed for the whole path | `path.py` | `path` | in use (direct connections; relay as fallback) | Second part of the layers idea. Holds the path figure, the worked estimate (four rows) and the "With real links" block. Every number is labelled an estimate; the assumptions and sources are printed. No measured direct-against-relayed figure exists in the public tree, so none is printed. The clause that satellite links commonly give no public address and accept no inbound connection is a general fact, not taken from the tree |
| Your hardware, in your custody | `custody.py` | `custody` | in use | Decision record 1192 for "no host site has a public address" |
| Two ways data crosses the edge | `boundary.py` | `boundary` | built (federation); designed (sealing for named readers across a boundary); built (simple boundary node) | Two figures in one section. The public tree does describe the simple boundary node: decision records 1253 and 1263, and `docs/design/simple-boundary-node.md` (marked WIP there). It says the node sends released data as plain messages one way, meets the other side's IPsec gateway on the boundary host, and fails closed. The page text says "an encrypted tunnel" and does not name IPsec in the figure |
| The system documents itself | `self_documenting.py` | `self-documenting` | built | The only scene that names RMF, ACAS, STIG and Burp. Names OCSF and OpenTelemetry; no product |
| Grade our work | `grade.py` | `grade` | none | A band, not a scene; no figure. Links the private report form and the security policy of goatcore; promises only what that policy states (acknowledgement in 3 working days, triage in 7) |
| An air gap is one more boundary | `air_gap.py` | `air-gap` | in use (nothing reachable from the public internet; signed, verified releases); designed (a site with no link; one signed bundle for a cut-off site) | Goes right after "No inside, no outside" and the five habits. No public case is cited. The site bundle is decision record 1277, accepted and not built |
| Joining happens once | not built here | `join` | | Already on the page (the first lane's `join_svg`); no module written |
| After joining | not built here | `after` | | Already on the page (the first lane's `after_svg`); no module written |
| Five habits | not built here | `habits` | | Already on the page as five panels; no module written |
