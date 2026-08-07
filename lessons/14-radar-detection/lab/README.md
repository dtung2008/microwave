# Lecture 14 lab — The radar equation & detection

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

No new packages this week — the Monte Carlo runs on numpy, and the exact referees
(Marcum Q, Gamma thresholds) come from the scipy already installed.

## Files

| File | What it is |
|---|---|
| `setup_check.py` | pre-class environment verification → `SETUP OK` |
| `hour3_walkthrough.py` | hour 3's live-coding cells (`# %%` format) |
| `HOMEWORK.md` | the homework: story, modules, commands |
| `ANSWERS.md` | your answer sheet — two questions answered *before* running |
| `hw14_starter.py` | the only code file you edit and submit |
| `VERIFY.md` | instructor-side verification recipe |
| `solutions/` | instructor only |

## Troubleshooting

- **`import skrf` fails with an error about `np.typing`** — you have scikit-rf 2.0.x
  installed. The course pins `scikit-rf==1.13.0` (2.0.x is incompatible with the
  course's numpy pin): `pip install scikit-rf==1.13.0`. (This week's code does not
  import skrf, but `setup_check.py` verifies the course environment whole.)
- **numpy wheel errors on install** — you are on Python 3.13+. Install Python 3.12
  and recreate the venv.
- **The 10⁶-trial Monte Carlo is slow or runs out of memory** — you are probably
  drawing samples in a Python loop. Draw them as one numpy array
  (`rng.standard_normal(n)`); 10⁶ doubles is 8 MB and well under a second.
- **Your measured P_fa at design 10⁻⁶ is 0** — that is expected behavior, not a bug:
  the expected count in 10⁶ trials is 1. Q3 is about exactly this.
- **Garbled symbols (α, σ, λ) in the Windows console** — run `chcp 65001` first, or
  use Windows Terminal; the scripts also reconfigure stdout to UTF-8 themselves.
- **A plot window blocks the script** — that's `--plot` doing its job (close the
  window to continue). For headless runs: `set MPLBACKEND=Agg` (Windows) /
  `MPLBACKEND=Agg python ...` (macOS/Linux); figures are always also saved as PNG.
- **Smart App Control blocks numpy DLLs (Windows 11)** — this is why the course pins
  numpy 1.26.4; if you upgraded numpy, downgrade: `pip install numpy==1.26.4`.
