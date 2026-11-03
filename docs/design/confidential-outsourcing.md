# Confidential Outsourcing — Architecture and Pilot Pattern

**Status.** Pattern + Pilot A specified; Pilot A in planning per `../project/cc-pilot-frontier-inference.md`.
**Decision authority.** [ADR 0611](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0611-confidential-outsourcing-pattern.md) (the pattern) + ADR 0610 (companion: internal CC anchors).
**Block.** 45B (45A is the internal-anchor companion).

## 1. What this is

A way to use commercial-cloud managed services (frontier-model inference, GPU training clusters, terabyte-scale analytics, globally-routable confidential pub/sub) **without exposing plaintext to the cloud provider**, by encrypting data only to a cryptographic key bound to a verified enclave running a known-good build. The enclave is architecturally a *partner peer* — inbound and outbound data cross the same release-bridge that handles every other partner relationship ([ADR 0821](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0821-mission-partner-sharing-pattern.md), [ADR 0513](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0513-wasm-conditioning-sandbox.md)).

The pattern is **decoupled from operational sovereignty**. Three invariants make that real:

1. Every byte crossing the boundary is encrypted with FIPS-validated crypto regardless of what runs inside the enclave.
2. Inbound data is treated as untrusted-origin and goes through the same WASM conditioning + schema-enforcer as partner data.
3. The CC environment cannot be a hard dependency of any operational service — only a producer/consumer of opt-in topics. Removing a CC integration is a config change, not a refactor.

This is not a substrate. It is a **boundary discipline** that lets workloads we cannot host travel to and from commercial cloud safely. The substrate is unchanged.

## 2. Five-layer reference architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│  L0 — SOVEREIGN ANCHOR  (unchanged: mesh / mgmt-plane / Zenoh /      │
│       offline CA / policy engine / audit-integrity / data dictionary)│
└─────────────────────────────────┬────────────────────────────────────┘
                                  │
              policy-engine approval per topic / class
              schema-enforcer + WASM conditioning
              attestation-bound encryption to L3 enclave
                                  │
┌─────────────────────────────────▼────────────────────────────────────┐
│  L1 — BOUNDARY  (release-bridge + ingest-bridge, FIPS edge)          │
│       reuses Block 28 WASM sandbox + Block 17A.5 policy engine       │
└─────────────────────────────────┬────────────────────────────────────┘
                                  │  attestation cert request
                                  │
┌─────────────────────────────────▼────────────────────────────────────┐
│  L2 — ATTESTATION ROOT  (per-CSP verifier inside L0)                 │
│       Nitro signed PCR doc / GCP vTPM quote / Azure THIM             │
│       offline-CA-signed cert iff measurement matches Block 40 pin    │
└─────────────────────────────────┬────────────────────────────────────┘
                                  │  fresh attestation cert per session
                                  │
┌─────────────────────────────────▼────────────────────────────────────┐
│  L3 — CC WORKLOAD  (inside attested enclave on chosen CSP)           │
│       FIPS-validated crypto NOT required inside (per ADR 0611 D3)    │
│       only egress is back through L1 (or to managed-service API)     │
└─────────────────────────────────┬────────────────────────────────────┘
                                  │  WG / mTLS gRPC / vsock
                                  │
