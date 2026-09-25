# Security Policy

This repository is a multi-language playground of security and automation scripts (Python, C#, Batch, Shell, JavaScript, PHP). This policy covers the code in this repository and how to report problems with it responsibly.

## Supported Versions

The project has no release versioning — it is a single-branch collection of standalone scripts. Security fixes are applied to the `main` branch only.

| Target             | Supported          |
| ------------------ | ------------------ |
| `main` (latest)    | :white_check_mark: |
| Historical commits | :x:                |

## Reporting a Vulnerability

If you find a vulnerability in this codebase — for example in a scanner, credential-handling routine, or any script that mishandles user input or network responses — please report it responsibly.

**How to report:**

1. **Preferred:** open a [Private Vulnerability Report](https://github.com/sanguirIS/Ethical_Exploration/security/advisories/new) via the Security tab, so details stay out of public issues until a fix exists.
2. **Alternatively:** open a regular issue labeled `security`. Describe the problem, but do **not** include proof-of-concept output captured from live systems.

**What to include:**

- Affected file(s) and the relevant code path
- Steps to reproduce against a local or lab target you control
- Expected vs. actual behavior
- A proposed fix (optional, but appreciated)

**What to expect:**

- An acknowledgement within 3 business days.
- A fix, or a written explanation of why the report is out of scope, within 30 days.
- Credit in the fix notes, unless you prefer to remain anonymous.

## Out of Scope

- Vulnerabilities in third-party tools or dependencies (e.g. Nmap, curl) — report those to the upstream project.
- Issues caused by running these tools against systems you do not own or lack written permission to test.
- Social engineering of the maintainer, or exposure of information that is already public.

## Intended Use Reminder

All tools in this repository are intended for **educational purposes and authorized security testing only** — systems you own, or systems you have explicit written permission to assess. Using them against anything else is illegal in most jurisdictions and contrary to the spirit of this project.
