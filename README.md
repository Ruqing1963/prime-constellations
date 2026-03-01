# Prime Constellations of n^k − (n−1)^k

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC_BY_4.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

**Paper:** *Prime Constellations of n^k − (n−1)^k: Algebraic Obstructions, Bateman–Horn Verification, and the Non-Monotonicity of Maximum Constellation Lengths*

**Author:** Ruqing Chen, GUT Geoservice Inc., Montreal, Canada

**Repository:** [github.com/Ruqing1963/prime-constellations](https://github.com/Ruqing1963/prime-constellations)

## Summary

We study the polynomial family Q_k(n) = n^k − (n−1)^k for prime exponents k = 3, 5, 7, 11, 13. We prove that consecutive prime constellations have a sharp maximum length L(k), determined by the forbidden residue structure modulo the smallest splitting prime p₀(k), and verify this computationally through exhaustive enumeration up to n = 2×10⁹.

**Key results:**
- L(3) = 3, L(5) = 6, L(7) = 17, L(11) = 4, L(13) = 8 — all verified
- Bateman–Horn conjecture confirmed to 0.2% accuracy for polynomial degrees 4, 6, 10, 12
- L(k) is non-monotonic in k, controlled by the forbidden density ρ(k) = (k−1)/p₀(k)
- Residue-locking: all 239 quadruplets for k = 11 confined to exactly 2 of 23 residue classes

## Repository Structure

```
├── paper.tex              # LaTeX source (compile with pdflatex)
├── paper.pdf              # Compiled paper (14 pages)
├── figures/               # All 6 figures in PDF (referenced by paper.tex)
│   ├── fig1_bh_convergence.pdf
│   ├── fig2_Lk_nonmonotone.pdf
│   ├── fig3_forbidden_residues.pdf
│   ├── fig4_q11_lock.pdf
│   ├── fig5_density_decay.pdf
│   └── fig6_rho_vs_L.pdf
├── scripts/               # Computational scripts
│   ├── sieve.py           # Main sieve for Q_k(n) primes & constellations
│   ├── compute_Ck.py      # Bateman-Horn constant C(k) via Euler product
│   ├── verify_algebra.py  # Forbidden residues & L(k) verification
│   └── generate_figures.py# Regenerate all paper figures
├── data/                  # Summary data tables
│   └── results_summary.txt
├── README.md
└── .gitignore
```

## Reproducing Results

**Requirements:** Python 3.8+, gmpy2, matplotlib, numpy

```bash
pip install gmpy2 matplotlib numpy
```

**Verify algebraic results (fast, ~seconds):**
```bash
python scripts/verify_algebra.py
```

**Compute Bateman-Horn constants (fast, ~30s):**
```bash
python scripts/compute_Ck.py --P 10000000
```

**Run the full sieve (slow, ~hours per k on 15 cores):**
```bash
python scripts/sieve.py --k 5 --N 100000000 --cores 15
python scripts/sieve.py --k 7 --N 2000000000 --cores 15
```

**Regenerate figures:**
```bash
python scripts/generate_figures.py --output-dir figures
```

**Compile paper:**
```bash
pdflatex paper.tex && pdflatex paper.tex
```

## Citation

```bibtex
@article{chen2026constellations,
  author  = {Chen, Ruqing},
  title   = {Prime Constellations of $n^k - (n-1)^k$: Algebraic Obstructions,
             {Bateman--Horn} Verification, and the Non-Monotonicity of
             Maximum Constellation Lengths},
  year    = {2026},
  note    = {Preprint}
}
```

## License

This work is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
