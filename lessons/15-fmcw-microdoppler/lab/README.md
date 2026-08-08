# Lecture 15 lab — FMCW, Doppler & micro-Doppler

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

No new packages this week — the whole pipeline is numpy FFTs plus
`scipy.signal.stft` / `find_peaks` and `scipy.ndimage` (both already installed).

## Files

| File | What it is |
|---|---|
| `setup_check.py` | pre-class environment verification → `SETUP OK` |
| `hour3_walkthrough.py` | hour 3's live-coding cells (`# %%` format) |
| `HOMEWORK.md` | the homework: story, modules, commands |
| `ANSWERS.md` | your answer sheet — two questions answered *before* running |
| `hw15_starter.py` | the only code file you edit and submit |
| `VERIFY.md` | instructor-side verification recipe |
| `solutions/` | instructor only |

## Troubleshooting

- **`import skrf` fails with an error about `np.typing`** — you have scikit-rf 2.0.x
  installed. The course pins `scikit-rf==1.13.0` (2.0.x is incompatible with the
  course's numpy pin): `pip install scikit-rf==1.13.0`. (This week's pipeline does
  not import skrf, but `setup_check.py` verifies the course environment whole.)
- **numpy wheel errors on install** — you are on Python 3.13+. Install Python 3.12
  and recreate the venv.
- **The micro-Doppler capture is slow or eats memory** — `make_md_capture()` builds
  an 8000×512 complex cube (~65 MB) in one vectorized shot and takes ~1 s. If yours
  takes minutes, you are looping over chirps in Python — process the cube with
  whole-array FFTs (`np.fft.fft(cube, axis=...)`), never chirp-by-chirp.
- **Your recovered velocities have the wrong sign** — you fftshifted the Doppler
  axis but not the `velocity_axis_m_s` labels (or vice versa), or you conjugated
  the cube. The convention is stated once in `hw15_starter.py`'s docstring:
  receding = positive; the planted car recedes at +11.8 m/s and is your sign check.
- **Your HERM spacing reads 400 (or 600) Hz** — your estimator took a bare median
  of adjacent detected-line differences; missed weak lines make those differences
  multiples of the truth. See the module-3 hint in HOMEWORK.md.
- **Garbled symbols (α, λ, ±) in the Windows console** — run `chcp 65001` first, or
  use Windows Terminal; the scripts also reconfigure stdout to UTF-8 themselves.
- **A plot window blocks the script** — that's `--map` doing its job (close the
  window to continue). For headless runs: `set MPLBACKEND=Agg` (Windows) /
  `MPLBACKEND=Agg python ...` (macOS/Linux); figures are always also saved as PNG.
- **Smart App Control blocks numpy DLLs (Windows 11)** — this is why the course pins
  numpy 1.26.4; if you upgraded numpy, downgrade: `pip install numpy==1.26.4`.
