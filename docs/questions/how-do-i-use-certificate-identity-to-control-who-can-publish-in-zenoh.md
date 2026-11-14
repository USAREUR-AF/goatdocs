# How do I use certificate identity to control who can publish in Zenoh?

Turn on mutual TLS on the router and write access rules whose subject is the certificate common name (CN). The router verifies each client's certificate against the certificate authorities it trusts, takes the CN from the certificate, and matches it against the subjects in its `access_control` rules. A rule then allows or denies that subject a `put`, a subscription or a query on a set of key expressions. With a default of deny, a client can publish only where a rule for its CN allows it.

## Two properties to design around

- **The CN is matched as a plain string.** Zenoh's access control has no matcher for the issuer of the certificate. If a router trusts two certificate authorities, either one can issue a certificate with any CN, and the router treats both the same. A name is an identity only while one authority can issue it, so give a router one issuing authority, or keep the names that different authorities may issue apart by other means.
- **The rules are read at start.** A new CN is admitted without a restart only if a rule that matches it is already loaded. See [How do I change Zenoh access rules without a restart?](how-do-i-change-zenoh-access-rules-without-a-restart.md)

A denied write is silent, so test rules by evaluating them. See [Why was my Zenoh publish silently dropped?](why-was-my-zenoh-publish-silently-dropped.md)

## How goat handles it

- Identity is issued by an offline certificate authority. Zenoh carries the identity; it does not issue it (built).
- The router's rules are default-deny per key expression and per subject, where the subject is the certificate CN. They are rendered from configuration by the `goat-zenoh` role (built).
- Workload certificates from SPIRE (X.509-SVIDs) are admitted the same way: the SVID's subject CN is matched by the same rules, and the router's trust roots include the SPIRE bundle (built).
- Content that must be limited to named readers is encrypted for them, so its protection does not depend on the path it takes or on a router rule (built; ADR 1094).
- Because the CN match ignores the issuer, goat does not add another organization's certificate authority to a core router. See [How do two organizations share pub/sub data without sharing a certificate authority?](how-do-two-organizations-share-pub-sub-data-without-sharing-a-certificate-authority.md)

## Read more

- [Zenoh data fabric, "Access control"](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/zenoh-data-fabric.md#access-control)
- [Identity, access and onboarding reference](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/identity-access-and-onboarding-reference.md)
- [Federated trust model](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/federated-trust-model.md)
- [ADR 1094: grant-keyed payload encryption](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1094-grant-keyed-payload-encryption.md)
