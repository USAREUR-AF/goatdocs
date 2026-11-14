# How do two organizations share pub/sub data without sharing a certificate authority?

Each organization keeps its own certificate authority and its own network, and the two exchange only public trust material: root certificates or trust bundles. Private keys never cross. Accepting the other side's root means you can verify the identities it issues. It grants those identities nothing. What a verified partner identity may read or write is a separate decision, made in your own access rules. Keep the two steps apart: organizations that treat "we federated" as "they are trusted" give partners more access than they intended.

## The parts of the decision

1. **Authentication:** who or what is this? A certificate, a key or a token.
2. **Trust anchoring:** do I accept the authority that vouches for it? Federation is this step only.
3. **Authorization:** what may it do?
4. **Admission:** can it reach me at the network level?
5. **Assurance:** how strongly do I believe the identity is genuine?

Federation is pairwise and not transitive: if A federates with B and B with C, A does not trust C. It can also be one-directional.

With SPIFFE, the trust domain is part of every identity (`spiffe://<trust domain>/...`), so a verifier can apply policy per partner. With plain X.509 names in Zenoh, it cannot: Zenoh's access control matches the certificate common name and has no matcher for the issuer. A partner's root added to a router's trust set lets that partner issue any name the router's rules recognize, so the trust step also performs the authorization step.

## How goat handles it

- goat does not add a partner's certificate authority to a core router.
- The decision recorded in ADR 1157 (status: Proposed) is one additional Zenoh router at the edge for each partner. It trusts that partner's certificate authority and no other, it accepts connections and does not make them, and it passes messages inward without rewriting them. The two edge routers are joined by one encrypted tunnel that belongs to neither side's internal network. Either side ends the relationship on its own machine.
- A partner may write only under an ingress prefix that carries its own code (`from/<code>/`), and may read only the declared release prefixes.
- SPIRE federation of trust bundles is implemented in the `spire` role and is off by default.
- `goatbuilder federate` drives a peering in numbered phases. The federation design documents state, part by part, what is built and what is measured.

## Read more

- [Federated trust model](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/federated-trust-model.md)
- [ADR 1157: cross-sovereign federation, one edge router per partner](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1157-cross-sovereign-federation-edge-terminated.md)
- [ADR 1020: federated peering trust model](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1020-zenoh-federated-peering-trust-model.md)
- [Federation plan](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/federation-plan.md)
- [How do I use certificate identity to control who can publish in Zenoh?](how-do-i-use-certificate-identity-to-control-who-can-publish-in-zenoh.md)
