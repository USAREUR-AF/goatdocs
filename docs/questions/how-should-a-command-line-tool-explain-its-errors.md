# How should a command-line tool explain its errors?

Give every error a stable code and four things: what happened, the likely causes, what to do (as a command where one exists), and where to read more. Keep all of them in one catalog that the program carries with it, so the explanation is available offline and the documentation is generated from the same source the program prints. Treat errors from the tools your program calls (ssh, git, a deployment tool) the same way, because the last words a person sees are often that tool's and not yours.

## What makes this work

- **One catalog.** One file holds every error. The program embeds it at build time, and the reference pages are generated from it. A check in continuous integration fails when the generated pages differ from the catalog.
- **Stable codes.** A code that a release has printed is never deleted or given another meaning, because logs keep it. A code that is no longer raised is marked retired and stays.
- **Text matching for other tools' errors.** A catalog entry can carry patterns that match the text another tool prints. The program can then interpret an error it did not produce.
- **An `explain` command.** It takes a code or any pasted error text and prints the entry.
- **Innermost error first.** When an error wraps another, print the interpretation of the inner one first. Its fix is the one closest to the cause.
- **Do not change captured output.** Print the interpretation at a terminal. A log file or a test gets the one-line error and the code.

## How goat handles it

This is built in goat's two command-line tools, `goat` and `goatbuilder`.

- The catalog is `ops/errors/catalog.yaml` in goatcore. A crate shared by both tools embeds it.
- Codes have three shapes: `E_*` for `goat`, `GB-NNN` for `goatbuilder`, and `X-<TOOL>-NNN` for a tool either one calls.
- `goat explain <code>` and `goatbuilder explain <code>` print an entry. Both accept pasted text, and `-` reads it from standard input.
- A text that matches no pattern is matched by its words against the catalog. Matching by meaning, with an embedding model, is designed, not built.
- The reference table and one page per code are generated from the catalog, and the catalog check fails a pull request that leaves them out of date.

## Read more

- [Error interpretation](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/error-interpretation.md)
- [ADR 1199: one error catalog, interpreted by both tools](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1199-one-error-catalog-interpreted-by-both-clis.md)
- [Error reference: every code](https://github.com/USAREUR-AF/goatcore/blob/main/docs/reference/errors.md)
