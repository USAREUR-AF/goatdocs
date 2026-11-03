# Why Not the Traditional Architecture

> **60-second summary:** The hub-and-spoke perimeter model fails at three points: the perimeter devices themselves are the target (ArcaneDoor, Salt Typhoon), the hub is a single point of total failure, and 13-subsystem complexity creates unauditable attack surface. Every major government network breach in two decades entered through people or supply chains, not protocol exploits. NIST, EO 14028, and the DoD Zero Trust Strategy all repudiate the model. The replacement is identity-based mesh: trust nothing, verify every peer cryptographically, assume breach.

The Maginot Line was the most sophisticated fixed fortification ever built. Germany went around it through Belgium in six weeks. The perimeter model is the Maginot Line of network security — every major breach of the last two decades came through people, supply chains, and the perimeter devices themselves. Not through the wall.

**Three problems:**

1. **The perimeter devices are themselves the vulnerability.** Cisco ASA/FTD zero-days (ArcaneDoor, Salt Typhoon) gave state actors persistent access to government firewalls. The wall was the entry point.

2. **Hub-and-spoke collapses entirely when the hub is unreachable.** Every spoke depends on the central router. goat peers talk directly and keep working when the internet is gone.

3. **Complexity creates attack surface.** A Cisco DMVPN deployment requires 13 protocol subsystems configured correctly and simultaneously. WireGuard is one protocol, six config lines, 4,000 lines of auditable source code.

---

## What the Traditional Model Gets Right

Four things, and they remain valid:

**Defense in depth.** Layered controls are sound. The problem is that the implementation collapsed into a single-vendor perimeter appliance that became the target itself.

**Cryptographic tunnel isolation.** IPSec's core guarantee — authenticated, encrypted site-to-site communication — is mathematically sound. AES-256-GCM in an IPSec tunnel works. The cipher was never the weak link.

**Deterministic routing.** OSPF and EIGRP provide convergent routing with known failure modes. In a controlled backbone, predictable traffic flow has operational value.

**Physical separation.** Air gaps work. SIPRNet and JWICS as physically separate networks is good first-principles thinking.

---

## Where It Fails

### Complexity as Attack Surface

A single Cisco DMVPN site-to-site deployment requires:

| # | Subsystem | Purpose |
|---|---|---|
| 1 | IKE Phase 1 (ISAKMP) | Key exchange negotiation |
| 2 | Pre-Shared Keys or PKI | Peer authentication |
| 3 | IPSec Transform Sets | Encryption + integrity selection |
| 4 | IPSec Profiles / Crypto Maps | Binding policy to interfaces |
| 5 | Crypto ACLs | "Interesting traffic" definition |
| 6 | GRE / mGRE Tunnels | Multipoint encapsulation |
| 7 | NHRP | Tunnel-to-physical address resolution |
| 8 | OSPF / EIGRP / BGP | Routing over tunnels |
| 9 | VRF | Traffic segmentation |
| 10 | Interface ACLs | Per-hop filtering |
| 11 | NAT | Address translation |
| 12 | Zone-Based Firewall / CBAC | Stateful inspection |
| 13 | SNMP / Syslog / NetFlow | Monitoring |

A configuration error in any layer can silently degrade security while passing connectivity tests.

A WireGuard peer:

```
[Interface]
PrivateKey = <key>
Address = 10.0.0.1/24

[Peer]
PublicKey = <key>
AllowedIPs = 10.0.0.2/32
Endpoint = 203.0.113.1:51820
```

One protocol. 4,000 lines of formally verifiable source code vs. 100,000+ lines of unauditable proprietary firmware.

### IPSec Announces Itself

WireGuard does not respond to unauthenticated packets. A WireGuard endpoint is indistinguishable from a closed port.

IPSec's IKE service (UDP 500) does the opposite:
- `ike-scan` discovers and fingerprints IKE hosts from a single probe
- IKE Aggressive Mode transmits the hashed PSK unencrypted, enabling offline brute-force
- IKEv1 Main Mode is also vulnerable to offline brute-force (CVE-2018-5389)
- Vendor ID payloads leak appliance version and build number

### The Perimeter Hardware Is the Target

| Incident | Vector | Impact |
|---|---|---|
| ArcaneDoor (2024) | Zero-days in Cisco ASA/FTD (CVE-2024-20353, CVE-2024-20359) | State-sponsored persistent backdoors in government firewalls. Survived reboots and firmware upgrades. |
| Salt Typhoon (2024) | Chinese MSS via Cisco routers at US telecoms | 9 carriers compromised. Wiretapped calls of presidential campaign staff. |
| IOS XE (2023) | Unauthenticated admin creation (CVE-2023-20198, CVSS 10.0) | 40,000-50,000 devices compromised with BadCandy implant. |
| Smart Install (2018) | Remote code execution (CVE-2018-0171) | Still actively exploited 7+ years later by Russian APT. |

