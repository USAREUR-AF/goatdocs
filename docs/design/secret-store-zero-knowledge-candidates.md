# Zero-knowledge self-hosted secret stores: fact sheet (checked 2026-10-31)

Sources for the candidates in [secret-store-requirements.md](https://github.com/usareur-af/goatcore/blob/main/docs/design/secret-store-requirements.md) and [ADR 1212](https://github.com/usareur-af/goatcore/blob/main/docs/adr/1212-team-secrets-never-decryptable-on-the-server.md). Every fact carries the URL it was read from and the date; re-check before relying on a version number.

All sources checked 2026-10-31.

Scope note. "Zero-knowledge" here means: the server stores only ciphertext and keys wrapped under user-held secrets, and sharing re-wraps keys on the client. Every web-vault product still serves the client JavaScript from the same server, so a root attacker can alter the client; a 2026 USENIX paper demonstrates such malicious-server attacks on Bitwarden clients (https://www.usenix.org/system/files/conference/usenixsecurity26/sec26_prepub_scarlata.pdf). Only Passbolt (extension distributed via browser stores, white paper p.8) and SOPS/age (no server) avoid this.

## 1. Vaultwarden + Bitwarden CLI `bw`

- Releases: 1.37.4 (5 Oct 2026), 1.37.3 (13 Sep), 1.37.2 (22 Aug), 1.37.1 (29 Jul). Roughly monthly, security-driven. https://github.com/dani-garcia/vaultwarden/releases
- Licence AGPL-3.0. https://raw.githubusercontent.com/dani-garcia/vaultwarden/main/LICENSE.txt
- Crypto is Bitwarden's client model: PBKDF2-SHA256 600k (or Argon2id 32 MiB / 6 iterations / 4 threads) -> master key -> HKDF -> AES-256-CBC-wrapped user symmetric key; vault items AES-256-CBC + HMAC; per-user RSA pair; organisation key wrapped RSA-OAEP to each member's public key. Server stores wrapped keys, a re-hashed master-password hash, ciphertext. https://bitwarden.com/help/bitwarden-security-white-paper/ , https://bitwarden.com/help/kdf-algorithms/
- SSO/OIDC: added in 1.35.0 (27 Dec 2025). "A master password will still be required and not controlled by the SSO", so zero-knowledge holds; SSO_ONLY removes the email+password login path only. No experimental label on the wiki; Auth0 documented as broken; 1.36.0 and 1.37.3 carried SSO security fixes. https://github.com/dani-garcia/vaultwarden/releases/tag/1.35.0 , https://github.com/dani-garcia/vaultwarden/wiki/Enabling-SSO-support-using-OpenId-Connect
- FIDO2/WebAuthn as second factor: yes, needs HTTPS and DOMAIN set. Passkey passwordless login: not supported; PR #7370 "Add passwordless webauthn login" (with PRF unlock) open since 23 Jun 2026, last activity 19 Oct 2026. YubiKey OTP, Duo, email 2FA supported. https://github.com/dani-garcia/vaultwarden/wiki/Enabling-U2F-(and-FIDO2-WebAuthn)-authentication , https://github.com/dani-garcia/vaultwarden/pull/7370 , https://github.com/dani-garcia/vaultwarden/wiki
- CLI: `bw config server <url>`; non-interactive = `bw login --apikey` (BW_CLIENTID / BW_CLIENTSECRET) then `bw unlock --passwordenv BW_PASSWORD` (or `--passwordfile`) -> BW_SESSION; `bw get password|username|notes|item <id>`; `bw serve` local REST on :8087. "Your API key is not a substitute for your master password." No `op run` equivalent; an adapter would call `bw get` per reference. Latest CLI v2026.10.1 (29 Oct 2026). https://bitwarden.com/help/cli/ , https://github.com/bitwarden/clients/releases
- Secrets Manager: not supported. Maintainer, 23 Feb 2023: "No, this is a Bitwarden licensed feature, not an OpenSource Software/GPLv3 licensed feature"; 27 Feb 2024: "We would have to build everything including a front-end. That is just too much." https://github.com/dani-garcia/vaultwarden/discussions/3278
- Event logs: ORG_EVENTS_ENABLED (default false), EVENTS_DAYS_RETAIN unset = kept indefinitely. Which Bitwarden event codes Vaultwarden emits is not enumerated in the docs read. https://raw.githubusercontent.com/dani-garcia/vaultwarden/main/.env.template
- Backup: db.sqlite3 (+ -wal), attachments/, sends/, config.json (plaintext admin token, SMTP credentials), rsa_key* (JWT signing). Vault data in the backup stays "encrypted with personal and/or organization keys". https://github.com/dani-garcia/vaultwarden/wiki/Backing-up-your-vault
- Attacker with disk + root gets: ciphertext, master-password hashes (offline guessing at PBKDF2 600k), JWT signing key (forge sessions, remove 2FA via admin; wiki says this "wouldn't expose vault data"), admin token, SMTP credentials, plus the ability to serve altered web-vault JavaScript to future logins.
- FIPS: Bitwarden's KDF page says PBKDF2 at default iterations "satisfies FIPS-140 requirements". Bitwarden's validated module (cert #5507, FIPS 140-3 Level 1 software, validated 2026-08-27, DEKRA) covers Bitwarden's own server code, not Vaultwarden's Rust code. https://bitwarden.com/help/kdf-algorithms/ , https://sec-certs.org/fips/a33b9df1b504c55a/

## 2. Bitwarden official self-hosted server

- Licence: AGPLv3 for the repository, Bitwarden License for /bitwarden_license. The server runs free; only Families and Enterprise organisations can be imported to a self-hosted server; Teams cannot. Enterprise $6/user/month billed annually (12 users = about $864/yr). SSO, Key Connector and self-hosting are Enterprise; event logs Teams + Enterprise. https://github.com/bitwarden/server/blob/main/LICENSE.txt , https://bitwarden.com/help/self-host-an-organization/ , https://bitwarden.com/pricing/business/
- SSO (SAML 2.0 / OIDC) is authentication only; decryption is one of three options:
  - master password: zero-knowledge intact;
  - trusted devices: device key "never leaves the client", server stores the user key wrapped to the device public key, admin approval flow for new devices; accounts without a master password have no CLI access;
  - Key Connector: self-host only, org-held RSA key pair decrypts stored user keys, accounts become "owned by the organization", so the org's server can decrypt. Members lose master passwords; owners/admins keep theirs. CLI API-key login works for Key Connector members.
  https://bitwarden.com/help/about-sso/ , https://bitwarden.com/help/about-trusted-devices/ , https://bitwarden.com/help/about-key-connector/ , https://bitwarden.com/help/sso-decryption-options/
- Passkey login: web app and Chromium-based extensions; a PRF-capable key (YubiKey 5 + Chrome cited) unlocks the vault without the master password; master password stays on the account; unavailable with Require-SSO, trusted devices or Key Connector; self-host availability not stated. https://bitwarden.com/help/login-with-passkeys/
- FIDO2 second factor free, 5 keys (10 Premium). No smart-card / PIV login documented. https://bitwarden.com/help/setup-two-step-login-fido/
- Event logs: viewed password 1108, copied password 1111, individual export 1007, org export 1602, Secrets Manager secret accessed 2100; kept indefinitely; about 60 s client batching; Bitwarden says logs "may not be sufficient" for security or forensics. https://bitwarden.com/help/event-logs/
- Secrets Manager: access token = "an API key, containing a client id and secret" plus "a unique encryption key, which will be used to decrypt an encrypted payload" holding the org symmetric key; "the organization symmetric key is decrypted locally using the access token's unique encryption key", so the server never holds the plaintext org key. Tokens are never stored server-side; revocation blocks new logins immediately, an existing session lives up to 1 h. `bws run -- cmd` injects secrets by name, `--project-id` scopes to one project. Free tier 2 users / 3 projects / 3 machine accounts; Teams 20 and Enterprise 50 machine accounts included. https://bitwarden.com/help/secret-decryption/ , https://bitwarden.com/help/access-tokens/ , https://bitwarden.com/help/secrets-manager-cli/ , https://bitwarden.com/help/secrets-manager-plans/
- Secrets Manager self-hosting: Enterprise-only per Bitwarden staff on 16 Nov 2023, while the current plans page shows "Coming Soon: Self-host option". Ambiguous. https://community.bitwarden.com/t/now-available-enterprise-self-hosting-for-bitwarden-secrets-manager/60260 , https://bitwarden.com/help/secrets-manager-plans/
- FIPS: cert #5507 is "server-side cryptographic operations", first used in Bitwarden Government Cloud; nothing says self-hosters receive the FIPS build; client-side crypto not addressed. https://cioinfluence.com/security/bitwarden-advances-government-readiness-with-fips-140-3-validated-cryptographic-module/ , https://sec-certs.org/fips/a33b9df1b504c55a/
- Audits: SOC 2 Type 2, ISO 27001, Cure53 / ETH Zurich 2025 crypto audit. https://bitwarden.com/help/is-bitwarden-audited/

## 3. Passbolt (Community / Pro)

Primary crypto source: Security White Paper, Passbolt Pro Edition v5.10, March 2026 (rev10), https://www.passbolt.com/docs/files/security_white_paper_-_passbolt_pro_edition_v5.10_-_(march_2026_-_rev10).pdf ; page numbers below refer to it.

- Releases: API v5.17.0 (20 Oct 2026), 5.16.0 (17 Sep 2026), 5.15.0 (21 Aug 2026); monthly. https://github.com/passbolt/passbolt_api/releases
- Licence AGPLv3 for both CE and Pro. Pro EUR 4.50/user/month billed annually, minimum 10 users (about EUR 540/yr floor). Pro-only: SSO, MFA policies, activity and action logs, tags, LDAP, SCIM, account recovery (escrow). Folders are in CE. https://www.passbolt.com/pricing
- Crypto: OpenPGP (RFC 9580); default user keys curve25519 / ed25519 (historically RSA 3072); each secret encrypted once per user that needs it with a random session key, AES-256 CFB, signed by the sender (pp.16-19). Server holds ciphertext and public keys; the private key is on the server only in encrypted form, under the Organization Recovery Key, when account recovery is enabled (p.19, p.21). The server's own GPG key is passphrase-less cleartext on disk and is used for authentication challenges and to encrypt LDAP credentials (p.22). Passbolt provides no at-rest encryption of its own (p.14).
- Non-zero-knowledge default in v5: the server holds the shared metadata key and "could decrypt, inspect, or alter metadata" (names, usernames, descriptions); folders, tags and comments are plaintext; clients do not verify signatures on decrypt, "a potential vector for forgery"; a database attacker can add a user or replace a public key, join a group and wait for a share (pp.55-57).
- Authentication: GpgAuth / GpgJwtAuth challenge on the user's private key (pp.23-27). MFA: TOTP, YubiKey OTP (requires outbound to api*.yubico.com), Duo (pp.27-29); v5.17.0 adds passkeys (WebAuthn/FIDO2) as an MFA option, up to 10 per user, passwordless sign-in planned. https://github.com/passbolt/passbolt_api/releases
- SSO (Pro; OIDC/OAuth2: Entra ID, Google, Keycloak, Okta, PingOne, AD FS): the passphrase is kept in the browser extension encrypted with a non-extractable device key P1K, then wrapped with P2K, which the server stores and releases after IdP login; AES-256-GCM. Server alone cannot decrypt; an attacker needs server and browser storage. Hybrid: passphrase login still works (pp.29-32). https://www.passbolt.com/docs/admin/authentication/sso/
- Account recovery (Pro): passphrase-less copies of user private keys stored encrypted to the Organization Recovery Key (RSA 4096 recommended); admins decrypt on request; recommended to keep the ORK offline. https://www.passbolt.com/docs/admin/authentication/account-recovery/account-recovery-configuration/
- CLI go-passbolt-cli (MIT, tested against API 5.6.1+): needs private key + passphrase ("Passwordless private keys are not supported"); `passbolt exec -- cmd` resolves environment variables whose value is `passbolt://<resource-id>` into the child process only: the closest `op run` equivalent found. MFA: TOTP only. `passbolt configure` persists key and password via viper with no encryption or keyring visible in the code: plaintext inferred, not documented. https://github.com/passbolt/go-passbolt-cli , https://raw.githubusercontent.com/passbolt/go-passbolt-cli/main/internal/cmd/configure.go
- Machine identities: none documented; a machine is a user account with its own key pair.
- Audit: user action logs and syslog export are Pro (white paper p.42; pricing page).
- FIPS: no vendor statement; a CE user reported OS FIPS mode broke login and account creation. https://community.passbolt.com/t/can-passbolt-ce-run-with-fips-mode-enabled-issues-after-enabling-fips-on-an-existing-install/14011
- Backup: database (secret ciphertext; metadata plaintext in default mode) plus the server GPG key pair.
- Attacker with server root gets: all secret ciphertext, all metadata in default mode, server GPG key (impersonate server to clients), the ability to inject keys/users and wait (pp.56-57). The extension code is not served by the server (p.8).

## 4. Psono and other candidates

- Psono server CE is Apache-2.0. Crypto NaCl (Curve25519, Salsa20), client-side before upload. Enterprise-only: LDAP / SAML / OIDC and group mapping, audit logging, 2FA enforcement, disabling API keys. The feature matrix footnote says for SAML/OIDC "the server needs a way to to access the users secrets" to hand the client a substitute password, so SSO breaks zero-knowledge. 2FA: YubiKey, Duo, WebAuthn, TOTP. `COMPLIANCE_SERVER_SECRETS: 'noone'` stops server-held encrypted copies of user keys. psonoci (beta): API key id + 64-byte hex secret key, `psonoci run -- cmd` injects env variables from the secrets the key is granted; API keys bypass external authentication. Pricing page returned 404; third parties list a free Enterprise Edition Limited up to 10 users and EUR 2.00-2.50/user/month with a 25-user minimum: unconfirmed. https://gitlab.com/psono/psono-server , https://psono.com/security , https://doc.psono.com/admin/overview/supported-features.html , https://doc.psono.com/user/getting-started/features.html , https://doc.psono.com/user/psonoci/usage.html
- Infisical is server-side: "The root encryption key is a 256-bit AES key provided by the operator as an environment variable" and the server decrypts before responding. Same class as OpenBao; does not meet the property. https://infisical.com/docs/internals/security

## 5. Git + SOPS + age

- SOPS v3.13.3 (23 Jul 2026), v3.13.2 (30 Jun), v3.13.1 (16 May); MPL-2.0. Backends: age, PGP, AWS KMS, GCP KMS, Azure Key Vault, HuaweiCloud KMS, HashiCorp Vault / OpenBao transit. Values encrypted AES-256-GCM under a per-file data key; key names stay cleartext. https://github.com/getsops/sops/releases , https://getsops.io/docs/ , https://getsops.io/docs/security/
- Key groups: the data key is Shamir-split, one fragment per group, any key in a group recovers its fragment; threshold default = number of groups; set with `--shamir-secret-sharing-threshold` or `shamir_threshold` in .sops.yaml; `sops groups` edits groups. https://getsops.io/docs/usage/identities/key-groups/
- Membership change: `sops updatekeys` re-wraps the existing data key to the recipients in .sops.yaml without rotating it; `sops rotate` generates a new data key and re-encrypts every value; on removal the docs say to rotate because removed owners "had access to the data key in the past"; for a compromised key run updatekeys then rotate. Earlier git revisions remain decryptable to a removed recipient. https://getsops.io/docs/usage/key-management/
- `sops exec-env file cmd`: decrypted values go into the child process environment only, "never written to disk"; `sops exec-file` passes a FIFO by default (`--no-fifo` writes a temp file); `--user` drops privilege after decrypting. It injects the whole file, not one reference; `op run`-style per-reference injection needs a short wrapper using `sops decrypt --extract '["key"]'`. https://getsops.io/docs/usage/advanced/ , https://getsops.io/docs/usage/common-operations/
- age keys in SOPS: SOPS_AGE_KEY_FILE / SOPS_AGE_KEY / SOPS_AGE_KEY_CMD; ssh-ed25519 and ssh-rsa public keys usable as recipients (a host's SSH key can be its machine identity, read from SOPS_AGE_SSH_PRIVATE_KEY_FILE). age plugins are not mentioned on that page. https://getsops.io/docs/usage/identities/age/
- age v1.3.2 (29 Aug 2026), BSD-3-Clause. Spec primitives: X25519, HKDF-SHA-256, ChaCha20-Poly1305 in 64 KiB chunks, scrypt for passphrases; hybrid ML-KEM-768 + X25519 recipients since v1.3.0; P-256 only via hardware "tag" recipients. No FIPS statement; ChaCha20-Poly1305 is not a FIPS-approved cipher. https://github.com/FiloSottile/age/releases , https://github.com/C2SP/C2SP/blob/main/age.md
- age-plugin-yubikey v0.5.1 (8 Apr 2026): identity is a P-256 key in a PIV retired slot on YubiKey 4/5 series, PIN and touch policies; "any PIV token with an ECDSA P-256 key and certificate in one of the 20 retired slots should work", CAC not mentioned or tested. https://github.com/str4d/age-plugin-yubikey
- KMS recipients place a decrypting key with the cloud provider: defeats the property. PGP recipients keep it on the person. Audit = git history of commits; there is no read log.

## 6. Card / YubiKey sign-in and OIDC versus zero-knowledge

- YubiKey as a second factor: FIDO2 in Vaultwarden, Bitwarden, Psono; OTP in Passbolt, plus passkey MFA from Passbolt 5.17.0.
- YubiKey as the only sign-in secret: Bitwarden passkey + PRF (web app and Chromium extensions only); age-plugin-yubikey (the decryption key lives on the token).
- PIV/CAC as sign-in: none of the vault products document it; only age via a PIV P-256 slot, and a CAC would need such a key in a retired slot.
- OIDC with zero-knowledge kept: Vaultwarden (master password remains), Bitwarden with master-password or trusted-device decryption, Passbolt (two-key split, server holds P2K only).
- OIDC that trades it away: Bitwarden Key Connector (org server holds the RSA key that decrypts user keys), Psono SAML/OIDC (server must reach user secrets).

## Machine access without a human unlocking a vault

| Candidate | Documented mechanism | Key the machine holds |
|---|---|---|
| Vaultwarden | a user account; `bw login --apikey` + `bw unlock --passwordenv` | API key and the master password |
| Bitwarden | Secrets Manager machine account access token (Enterprise for self-host) | API key + wrapping key for the org symmetric key |
| Passbolt | a user account's key pair in the CLI config | OpenPGP private key + passphrase |
| Psono | API key restricted to chosen secrets; `psonoci run` | key id + secret key |
| SOPS + age | per-host age identity or ssh-ed25519 host key as recipient | X25519 (or ssh) private key |

## Comparison

| Candidate | Zero-knowledge server | Public-safe | CLI per-command injection | Machine access | Card / YubiKey sign-in | OIDC sign-in | FIPS crypto | Licence |
|---|---|---|---|---|---|---|---|---|
| Vaultwarden + bw | yes (but serves client JS) | yes, with that caveat | adapter over `bw get` | user account + API key + password | FIDO2 2FA only | yes, master password kept | PBKDF2 claim only | AGPL-3.0 |
| Bitwarden self-host | yes unless Key Connector | yes | `bws run` (Secrets Manager); adapter for `bw` | Secrets Manager machine tokens | FIDO2 2FA; passkey + PRF | yes; Key Connector breaks ZK | cert #5507, server-side, cloud | AGPL + Bitwarden Licence; $6/user/mo |
| Passbolt | secrets yes; metadata no by default | yes | `passbolt exec` with `passbolt://` refs | user key pair only | OTP; passkey MFA | yes (Pro), ZK kept | none | AGPL-3; Pro EUR 4.50/user, min 10 |
| Psono | yes, until SSO is enabled | yes | `psonoci run` | API keys | FIDO2 / OTP 2FA | Enterprise; breaks ZK | none | Apache-2.0 CE; EE paid |
| SOPS + age | no server | not applicable | `exec-env` whole file; adapter for single refs | age or ssh host key | PIV via age-plugin-yubikey | no | none (ChaCha20) | MPL-2.0 / BSD-3 |

## Ambiguities left open

- Bitwarden Secrets Manager self-hosting: 2023 statements say Enterprise-only and available; the current plans page says "Coming Soon".
- Which Bitwarden event codes Vaultwarden actually emits.
- go-passbolt-cli stores key and password in plaintext: inferred from code, not documented.
- Psono prices and the Enterprise Edition Limited cap: third-party figures only.
- Whether Bitwarden passkey login works on self-hosted servers.