┌─────────────────────────────────▼────────────────────────────────────┐
│  L4 — CONNECTIVITY  (cc-bridge peer paired with sovereign boundary)  │
│       low-rate Zenoh control + events; bulk over dedicated channel   │
└──────────────────────────────────────────────────────────────────────┘
```

### 2.1 L0 — Sovereign anchor

Unchanged. Mesh (Block 22 silent control plane), mgmt-plane (postgres-spock + signal + netbird-mgmt), Zenoh fabric, [policy engine](https://github.com/usareur-af/goatcore/blob/main/docs/design/egress-proxy.md) §6, audit-integrity ([ADR 0811](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0811-audit-log-integrity.md)), [data-dictionary discipline](https://github.com/usareur-af/goatcore/blob/main/docs/design/data-dictionary.md). Every L0 property — Island Mode, FIPS-validated crypto, supply-chain integrity, identity rooting — is preserved.

### 2.2 L1 — Boundary (egress + ingress release-bridge)

The crossing point. Built on the existing [Block 28 WASM conditioning sandbox](https://github.com/usareur-af/goatcore/blob/main/docs/design/wasm-conditioning-sandbox.md) pattern, extended bidirectionally.

**Egress path (L0 → L3):**

1. Producer publishes to a release-namespace topic (`release/cc-<csp>-<service>/<topic>`).
2. **Schema-enforcer** rejects undeclared publishes ([data dictionary](https://github.com/usareur-af/goatcore/blob/main/docs/design/data-dictionary.md)).
3. **Policy-engine approval** ([Block 17A.5](https://github.com/usareur-af/goatcore/blob/main/docs/design/egress-proxy.md) §6) — per-topic, per-destination, per-class. Approval is durable; revocation is immediate.
4. **WASM conditioning module** (signed by us; runs in fuel-bounded + memory-bounded + wall-clock-bounded sandbox per [ADR 0513](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0513-wasm-conditioning-sandbox.md)) — applies redaction, format normalization, lineage stamping.
5. **Attestation-bound encryption** — release-bridge requests fresh attestation cert from L2 (§2.3); encrypts the conditioned payload using the attested public key (X25519 or P-256). The DEK is per-message; sealed only to *this enclave instance*'s session key.
6. **Audit + lineage edge** captured ([ADR 0811](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0811-audit-log-integrity.md), [`lineage.md`](https://github.com/usareur-af/goatcore/blob/main/docs/design/lineage.md)).
7. **Wide-event emission** ([Block 27](https://github.com/usareur-af/goatcore/blob/main/docs/design/observability-wide-events.md)) — every CC-boundary crossing produces an OpenTelemetry event with `cc_boundary=egress`, `csp=<csp>`, `service=<service>`, `attestation_digest=<sha256>`, `correlation_id=<id>`.

**Ingress path (L3 → L0):**

1. Enclave publishes to the same logical topic, encrypted to the boundary's mesh-side public key.
2. Boundary decrypts, then treats payload as **untrusted-origin**.
3. **Schema-enforcer** — must be declared at `attest/schema/<topic>` or rejected.
4. **WASM conditioning** — partner-class conditioning applies (this is what makes the enclave architecturally a partner).
5. Re-published onto sovereign fabric under reserved `import/cc-<csp>-<service>/<topic>` namespace.
6. **Audit + lineage** — provenance edge marked with attestation digest captured at the time of crossing; this is durable evidence that the bytes came from a known-good enclave build.
7. **Wide-event emission** — `cc_boundary=ingress`.

**Why a release-bridge and not "just publish to the enclave."** The boundary IS the FIPS edge. Without the bridge, every producer + every consumer would need its own attestation client and its own encryption-to-attested-key path. Centralizing makes the boundary auditable in one place, makes the FIPS-departure scope (D3 in [ADR 0611](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0611-confidential-outsourcing-pattern.md)) provable in one place, and makes ripping out a CC integration a single config change.

### 2.3 L2 — Attestation root + key custody

**Per-CSP verifier crate.** Each CSP's attestation document format gets its own verifier crate at `cc-bridge/attestation/<csp>/`:

- **GCP** — `cc-bridge/attestation/gcp/`. Verifies vTPM quote (TPM 2.0 EK certificate chain rooted at Google attestation root + PCR values matching reproducible-build pin). Pilot target.
- **AWS** — `cc-bridge/attestation/nitro/`. Verifies signed Nitro attestation document (CBOR-encoded, COSE-signed, PCR0/1/2/3 + user data). Future.
- **Azure** — `cc-bridge/attestation/azure/`. Verifies via THIM (Trusted Hardware Identity Management) + AMD/Intel attestation roots. Future.

**Reproducible-build pin.** Every enclave build is reproduced from goat trunk + pinned dependencies + recorded toolchain version, producing a stable measurement (PCR set or equivalent). The pin set is committed to `cc-bridge/build-pins/<csp>/<service>/<version>.toml`, signed by the offline CA at release time, and consumed by the verifier at attestation time. This is the **trust root** — without a matching pin, the verifier issues no cert, and the boundary releases nothing. Pin management composes with Block 40 reproducible builds + binary transparency.

**Offline-CA-signed attestation cert.** When a verifier matches, it issues a short-lived (default 1 h) X.509 cert binding the enclave's attested public key to the build pin's identifier, signed by an intermediate CA delegated from the offline-CA root (ADR 0406). The release-bridge consumes the cert, encrypts to its public key, and treats the cert as the only authorization for the crossing.

**Key custody inside enclave.** The enclave generates its session keypair at boot inside the TEE. The private key never leaves the TEE memory boundary — TEE-bound by hardware, validated by the same attestation that authorized the boundary to talk to it.

**Attestation cadence.** Per-session by default (attestation cert is checked on first packet of a session, cached for the cert's lifetime, refreshed on the next session). Pilot tuning may shorten cadence on evidence.

### 2.4 L3 — CC workload

The actual workload runs inside the enclave. Constraints:

- **No FIPS-validated crypto required inside.** Per [ADR 0611](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0611-confidential-outsourcing-pattern.md) D3, the FIPS departure is purposeful, scoped, and sealed by L2 attestation. Inside the enclave, the workload uses whatever crypto is best for the job (rustls + ring, BoringSSL, etc.).
- **Egress restricted.** Workload egress is policy-controlled at build time. In pilot, egress is **only back through L1 to sovereign**. Workloads that need to call managed-service APIs (Bedrock, Vertex AI, Confluent Cloud) get explicit egress allowlists for those endpoints — direct from enclave with TLS — and the enclave acts as a confidential proxy. The workload's egress allowlist is part of the reproducible-build pin (so attestation covers it).
- **No persistent state.** Pilot enclaves are stateless and ephemeral. State (model weights, intermediate computation, vector indices) lives in objects encrypted-to-attestation that are loaded at startup. State that survives the session is sealed back across L1 to sovereign storage.
- **Audit-by-construction.** Workload code includes an audit hook that emits structured events back through L1; the hook is part of the framework, not optional. Audit suppression by the workload is structurally impossible because the wide-event channel is part of the L4 connectivity, not workload-controlled.

### 2.5 L4 — Connectivity

**`cc-bridge` peer class.** A new peer class in the federation plane ([ADR 0216](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0216-goat-net-federation-and-site-planes.md)). Lives at the commercial-cloud side, paired with a sovereign-side boundary peer over WireGuard.

- **Control plane** (low-rate) — Zenoh control + event traffic over WG: attestation requests, lineage edges, wide events, cmd/query.
- **Data plane** (variable-rate) — dedicated channel per workload class:
  - In-instance enclave-to-host: AWS Nitro vsock; GCP / Azure CVM use a unix socket bound to a dedicated network namespace.
  - Cross-instance: mTLS gRPC, the mTLS roots sealed to attestation per §2.3.
- **Federation plane participant.** The cc-bridge peer registers in the federation plane, advertises capability, and accepts policy + identity assertions from sovereign-side peers. Site-plane data does not flow over this channel — the partition is enforced at the namespace layer (only `release/cc-<csp>-<service>/...` and `import/cc-<csp>-<service>/...` topics traverse).

## 3. Reserved namespaces

| Namespace | Direction | Authorization | Audit |
|---|---|---|---|
| `release/cc-<csp>-<service>/<topic>` | sovereign → enclave | policy engine per topic + WASM conditioning | every emission |
| `import/cc-<csp>-<service>/<topic>` | enclave → sovereign | schema-enforcer + WASM conditioning at boundary | every emission |
| `attest/cc-<csp>-<service>/<build-id>` | sovereign-anchor-internal | reproducible-build pin published by release manager | append-only |
| `cmd/cc-<csp>-<service>/...` | sovereign → enclave (request-response) | policy engine + WASM conditioning | every command |

The mirror of the existing `release/<partner>/...` and `attest/queryable/<peer>` patterns is deliberate — the enclave is architecturally a partner, and treating it as one means the existing audit + lineage + policy machinery covers it for free.

## 4. Threat model

What the pattern defends against and what it does not.

**Defends against:**

- **Cloud-provider host root** seeing plaintext. The enclave boundary stops this; attestation ensures the right enclave got the data.
- **Cloud-provider hypervisor** seeing plaintext (modulo TEE side-channel risk; see below).
- **Compromised image substitution** — a tampered enclave build cannot match the reproducible-build pin, so the verifier issues no cert, so the boundary releases nothing.
- **Insider operator at the CSP** with provisioning access — same as host root.
- **Network-path interception** in commercial cloud — the WG tunnel + per-message DEK sealed to attestation prevents this.
- **Replay** — each session uses a fresh attestation cert + per-message DEK; replay across sessions is structurally infeasible.

**Does not defend against (residual risks):**

- **TEE side-channel attacks** (academic SEV-SNP / SGX exploits) — TEEs raise the bar but do not absolutize protection. Mitigations: keep enclave egress narrow, capture every crossing in lineage so post-incident forensics is tractable, monitor advisories, update reproducible-build pins on remediation.
- **CSP-controlled firmware below the TEE** — we cannot independently attest firmware below what the TEE root-of-trust covers. Mitigation: workload class scoping (synthetic data first; operational data only with separate per-class authorization).
- **Compromised reproducible-build pipeline** — if the pin itself is wrong, attestation passes garbage. Mitigations: Block 40 binary transparency log + multi-party signing of pins (Block 43 FROST).
- **WASM module bugs** — egress conditioning module can fail to redact correctly. Mitigations: [ADR 0513](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0513-wasm-conditioning-sandbox.md) module review process; for the pilot, synthetic data eliminates the risk class.
- **Managed-service-side compromise** — Bedrock / Vertex / Confluent themselves can be compromised. The enclave proxy limits exposure, but the managed-service answer is part of the trusted output. Mitigations: workload-class scoping; managed-service confidentiality features (Vertex AI Confidential Inference) that extend the TEE boundary.

## 5. Composition with existing primitives

| Primitive | Role in confidential outsourcing |
|---|---|
| [WASM conditioning sandbox](https://github.com/usareur-af/goatcore/blob/main/docs/design/wasm-conditioning-sandbox.md) ([ADR 0513](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0513-wasm-conditioning-sandbox.md)) | Egress + ingress conditioning at L1 |
| [Mission partner sharing pattern](https://github.com/usareur-af/goatcore/blob/main/docs/design/mission-partner-sharing.md) ([ADR 0821](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0821-mission-partner-sharing-pattern.md)) | The enclave IS a partner; namespace + auth pattern reused |
| [Policy engine](https://github.com/usareur-af/goatcore/blob/main/docs/design/egress-proxy.md) §6 (Block 17A.5) | Per-topic per-destination per-class authorization for boundary crossings |
| [Data dictionary](https://github.com/usareur-af/goatcore/blob/main/docs/design/data-dictionary.md) ([ADR 0512](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0512-rapid-adaptation-with-ai.md)) | Schema-enforcer at both boundary directions |
| [Lineage](https://github.com/usareur-af/goatcore/blob/main/docs/design/lineage.md) | Provenance edges across the boundary; attestation digest captured per crossing |
| [Audit-integrity](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0811-audit-log-integrity.md) | All boundary crossings audit-logged with tamper-evidence |
| [Wide events](https://github.com/usareur-af/goatcore/blob/main/docs/design/observability-wide-events.md) (Block 27) | One-query view of cross-boundary flows by `correlation_id` |
| Reproducible builds (Block 40) | Build-pin authority for attestation |
| Offline CA | Roots the attestation-cert chain |
| Federation plane ([ADR 0216](https://github.com/usareur-af/goatcore/blob/main/docs/adr/0216-goat-net-federation-and-site-planes.md)) | Where the cc-bridge peer registers; site plane stays local |
| [Vendor data services charter](../vendor-templates/data-services-provider-charter.md) | The CSP managed service is a vendor; ingestion mandate + 30-day bulk export apply |

The pattern is **net-additive on existing primitives**, not a parallel architecture. That keeps the cost of reasoning about it low.

## 6. Pilot map

Three pilot candidates, ordered:

### Pilot A — Frontier-model proxy with sealed prompt/answer (in planning)

`../project/cc-pilot-frontier-inference.md`. Synthetic prompts shaped like Scout queries, sealed to attested GCP Confidential VM running a model proxy, calls Vertex AI Confidential Inference, returns sealed answer. Proves: attestation works, encryption-to-attested-key works, sealed output through the boundary works, latency is bearable, audit + lineage complete. Value claim: a frontier model that physically won't fit on AGX Orin becomes an option for the Scout pattern.

### Pilot B — Globally-available confidential pub/sub (deferred)

Multi-cloud (GCP + AWS) confidential brokers, synthetic event stream, cross-cloud subscribers. Proves federation-plane-in-commercial-cloud. Higher complexity; depends on multi-CSP cooperation; value harder to bound. Sequenced after Pilot A produces verdict-bearing evidence.

### Pilot C — Model fine-tuning on synthetic tactical corpus (deferred)

Synthetic-tactical-corpus fine-tuning of a small open-weights model on H100/H200. Proves the heavier-weight workload class (long-running, GPU-resident, multi-stage). Sequenced after Pilot A; before Pilot B if the value calculus shifts.

Pattern adoption gate: **all three pilots produce evidence, then operational-data authorization is a separate per-workload-class decision.** Synthetic-data discipline holds across all pilots until that gate.

## 7. Open questions

- **Reproducible build for GCP Confidential VM image** — the build pipeline must produce identical-byte images for attestation pin matching. Pilot A 45B.1 work item.
- **Vertex AI Confidential Inference attestation evidence shape** — what does Google publish, can our verifier consume it directly, or does the proxy enclave bridge attestation chains? Pilot A spike.
- **Fuel + memory budget for WASM conditioning at frontier-prompt sizes** — current Block 28 limits are tuned for partner conditioning at small payloads; frontier prompts could be ~32KB-100KB. Pilot A evidence drives sizing.
- **Lineage edge density** — every crossing produces an edge; for high-rate workloads (Pilot B at scale) this could pressure the lineage store. Sizing measurement under Pilot B; potentially a sampled-lineage option for high-rate workloads.
- **Attestation cert lifetime tuning** — 1 h is a guess; Pilot A measurement informs the production value.
- **CSP-side audit ingestion** — does the wide-event stream from inside the enclave compose with the sovereign-side audit-integrity tier, or does it need its own substrate? Initial answer: rides on the existing per-site MinIO substrate via L1 boundary; verify under Pilot A load.
- **Operational-data authorization gate** — what is the structured decision shape that admits an operational workload class to cross? Likely a soak-driver + decision-review template per workload class, mirroring the Ory IdP decision review.

## 8. Anti-patterns

| Misread | Actual posture |
|---|---|
| "We're moving to the cloud." | No. The sovereign anchor is unchanged. The pattern lets specific workloads we cannot host travel to commercial cloud safely. |
| "Confidential computing is just FIPS for the cloud." | No. CC is a boundary discipline that lets us use TEEs as untrusted-host-but-trusted-workload zones. FIPS is preserved at the boundary; what runs inside the enclave is a deliberate, scoped FIPS departure. |
| "We need confidential compute everywhere now." | No. CC has cost and complexity. Apply it where the threat model genuinely demands it (cloud-provider compromise of in-use data); skip it where the threat model is solved by other means (sovereign hardware, ciphertext-only relays). |
| "If we adopt this, we're locked into [CSP]." | No. L1/L2 architecture is CSP-agnostic. The pilot CSP is a deployment choice, not an architecture commitment. |
| "Operational data can flow as soon as the pilot succeeds." | No. Pilot proves the primitives. Operational data crossing is a separate per-workload-class decision with its own evidence + review. |
| "The enclave is part of our trust boundary." | No. The enclave is a partner. It conditions inbound the same way; it depends on attestation per crossing. |
| "Attestation = security." | No. Attestation matches a build pin to a measurement. Side channels, supply-chain attacks on the build pipeline, and managed-service-side compromise all sit outside attestation's protection. The pattern is a defense-in-depth element, not the whole defense. |

## 9. Decision triggers — when to revisit this design

- Pilot A produces verdict (success / fail / fail-with-named-gaps).
- A hyperscaler ships a FIPS-validated TEE (D3 of ADR 0611 reopens).
- Cross-CSP attestation portability standardizes (D7 of ADR 0611 becomes a non-decision).
- Operational data is proposed for crossing — separate authorization required, this design adds the per-workload review template.
- A side-channel attack on the chosen TEE family produces a practical exploit.
- Block 19 boundary node FIPS PQC path lands — composition with non-FIPS-inside-enclave gets concrete.

## Change history

| Date | Change | By |
|---|---|---|
| 2026-05-02 | Initial draft — five-layer reference architecture, three decoupling invariants, reserved namespaces, threat model, pilot map (A in plan, B+C deferred), composition table, anti-patterns | engineering lead |
