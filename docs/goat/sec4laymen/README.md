# sec4laymen

The security page for readers with no technical background: what the team builds and why it
matters, with every special word explained at its first use.

- `build.py` writes `index.html` from its own text, the drawings in `figures.py`, and the two
  measured times in `../security/run.json`. Run `python3 -I docs/goat/sec4laymen/build.py`
  after any change; the workflow runs it with `--check`.
- The page states nothing that the security page (`../security/`) does not state. When that page
  changes a claim or a status, change this one to match.
- Rule for the text: no term is used before it is explained, and each is explained once, at first
  use, then listed again under "Words used here".