CISA issued Emergency Directive ED 25-03 ordering immediate mitigation of compromised Cisco ASA and Firepower devices across federal civilian agencies.

### People Are the Attack Vector

Every major government network breach entered through human action — a credential, a USB drive, a supply chain compromise. Not a protocol exploit.

| Incident | Year | Vector |
|---|---|---|
| Operation Buckshot Yankee | 2008 | USB drive at a Middle East base. Worm crossed into SIPRNet and JWICS. |
| Manning / WikiLeaks | 2010 | Authorized SIPRNet user exfiltrated 400,000 classified documents. |
| OPM | 2015 | Stolen contractor credentials. 22.1 million records including clearance investigations. |
| SolarWinds | 2020 | Trojanized vendor update. Golden SAML bypassed MFA. 250+ federal agencies. |
| Microsoft GCC | 2023 | Chinese actors exploiting Microsoft product weakness. Commerce Secretary emails stolen. |

In every case, the perimeter was either bypassed entirely or was itself the entry point. The model maximizes blast radius by granting implicit trust to everything inside the wall.

### Lateral Movement

Subnet-based segmentation is coarse. ACLs permit classes of traffic, not individual identity-to-identity flows. Once an attacker has a valid credential, the network trusts them — because the perimeter model says everything inside the wall is trusted.

70% of breaches involve lateral movement. In Operation Buckshot Yankee, a USB worm jumped from unclassified to classified networks. In OPM, stolen contractor credentials accessed the entire personnel database. In SolarWinds, one compromised update server became a skeleton key.

---

## Armor vs. Immune System

The perimeter model is armor. It protects from the outside and fails completely when penetrated. The threat it was designed for — an external attacker probing a fortified boundary — is not the threat that actually materializes. The real threats are invisible, already inside, and constantly adapting: a compromised credential, a trojanized vendor update, a zero-day in the armor itself.

This requires an immune system, not a thicker shell. An immune system assumes hostile agents are already present. It doesn't rely on keeping them out. It identifies them at every cell, contains them locally, and adapts its response as the threat changes.

In network terms: every peer authenticates every other peer, every time. Compromise of one node doesn't grant access to another — there is no inherited trust from being "inside." Policy adapts centrally and propagates to the edge. The blast radius of any single failure is one peer, not the network.

---

## The Compliance Problem

The perimeter model survives because it is certifiable, not because it works. It maps to checkbox frameworks. You can audit a firewall rule. You can count subnets. You can point to a STIG.

ProPublica's 2025 investigation into Microsoft GCC High FedRAMP authorization:
- 480 hours and 18 technical deep-dives over years
- Internal reviewers concluded: *"There is a lack of confidence in assessing the system's overall security posture"*
- Microsoft failed to provide basic data flow diagrams
- Authorization was granted Christmas Day 2024 under pressure from DOJ's CIO, who was subsequently hired by Microsoft
- Chinese state actors had already compromised Microsoft GCC in 2023

The pattern repeats across Cisco STIGs, FedRAMP, and CMMC: define security as compliance, make compliance expensive enough to favor incumbents, never measure whether compliant systems resist attack, blame operators for "misconfiguration" when they don't.

---

## The Virtualization Layer Question

A common instinct when building hardened infrastructure is to start with a hypervisor — typically VMware ESXi — and run everything as virtual machines on top. This adds a proprietary abstraction layer underneath your entire security posture. It deserves scrutiny.

### The ESXi Path

The standard enterprise pattern: install ESXi on bare metal, manage it with vCenter/vSphere, then deploy STIG'd Ubuntu VMs running your services. This creates the following stack:

```
  Services (Netbird, Docker, applications)
  ──────────────────────────────────────
  Ubuntu 24.04 (STIG hardened, FIPS kernel)
  ──────────────────────────────────────
  VMware ESXi  ← proprietary, closed-source
  ──────────────────────────────────────
  Hardware (x86 mini PC)
```

The problems:

**The hypervisor is an unauditable trust root.** ESXi sits beneath the OS. It has full access to memory, storage, and network traffic of every VM. If ESXi is compromised, every VM is compromised — and you cannot audit the code to verify it isn't. You have STIG'd the guest OS while trusting a proprietary layer you cannot inspect underneath it.

**ESXi has its own CVE history.** VMware hypervisor escapes are not theoretical. CVE-2023-20867 (VMware Tools authentication bypass exploited by Chinese APT UNC3886), CVE-2024-37085 (ESXi Active Directory authentication bypass, CVSS 9.8, exploited by ransomware groups), and CVE-2025-22224 (VCMI heap overflow allowing guest-to-host escape, actively exploited in the wild, CISA KEV listed). A VM escape in ESXi gives an attacker the same access as physical access to the hardware.

