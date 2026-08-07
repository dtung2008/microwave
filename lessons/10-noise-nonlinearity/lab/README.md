# Lecture 10 lab — Noise & nonlinearity

## Install (once, for the whole course)

**Python 3.12, exactly.** The course pins `numpy==1.26.4`, which has no wheels for
Python 3.13+. Check with `python --version`.

From the repo root (all OSes — Windows shown; use `python3.12` on macOS/Linux):

```
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Then, from this directory:

```
python setup_check.py           # must print SETUP OK
```

This week is pure NumPy/SciPy — scikit-rf is only pin-checked, not used. The setup
check also smoke-tests the two things the lecture lives on: Friis's cascade limit
(a 2 dB pad in front adds exactly 2 dB of NF) and the two-tone IM3 bins.

## Files

| File | What it is |
|---|---|
| `setup_check.py` | pre-class environment verification → `SETUP OK` |
| `hour3_walkthrough.py` | hour 3's live-coding cells (`# %%` format) |
| `HOMEWORK.md` | the homework: story, modules, commands |
| `ANSWERS.md` | your answer sheet — two questions answered *before* running |
| `hw10_starter.py` | the only code file you edit and submit |
| `VERIFY.md` | instructor-side verification recipe |
| `solutions/` | instructor only |

## Troubleshooting

- **`import skrf` fails with an error about `np.typing`** — you have scikit-rf 2.0.x
  installed. The course pins `scikit-rf==1.13.0` (2.0.x is incompatible with the
  course's numpy pin): `pip install scikit-rf==1.13.0`.
- **numpy wheel errors on install** — you are on Python 3.13+. Install Python 3.12
  and recreate the venv.
- **Garbled symbols (Ω, °, λ) in the Windows console** — run `chcp 65001` first, or
  use Windows Terminal; the scripts also reconfigure stdout to UTF-8 themselves.
- **A plot window blocks the script** — that's `--plot` doing its job (close the
  window to continue). For headless runs: `set MPLBACKEND=Agg` (Windows) /
  `MPLBACKEND=Agg python ...` (macOS/Linux); figures are always also saved as PNG.
- **`cascade_iip3_dbm` returns `nan` or warns about divide** — you special-cased
  the passive elements instead of letting `1/inf = 0` flow through; feed the
  ∞-dBm intercepts to `undb` and divide — NumPy does the right thing.
- **Your NF numbers are all a little wrong (0.1–1 dB)** — you are probably
  cascading in dB somewhere. Hour 3's deliberate bug is exactly this; run the
  lossy-first invariant in `--check` (must print 2.0000, not anything else).
