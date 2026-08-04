# Performance ledger — verification runs

Source of truth for every number quoted in scripts, HOMEWORK.md, and VERIFY.md.
Numbers are measured on the reference machine (Windows 11, Python 3.12.10, repo venv),
never invented. Format inherited from `../optimizations/performance.md`.

## Environment (installed 2026-08-04)

numpy 1.26.4 (pinned) · scipy 1.13.1 · matplotlib 3.10.9 · pandas 3.0.5 ·
scikit-rf 1.13.0 (pinned — **not** 2.0.x: 2.0.0/2.0.1 crash on plain `import skrf`
under numpy 1.26.4, `np.typing.NDArray` at import time; verified on this machine,
survey.md §3.6 risk 0).

## Lecture 1 — Microwave systems panorama (verified 2026-08-04)

| Path | Command | Criterion (syllabus) | Measured | Runtime |
|---|---|---|---|---|
| env | `python setup_check.py` | prints `SETUP OK` | `SETUP OK` | 0.9 s |
| walkthrough | `python hour3_walkthrough.py` | deterministic, all cells run | full output, no errors; `ring_slot.png` written | 1.1 s |
| starter | `python hw1_starter.py --check` | unimplemented → "not implemented", exit 0 | as specified, exit 0 | 0.15 s |
| solution | `python solutions/hw1_solution.py --check` | dB engine vs watts referee ≤ 1e-6 dB | worst delta **1.42e-14 dB** | 0.13 s |
| solution | same | inverse round-trips forward to 0.1% | R_max(σ=1) = 12.98 km, SNR there **13.0000 dB** (exact) | — |
| solution | same | three-target ranges within 1% of instructor values | airliner **32.65 km** · fighter **12.98 km** · drone **4.11 km** (these ARE the instructor values) | — |
| solution | same | σ^¼ law | σ×2 → range ×**1.1892** (2^¼ = 1.1892); airliner/drone ratio **7.953** = 4000^¼ | — |
| plots | `MPLBACKEND=Agg python solutions/hw1_solution.py --plot` | writes `hw1_plots.png`, two panels | written; verticals at 4.11/12.98/32.65 km; +1/4 guide collinear with range curve (visually confirmed) | ~1 s |
| compile | `python -m py_compile` (all 4 .py) | silence | silence | — |

Numbers quoted in script/slides/HOMEWORK.md, all confirmed by the runs above:
FSPL(1 GHz, 1 km) = 92.45 dB · kT₀ = −173.98 dBm/Hz · 1 MHz floor = −113.98 dBm ·
WiFi at 50 m: −46.03 dBm / 47.93 dB (at 200 m: 35.89 dB; at 1 km: 21.91 dB) ·
σ=1 m² at 15 km: 10.49 dB · range doubling costs 12.04 dB (one-way 6.02) ·
400-km factor: 22,524× · deliberate-bug drone range: 23.09 km (×5.62).

Notes: lab is fully deterministic (no RNG), so outputs are exactly reproducible.
`hw1_plots.png` / `ring_slot.png` are regenerable and gitignored.
