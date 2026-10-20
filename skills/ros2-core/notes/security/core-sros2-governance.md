---
id: core-sros2-governance
type: reference
owner: equipo-ros2
updated: 2026-10-20
review_by: 2027-04-18
source: manual
confidentiality: internal
title: "governance.xml and governance.p7s: domain-wide security rules"
domain: core
area: security
distro: humble
tested: false
audience: dev
summary: "sros2 default governance (no unauthenticated participants, encrypted discovery and data), field meanings, S/MIME signature, ROS_DOMAIN_ID binding."
tags: [sros2, governance.xml, governance.p7s, S/MIME, allow_unauthenticated_participants, rtps_protection_kind, ROS_DOMAIN_ID, DDS-Security]
see: ["[[core-sros2-permissions]]", "[[core-sros2-openssl-inspect]]", "[[core-sros2-keystore]]", "[[core-env-variables]]"]
requires: []
version_notes:
  - "humble: governance.p7s is an S/MIME document (clear text + detached PKCS#7 signature) signed by the Permissions CA, not 'SMIL' as the course said — https://github.com/ros2/sros2/blob/humble/sros2/sros2/_utilities.py (V106)"
  - "humble: governance and permissions carry ROS_DOMAIN_ID at generation time (default 0); certificates have no domain — https://github.com/ros2/sros2/blob/humble/sros2/sros2/keystore/_keystore.py (V113)"
  - "humble: default governance file of sros2, unchanged up to Lyrical — https://github.com/ros2/sros2/blob/humble/sros2/sros2/policy/defaults/dds/governance.xml (V126)"
  - "jazzy: files are signed with the cryptography PKCS7 builder (OpenSSL binding as fallback); same output format — https://docs.ros.org/en/rolling/Releases/Jazzy-Jalisco-Complete-Changelog.html (V106)"
---
# governance.xml and governance.p7s: domain-wide security rules

**TL;DR** The governance document sets the security rules of the whole domain: who may join, and what is encrypted or signed. `create_keystore` writes it into `enclaves/` with the current `ROS_DOMAIN_ID`, and signs it as `governance.p7s` with the Permissions CA. Every enclave links to that signed file.

## Default governance (written by sros2)
```xml
<dds xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://www.omg.org/spec/DDS-SECURITY/20170901/omg_shared_ca_governance.xsd">
  <domain_access_rules>
    <domain_rule>
      <domains>
        <id>0</id>
      </domains>
      <allow_unauthenticated_participants>false</allow_unauthenticated_participants>
      <enable_join_access_control>true</enable_join_access_control>
      <discovery_protection_kind>ENCRYPT</discovery_protection_kind>
      <liveliness_protection_kind>ENCRYPT</liveliness_protection_kind>
      <rtps_protection_kind>SIGN</rtps_protection_kind>
      <topic_access_rules>
        <topic_rule>
          <topic_expression>*</topic_expression>
          <enable_discovery_protection>true</enable_discovery_protection>
          <enable_liveliness_protection>true</enable_liveliness_protection>
          <enable_read_access_control>true</enable_read_access_control>
          <enable_write_access_control>true</enable_write_access_control>
          <metadata_protection_kind>ENCRYPT</metadata_protection_kind>
          <data_protection_kind>ENCRYPT</data_protection_kind>
        </topic_rule>
      </topic_access_rules>
    </domain_rule>
  </domain_access_rules>
</dds>
```

## What each field means (DDS-Security, as documented by Fast DDS)
| Field | Value here | Meaning |
|---|---|---|
| `domains/id` | `0` | domain(s) the rule applies to; sros2 writes `ROS_DOMAIN_ID` (default 0) |
| `allow_unauthenticated_participants` | false | participants that cannot authenticate are not matched |
| `enable_join_access_control` | true | a remote participant's permissions are checked when it joins |
| `discovery_protection_kind` | ENCRYPT | the secure endpoint-discovery channel is encrypted (`SIGN` = MAC only, `NONE`) |
| `liveliness_protection_kind` | ENCRYPT | the secure liveliness channel is encrypted |
| `rtps_protection_kind` | SIGN | every whole RTPS message carries a MAC |
| `topic_expression` | `*` | topics this rule covers (POSIX `fnmatch`); rules are tried in order, the first match applies |
| `enable_discovery_protection` / `enable_liveliness_protection` | true | that topic's discovery and liveliness data go through the secure channels |
| `enable_read_access_control` / `enable_write_access_control` | true | creating or matching readers and writers is checked against the permissions |
| `metadata_protection_kind` / `data_protection_kind` | ENCRYPT | RTPS submessages / data payload are encrypted |

So with the default governance, an unsecured node cannot join, discovery is hidden, and every topic is access-controlled and encrypted.

## governance.p7s
`governance.p7s` is an **S/MIME** document: the same XML in clear text, followed by a detached PKCS#7 signature made with the Permissions CA key. Its shape (signature shortened):
```text
MIME-Version: 1.0
Content-Type: multipart/signed; protocol="application/x-pkcs7-signature"; micalg="sha-256"; boundary="----66A4…"
This is an S/MIME signed message
------66A4…
Content-Type: text/plain
<dds …> … </dds>                                   # governance.xml, unchanged
------66A4…
Content-Type: application/x-pkcs7-signature; name="smime.p7s"
MIIC+gYJKoZIhvcNAQcC…                              # base64 signature
------66A4…--
```
The XML alone proves nothing: the signature shows that the Permissions CA approved it. Check it with `openssl smime -verify` ([[core-sros2-openssl-inspect]]).

## Pitfalls
- Domain binding: the governance and every `permissions.xml` contain the `ROS_DOMAIN_ID` that was set when they were generated. Certificates contain no domain. Set `ROS_DOMAIN_ID` before `create_keystore`/`generate_artifacts`, or regenerate after changing it [verify: exact error with a mismatch].
- Editing `governance.xml` changes nothing at runtime: re-sign it into `governance.p7s` (Permissions CA key), or recreate the keystore.
- [changed in Jazzy: signing uses the `cryptography` PKCS7 builder; the file format is the same.]
