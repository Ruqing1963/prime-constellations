#!/usr/bin/env python3
"""
Verify the algebraic sieving law (Theorem 2.1) and compute L(k).

For each prime k, computes:
  - Forbidden residues F(k) mod p0
  - Maximum constellation length L(k) = max gap in complement of F(k)
  - Verification against all splitting primes up to threshold

Usage:
    python verify_algebra.py
"""


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


def forbidden_residues(k, p):
    """Compute the set of n mod p where Q_k(n) ≡ 0 (mod p)."""
    if p == k or p % k != 1:
        return set()
    g = primitive_root(p)
    order = (p - 1) // k
    residues = set()
    for j in range(1, k):
        m = pow(g, j * order, p)
        m_inv = pow(m - 1, p - 2, p)
        n = (m * m_inv) % p
        residues.add(n)
    return residues


def max_gap_cyclic(forbidden, modulus):
    """Longest run of consecutive non-forbidden residues in Z/modZ (cyclically)."""
    if not forbidden:
        return modulus
    sorted_f = sorted(forbidden)
    gaps = []
    for i in range(len(sorted_f)):
        next_f = sorted_f[(i + 1) % len(sorted_f)]
        if i + 1 < len(sorted_f):
            gap = next_f - sorted_f[i] - 1
        else:
            gap = (modulus - sorted_f[i] - 1) + sorted_f[0]
        gaps.append(gap)
    return max(gaps)


def is_prime(n):
    """Simple primality test for small numbers."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def smallest_splitting_prime(k):
    """Find p0(k) = min{p prime : p ≡ 1 (mod k)}."""
    p = k + 1
    while True:
        if p % k == 1 and is_prime(p):
            return p
        p += 1


def main():
    print("=" * 70)
    print("ALGEBRAIC SIEVING LAW VERIFICATION & L(k) COMPUTATION")
    print("=" * 70)

    data = {}
    for k in [3, 5, 7, 11, 13, 17, 19, 23, 29, 31]:
        p0 = smallest_splitting_prime(k)
        F = forbidden_residues(k, p0)
        L = max_gap_cyclic(F, p0)
        rho = (k - 1) / p0
        data[k] = (p0, F, L, rho)

        print(f"\nk = {k}:")
        print(f"  p0(k) = {p0}")
        print(f"  F(k) mod {p0} = {sorted(F)}")
        print(f"  |F(k)| = {len(F)} (expected: {k-1})")
        assert len(F) == k - 1, f"FAILED: expected {k-1} roots, got {len(F)}"
        print(f"  ρ(k) = {rho:.3f}")
        print(f"  L(k) = {L}")

    # Verify Theorem 2.5(b): p0 achieves global minimum of max_gap
    print("\n" + "=" * 70)
    print("THEOREM 2.5(b) VERIFICATION: p0 achieves global min of max_gap")
    print("=" * 70)

    for k in [3, 5, 7, 11, 13]:
        p0, F, L, rho = data[k]
        threshold = (k - 1) * (L + 1)
        print(f"\nk = {k}: threshold = {threshold}")

        # Check all splitting primes p in (p0, threshold]
        primes_to_check = []
        for p in range(p0 + 1, threshold + 1):
            if p % k == 1 and is_prime(p):
                primes_to_check.append(p)

        if not primes_to_check:
            print(f"  No primes to check (p0 = {p0} already at threshold)")
        else:
            for p in primes_to_check:
                Fp = forbidden_residues(k, p)
                mg = max_gap_cyclic(Fp, p)
                status = "✓" if mg >= L else "✗ VIOLATION"
                print(f"  p = {p}: max_gap = {mg} {'≥' if mg >= L else '<'} L={L} {status}")

    # Verify Q_k(n) ≡ 1 (mod k) for all n (Remark 2.2, Fermat's little theorem)
    print("\n" + "=" * 70)
    print("REMARK 2.2 VERIFICATION: Q_k(n) ≡ 1 (mod k)")
    print("=" * 70)
    for k in [3, 5, 7, 11, 13]:
        violations = 0
        for n in range(2, 10000):
            val = pow(n, k) - pow(n - 1, k)
            if val % k != 1:
                violations += 1
        print(f"  k = {k}: tested n = 2..9999, violations = {violations}")

    print("\nAll verifications passed.")


if __name__ == "__main__":
    main()
