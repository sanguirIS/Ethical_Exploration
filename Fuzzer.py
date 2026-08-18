#!/usr/bin/env python3
"""
Ethical Exploration - Web Application Parameter & Endpoint Fuzzer
License: GNU General Public License v3.0 (GPL-3.0)
Description: High-performance fuzzing tool that injects test vectors into URL query parameters,
             request bodies, headers, and paths using the 'FUZZ' keyword placeholder.
"""

import argparse
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    import urllib.request
    import urllib.error
    HAS_REQUESTS = False

print_lock = threading.Lock()

DEFAULT_PAYLOADS = [
    "admin", "test", "user", "guest", "root", "dev", "staging",
    "../etc/passwd", "..\\..\\windows\\win.ini",
    "' OR 1=1--", "<script>alert(1)</script>", "${7*7}", "{{7*7}}",
    "null", "undefined", "true", "false", "-1", "0", "99999999"
]


def execute_fuzz_test(url_template, payload, method="GET", post_template=None, headers=None,
                       filter_codes=None, timeout=7):
    """Executes a single fuzz test replacing 'FUZZ' keyword."""
    target_url = url_template.replace("FUZZ", payload) if "FUZZ" in url_template else f"{url_template}{payload}"
    post_data = None
    if post_template and "FUZZ" in post_template:
        post_data = post_template.replace("FUZZ", payload)
    elif post_template:
        post_data = post_template

    req_headers = {"User-Agent": "Mozilla/5.0 (SecurityAudit; Fuzzer/1.0)"}
    if headers:
        for k, v in headers.items():
            req_headers[k] = v.replace("FUZZ", payload) if "FUZZ" in v else v

    start_time = time.time()
    try:
        if HAS_REQUESTS:
            if method.upper() == "POST":
                resp = requests.post(target_url, data=post_data, headers=req_headers, timeout=timeout, allow_redirects=False)
            else:
                resp = requests.get(target_url, headers=req_headers, timeout=timeout, allow_redirects=False)
            duration = round((time.time() - start_time) * 1000, 2)
            code = resp.status_code
            length = len(resp.content)
            word_count = len(resp.text.split())
        else:
            data_bytes = post_data.encode("utf-8") if post_data else None
            req = urllib.request.Request(target_url, data=data_bytes, headers=req_headers, method=method.upper())
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    duration = round((time.time() - start_time) * 1000, 2)
                    code = resp.status
                    content = resp.read()
                    length = len(content)
                    word_count = len(content.decode("utf-8", errors="ignore").split())
            except urllib.error.HTTPError as e:
                duration = round((time.time() - start_time) * 1000, 2)
                code = e.code
                content = e.read()
                length = len(content)
                word_count = len(content.decode("utf-8", errors="ignore").split())

        if filter_codes is None or code in filter_codes:
            with print_lock:
                badge = f"[{code}]"
                if code in (200, 201):
                    badge_str = f"[+] {badge}"
                elif code in (301, 302, 307):
                    badge_str = f"[*] {badge}"
                elif code in (500, 502, 503):
                    badge_str = f"[!] {badge}"
                else:
                    badge_str = f"[-] {badge}"
                print(f"{badge_str:<12} Payload: {payload:<25} Size: {length:<8} Words: {word_count:<6} Time: {duration}ms")
            return (code, payload, length, word_count, duration)

    except Exception:
        pass
    return None


def run_fuzzer(url, wordlist=None, payloads=None, method="GET", post_data=None,
               filter_codes=None, threads=10, timeout=7, output_file=None):
    """Coordinates fuzzing execution."""
    test_payloads = []
    if wordlist and os.path.isfile(wordlist):
        with open(wordlist, "r", encoding="utf-8", errors="ignore") as f:
            test_payloads = [line.strip() for line in f if line.strip()]
    elif payloads:
        test_payloads = payloads
    else:
        test_payloads = DEFAULT_PAYLOADS

    print("=" * 65)
    print("  Ethical Exploration - Web Application Fuzzer")
    print("=" * 65)
    print(f"[*] Target Template : {url}")
    print(f"[*] HTTP Method     : {method.upper()}")
    print(f"[*] Total Payloads  : {len(test_payloads)}")
    print(f"[*] Concurrency     : {threads} threads")
    print(f"[*] Filter Codes    : {filter_codes if filter_codes else 'All'}")
    print("-" * 65)

    results = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(execute_fuzz_test, url, p, method, post_data, None, filter_codes, timeout): p
            for p in test_payloads
        }
        for future in as_completed(futures):
            res = future.result()
            if res:
                results.append(res)

    print("-" * 65)
    print(f"[*] Fuzzing completed. Collected {len(results)} matching responses.")

    if output_file:
        with open(output_file, "w", encoding="utf-8") as out:
            out.write(f"# Fuzzing results for {url}\n")
            out.write("Status\tPayload\tLength\tWords\tDuration(ms)\n")
            for item in results:
                out.write(f"{item[0]}\t{item[1]}\t{item[2]}\t{item[3]}\t{item[4]}\n")
        print(f"[+] Output written to '{output_file}'")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Ethical Exploration - Web Application Fuzzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 Fuzzer.py -u "https://example.com/item?id=FUZZ" -w sample_wordlists/directories.txt
  python3 Fuzzer.py -u "https://example.com/api/FUZZ" -c 200,301,302 -t 15
  python3 Fuzzer.py -u "https://example.com/search" -m POST -d "q=FUZZ"
"""
    )
    parser.add_argument("-u", "--url", default="https://example.com/FUZZ", help="Target URL with FUZZ keyword")
    parser.add_argument("-w", "--wordlist", help="Path to custom payload wordlist")
    parser.add_argument("-m", "--method", default="GET", choices=["GET", "POST"], help="HTTP Method")
    parser.add_argument("-d", "--data", help="POST body template with FUZZ keyword")
    parser.add_argument("-c", "--codes", help="Filter by comma-separated status codes (e.g. 200,302)")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of threads (default: 10)")
    parser.add_argument("--timeout", type=int, default=7, help="Request timeout in seconds")
    parser.add_argument("-o", "--output", help="Save results to specified file")

    args = parser.parse_args()

    filter_codes = [int(c.strip()) for c in args.codes.split(",") if c.strip().isdigit()] if args.codes else None

    run_fuzzer(
        url=args.url,
        wordlist=args.wordlist,
        method=args.method,
        post_data=args.data,
        filter_codes=filter_codes,
        threads=args.threads,
        timeout=args.timeout,
        output_file=args.output
    )


if __name__ == "__main__":
    main()