**Licensing and vendor dependency.** ESXi requires a vSphere license for anything beyond basic evaluation. Broadcom's 2024 acquisition of VMware eliminated perpetual licenses in favor of subscription-only pricing, with reported cost increases of 3-12x. You are dependent on a vendor's pricing decisions for the foundation layer of your infrastructure. If the license lapses or the vendor changes terms, your hypervisor stops receiving patches.

**Operational overhead.** ESXi requires specialized expertise to install, configure, and maintain. vCenter adds another attack surface and another set of credentials to manage. Patching the hypervisor requires downtime or vMotion infrastructure. This is overhead that produces no mission capability — it exists only to run VMs.

**FIPS compliance gap.** You can STIG the guest Ubuntu and enable a FIPS kernel inside the VM. But the hypervisor layer handling disk I/O, network traffic, and memory management is not FIPS-validated. Data transiting ESXi's virtual switch or virtual disk controller passes through unvalidated code. The FIPS boundary has a hole in the floor.

### The Bare Metal Path (goat)

```
  Services (Netbird, Docker, applications)
  ──────────────────────────────────────
  Ubuntu 24.04 (STIG hardened, FIPS kernel)
  ──────────────────────────────────────
  Hardware (x86 mini PC)
```

One fewer layer. The OS is the trust root. LUKS encrypts the disk directly. The FIPS kernel covers all code between hardware and application. Docker provides process isolation for services without a hypervisor's overhead or attack surface. There is no proprietary layer you cannot audit between your hardened OS and the hardware.

### When Virtualization Makes Sense

Virtualization is not wrong in all cases. It is the right choice when:

- **Multi-tenancy is required** — multiple security domains on shared hardware, each needing strong isolation
- **Hardware consolidation** — running many diverse workloads on expensive server hardware where the licensing cost is marginal
- **Rapid provisioning matters more than depth** — dev/test environments, lab infrastructure

For a tactical edge node running a single-purpose workload (mesh networking), virtualization adds cost, complexity, attack surface, and a proprietary dependency — with no corresponding benefit. The network host runs one thing. It doesn't need a hypervisor.

### Alternatives If You Need Isolation

If you do need VM-level isolation on a tactical node without a proprietary hypervisor:

| Option | Type | Auditable | FIPS path | Trade-off |
|---|---|---|---|---|
| **KVM/QEMU** | Type-1 (Linux kernel) | Yes (GPL) | Yes (kernel FIPS module covers it) | Requires Linux expertise |
| **Proxmox VE** | KVM + management UI | Yes (AGPL) | Yes (Debian FIPS kernel) | Heavier than bare metal, lighter than vSphere |
| **Firecracker** | MicroVM (KVM-based) | Yes (Apache 2.0) | Yes (host kernel FIPS) | Minimal overhead, designed for single-purpose VMs |
| **Docker/Podman** | Container isolation | Yes (Apache 2.0) | Yes (host kernel FIPS) | Not VM-level isolation, but sufficient for single-trust-domain |

KVM is part of the Linux kernel. If you FIPS the kernel, the hypervisor is FIPS'd. There is no separate proprietary layer to validate, license, or trust.

---

## What NIST Already Says

The government's own standards body has repudiated the perimeter model:

**NIST SP 800-207:** *"Perimeter-based network security has been shown to be insufficient since once attackers breach the perimeter, further lateral movement is unhindered."*

**Executive Order 14028 (2021):** *"Agencies can no longer trust a user or device simply because they are 'inside' the network."*

**DoD Zero Trust Strategy:** *"The DoD requires an enhanced cybersecurity framework built upon Zero Trust principles that must be adopted across the Department, enterprise-wide, as quickly as possible."*

The doctrine exists. The policy is signed. Procurement continues flowing to the same perimeter vendors.

---

## The Inversion

| | Traditional Model | goat |
|---|---|---|
| **Primary threat** | External attacker at the perimeter | Insider, credential theft, supply chain |
| **Trust boundary** | Network perimeter | None — assume breach |
| **Identity** | IP address + subnet | Cryptographic key per device |
| **Segmentation** | Subnets and VLANs (coarse, static) | Per-flow policy on identity (fine, dynamic) |
| **Blast radius** | Everything inside the wall | Single compromised peer |
| **Hub failure** | Total collapse | Peers keep talking |
| **Visibility** | Firewall logs at chokepoints | Every peer interaction authenticated and logged |
| **Vendor posture** | Proprietary, certified | Open, auditable, verifiable |

The castle was never the right metaphor. The network is a city. You don't protect a city with a wall. You protect it with locks on every door and IDs checked at every threshold — and you assume someone is already inside.
