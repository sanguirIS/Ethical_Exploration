#!/usr/bin/env python3
"""
Ethical Exploration - Multi-Threaded TCP Port Scanner & Service Banner Grabber
License: GNU General Public License v3.0 (GPL-3.0)
Description: High-speed multi-threaded port scanner featuring service identification,
             banner grabbing, and flexible port range specifications.
"""

import argparse
import socket
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

print_lock = threading.Lock()

TOP_PORTS = [
    20, 21, 22, 23, 25, 53, 69, 80, 110, 111, 135, 139, 143, 443, 445, 993, 995,
    1433, 1521, 2049, 3306, 3389, 5432, 5900, 6379, 8000, 8080, 8443, 8888, 9000, 27017
]


def parse_ports(port_arg):
    """Parses port string (e.g. '80,443', '1-1024', 'top', 'all') into list of integers."""
    if not port_arg or port_arg.lower() == "top":
        return TOP_PORTS
    if port_arg.lower() == "all":
        return list(range(1, 65536))

    ports = set()
    parts = port_arg.split(",")
    for part in parts:
        part = part.strip()
        if "-" in part:
            try:
                start, end = map(int, part.split("-"))
                ports.update(range(max(1, start), min(65535, end) + 1))
            except ValueError:
                continue
        elif part.isdigit():
            p = int(part)
            if 1 <= p <= 65535:
                ports.add(p)
    return sorted(list(ports))


def grab_banner(target_ip, port, timeout=1.5):
    """Attempts to grab the service banner from an open port."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((target_ip, port))
            # Send generic probe
            s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
            banner = s.recv(1024).decode("utf-8", errors="ignore").strip()
            if banner:
                first_line = banner.split("\n")[0].strip()
                return first_line[:50]
    except Exception:
        pass
    return ""


def get_service_name(port):
    """Looks up standard service name for given port."""
    try:
        return socket.getservbyport(port, "tcp")
    except (socket.error, OSError):
        common = {
            3306: "mysql", 5432: "postgresql", 6379: "redis", 27017: "mongodb",
            8080: "http-proxy", 8443: "https-alt", 3389: "ms-wbt-server",
            1433: "ms-sql-s", 1521: "oracle"
        }
        return common.get(port, "unknown")


def scan_single_port(target_ip, port, timeout=1.0, banner_grab=True):
    """Tests if a single TCP port is open."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex((target_ip, port))
            if result == 0:
                service = get_service_name(port)
                banner = grab_banner(target_ip, port, timeout) if banner_grab else ""
                with print_lock:
                    banner_str = f" | Banner: {banner}" if banner else ""
                    print(f"[+] Port {port:<6}/tcp  OPEN   Service: {service:<15}{banner_str}")
                return (port, service, banner)
    except Exception:
        pass
    return None


def port_scanner(target, ports=None, threads=50, timeout=1.0, grab_banners=True):
    """Coordinates multi-threaded TCP port scanning."""
    if ports is None:
        ports = TOP_PORTS

    print("=" * 65)
    print("  Ethical Exploration - Multi-Threaded TCP Port Scanner")
    print("=" * 65)

    try:
        target_ip = socket.gethostbyname(target)
    except socket.gaierror as e:
        print(f"[!] Error: Could not resolve hostname '{target}': {e}", file=sys.stderr)
        return []

    print(f"[*] Target Host      : {target} ({target_ip})")
    print(f"[*] Ports to scan    : {len(ports)}")
    print(f"[*] Thread count     : {threads}")
    print(f"[*] Socket timeout   : {timeout}s")
    print("-" * 65)

    start_time = time.time()
    open_ports = []

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(scan_single_port, target_ip, p, timeout, grab_banners): p for p in ports}
        for future in as_completed(futures):
            res = future.result()
            if res:
                open_ports.append(res)

    open_ports.sort(key=lambda x: x[0])
    elapsed = max(time.time() - start_time, 0.01)

    print("-" * 65)
    print(f"[*] Scan completed in {elapsed:.2f}s.")
    print(f"[*] Discovered {len(open_ports)} open port(s) on {target_ip}.")
    return open_ports


def main():
    parser = argparse.ArgumentParser(
        description="Ethical Exploration - Multi-Threaded Port Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 portScan.py -t 127.0.0.1 -p 1-1024
  python3 portScan.py -t example.com -p top --threads 100
  python3 portScan.py -t 192.168.1.1 -p 22,80,443,8080,3306
"""
    )
    parser.add_argument("-t", "--target", default="127.0.0.1", help="Target hostname or IP address")
    parser.add_argument("-p", "--ports", default="top", help="Port range: 'top', 'all', '1-1024', or '80,443,8080'")
    parser.add_argument("--threads", type=int, default=50, help="Number of concurrent worker threads (default: 50)")
    parser.add_argument("--timeout", type=float, default=1.0, help="Connection timeout in seconds (default: 1.0)")
    parser.add_argument("--no-banner", action="store_true", help="Disable service banner grabbing")

    args = parser.parse_args()
    port_list = parse_ports(args.ports)

    port_scanner(
        target=args.target,
        ports=port_list,
        threads=args.threads,
        timeout=args.timeout,
        grab_banners=not args.no_banner
    )


if __name__ == "__main__":
    main()
