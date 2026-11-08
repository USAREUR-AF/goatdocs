# Partner Data Sharing Charter — TEMPLATE

> **A lighter instrument now exists, and it is the default.** For the ordinary case — one owner opening its **own** unclassified data on terms it sets — use the [Release Declaration and Accession](release-declaration-and-accession.md) instead: the owner publishes terms once, unilaterally, and each recipient accedes with a single signature. No negotiation, no countersignature, no per-recipient instrument. **This charter remains the right instrument where a relationship genuinely needs bilateral terms** — reciprocal obligations, jointly-owned data, negotiated liability. Never sign both over the same data ([ADR 1143](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1143-unilateral-release-declaration-and-accession.md)).

> **Template status.** This is the canonical template for an unclassified data-sharing partnership under the GOAT-Net data-sharing pattern (ADR [`../adr/0821-mission-partner-sharing-pattern.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0821-mission-partner-sharing-pattern.md), design at [`../design/mission-partner-sharing.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/mission-partner-sharing.md)). When a real partnership instantiates this charter, **copy this file** to a per-partnership location, fill in the placeholders, and delete this template-status block.

> **Critical framing — necessary but not compelling.** Signing this charter establishes the **framework** that *enables* data sharing between the parties. It does **not obligate** either party to share any specific data. Specific data flows remain bilateral, case-by-case decisions made through the procedures in section 6 (release-decision workflow). Without a signed charter, no `release/<partner>/...` allowlist entries are issued. With a signed charter, allowlist entries are *possible* — each requires per-topic approval. The charter unlocks the shape; data discretion stays absolute.

> **Maturity caveat.** GOAT-Net is at proof-of-concept stage. The direction is sound and anchored in mainstream distributed-systems patterns; specific scaling, performance, and operational characteristics will be discovered, not asserted. A viable scaling plan exists (ADR 0216 — federation plane / site plane separation) and becomes operative *if* GOAT-Net earns it through the early phases. Partners signing this charter are entering an early-phase relationship; performance expectations under section 3.3 are calibrated honestly to commercial-internet realism, not aspirational SLAs.

---

# Data Sharing Charter

**Between:**

- **Party A:** [PARTY A LEGAL NAME] (the operator of GOAT-Net)
- **Party B:** [PARTY B LEGAL NAME] (the mission partner)

**Effective date:** [DATE]
**Charter version:** 1.0
**Reciprocity:** [BILATERAL | ONE-DIRECTIONAL — A → B | ONE-DIRECTIONAL — B → A]

---

## 1. Purpose

This charter establishes the framework for unclassified data sharing between Party A and Party B over the **GOAT-Net (Geo-Distributed Open Architecture Transformation Network)** data backbone, under the conventions described in ADR 0821.

The framework is **necessary but not compelling**: signing this charter does not obligate either party to share any specific data. Specific data flows are decided per topic, per direction, through the release-decision workflow in section 6.

## 2. Scope (placeholder — fill at instantiation)

### 2.1. Data type and operational requirement

> **Placeholder — fill in at charter instantiation.**
>
> Describe the type(s) of data anticipated to flow under this charter and the operational requirement(s) the data sharing supports. Concrete enough for the parties to understand what flows mean operationally; not so prescriptive that future per-topic decisions are pre-empted.
>
> Example phrasing: *"Position reports from sensor sources at named sites; supporting shared situational awareness for [mission context]. Specific topics, sources, and rates are decided per-flow through section 6."*

### 2.2. Mission context

> **Placeholder — fill in at charter instantiation.**
>
> The broader mission this partnership supports. Names organizations, mission area, geographic scope, time horizon. Not classification-bearing.

### 2.3. Out of scope

This charter explicitly does **not** cover:

- Cross-domain (classification-crossing) data sharing — see Party A's CDS conditioning regime, separate agreement required.
- Real-time control or actuation across the boundary — `cmd/` topics are not in scope.
- Any flow not explicitly approved per section 6.

---

## 3. Four-facet expectations

Any data that flows under this charter is held to the following expectations. **Expectations, not SLAs** — the parties commit to good-faith effort to meet them; hard SLAs would require a contract beyond this charter.

### 3.1. Security

- Encryption in transit: TLS 1.3 minimum on every hop touching shared data; no plaintext.
- Identity assurance: end-user identity equivalent to NIST SP 800-63 IAL2 / AAL2 or above, federated via OIDC.
- Audit retention: ≥ 90 days on each party's audit logs covering accesses to shared data.
- Incident notification SLA: 24 hours for confirmed incidents, 72 hours for suspected, on either party's side.

### 3.2. Functionality

