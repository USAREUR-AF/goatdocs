# Joining a goatnet as a partner organisation — what to expect

You do not need any prior context to read this. It is the pre-enrollment
packet for the **partner peer** path: your organisation's people and devices
join an existing goat fabric that someone else operates. (If you want your
own site federated with ours, or a completely standalone fabric of your own,
those are different paths with their own packets — ask your contact.)

Two things to know up front, honestly:

1. **The fabric is operated by its host organisation.** You are joining their
   network under their operating rules. Everything below describes what you
   get and what is enforced — and, where enforcement is still being rolled
   out, it says so plainly rather than promising it.
2. **Treat a shared goatnet as one room until told otherwise.** Read
   separation between organisations is applied per-organisation by the
   operators — it is not something being a partner switches on automatically.
   If something must not be visible to the other organisations on that
   fabric, raise it with the operators BEFORE publishing it.

Total reading time: about ten minutes.

---

## How your people get identities

Nobody fills in your people's records for them, and no single person on the
host side can both invite and admit someone. Onboarding runs in three stages:

1. **A sponsor invites you.** A named person on the goatnet vouches for the
   invitation. Sponsors can only sponsor up to their own access level — the
   gate refuses rather than quietly downgrading.
2. **Your person submits their own details** at an intake page reachable
   before they have any credentials. They state their name, their
   organisation, and what they need; they cannot self-select an
   administrative level.
3. **An admin approves,** and only then is anything minted.

What arrives after approval is a welcome email carrying, depending on the
person's level: a one-time mesh enrollment key, a one-time login link, and —
for people who will publish data — a one-time link to a credential bundle
that never travels by email. Every one-time link has a stated expiry and a
stated recovery path ("ask an admin to re-send") — a missed window is never a
locked door.

Once on the mesh, your people land on the goatnet's own onboarding guide,
which has a **Partner view** written specifically for your situation: what is
different where data crosses organisation lines. The welcome email links it
directly for partner-organisation members.

## Access levels, in plain words

Your organisation does not get one blanket level; each person gets the level
their work needs:

| Level | What it means |
|---|---|
| Browse | Sees the fabric's surfaces; publishes nothing |
| Developer | Holds a fabric identity; publishes under their own namespace |
| Admin tiers | Bring people on, manage access — granted per person, sparingly |

"Partner" is **who your organisation is, not a permission level** — it is
recorded on the identity and never silently changes what a level may do.

## How data works

- **Your namespace is yours alone.** Everything a person or machine of yours
  publishes lives under its own write anchor. Nobody else — no other
  organisation, not even an operator — can publish under it. There is no
  grant that adds a second writer to your root.
- **Data crosses organisations only through release lanes.** A lane is a
  shared namespace opened for a named set of organisations. Released to just
  you: bilateral. Released to a broader set: everyone in the set. Membership
  of the set IS the audience; there is nothing to configure on your side.
- **Publishing into a lane is a separate, named grant** made by the goatnet's
  admins. Being able to read a lane never implies you may write into it.
- **Refusals are silent by design.** A publish outside your namespace, or
  into a lane you were not granted, simply does not arrive. If data seems to
  vanish, ask before debugging for an afternoon.
- **Some streams are encrypted to a granted audience.** If you hold a fabric
  certificate and are in the audience, decryption happens in your own
  process — the platform holds no keys. Staff without certificates read such
  streams through mediated web surfaces, which is a supported path.

## Your machines

- Machines enroll through your organisation's own custodian identity, against
  a quota the operators grant. **The starting quota is zero** — that is the
  control working, not an error; ask for the quota before enrolling.
- Each machine gets its own identity and its own namespace — not a share of
  a person's.
- Gear that also talks to your own platform — anything with a path off the
  goat fabric — is enrolled under a deliberately narrow device class with
  management-plane reach only. Those restrictions describe the device's
  exposure, not distrust of you; widening one is an operator decision, never
  a side effect of enrolment.

## What we ask of you

- **A named point of contact** who will hold the custodian identity for your
  machines and be the person operators talk to about quota and lanes.
- **Say what is sensitive before you publish it**, so partitions and lanes
  can be set up ahead of the data rather than after it.
- **One-time links get used promptly.** Enrollment keys and bundle links are
  single-use and expire; recovery is easy but adds a round-trip.
- **No workarounds.** If a lane you expect is missing or a write is refused,
  ask — do not paste data somewhere reachable to move faster.

## What to have ready before day one

- The list of people to onboard: name, email, and what each needs to do
  (browse / publish / administer your own cohort).
- The machines you intend to enroll and which of them also talk to your own
  platform (those get the narrow device class).
- Your organisation's name as you want it recorded, and the nation it
  belongs to — releasability attribution uses it.

Your host contact fills in the goatnet-specific values — intake address,
sponsor, timelines — when they hand you this packet.
