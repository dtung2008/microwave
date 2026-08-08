# Lecture 16 lab — Beamforming, DOA & collision avoidance (capstone)

## Install

Same course environment as lectures 1–15 (**Python 3.12, exactly**; venv at the
repo root; `pip install -r requirements.txt`), plus this lecture's one extra —
the independent DOA referee:

```
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install pyargus
```

Then, from this directory:

```
python setup_check.py           # must print SETUP OK
```

`setup_check.py` verifies the base stack *and* that `pyargus` imports and finds a
planted 20° source — if it fails only on pyargus, the fix is the one `pip install`
above.

## Files

| File | What it is |
|---|---|
| `setup_check.py` | pre-class environment verification → `SETUP OK` |
| `hour3_walkthrough.py` | hour 3's live-coding cells (`# %%` format) |
| `HOMEWORK.md` | the homework: story, modules, commands |
| `ANSWERS.md` | your answer sheet — two questions answered *before* running |
| `hw16_starter.py` | the only code file you edit and submit |
| `VERIFY.md` | instructor-side verification recipe |
| `solutions/` | instructor only |

## Troubleshooting

- **`import pyargus` fails** — `pip install pyargus` inside the course venv.
  pyargus is pure Python (numpy/scipy/matplotlib deps only) and installs in
  seconds; it has no `__version__` attribute — that is normal, `setup_check.py`
  prints `(no __version__)`.
- **pyargus prints "ERROR: Correlation matrix is not quadratic"** — you fed it
  snapshots as (elements × snapshots); its `corr_matrix_estimate` wants
  (snapshots × elements). Transpose: `X.T`. The starter's `_pyargus_spectra`
  shows the full convention mapping (including the 90° − θ angle flip).
- **Your spectra peak at the mirror angle (−θ instead of +θ)** — a conjugation
  slip: either your steering vector uses e^(−j·k·d·n·sin θ) or your covariance is
  X.conj() @ X.T. Both conventions exist in the literature; the course fixes one
  (`steering_vector`'s docstring) so the referee comparison is meaningful.
- **`np.linalg.solve` raises `LinAlgError: Singular matrix`** — your covariance
  came from fewer snapshots than elements (K < 16) with no diagonal loading.
  In the homework proper K is always ≥ 32; if you see this you are re-living
  hour 3's deliberate bug — add loading, or more snapshots.
- **Garbled symbols (Ω, °, λ) in the Windows console** — run `chcp 65001` first,
  or use Windows Terminal; the scripts also reconfigure stdout to UTF-8.
- **A plot window blocks the script** — that's `--plot` doing its job (close the
  window to continue). For headless runs: `set MPLBACKEND=Agg` (Windows) /
  `MPLBACKEND=Agg python ...` (macOS/Linux); figures are always also saved as PNG.
