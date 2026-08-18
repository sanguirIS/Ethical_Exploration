#!/usr/bin/env python3
"""
Ethical Exploration - High-Speed Multi-Threaded Web Directory & File Bruteforcer
License: GNU General Public License v3.0 (GPL-3.0)
Description: Discovers hidden paths, directories, backups, and administrative endpoints
             using multi-threaded probing, custom wordlists, and status code filters.
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
    import urllib.error
    HAS_REQUESTS = False

print_lock = threading.Lock()


def probe_path(base_url, path, status_codes, timeout=7, headers=None):
    """Probes an individual URL path."""
    clean_url = base_url.rstrip("/") + "/" + path.lstrip("/")
    req_headers = {"User-Agent": "Mozilla/5.0 (SecurityAudit; DirectoryBruteforcer/1.0)"}
    if headers:
        req_headers.update(headers)

    try:
        if HAS_REQUESTS:
            resp = requests.get(clean_url, headers=req_headers, timeout=timeout, allow_redirects=False)
            code = resp.status_code
            length = len(resp.content)
            redirect_to = resp.headers.get("Location", "")
        else:
            req = urllib.request.Request(clean_url, headers=req_headers, method="GET")
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    code = resp.status
                    length = len(resp.read())
                    redirect_to = resp.headers.get("Location", "")
            except urllib.error.HTTPError as e:
                code = e.code
                length = len(e.read())
                redirect_to = e.headers.get("Location", "")

        if code in status_codes:
            extra = f" -> Redirect: {redirect_to}" if redirect_to else ""
            with print_lock:
                badge = f"[{code}]"
                if code == 200:
                    badge_str = f"[+] {badge}"
                elif code in (301, 302, 307, 308):
                    badge_str = f"[*] {badge}"
                elif code in (401, 403):
                    badge_str = f"[!] {badge}"
                else:
                    badge_str = f"[-] {badge}"
                print(f"{badge_str:<12} {clean_url:<50} (Size: {length} B){extra}")
            return (code, clean_url, length, redirect_to)

    except Exception:
        pass
    return None


def directory_bruteforce(url, wordlist, extensions=None, status_codes=None, threads=10, timeout=7, output_file=None):
    """Executes multi-threaded directory busting against target URL."""
    if status_codes is None:
        status_codes = [200, 204, 301, 302, 307, 401, 403]

    if not os.path.isfile(wordlist):
        print(f"[!] Error: Wordlist '{wordlist}' not found.", file=sys.stderr)
        return []

    with open(wordlist, "r", encoding="utf-8", errors="ignore") as f:
        raw_words = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    # Build queue with extensions
    targets = []
    for word in raw_words:
        targets.append(word)
        if extensions:
            for ext in extensions:
                ext_clean = ext if ext.startswith(".") else f".{ext}"
                targets.append(f"{word}{ext_clean}")

    print("=" * 65)
    print("  Ethical Exploration - Directory & File Discovery Engine")
    print("=" * 65)
    print(f"[*] Target URL      : {url}")
    print(f"[*] Wordlist        : {wordlist}")
    print(f"[*] Total Payloads  : {len(targets)}")
    print(f"[*] Extensions      : {', '.join(extensions) if extensions else 'None'}")
    print(f"[*] Status Filter   : {status_codes}")
    print(f"[*] Concurrency     : {threads} threads")
    print("-" * 65)

    discovered = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(probe_path, url, path, status_codes, timeout): path for path in targets}
        for future in as_completed(futures):
            res = future.result()
            if res:
                discovered.append(res)

    print("-" * 65)
    print(f"[*] Discovery complete. Found {len(discovered)} valid endpoints.")

    if output_file:
        with open(output_file, "w", encoding="utf-8") as out:
            out.write(f"# Directory Brute Force Results for {url}\n")
            for item in discovered:
                code, link, length, redir = item
                out.write(f"[{code}] {link} ({length} bytes) {redir}\n")
        print(f"[+] Saved results to '{output_file}'")

    return discovered


def main():
    parser = argparse.ArgumentParser(
        description="Ethical Exploration - Multi-Threaded Web Directory & File Bruteforcer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 DirectoryBruteforce.py -u https://example.com -w sample_wordlists/directories.txt
  python3 DirectoryBruteforce.py -u http://127.0.0.1:8080 -w directories.txt -e php,html,txt -t 20 -c 200,301,302
"""
    )
    parser.add_argument("-u", "--url", default="https://example.com", help="Target base URL")
    parser.add_argument("-w", "--wordlist", default="sample_wordlists/directories.txt", help="Path to directory wordlist")
    parser.add_argument("-e", "--extensions", help="Comma-separated file extensions (e.g. php,html,txt,json)")
    parser.add_argument("-c", "--codes", default="200,204,301,302,307,401,403", help="Comma-separated status codes to show")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of concurrent threads (default: 10)")
    parser.add_argument("--timeout", type=int, default=7, help="Request timeout in seconds")
    parser.add_argument("-o", "--output", help="Save discovered paths to output file")

    args = parser.parse_args()

    ext_list = [x.strip() for x in args.extensions.split(",")] if args.extensions else []
    status_list = [int(x.strip()) for x in args.codes.split(",") if x.strip().isdigit()]

    directory_bruteforce(
        url=args.url,
        wordlist=args.wordlist,
        extensions=ext_list,
        status_codes=status_list,
        threads=args.threads,
        timeout=args.timeout,
        output_file=args.output
    )


if __name__ == "__main__":
    main()
