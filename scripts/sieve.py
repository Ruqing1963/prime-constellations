#!/usr/bin/env python3
"""
Segmented sieve for prime values of Q_k(n) = n^k - (n-1)^k.

Usage:
    python sieve.py --k 5 --N 100000000 --sieve-limit 5000000 --cores 15

Outputs:
    data/primes_k{k}.txt       — list of n where Q_k(n) is prime
    data/constellations_k{k}.txt — m-tuplets found (start_n, length)
"""

import argparse
import gmpy2
from multiprocessing import Pool
from itertools import groupby
import time
import os
import sys


def Q(k, n):
    """Compute Q_k(n) = n^k - (n-1)^k using gmpy2 for speed."""
    return gmpy2.mpz(n)**k - gmpy2.mpz(n - 1)**k


def roots_mod_p(k, p):
    """
    Find all n mod p such that Q_k(n) ≡ 0 (mod p).
    By Theorem 2.1, solutions exist iff p ≡ 1 (mod k), giving k-1 roots.
    """
    if p == k or p % k != 1:
        return []
    # Find a generator of (Z/pZ)*
    g = primitive_root(p)
    # k-th roots of unity: g^(j*(p-1)/k) for j = 1, ..., k-1
    # (j=0 gives m=1 which yields no valid n)
    order = (p - 1) // k
    roots = []
    for j in range(1, k):
        m = pow(g, j * order, p)
        # n ≡ m * (m-1)^{-1} mod p
        m_inv = pow(m - 1, p - 2, p)
        n = (m * m_inv) % p
        roots.append(n)
    return sorted(roots)


def primitive_root(p):
    """Find smallest primitive root mod p."""
    if p == 2:
        return 1
    phi = p - 1
    factors = set()
    n = phi
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.add(d)
            n //= d
        d += 1
    if n > 1:
        factors.add(n)

    for g in range(2, p):
        if all(pow(g, phi // f, p) != 1 for f in factors):
            return g
    return None


def sieve_chunk(args):
    """Sieve a chunk [lo, hi) and return indices where Q_k(n) is probably prime."""
    k, lo, hi, sieve_data = args
    size = hi - lo
    is_composite = bytearray(size)

    for p, residues in sieve_data:
        for r in residues:
            start = (-lo % p + r) % p
            for idx in range(start, size, p):
                is_composite[idx] = 1

    primes_n = []
    for i in range(size):
        if not is_composite[i]:
            n = lo + i
            if n >= 2:
                val = Q(k, n)
                if val > 1 and gmpy2.is_bpsw_prp(val):
                    primes_n.append(n)
    return primes_n


def find_constellations(prime_ns, min_length=3):
    """Find runs of consecutive n values where Q_k(n) is prime."""
    if not prime_ns:
        return []
    prime_set = set(prime_ns)
    sorted_ns = sorted(prime_ns)

    constellations = []
    run_start = sorted_ns[0]
    run_len = 1

    for i in range(1, len(sorted_ns)):
        if sorted_ns[i] == sorted_ns[i - 1] + 1:
            run_len += 1
        else:
            if run_len >= min_length:
                constellations.append((run_start, run_len))
            run_start = sorted_ns[i]
            run_len = 1

    if run_len >= min_length:
        constellations.append((run_start, run_len))

    return constellations


def main():
    parser = argparse.ArgumentParser(description="Sieve for Q_k(n) primes")
    parser.add_argument("--k", type=int, required=True, help="Prime exponent")
    parser.add_argument("--N", type=int, default=10**8, help="Search limit")
    parser.add_argument("--sieve-limit", type=int, default=5*10**6, help="Sieve prime limit B")
    parser.add_argument("--chunk-size", type=int, default=5*10**6, help="Chunk size")
    parser.add_argument("--cores", type=int, default=4, help="CPU cores")
    parser.add_argument("--output-dir", type=str, default="data", help="Output directory")
    args = parser.parse_args()

    k = args.k
    N = args.N
    B = args.sieve_limit

    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Sieving Q_{k}(n) for n ≤ {N:,}")
    print(f"Sieve limit B = {B:,}, chunk size = {args.chunk_size:,}, cores = {args.cores}")

    # Step 1: Precompute sieve data
    print("Precomputing roots for splitting primes...")
    t0 = time.time()
    sieve_data = []
    # Simple sieve for primes up to B
    is_p = bytearray(b'\x01') * (B + 1)
    is_p[0] = is_p[1] = 0
    for i in range(2, int(B**0.5) + 1):
        if is_p[i]:
            for j in range(i*i, B + 1, i):
                is_p[j] = 0

    for p in range(2, B + 1):
        if is_p[p] and p % k == 1:
            r = roots_mod_p(k, p)
            if r:
                sieve_data.append((p, r))

    print(f"  {len(sieve_data)} splitting primes, {time.time()-t0:.1f}s")

    # Step 2: Sieve in parallel chunks
    print("Sieving...")
    t0 = time.time()
    chunks = []
    for lo in range(2, N + 1, args.chunk_size):
        hi = min(lo + args.chunk_size, N + 1)
        chunks.append((k, lo, hi, sieve_data))

    all_primes = []
    with Pool(args.cores) as pool:
        for i, result in enumerate(pool.imap(sieve_chunk, chunks)):
            all_primes.extend(result)
            if (i + 1) % 10 == 0:
                elapsed = time.time() - t0
                pct = (i + 1) / len(chunks) * 100
                print(f"  {pct:.0f}% done, {len(all_primes):,} primes found, {elapsed:.0f}s")

    all_primes.sort()
    elapsed = time.time() - t0
    print(f"Found {len(all_primes):,} primes in {elapsed:.1f}s")

    # Step 3: Find constellations
    constellations = find_constellations(all_primes, min_length=3)
    print(f"Found {len(constellations)} constellations of length ≥ 3")

    # Constellation census
    from collections import Counter
    lengths = Counter(length for _, length in constellations)
    max_len = max(lengths.keys()) if lengths else 0
    print(f"Census: {dict(sorted(lengths.items()))}")
    print(f"Maximum constellation length observed: {max_len}")

    # Step 4: Save results
    primes_file = os.path.join(args.output_dir, f"primes_k{k}.txt")
    with open(primes_file, "w") as f:
        f.write(f"# Q_{k}(n) primes for n <= {N}\n")
        f.write(f"# Total: {len(all_primes)}\n")
        for n in all_primes:
            f.write(f"{n}\n")
    print(f"Saved primes to {primes_file}")

    const_file = os.path.join(args.output_dir, f"constellations_k{k}.txt")
    with open(const_file, "w") as f:
        f.write(f"# Constellations for Q_{k}(n), n <= {N}\n")
        f.write(f"# Format: start_n, length\n")
        for start, length in sorted(constellations, key=lambda x: -x[1]):
            f.write(f"{start},{length}\n")
    print(f"Saved constellations to {const_file}")


if __name__ == "__main__":
    main()
