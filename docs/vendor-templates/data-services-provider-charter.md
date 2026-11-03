# Data Services Provider Charter — VENDOR TEMPLATE

> **Template status.** This is the canonical template for a vendor providing data, data services, or data-emitting capabilities into **GOAT-Net (Geo-Distributed Open Architecture Transformation Network)**. It is *unilateral and prescriptive* — distinct from the Partner Data Sharing Charter (which is bilateral and respects partner sovereignty). Vendors selling data services into GOAT-Net sign this charter as a precondition of ingestion.

> **Critical framing — vendor obligations are not optional.** A vendor that cannot or will not meet the obligations in this charter does not get their data into GOAT-Net. There is no "exception" path that bypasses the discipline. Where a vendor uses binary or proprietary formats (a real and common case), §3 requires an explicit explanation and a remediation plan toward open standards — the format is accepted, but the obligation to migrate is not waived.

> **Premise.** Virtually no commercial vendor today operates as a *true* data services provider — one that registers their data definitions, ships into open data backbones, avoids vendor lock-in, and supports portable consumer access. This charter is the discipline that turns a vendor into one. We adopt it because the alternative is accumulating vendor cruft that costs more to migrate later than to do right now.

> **Maturity caveat.** GOAT-Net is at proof-of-concept stage. The direction is sound and anchored in mainstream distributed-systems patterns; specific scaling, performance, and operational characteristics will be discovered, not asserted. A viable scaling plan exists (ADR 0216 — federation plane / site plane separation) and becomes operative *if* GOAT-Net earns it through the early phases. Vendors signing this charter today are entering an early-phase relationship; the discipline (mandatory schema declaration, anti-lock-in clauses, GOAT-Net ingestion mandate) is sound and stable across maturity, but specific operational scale at the GOAT-Net ingestion boundary will be measured rather than promised.

> **Measurement system that gives this charter teeth.** This charter's obligations — particularly schema declaration (§3), GOAT-Net ingestion mandate (§4), anti-lock-in (§6), and data ownership / portability — are aspirational without a measurement loop closing on them. That loop lives in [`../design/engineering-health-assessment.md`](../design/engineering-health-assessment.md), specifically the **Ownership Principle** (the Customer owns the metrics; the Vendor is a measured component) and the **Data Leverage metric** (time-to-answer from Customer-controlled data, extraction posture per source, decision-support coverage). A Vendor that cannot or will not expose the telemetry the Customer needs to score these metrics is by definition non-compliant with this charter, independent of any individual §3-§9 line.

---

# Data Services Provider Charter

**Vendor:** [VENDOR LEGAL NAME] (the Data Services Provider, "Vendor")
**Customer:** [CUSTOMER LEGAL NAME] (the operator of GOAT-Net)
**Effective date:** [DATE]
**Charter version:** 1.0
**Procurement reference:** [PO / contract number]

---

## 1. Purpose

This charter defines the obligations the Vendor agrees to as a precondition of providing data, data services, or data-emitting capabilities into **GOAT-Net**, the Customer's data backbone. Compliance with these obligations is a condition of procurement; non-compliance blocks ingestion and may trigger contract review.

GOAT-Net is the Customer's open-architecture data substrate. Conceptually it is the union of: a Zenoh-based message fabric, sovereign identity primitives, audit and lineage infrastructure, and a mandatory data dictionary. Vendors do not interact with GOAT-Net as a product platform; they emit data into it as a backbone, under the obligations described below.

## 2. Definitions

