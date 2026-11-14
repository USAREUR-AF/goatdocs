# What do you give up with brokerless pub/sub?

You give up the four things a broker provides because every message passes through it: one place to enforce priority and rate limits, a delivery lifecycle (acknowledgements, retries, a dead-letter queue), a place to change authorization while the system runs, and feedback to a publisher whose write was refused or dropped. You gain the removal of the broker itself, which is a single point of failure and a limit on message rate. Each of the four functions still has to exist somewhere, so a brokerless design moves each one to a place where it can be enforced or observed.

## Where each function goes

| A broker gives | Without a broker | Where the function moves |
|---|---|---|
| Central priority and rate enforcement | No single place protects important traffic | The producers, the relays and the network layer |
| Acknowledgements, retries, dead-letter queue | A publish is sent once and not confirmed | The producer, which asks for confirmation when a write must arrive |
| Authorization changes at runtime | Rules are static | The identity layer: issue or revoke a credential; do not edit a rule |
| A refusal reported to the publisher | A denied or dropped write is silent at both ends | Monitoring that compares who should be publishing with who is |
| (the broker is the bottleneck) | Nothing is lost | Message rate grows with the number of nodes and independent flows |

## How goat handles it

goat's data fabric is Zenoh over a WireGuard mesh, with no component that every message passes through. The design documents treat the consequences as one subject:

- **Authorization:** a pool of pre-declared slots in the router's static rules, with onboarding and cut-off done by certificate and mesh membership (built). See [How do I change Zenoh access rules without a restart?](how-do-i-change-zenoh-access-rules-without-a-restart.md)
- **Delivery:** a producer that needs proof of arrival uses Zenoh query/reply or `goat pub --confirm`, which reads the value back from storage (built). goat does not build a dead-letter queue.
- **Silent denial:** see [Why was my Zenoh publish silently dropped?](why-was-my-zenoh-publish-silently-dropped.md)
- **Priority:** quality-of-service class bound to the authenticated key prefix, so a producer cannot raise its own priority (designed, not built; ADR 1033).

## Read more

- [Brokerless pub/sub: one root, and the consequences](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/zenoh-brokerless-consequences.md)
- [Zenoh data fabric](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/zenoh-data-fabric.md)
- [Zenoh QoS and prioritization](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/zenoh-qos-and-prioritization.md)
