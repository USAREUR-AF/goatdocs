# How do I change Zenoh access rules without a restart?

You cannot. A Zenoh router reads its `access_control` configuration when it starts, and the [Zenoh access-control manual](https://zenoh.io/docs/manual/access-control/) states that the configuration cannot be updated at runtime and requires a restart. The practical answer is to write the rules so that the events that happen often do not change them: declare rules in advance for subjects that do not exist yet, and make a new publisher valid by issuing it a certificate whose common name (CN) matches a rule that is already loaded.

## Why this works

A Zenoh access rule names a subject and a set of key expressions. A subject is a network interface, a TLS certificate CN or a username. The router does not need to know a publisher in advance. It needs a rule whose subject matches the CN the publisher presents. If the rule exists before the publisher does, adding the publisher is a certificate issuance, and the router keeps running.

What still needs a restart is any change to the rules themselves: a new kind of grant, a new restricted read tier, or a larger set of pre-declared subjects.

## How goat handles it

goat renders the router's rules from a pool of numbered slots (built; the write model in use).

- The pool is written into the access-control file once. Each slot is a subject and the key prefix that subject may write under.
- Onboarding a system gives it a certificate stamped with a free slot. The rule for that slot is already loaded, so the system can write immediately.
- Each system writes only under its own prefix. The rule enforces this, so one system cannot write or delete under another system's prefix.
- The change that happens often is a new writer. Read grants are declared in configuration and change less often. Content that must stay secret is encrypted for named readers, so it does not depend on a read rule.
- Cutting a system off is done at the mesh layer, where a change takes effect at once.
- The pool is refilled by a planned router restart. A change to a declared grant is also a re-render and a router restart.

Because a denied write is silent in Zenoh, goat tests a rule change by evaluating the rules (`goat acl test`), not by watching for errors.

## Read more

- [Zenoh data fabric, "Authorization — Zenoh is the static outlier"](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/zenoh-data-fabric.md): the comparison with NATS, DDS Security and MQTT brokers, which change authorization at runtime
- [ADR 1025: pre-cut identity-bound slot pool](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1025-zenoh-dynamic-tenant-authz-slot-pool.md)
- [Brokerless pub/sub: the consequences](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/zenoh-brokerless-consequences.md)