- **GOAT-Net** — the Customer's data backbone (Geo-Distributed Open Architecture Transformation Network).
- **Data services** — any commercial offering that emits, transforms, or hosts data the Customer ingests, queries, or relies on operationally.
- **Open standard** — a publicly-specified, royalty-free, machine-introspectable format with at least two independent implementations. Examples: JSON Schema, OpenAPI, AsyncAPI, OGC standards, MISB / STANAG (where royalty-free), STIX / TAXII, Apache Parquet, Apache Arrow, Protobuf-with-public-schemas.
- **Proprietary format** — any format whose specification is not publicly available, or whose specification is publicly available but encumbered (royalty-bearing, NDA-restricted, single-vendor implementation).
- **Binary format** — any format that is not directly machine-introspectable as a structured document (JSON, YAML, XML, Protobuf-with-schema, etc.). Includes encoded video, encoded audio, encoded radar I/Q, vendor-specific telemetry binaries.

## 3. Mandatory schema declaration (§3 of the data dictionary discipline)

The Vendor's data emissions into GOAT-Net **must declare** their topic schemas before publishing. **Two valid states**, no third:

### 3.1. Registered schema (preferred)

For all open-standard, machine-introspectable formats: full JSON-Schema-shaped declaration at `attest/schema/<topic-pattern>` with project extensions (`unit`, `confidence`, `entity_ref`, `description`, `range`, `freshness_target_seconds`).

### 3.2. Binary-declared (with remediation obligation)

For binary or proprietary formats: declaration at `attest/schema-declaration/<topic-pattern>` carrying:

- Vendor name + format name + format version.
- Plain-language description of the byte stream.
- Out-of-band schema reference (vendor specification document).
- **A written explanation** of why the format is binary or proprietary — what specific need the format addresses that no open standard meets today.
- **A remediation plan** with:
  - Named target open standard(s) the format will migrate to.
  - Named milestones with dates.
  - Periodic review cadence (default: annual).

### 3.3. No third state

Topics with no declaration in either state are **rejected** at the GOAT-Net ingestion boundary. There is no "ingest first, declare later" exception.

### 3.4. Schema evolution

