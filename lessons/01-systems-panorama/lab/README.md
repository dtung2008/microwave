# Lecture 1 lab — Microwave systems panorama

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

## Files

| File | What it is |
|---|---|
| `setup_check.py` | pre-class environment verification → `SETUP OK` |
| `hour3_walkthrough.py` | hour 3's live-coding cells (`# %%` format) |
| `HOMEWORK.md` | the homework: story, modules, commands |
| `ANSWERS.md` | your answer sheet — two questions answered *before* running |
| `hw1_starter.py` | the only code file you edit and submit |
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
- **Smart App Control blocks numpy DLLs (Windows 11)** — this is why the course pins
  numpy 1.26.4; if you upgraded numpy, downgrade: `pip install numpy==1.26.4`.
