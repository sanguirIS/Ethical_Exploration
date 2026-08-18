#!/usr/bin/env python3
"""
Ethical Exploration - Multi-Algorithm Hash Identifier & Cracking Engine
License: GNU General Public License v3.0 (GPL-3.0)
Description: Identifies and cracks hash digests using dictionary attacks across multiple
             cryptographic algorithms (MD5, SHA-1, SHA-224, SHA-256, SHA-384, SHA-512, NTLM).
"""

import argparse
import hashlib
import os
import sys
import time


HASH_TYPES = {
    32: ["md5", "ntlm"],
    40: ["sha1"],
    56: ["sha224"],
    64: ["sha256"],
    96: ["sha384"],
    128: ["sha512"]
}


def compute_ntlm(text):
    """Computes NTLM hash (MD4 of UTF-16LE text)."""
    try:
        return hashlib.new("md4", text.encode("utf-16le")).hexdigest()
    except ValueError:
        # If OpenSSL MD4 is disabled by security policy
        return None


def calculate_hash(algo, text, salt="", salt_pos="suffix"):
    """Calculates digest for given algorithm and optional salt."""
    if salt:
        if salt_pos == "prefix":
            full_text = f"{salt}{text}"
        else:
            full_text = f"{text}{salt}"
    else:
        full_text = text

    algo_lower = algo.lower()
    if algo_lower == "ntlm":
        return compute_ntlm(full_text)
    elif algo_lower in hashlib.algorithms_available:
        h = hashlib.new(algo_lower)
        h.update(full_text.encode("utf-8", errors="ignore"))
        return h.hexdigest()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algo}")


def identify_hash(hash_str):
    """Suggests possible hash algorithms based on hex digest length."""
    clean = hash_str.strip().lower()
    length = len(clean)
    return HASH_TYPES.get(length, [])


def crack_hash(target_hash, wordlist, algorithm=None, salt="", salt_pos="suffix"):
    """Cracks target hash using dictionary attack."""
    target_clean = target_hash.strip().lower()
    possible_algos = identify_hash(target_clean)

    if algorithm:
        algos_to_try = [algorithm.lower()]
    elif possible_algos:
        algos_to_try = possible_algos
    else:
        algos_to_try = ["md5", "sha1", "sha256", "sha512"]

    if not os.path.isfile(wordlist):
        print(f"[!] Error: Wordlist '{wordlist}' not found.", file=sys.stderr)
        return None

    print("=" * 60)
    print("  Ethical Exploration - Cryptographic Hash Cracker")
    print("=" * 60)
    print(f"[*] Target Hash      : {target_clean}")
    print(f"[*] Wordlist         : {wordlist}")
    print(f"[*] Candidate Algos  : {', '.join(algos_to_try)}")
    if salt:
        print(f"[*] Salt applied     : '{salt}' ({salt_pos})")
    print("-" * 60)

    start_time = time.time()
    total_tested = 0

    with open(wordlist, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            candidate = line.rstrip("\r\n")
            if not candidate:
                continue

            total_tested += 1

            for algo in algos_to_try:
                try:
                    digest = calculate_hash(algo, candidate, salt, salt_pos)
                    if digest and digest.lower() == target_clean:
                        elapsed = max(time.time() - start_time, 0.0001)
                        rate = int(total_tested / elapsed)
                        print("\n" + "=" * 60)
                        print(f"[+] HASH CRACKED SUCCESSFULLY!")
                        print(f"[+] Algorithm : {algo.upper()}")
                        print(f"[+] Plaintext : {candidate}")
                        print(f"[+] Speed     : {rate:,} tests/sec (Elapsed: {elapsed:.2f}s)")
                        print("=" * 60)
                        return candidate
                except Exception:
                    pass

    elapsed = max(time.time() - start_time, 0.0001)
    rate = int(total_tested / elapsed)
    print(f"\n[-] Exhausted wordlist ({total_tested:,} candidates tested at {rate:,} tests/sec).")
    print("[-] Password not found.")
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Ethical Exploration - Multi-Algorithm Hash Identifier & Cracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python3 HashCracker.py -H 5f4dcc3b5aa765d61d8327deb882cf99 -w sample_wordlists/passwords.txt
  python3 HashCracker.py -H 5baa61e4c9b93f3f0682250b6cf8331b7ee68fd8 -w sample_wordlists/passwords.txt -a sha1
  python3 HashCracker.py -H e5e9fa1ba31ecd1ae84f75caaa474f3a663f05f4 -w passwords.txt --salt "xyz" --salt-pos prefix
"""
    )
    parser.add_argument("-H", "--hash", default="5f4dcc3b5aa765d61d8327deb882cf99", help="Target hash digest to crack")
    parser.add_argument("-w", "--wordlist", default="sample_wordlists/passwords.txt", help="Path to password dictionary")
    parser.add_argument("-a", "--algo", help="Algorithm: md5, sha1, sha224, sha256, sha384, sha512, ntlm (Default: auto-detect)")
    parser.add_argument("-s", "--salt", default="", help="Salt string to apply")
    parser.add_argument("--salt-pos", choices=["prefix", "suffix"], default="suffix", help="Position of salt (default: suffix)")

    args = parser.parse_args()

    crack_hash(
        target_hash=args.hash,
        wordlist=args.wordlist,
        algorithm=args.algo,
        salt=args.salt,
        salt_pos=args.salt_pos
    )


if __name__ == "__main__":
    main()