Schema changes follow the GOAT-Net schema-evolution discipline (ADR [`../adr/0506-fabric-schema-evolution.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0506-fabric-schema-evolution.md)) — versioned declarations, declared compatibility (`backward` / `forward` / `none`), rollover windows.

## 4. GOAT-Net ingestion mandate

All Vendor data the Customer ingests **must land in GOAT-Net**. The Vendor commits to:

- **Not** keep canonical copies of Customer-owned data in vendor-proprietary cloud stores accessible only via the Vendor's portal or API.
- **Not** require the Customer to use a vendor-specific UI, console, or platform to access their own data.
- **Not** mediate Customer access to Customer data through a vendor-controlled chokepoint.

Where the Vendor's product naturally produces data in a vendor portal (a SaaS use case), the Vendor commits to an emit-to-GOAT-Net pipeline that forwards a canonical copy of the data to the Customer's GOAT-Net ingestion boundary in real-time or near-real-time, with the schema-declaration discipline of §3 applied.

## 5. Open-standards preference

The Vendor commits, where reasonable choice exists, to use the open standards in §2 (Definitions) for data emission. Where vendor-specific formats are unavoidable, §3.2 (binary-declared with remediation) applies.

The Customer maintains a **preferred open-standard catalog** at [`../design/data-dictionary.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/data-dictionary.md) §"Open standard preference catalog" (where named) and may add to it. Vendors are expected to default to catalog-listed standards before introducing alternatives.

## 6. Anti-vendor-lock-in clauses

- **Data ownership.** Customer-emitted-or-derived data is Customer-owned. The Vendor does not claim derivative-work ownership over data the Customer's systems produce by passing through the Vendor's product.
- **Portability.** At contract end, the Vendor commits to a one-time **bulk export** of all Customer data in the Vendor's possession, in declared formats per §3, within 30 days. The Customer's right to ingest this data into a non-Vendor system is unrestricted.
- **No platform-mediated access.** Customer access to Customer data does not require running Vendor software, paying a Vendor subscription post-contract-end, or operating a Vendor-supplied client.
- **Documentation.** The Vendor publishes implementation-grade documentation for any binary or proprietary format covered under §3.2 sufficient for the Customer to write a parser independently. NDA-restricted documentation is not acceptable for Customer-owned data formats.

## 7. Identity, audit, and lineage

The Vendor's data emissions are subject to the same identity, audit, and lineage discipline as all GOAT-Net emissions:

- **Workload identity.** Vendor service accounts use OIDC + workload identity per Customer-issued credentials. Service-account credentials are scoped to the Vendor's emission namespace.
- **Audit.** Every emission lands in the audit-logger interceptor (ADR [`../adr/0508-audit-logger-interceptor.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0508-audit-logger-interceptor.md)) keyed by the Vendor's identity. Vendor-side audit retention obligations are separate (§9.4).
- **Lineage.** Vendor emissions feed the lineage materializer (per [`../design/lineage.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/lineage.md)) automatically. The Vendor's data is subject to the same provenance walking as any other fabric topic.

## 8. Citation and source-fidelity (where the Vendor produces derived data)

If the Vendor's product *derives* data from upstream sources (sensor fusion, classification, scoring), Vendor emissions carry the standard citation array (`sources: [{topic, timestamp, digest}]`) per the rapid-adaptation citation discipline (ADR [`../adr/0512-rapid-adaptation-with-ai.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0512-rapid-adaptation-with-ai.md) §"Citation discipline"). Zero-citation derived emissions are rejected at the GOAT-Net ingestion boundary.

If the Vendor's product *originates* data from sensors the Vendor operates, citation is omitted (no upstream fabric source) but `source_id` and provenance metadata in the schema must identify the originating sensor.

## 9. Vendor-side obligations summary

| § | Obligation |
|---|---|
| 3.1 | Register schemas for all machine-introspectable formats at `attest/schema/<topic>` |
| 3.2 | Submit binary-declaration + explanation + remediation plan for binary / proprietary formats |
| 3.4 | Follow schema-evolution discipline for schema changes |
| 4 | Land all Customer data in GOAT-Net; no vendor-portal-only canonical stores |
| 5 | Default to open standards from the preferred catalog |
| 6 | Honor data ownership, portability (30-day bulk export), no platform-mediated access |
| 7 | Operate under Customer-issued workload identity; emissions feed audit + lineage |
| 8 | Carry citation arrays on derived emissions |
| 9.4 | Maintain ≥ 90-day audit retention on Vendor-side access logs |
| 10 | Submit to periodic review (§10) |

### 9.1. Throughput and latency

Vendor commits to throughput and latency targets declared in Appendix A. Targets are calibrated to the operational requirement, not vendor product marketing.

### 9.2. Availability

Vendor commits to ≥ 99.5% monthly availability of the emission pipeline into GOAT-Net (calibrated higher than partner expectations because vendor relationships are commercial). Lower commitments require Customer waiver in writing.

### 9.3. Incident notification

Vendor commits to incident notification — confirmed within 24 hours, suspected within 72 hours — for any incident affecting Customer data or the emission pipeline.

### 9.4. Vendor-side audit retention

Vendor maintains ≥ 90-day audit retention on Vendor-side access logs covering Customer data. Customer may request audit records for incident investigation; Vendor commits to good-faith response within five business days.

## 10. Compliance review

- **Quarterly.** Customer reviews Vendor schema-compliance dashboard. Non-compliant emissions, missed remediation milestones, and audit gaps are flagged. Vendor receives the report and addresses in the next quarter.
- **Annual.** Full review of the binary-format inventory (Appendix B) and remediation plan progress. Remediation plans without progress trigger procurement review.
- **Ad hoc.** Triggered by an incident or significant deviation; performed within 30 days of trigger.

## 11. Non-compliance consequences

- **Schema declaration missing or invalid:** emissions rejected at the GOAT-Net ingestion boundary. Service degradation is not the Customer's responsibility.
- **GOAT-Net ingestion mandate violated** (canonical data hidden in Vendor portal): contract review; remediation plan required within 30 days; non-remediation triggers contract termination.
- **Anti-lock-in clauses violated:** contract review; same remediation cadence.
- **Repeated remediation milestone misses on a binary-declared format:** procurement review; possible change of vendor at contract renewal.

This is **not** an SLA penalty schedule — it is a precondition discipline. The Customer does not credit downtime; the Customer enforces ingestion boundary discipline.

## 12. Termination

- **For-cause termination.** Customer may terminate immediately on a confirmed material breach of §3, §4, or §6.
- **Mutual termination.** Either party may terminate per the underlying procurement contract terms.
- **Surviving clauses.** §6 (anti-lock-in, particularly bulk export and portability) survives termination per the underlying contract terms — typically 30 days post-termination for the bulk export, ongoing for documentation access.

## 13. Signatures

| Field | Vendor | Customer |
|---|---|---|
| Signatory name | [NAME] | [NAME] |
| Signatory title | [TITLE] | [TITLE] |
| Date | [DATE] | [DATE] |
| Signature | __________________ | __________________ |

---

## Appendix A — Vendor Inventory and Throughput Targets (placeholder)

> **Fill in at charter instantiation.**

### A.1. Data the Vendor provides

| Topic class | Description | Format (open / binary-declared) | Schema reference |
|---|---|---|---|
| [class] | [description] | [format] | `attest/schema/...` or `attest/schema-declaration/...` |

### A.2. Throughput and latency targets

| Topic class | Sustainable throughput | Burst tolerance | End-to-end latency target |
|---|---|---|---|
| [class] | [Kbps / Mbps] | [%] | [ms / s] |

### A.3. Availability target

[≥ 99.5% monthly default; document any waiver here.]

---

## Appendix B — Binary-Format Inventory and Remediation Plan (placeholder)

> **Fill in at charter instantiation.** Lists every binary or proprietary format the Vendor uses, with §3.2 obligations satisfied per format.

### B.1. Format-by-format

| Format | Vendor:Format:Version | Why open standards don't fit | Target open standard for migration | Milestone date(s) | Review cadence |
|---|---|---|---|---|---|
| [format-1] | [vendor:fmt:ver] | [explanation] | [target standard] | [dates] | [annual / semi-annual] |

### B.2. Aggregate remediation timeline

[Gantt-style or milestone list across all binary formats, showing the Vendor's path toward a fully open-standards data emission posture.]

---

## Appendix C — Open-Standard Preferences (Customer-Provided)

> **Filled by Customer at charter instantiation; updated as the catalog evolves.**

The Customer maintains a preferred-open-standards catalog. Vendors default to these where applicable; deviations require §3.2 binary-declared treatment.

| Domain | Preferred standard(s) |
|---|---|
| Schema description | JSON Schema (draft 2020-12), OpenAPI 3.1, AsyncAPI 2.x |
| Time-series / telemetry | JSON, Protobuf-with-public-schema, Apache Arrow / Parquet (bulk) |
| Geospatial | OGC standards (GeoJSON, GeoPackage, STAC, SensorThings API) |
| Video | MISB ST 0601 (where royalty-free); H.264/H.265 with sidecar metadata |
| Cyber threat intel | STIX 2.1 + TAXII 2.1 |
| Identity | OIDC, OAuth 2.0, SAML 2.0, FIDO2 / WebAuthn |
| Crypto | NIST-approved primitives; FIPS 140-3 modules where validation required |

---

*End of charter template. Companion documents: rapid-adaptation-with-AI ADR [`../adr/0512-rapid-adaptation-with-ai.md`](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0512-rapid-adaptation-with-ai.md); data-dictionary design [`../design/data-dictionary.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/data-dictionary.md); lineage design [`../design/lineage.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/lineage.md); partner counterpart [`../partner-templates/data-sharing-charter.md`](../partner-templates/data-sharing-charter.md).*
