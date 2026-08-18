#!/usr/bin/env python3
"""
Ethical Exploration - High-Speed Subdomain Enumeration & Reconnaissance Tool
License: GNU General Public License v3.0 (GPL-3.0)
Description: Performs multi-threaded DNS resolution and HTTP/HTTPS probing to discover
             valid subdomains, IP bindings, and active web services across a target domain.
"""

import argparse
import os
import random
import socket
import string
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


def check_wildcard_dns(domain):
    """Detects if the target domain uses a wildcard DNS catch-all record."""
    random_sub = "".join(random.choices(string.ascii_lowercase + string.digits, k=16))
    test_host = f"{random_sub}.{domain}"
    try:
        ip = socket.gethostbyname(test_host)
        return ip
    except (socket.gaierror, socket.herror):
        return None


def probe_http(hostname, port=80, timeout=3):
    """Probes HTTP service on target hostname."""
    scheme = "https" if port == 443 else "http"
    url = f"{scheme}://{hostname}:{port}" if port not in (80, 443) else f"{scheme}://{hostname}"

    if HAS_REQUESTS:
        try:
            resp = requests.get(url, timeout=timeout, allow_redirects=True, headers={"User-Agent": "Mozilla/5.0 (Recon/1.0)"})
            return resp.status_code, resp.headers.get("Server", "")
        except Exception:
            return None, None
    else:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Recon/1.0)"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, resp.headers.get("Server", "")
        except urllib.error.HTTPError as e:
            return e.code, e.headers.get("Server", "")
        except Exception:
            return None, None


def resolve_subdomain(subdomain, domain, wildcard_ip=None, probe_web=True, timeout=3):
    """Resolves DNS and probes web server on discovered host."""
    full_host = f"{subdomain.strip().lower()}.{domain.strip().lower()}"
    try:
        ip = socket.gethostbyname(full_host)
        if wildcard_ip and ip == wildcard_ip:
            return None  # Ignore wildcard false positive

        http_info = ""
        if probe_web:
            status, server = probe_http(full_host, 80, timeout)
            if status is None:
                status, server = probe_http(full_host, 443, timeout)
            if status:
                http_info = f" [HTTP: {status}{f', Server: {server}' if server else ''}]"

        with print_lock:
            print(f"[+] Discovered: {full_host:<35} -> {ip:<16}{http_info}")

        return (full_host, ip, http_info)

    except (socket.gaierror, socket.herror):
        return None
    except Exception:
        return None


def find_subdomains(domain, wordlist, threads=15, probe_web=True, timeout=3, output_file=None):
    """Coordinates multi-threaded subdomain discovery."""
    if not os.path.isfile(wordlist):
        print(f"[!] Error: Wordlist '{wordlist}' not found.", file=sys.stderr)
        return []

    with open(wordlist, "r", encoding="utf-8", errors="ignore") as f:
        subdomains = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    print("=" * 65)
    print("  Ethical Exploration - Subdomain Enumeration Engine")
    print("=" * 65)
    print(f"[*] Target Domain    : {domain}")
    print(f"[*] Wordlist         : {wordlist} ({len(subdomains)} entries)")
    print(f"[*] Threads          : {threads}")
    print(f"[*] Web Probing      : {'Enabled' if probe_web else 'Disabled'}")

    wildcard_ip = check_wildcard_dns(domain)
    if wildcard_ip:
        print(f"[!] Wildcard DNS detected pointing to: {wildcard_ip}")
    print("-" * 65)

    results = []
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [
            executor.submit(resolve_subdomain, sub, domain, wildcard_ip, probe_web, timeout)
            for sub in subdomains
        ]
        for future in as_completed(futures):
            res = future.result()
            if res:
                results.append(res)

    print("-" * 65)
    print(f"[*] Reconnaissance complete. Discovered {len(results)} active subdomain(s).")

    if output_file:
        with open(output_file, "w", encoding="utf-8") as out:
            out.write(f"# Subdomains found for {domain}\n")
            for host, ip, extra in results:
                out.write(f"{host}\t{ip}\t{extra.strip()}\n")
        print(f"[+] Output written to '{output_file}'")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Ethical Exploration - Subdomain Enumerator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 SubdomainFinder.py -d example.com -w sample_wordlists/subdomains.txt
  python3 SubdomainFinder.py -d target.org -w subdomains.txt -t 30 --no-probe -o found_subs.txt
"""
    )
    parser.add_argument("-d", "--domain", default="example.com", help="Target domain (e.g. example.com)")
    parser.add_argument("-w", "--wordlist", default="sample_wordlists/subdomains.txt", help="Path to subdomain wordlist")
    parser.add_argument("-t", "--threads", type=int, default=15, help="Number of worker threads (default: 15)")
    parser.add_argument("--no-probe", action="store_true", help="Skip HTTP/HTTPS banner probing")
    parser.add_argument("--timeout", type=int, default=3, help="Probe timeout in seconds")
    parser.add_argument("-o", "--output", help="Save discovered subdomains to file")

    args = parser.parse_args()

    find_subdomains(
        domain=args.domain,
        wordlist=args.wordlist,
        threads=args.threads,
        probe_web=not args.no_probe,
        timeout=args.timeout,
        output_file=args.output
    )


if __name__ == "__main__":
    main()
