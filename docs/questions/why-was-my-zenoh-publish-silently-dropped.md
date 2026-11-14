# Why was my Zenoh publish silently dropped?

A Zenoh `put` is sent without confirmation, and a router that denies it by an access rule reports nothing to the publisher or to the subscriber. The publisher's call succeeds either way. The usual causes are an access rule that does not cover the key for the identity the publisher presented, a certificate the router does not accept, or no subscriber and no storage matching the key. To find out which, do not wait for an error. Read the value back from a storage, use query/reply for a write that must arrive, or evaluate the router's rules for your identity and key.

## Ways to get an answer

- **Read back.** Publish a unique value and query a storage for it. If the value is there, the write was admitted.
- **Query/reply.** For a write that must arrive, send it as a query to a queryable that replies. A reply is the acknowledgement.
- **Evaluate the rules.** Take the router's access-control file and check the identity, action and key expression against it offline. This answers the question without sending anything.
- **Compare expected with actual.** An operator who knows which publishers should be producing can alert when one is silent.

## How goat handles it

- `goat pub --confirm` publishes and then reads the value back from storage. It reports landed, value mismatch or not found, and exits non-zero when the write is not confirmed (built).
- `goat doctor --topic <key>` writes a marker value under the caller's own prefix and reads it back, to answer whether the caller can write there (built).
- `goat acl test` evaluates declared assertions against the access rules, so a rule change is tested before it reaches a router (built).
- Expected-versus-actual monitoring: Prometheus rules that alert when a declared publisher is silent or an undeclared one is producing (built; ADR 1022 lists what remains).
- A dead-letter queue for denied writes is not built. ADR 1022 records why goat does not build one.

## Read more

- [ADR 1022: Zenoh denial observability](https://github.com/USAREUR-AF/goatcore/blob/main/docs/adr/1022-zenoh-denial-observability.md)
- [Brokerless pub/sub: the consequences](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/zenoh-brokerless-consequences.md)
- [Zenoh data fabric, "Access control"](https://github.com/USAREUR-AF/goatcore/blob/main/docs/design/zenoh-data-fabric.md#access-control)
- [What do you give up with brokerless pub/sub?](what-do-you-give-up-with-brokerless-pub-sub.md)
