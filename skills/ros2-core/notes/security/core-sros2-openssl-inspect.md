---
id: core-sros2-openssl-inspect
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "Inspect and verify SROS2 key material with openssl"
domain: core
area: security
distro: humble
tested: false
audience: dev
summary: "openssl x509 / ec / smime -verify on keystore files: CA fields (sros2CA, P-256, 10 years), key match, signature check."
tags: [openssl, x509, smime, verify, sros2CA, prime256v1, P-256, ecdsa-with-SHA256, certificate expiry]
see: ["[[core-sros2-keystore]]", "[[core-sros2-governance]]", "[[core-sros2-permissions]]"]
requires: []
version_notes:
  - "humble: sros2CA is the default common name of the CA certificate, not a user (the course said 'default user') — https://github.com/ros2/sros2/blob/humble/sros2/sros2/keystore/_keystore.py (V111)"
  - "humble: CA = ECDSA P-256, SHA-256, CA:TRUE pathlen:1; valid from creation - 1 day to creation + 3650 days — https://github.com/ros2/sros2/blob/humble/sros2/sros2/_utilities.py (V119)"
  - "lyrical: validity starts at creation time (the 1-day backdate was removed) — https://docs.ros.org/en/rolling/Releases/Lyrical-Luth-Complete-Changelog.html (V119)"
  - "humble: openssl smime -verify checks the Permissions CA signature of governance.p7s and permissions.p7s — https://docs.ros.org/en/humble/Tutorials/Advanced/Security/The-Keystore.html (V117)"
---
# Inspect and verify SROS2 key material with openssl

**TL;DR** `openssl x509` shows what a certificate says, `openssl ec` shows the CA key (only on a trusted machine), and `openssl smime -verify` proves that a `.p7s` file was signed by the Permissions CA. Never paste private key bytes into notes, tickets or chats.

## CA certificate
```bash
cd ~/security_ws/turtlebot_keystore/public
openssl x509 -in ca.cert.pem -text -noout
```
Output (hex blocks shortened):
```text
Certificate:
    Data:
        Version: 3 (0x2)
        Serial Number: 25:4e:78:cd:…
        Signature Algorithm: ecdsa-with-SHA256
        Issuer: CN = sros2CA
        Validity
            Not Before: Oct 14 08:25:39 2022 GMT
            Not After : Oct 12 08:25:39 2032 GMT
        Subject: CN = sros2CA
        Subject Public Key Info:
            Public Key Algorithm: id-ecPublicKey
                Public-Key: (256 bit)
                pub: 04:c5:4a:18:9c:…
                ASN1 OID: prime256v1
                NIST CURVE: P-256
        X509v3 extensions:
            X509v3 Basic Constraints: critical
                CA:TRUE, pathlen:1
    Signature Algorithm: ecdsa-with-SHA256
```
- `sros2CA` is the default **common name** of the CA, used as both issuer and subject: a self-signed root CA.
- sros2 uses elliptic-curve keys (prime256v1, the curve DDS-Security asks for) instead of RSA.
- Validity is about ten years: from the day before creation to creation + 3650 days. Then an expired-certificate error appears and a new certificate is needed.
- An enclave's own certificate has subject `CN=<enclave path>` and issuer `CN=sros2CA`: `openssl x509 -in ../enclaves/teleop/cert.pem -noout -subject -issuer`.

## CA private key (trusted machine only)
```bash
cd ~/security_ws/turtlebot_keystore/private
cat ca.key.pem                         # -----BEGIN PRIVATE KEY----- … (PKCS#8, not encrypted)
openssl ec -in ca.key.pem -text -noout
```
```text
read EC key
Private-Key: (256 bit)
priv: <32 secret bytes, never share>
pub: 04:c5:4a:18:9c:…                  # same as the pub of ca.cert.pem
ASN1 OID: prime256v1
NIST CURVE: P-256
```
The public key printed here matches the certificate's: this is the key the certificate was made for.

## Signed files
```bash
cd ~/security_ws/turtlebot_keystore/enclaves
openssl smime -verify -in governance.p7s -CAfile ../public/permissions_ca.cert.pem
# prints the XML, then: Verification successful
cd teleop
openssl smime -verify -in permissions.p7s -CAfile permissions_ca.cert.pem
```
The check proves who signed the file (the Permissions CA) and that nobody changed it. It does not validate nodes.

## Pitfalls
- `openssl ec` and `cat` on `ca.key.pem` print the secret key: run them only where the key may live, and never copy the output.
- A verification failure after editing a `.p7s` file means the node will not start with `Enforce` ([[core-sros2-permissions]]).
- [changed in Lyrical: validity starts at creation time, no one-day backdate.]
