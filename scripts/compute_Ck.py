#!/usr/bin/env python3
"""
Compute the Bateman-Horn constant C(k) for Q_k(n) = n^k - (n-1)^k.

The Euler product is:
    C(k) = ∏_p (1 - ω(p)/p) / (1 - 1/p)

where ω(p) = k-1 if p ≡ 1 (mod k), and 0 otherwise (for p ≠ k).

Usage:
    python compute_Ck.py --P 10000000

Outputs convergence table and final C(k) values for k = 3, 5, 7, 11, 13.
"""

import argparse
import math


def simple_sieve(limit):
    """Sieve of Eratosthenes returning list of primes up to limit."""
    is_prime = bytearray(b'\x01') * (limit + 1)
    is_prime[0] = is_prime[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = 0
    return [i for i in range(2, limit + 1) if is_prime[i]]


def compute_Ck(k, primes, checkpoints=None):
    """
    Compute C(k) via Euler product over given primes.
    Returns dict of {checkpoint: C(k) value} if checkpoints given.
    """
    product = 1.0
    results = {}
    ci = 0

    for p in primes:
        if p == k:
            w = 0
        elif p % k == 1:
            w = k - 1
        else:
            w = 0

        numer = 1.0 - w / p
        denom = 1.0 - 1.0 / p
        product *= numer / denom

        if checkpoints and ci < len(checkpoints) and p >= checkpoints[ci]:
            results[checkpoints[ci]] = product
            ci += 1

    results[primes[-1]] = product
    return results


def main():
    parser = argparse.ArgumentParser(description="Compute Bateman-Horn C(k)")
    parser.add_argument("--P", type=int, default=10**7,
                        help="Maximum prime for Euler product (default: 10^7)")
    args = parser.parse_args()

    print(f"Sieving primes up to {args.P:,}...")
    primes = simple_sieve(args.P)
    print(f"Found {len(primes):,} primes.\n")

    checkpoints = [10**e for e in range(3, 8) if 10**e <= args.P]

    for k in [3, 5, 7, 11, 13]:
        results = compute_Ck(k, primes, checkpoints)

        c_final = results[primes[-1]]
        print(f"k = {k}:  C(k) = {c_final:.6f}")
        print(f"  {'P_max':>12}  {'C(k)':>10}  {'Δ from final':>14}")
        print(f"  {'-'*40}")

        for pmax in sorted(results.keys()):
            delta = (results[pmax] - c_final) / c_final * 100
            print(f"  {pmax:>12,}  {results[pmax]:>10.6f}  {delta:>+13.4f}%")
        print()

    # Print final table for paper
    print("=" * 50)
    print("FINAL VALUES FOR PAPER (Table 4)")
    print("=" * 50)
    for k in [5, 7, 11, 13]:
        results = compute_Ck(k, primes)
        c = results[primes[-1]]
        print(f"  k = {k:>2}:  C(k) = {c:.3f}")


if __name__ == "__main__":
    main()
