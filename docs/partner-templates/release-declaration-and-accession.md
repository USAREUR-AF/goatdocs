# Release Declaration and Accession — TEMPLATE

**Draft · revised 28 August 2026.** This document circulates as part of the federated data-sharing bundle; every document in that bundle carries the same revision date, so a reader holding a mixed set can tell at a glance that one of them is stale.

> **What this is.** One instrument that replaces the bilateral data-sharing agreement for unclassified data. It has two halves that are signed by different people at different times:
>
> - **Part I — the Declaration.** The data owner fills this in and publishes it. **Unilateral**: nobody negotiates it, nobody countersigns it, and it is complete the moment the owner adopts it. It says what the owner releases, who may take it, how a recipient must handle it, and how the owner takes it back.
> - **Part II — the Accession.** A recipient who wants the data fills in this half and returns it. **One act, no counter-draft.** Acceding accepts Part I exactly as published. Editing Part I is not acceding; it is asking for a different declaration, which the owner is free to write or refuse.
>
> **Acceding is an undertaking, not a receipt.** The recipient binds itself, under signature by a person mandated to give it, to every handling term in section 5 — what the data may be used for, whether it may be passed on, keeping its origin attached, protecting it in proportion to the sensitivity the owner has stated, keeping an access record, reporting an incident, and what happens on withdrawal. What this instrument removes is the *negotiation* over those terms, never the terms themselves.
>
> Part I serves every recipient that accedes to it. The tenth recipient costs what the first cost.

> **Template status.** This is the template for release under paragraph 21 of the *Framework Policy on Data Access and Release in Federated Mission Environments*, which circulates with it. To use it: take a copy, fill the placeholders, and delete this block and the one below.

> **Unclassified only.** This instrument is for data its owner has determined to be unclassified. It does not release classified information, and it is not a substitute for a Security Agreement, a Security Assurance, or any national classified-release process. Where a would-be flow is classified, this instrument does not apply and does not claim to.

> **Relationship to a bilateral data-sharing charter.** A negotiated bilateral charter remains available, and is the right instrument where a relationship genuinely needs bilateral terms — reciprocal obligations, jointly-owned data, negotiated liability. This declaration is the **default** for the ordinary case: one owner opening its own data on terms it sets. Do not sign both for the same data.

---

# PART I — DECLARATION OF RELEASE

<table class="fieldtbl">
<tr><th>Declared by</th><td>[DECLARING ORGANIZATION — legal or official name]</td></tr>
<tr><th>Declaration identifier</th><td>[SHORT STABLE ID, e.g. REL-2026-001]</td></tr>
<tr><th>Version</th><td>1.0</td></tr>
<tr><th>Adopted</th><td>[DATE]</td></tr>
<tr><th>Published at</th><td>[WHERE THIS IS PUBLISHED]</td></tr>
<tr><th>Point of contact</th><td>[ROLE OR OFFICE — a role, not a named individual]</td></tr>
</table>

## 1. What I am declaring

I, the declaring organization, own the data described in section 2 and have determined it to be **unclassified**. I release it on the terms below to any recipient that accedes under Part II. I make this declaration on my own authority. It commits no one else, and it releases no data but my own.

## 2. What is released

