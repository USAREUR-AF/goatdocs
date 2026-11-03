# Manifesto

Position papers. One thesis per essay; each links to the implementing code in this repo. Cross-posted publicly when ready, two weeks apart, per Block 29B in `../project/implementation-plan.md`.

These are deliberately *opinions*, not features. The goal is to surface debate and attract contributors who care about the same questions.

## Index

| Essay | Thesis (one line) | Status |
|---|---|---|
| `phoenix-native-peers.md` | Peers should rebuild themselves from declarative supply-chain artifacts; persistent identity belongs to the operator, not the peer. | draft pending |
| `queryable-by-default.md` | Every state-holder in a distributed system should expose a schema-described query surface as a precondition of joining. | draft pending |
| `license-tier-posture.md` | A re-usable license-tier convention (Tier 1-5) and an explicit disqualification list for licenses that block downstream service-and-support business models. | draft pending |
| `anti-platform.md` | Provide primitives, conventions, and contracts; refuse to provide platforms that own the semantics. | draft pending |

## Authoring discipline

Each essay:

- Leads with the position, not the context.
- Argues against at least one specific alternative the reader probably believes.
- Cites code or ADRs in this repo where the position is implemented.
- Is short enough to read in 10 minutes.
- Survives a hostile reading by someone who builds the alternative.

Essays go through the standard PR review cycle and land as the project's public surface, not as drafts.

## Why publish before earning the right

The phoenix-native essay was originally gated on six "we did it at scale" readiness criteria from [`../design/phoenix-architecture.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/phoenix-architecture.md) §9.1. The strategy (per `../project/oss-strategy.md`) is to gate *operational-scale claims* on those criteria, but to publish the *architectural opinions* now. Public debate is how the ideas get pressure-tested.
