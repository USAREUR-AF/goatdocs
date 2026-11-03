# Standalone GOAT-Net — partner evaluation packet

> **For operational units evaluating GOAT-Net for a lab deployment, with a path to field operational use.**

This packet is everything you need to decide whether GOAT-Net is right for your unit, what it would take to stand up a lab instance at home station, and what the path looks like to push it into deployed operations.

You do not need any prior context to read this. Each document stands alone. Skim in order; revisit when you're ready to act.

## What's in this packet

| # | Document | What it answers |
|---|---|---|
| 00 | Executive overview | What is GOAT-Net, what does it solve, why would a unit want it |
| 01 | What you get | Capability map — what works today, what's coming, what's out of scope |
| 02 | Procurement requirements | Hardware BOM, cloud cost estimates, personnel, software licenses |
| 03 | [Lab phase plan](03-lab-phase.md) | Week-by-week stand-up at home station |
| 04 | Field phase plan (deployment) | Scaling in deployed environments |
| 05 | 30-day roadmap | What's hardening between today and ~1 month out |
| 06 | Asks and commitments | What you bring, what we provide, what's still open |

## Quick read order by audience

- **Network lead reviewing fit.** 00 → 01 → 02 → 06.
- **SA/SRE planning the work.** 00 → 03 → 04 → 02.
- **Commander deciding go/no-go.** 00 → 05 → 06.
- **Procurement officer.** 02 → 06.
- **You're already in.** 03, then concierge engagement (see 06).

## Two things to know up front

1. **GOAT-Net is at proof-of-concept stage.** Sovereign edge data backbones at this shape and scope have no established operational precedent at theater scale. The direction is sound and anchored in mainstream distributed-systems patterns; specific scaling, performance, and operational characteristics will be discovered, not asserted. We commit to the direction, not to specific numbers. Read 01-what-you-get.md carefully — every capability claim carries a maturity caveat.

2. **You will own everything.** Standalone GOAT-Net means your hardware, your cloud account, your offline CA, your identity domain, your data, your operations, your eventual ATO. We provide substrate + docs + concierge support during your first stand-up. We do not run managed service. We do not have keys to your fabric. We never see your operational data.

## How to engage

Read 00 first. If GOAT-Net looks like a fit:

1. Skim 01 + 02 to understand the capability surface and the procurement bill.
2. Read 03 + 04 to understand the journey shape.
3. Read 06 to understand what you'd commit to and what we'd commit to.
4. Reach out — see 06 for contact.

Total reading time, cover to cover: ~90 minutes.

## A note on this packet's currency

This packet was written **2026-05-07** and re-baselined **2026-08-14**. The substrate is changing; we add capabilities and harden existing ones on a roughly weekly cadence.

The re-baseline updated the capability map (01), the procurement figures (02), and the field-phase scale envelope (04) against what is actually built. **The 30-day roadmap (05) was deliberately left as a historical record** of what was planned in May 2026 rather than rewritten as a fresh forecast — it is marked expired at the top. Ask us for a live roadmap rather than reading dates out of it.

If you're reading this more than a couple of months after the re-baseline date, ask for a current version.