- OIDC-compliant Identity Provider with discovery endpoint reachable by the other party.
- Zenoh wire-protocol routability (or compliant shim per the shim pattern, ADR [`../adr/0209-shim-pattern.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0209-shim-pattern.md)).
- Identity assertion at the release-namespace boundary — every release event is bound to an end-user identity, not a network address.
- Optional inbound subscription capability (for reciprocal partnerships).

### 3.3. Performance (commercial-internet-realistic)

Calibrated to commercial transport-based internet:

- Round-trip latency to mutual relay: typical < 500ms; episodic spikes acceptable.
- Sustainable throughput: typed per partnership in Appendix A.
- Monthly availability: ≥ 99% (calibrated to commercial-internet realism).

### 3.4. Reciprocity

> **Section applies only to BILATERAL partnerships.** Strike for ONE-DIRECTIONAL partnerships.

If Party A exposes `release/goat/<topic>/...` to Party B, Party B *may* expose `release/<party-b-slug>/<topic>/...` to Party A under the **same** convention — same default-deny baseline, identity-bound + policy-gated + audit-logged release discipline, symmetric four-facet expectations.

Reciprocity is a *capability* of the charter; specific reciprocal flows still require per-topic approval per section 6.

---

## 4. Identity federation

Each party operates an OIDC IdP. Identity assertions are accepted within the issuing party's release-namespace scope only.

| Field | Party A | Party B |
|---|---|---|
| OIDC Discovery URL | [URL] | [URL] |
| IdP product | [Ory / Dex / Kanidm / Zitadel / Keycloak / other] | [Ory / Dex / Kanidm / Zitadel / Keycloak / other] |
| Identity assurance level | [IAL2 / IAL3] / [AAL2 / AAL3] | [IAL2 / IAL3] / [AAL2 / AAL3] |
| End-user authenticator(s) | [FIDO2 / certificate / TOTP+password / …] | [FIDO2 / certificate / TOTP+password / …] |

A partner-side identity has no authority outside its partner's release-namespace scope.

---

## 5. Audit and retention

Each party maintains an audit log covering accesses to and releases under this charter. Minimum retention: 90 days per side. Audit format is each party's choice; symmetric audit federation (the parties shipping audit logs to each other) is **optional** and decided per partnership in Appendix B.

Each party permits the other to **request access to audit records** related to a specific release event for incident-investigation purposes; the recipient of such a request commits to good-faith response within five business days.

---

## 6. Release-decision workflow

Specific data flows under this charter are decided per topic, per direction, through this workflow:

1. **Request.** Either party requests release of a topic in the agreed direction.
2. **Review.** The releasing party's named approver (Appendix B) reviews against operational considerations: does the topic content match the data-type scope (section 2.1)? Is the requesting context appropriate? Are any caveats needed?
3. **Approval.** Approval is recorded in the releasing party's policy engine (or equivalent governance system) with the approver's identity and timestamp.
4. **Allowlist entry.** The release boundary's allowlist is updated to permit the topic per the approval. Schema declaration must be in place (`attest/schema/<topic>` or `attest/schema-declaration/<topic>`) before the allowlist takes effect.
5. **Audit.** Every approval, every release event, every revocation lands in the audit log on both sides.
6. **Revocation.** Either party may revoke a previous approval at any time; revocation takes effect at the boundary within 24 hours.

This workflow keeps "what is releasable to whom" an explicit, auditable property — not an emergent network-configuration property.

---

## 7. Schema declaration discipline

Every topic released under this charter carries a schema declaration:

- **Registered schema** at `attest/schema/<topic>` for machine-introspectable formats (preferred).
- **Binary declaration** at `attest/schema-declaration/<topic>` for proprietary or binary formats — declares vendor, format, version, and a remediation plan to migrate to an open standard if applicable.

No third state — undeclared topics do not cross the boundary. Schema declaration discipline is described in [`../design/data-dictionary.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/data-dictionary.md).

---

## 8. Termination

- **Voluntary termination.** Either party may terminate this charter with 30 days' written notice. All allowlist entries are torn down at termination effective date.
- **For-cause termination.** Either party may terminate immediately on a material breach (defined as: failure to meet a four-facet expectation under section 3 after a written cure-period notice; confirmed unauthorized release; sustained failure to honor section 6 revocation requests).
- **Surviving clauses.** section 5 (audit retention) survives termination for the 90-day retention window. section 3.1 (security) applies to any retained data covered by section 5.

Outstanding data already shared at termination effective date retains its release-state — termination does not retroactively rescind permission to use already-shared data; both parties may continue using such data within the original release scope.

---

## 9. Reference architecture

Party B may, but is not required to, adopt the **Partner Reference Architecture (PRA)** described at [`../design/partner-reference-architecture.md`](../design/partner-reference-architecture.md) — a minimal Zenoh-on-ZTOL stack that interops cleanly with GOAT-Net. The PRA is a recommendation, not a requirement; Party B may run any architecture meeting the four-facet expectations.

---

## 10. Disputes

Disputes about charter interpretation, performance against expectations, or release-workflow decisions are escalated to the named POCs in Appendix B for good-faith resolution. Unresolved disputes escalate to the parties' respective senior leadership; this charter does not invoke external arbitration.

---

## 11. Amendments

This charter is amended only by a written amendment signed by both parties. Appendices A and B may be updated administratively (without formal amendment) by mutual written agreement of the named POCs in Appendix B; Appendix updates are versioned and dated.

---

## 12. Signatures

| Field | Party A | Party B |
|---|---|---|
| Signatory name | [NAME] | [NAME] |
| Signatory title | [TITLE] | [TITLE] |
| Date | [DATE] | [DATE] |
| Signature | __________________ | __________________ |

---

## Appendix A — Data Type and Operational Requirement (placeholder)

> **Fill in at charter instantiation.**

### A.1. Data type(s) anticipated

[Describe the type(s) of data anticipated to flow under this charter. Be concrete enough to give shape; not so prescriptive that future per-topic section 6 decisions are pre-empted. Reference [`../design/entity-vocabulary.md`](../design/entity-vocabulary.md) for entity terminology.]

### A.2. Operational requirement

[The mission requirement the data sharing supports. Names the operational outcome — what the partnership enables operators to do that they could not do before. Not classification-bearing.]

### A.3. Throughput targets (typed)

| Direction | Topic class | Expected throughput | Burst tolerance |
|---|---|---|---|
| A → B | [class] | [Kbps / Mbps] | [%] |
| B → A | [class] | [Kbps / Mbps] | [%] |

---

## Appendix B — Per-Partnership Technical Configuration

> **Fill in at charter instantiation.**

### B.1. Network endpoints

| Item | Party A | Party B |
|---|---|---|
| Bridge / boundary endpoint | [hostname:port] | [hostname:port] |
| Allowlisted CIDR(s) | [CIDR list] | [CIDR list] |
| WireGuard public key | [base64] | [base64] |

### B.2. OIDC configuration

| Item | Party A | Party B |
|---|---|---|
| OIDC Discovery URL | [URL] | [URL] |
| Client ID issued for the other party | [id] | [id] |
| Scopes accepted | [list] | [list] |

### B.3. Named POCs

| Role | Party A | Party B |
|---|---|---|
| Charter primary | [name, email] | [name, email] |
| Release approver | [name, email] | [name, email] |
| Incident contact | [name, email, 24×7 channel] | [name, email, 24×7 channel] |
| Charter administrator (Appendix updates) | [name, email] | [name, email] |

### B.4. Symmetric audit federation (optional)

- [ ] Party A ships audit log records of releases under this charter to Party B.
- [ ] Party B ships audit log records of releases under this charter to Party A.
- Format: [CEF / OCSF / vendor-native / …]
- Endpoint: [URL or syslog target]
- Retention at receiving party: [days, ≥ 90]

### B.5. Tier and reference architecture adoption

Pick exactly one path:

- [ ] **PRA tier** — Party B adopts the Partner Reference Architecture as published at [`../design/partner-reference-architecture.md`](../design/partner-reference-architecture.md). Party B operates the full eight-piece minimal stack on Party-B-controlled infrastructure.
- [ ] **Tier-0: `goat-moon-open-pod`** — Party B operates the reference moon-pod implementation at `moon-pod` on Party-B-controlled infrastructure. Conformance per [goatstuff `moon-pod-conformance.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/moon-pod-conformance.md).
- [ ] **Tier-0: vendor moon-pod** — Party B operates a `goat-moon-<product>-pod` from a third-party vendor (a commercial C2 or data platform). Vendor product: ____________________. Conformance per [goatstuff `moon-pod-conformance.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/moon-pod-conformance.md); Party A runs [`../../tests/moon-pod-conformance/`](https://github.com/usareur-af/goatcore/tree/main/tests/moon-pod-conformance) at onboarding to validate.
- [ ] **Tier-0: partner-built moon-pod** — Party B has built their own conformant moon-pod. Conformance per [goatstuff `moon-pod-conformance.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/moon-pod-conformance.md); Party A runs the conformance suite at onboarding.
- [ ] **Other** — Party B operates a different architecture meeting the four-facet expectations and (if Tier-0-class) the seven requirements; described in B.6 below.

### B.6. Partner architecture description (if not adopting PRA or a moon-pod)

[Brief description of partner-side architecture as it relates to the four-facet expectations. Sufficient detail for Party A to understand the boundary; not exhaustive. If claiming Tier-0 conformance under requirements at [goatstuff `moon-pod-conformance.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/moon-pod-conformance.md), include conformance smoke-test results.]

---

*End of charter template. Companion documents: ADR [`../adr/0821-mission-partner-sharing-pattern.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0821-mission-partner-sharing-pattern.md); ADR [`../adr/0223-goat-moon-pod-repo-containment.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0223-goat-moon-pod-repo-containment.md); design [`../design/mission-partner-sharing.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/mission-partner-sharing.md); reference architecture [`../design/partner-reference-architecture.md`](../design/partner-reference-architecture.md); Tier-0 contract [goatstuff `moon-pod-conformance.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/moon-pod-conformance.md); moon-pod spec [`../design/goat-moon-pod.md`](https://github.com/usareur-af/goatstuff/blob/main/docs/design/goat-moon-pod.md); vendor counterpart [`../vendor-templates/data-services-provider-charter.md`](../vendor-templates/data-services-provider-charter.md).*