| Field | Value |
|---|---|
| Data assets covered | [NAME THE STREAMS / PRODUCT LINES / DATASETS. Name the asset, not every message.] |
| Producing systems | [WHICH SYSTEMS ORIGINATE THIS DATA] |
| Labels carried | fidelity: [notional / simulated / real] · context: [experiment / exercise / operational] · access: [community / organization / controlled] |
| Update rate and volume, typical | [SO A RECIPIENT CAN SIZE FOR IT] |
| Explicitly **not** released | [ANYTHING A READER MIGHT REASONABLY ASSUME IS INCLUDED AND IS NOT] |
| **Sensitivity of what is released** | [STATE IT IN ONE OR TWO SENTENCES: what harm would follow from this data reaching someone it was not released to, and what about it is sensitive — for example what it would reveal about a capability, a position, an intention, or how it was obtained. This is what handling term 4 makes the recipient protect *proportionately*, so a recipient cannot calibrate its handling without it. If the honest answer is "little or none", say that — it is a legitimate answer, and it lowers the recipient's burden accordingly.] |

## 3. Who may accede

- [ ] **Open** — any participant admitted to the environment named in section 4 may accede.
- [ ] **Conditioned** — any such participant that also meets: [STATE THE CONDITION IN ONE SENTENCE. It must be a property a recipient can demonstrate, not a category it belongs to.]

**Alliance membership, nationality, and partner status are not conditions.** If a condition here has the effect of admitting allies and excluding partners without saying why in operational terms, it is the wrong condition — rewrite it or delete it.

## 4. Where this release operates

| Field | Value |
|---|---|
| Environment | [THE FEDERATED MISSION ENVIRONMENT / BACKBONE THIS DATA IS PUBLISHED INTO] |
| Admission bar a recipient must already hold | [THE ENVIRONMENT'S OWN ADMISSION REQUIREMENTS — this declaration adds to them, never replaces them] |
| Namespace / channel the data arrives on | [WHERE A RECIPIENT SUBSCRIBES] |

## 5. Handling terms a recipient accepts

These are the whole of what a recipient agrees to. They are deliberately short. Anything not on this list is not required, and a recipient should not be asked for it.

1. **Purpose.** Use the data for [STATE THE PURPOSE], and not for [STATE ANY EXCLUDED USE, or "no excluded use"].
2. **Onward sharing.** [ ] No onward sharing. · [ ] Onward sharing permitted within the recipient's own organization only. · [ ] Onward sharing permitted to any participant that has itself acceded to this declaration. · [ ] Other: [STATE IT]
3. **Attribution.** Keep the data's origin attached to it wherever it is stored, displayed, or forwarded. Do not present it as the recipient's own observation.
4. **Protection, proportionate to the stated sensitivity.** Protect the data commensurately with the sensitivity stated in section 2 — and in any case at least as well as the recipient protects its own unclassified operational data of the same kind, and no less than the environment's admission bar requires. Where the recipient judges that the statement in section 2 understates the harm, it applies the higher standard and tells the declarant.
5. **Audit.** Keep a record of who inside the recipient's organization accessed the data, retained for at least [N] days, and produce that record to the declarant on request.
6. **Incident notification.** Tell the declarant within [N] hours of discovering that the data has been disclosed outside these terms, or that the recipient's access has been compromised.
7. **On withdrawal.** When the declarant withdraws this declaration or the recipient's accession, stop consuming the data, and [ ] delete held copies · [ ] retain held copies under these same terms · [ ] other: [STATE IT].
8. **Derived products.** Products the recipient derives from this data are the recipient's own, subject to terms 3 and 7. [ADJUST IF THIS IS NOT TRUE FOR THIS DATA.]

## 6. Duration and revocation

| Field | Value |
|---|---|
| This declaration stands until | [DATE, or "withdrawn"] |
| Accessions expire after | [PERIOD — an accession that is not renewed lapses; renewal is a decision, not a default] |
| Withdrawal of the whole declaration | The declarant may withdraw at any time, for any reason, without notice period. Withdrawal is published at the location in the header. |
| Withdrawal of a single accession | The declarant may withdraw any single recipient's accession at any time, for any reason, without affecting any other recipient. |
| How withdrawal takes effect | At the identity and key layer of the environment — the recipient's grant is revoked and, for encrypted data, the key is changed. It does not wait on a notice period or a termination clause. |

## 7. What this declaration is not

- It is **not a promise of continuity.** The declarant may change what it publishes, or stop publishing, at any time.
- It is **not a service level.** No availability, latency, or completeness is promised unless section 2 says so explicitly.
- It is **not a warranty of fitness.** The data is what it is; the labels in section 2 are the honest statement of what it is.
- It is **not reciprocal.** A recipient takes on no obligation to share anything back. A recipient that wishes to share back publishes its own declaration.
- It is **not a security agreement.** See the unclassified-only note at the top.

**Signed for the declaring organization**

<div class="sigblock">
<div class="sigfield"><span class="lbl">Name</span><span class="line"></span></div>
<div class="sigfield"><span class="lbl">Role</span><span class="line"></span></div>
<div class="sigfield"><span class="lbl">Signature</span><span class="line"></span></div>
<div class="sigfield"><span class="lbl">Date</span><span class="line"></span></div>
</div>

---

# PART II — INSTRUMENT OF ACCESSION

> Fill in, sign, return to the contact in the Part I header. Do not edit Part I. Returning this form with Part I altered is not an accession.

<table class="fieldtbl">
<tr><th>Acceding organization</th><td>[LEGAL OR OFFICIAL NAME]</td></tr>
<tr><th>Acceding to declaration</th><td>[DECLARATION IDENTIFIER], version [VERSION]</td></tr>
<tr><th>Identity in the environment</th><td>[THE ORGANIZATION'S IDENTITY / SLOT / ANCHOR IN THE ENVIRONMENT NAMED IN SECTION 4]</td></tr>
<tr><th>Point of contact</th><td>[ROLE OR OFFICE]</td></tr>
</table>

## Declaration of undertaking

The acceding organization:

1. has read the declaration identified above, in the version identified above;
2. **accepts every handling term in section 5 of that declaration as published**, without amendment, reservation, or added condition — including, specifically, the undertaking at handling term 4 to protect the data in proportion to the sensitivity the declarant has stated at section 2, and confirms it has read that statement;
3. confirms it holds the admission standing required by section 4 and meets any condition in section 3;
4. names the point of contact above as the person to whom the declarant may address a withdrawal, an incident, or an audit request;
5. understands that this accession may be withdrawn by the declarant at any time, without notice and without cause, and that withdrawal takes effect at the key rather than at the end of a notice period;
6. understands that this accession expires as stated in section 6 unless renewed, and that renewal is a fresh decision by the declarant; and
7. understands that this accession creates **no obligation on the declarant** to continue publishing, and **no obligation on the acceding organization** to share anything in return.

**Signed for the acceding organization**

<div class="sigblock">
<div class="sigfield"><span class="lbl">Name</span><span class="line"></span></div>
<div class="sigfield"><span class="lbl">Role</span><span class="line"></span></div>
<div class="sigfield"><span class="lbl">Signature</span><span class="line"></span></div>
<div class="sigfield"><span class="lbl">Date</span><span class="line"></span></div>
</div>

---

## For the declarant — recording the accession

An accession is not in force until it is recorded. Recording it means:

| Step | What happens |
|---|---|
| 1. Record | The accession is entered in the environment's register of declarations and accessions, against the declaration identifier. |
| 2. Enact | An access grant is issued to the acceding organization's identity for the assets in section 2, with the expiry from section 6 and this declaration identifier as its recorded reason. |
| 3. Confirm | The declarant tells the acceding organization the grant is live. |
| 4. Review | At expiry, the grant lapses unless the declarant renews it. Lapse is the default. |

Withdrawal reverses steps 2 and 1, in that order: revoke the grant (and change the key, for encrypted assets) first, then mark the accession withdrawn in the register.
