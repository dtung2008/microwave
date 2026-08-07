# Lecture 9 lab — Filters II: distributed realizations

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

No new packages this week — the whole lab runs on numpy/scipy/matplotlib/skrf.

## Files

| File | What it is |
|---|---|
| `setup_check.py` | pre-class environment verification → `SETUP OK` |
| `hour3_walkthrough.py` | hour 3's live-coding cells (`# %%` format) |
| `HOMEWORK.md` | the homework: story, modules, formula card, commands |
| `ANSWERS.md` | your answer sheet — two questions answered *before* running |
| `hw9_starter.py` | the only code file you edit and submit |
| `openems_coupled_bpf.s2p` | the instructor's full-wave case-study export (when provided) |
| `PLACEHOLDER_coupled_bpf.s2p` | generated stand-in if the export is absent — loudly labeled |
| `VERIFY.md` | instructor-side verification recipe |
| `solutions/` | instructor only |

## The case-study file

openEMS (full-wave EM) is **instructor-run only** — you never install it. The
toolkit's `load_case_study()` post-processes whatever Touchstone sits at
`openems_coupled_bpf.s2p`; if the file is absent it generates
`PLACEHOLDER_coupled_bpf.s2p` (the ideal model with a documented ε_eff
perturbation) and every printed delta is tagged `[PLACEHOLDER numbers]`. Same
code path either way — when the export lands, only the numbers change.

## Troubleshooting

- **`import skrf` fails with an error about `np.typing`** — you have scikit-rf
  2.0.x installed. The course pins `scikit-rf==1.13.0`:
  `pip install scikit-rf==1.13.0`.
- **numpy wheel errors on install** — you are on Python 3.13+. Install Python
  3.12 and recreate the venv.
- **`--check` prints hundreds of dB at 4.8 GHz** — that is the ideal
  transmission zero at 2f₀ sitting exactly on the sweep grid, not a bug
  (HOMEWORK.md, "edges that bite").
- **`coupled_dims` raises a bracketing error** — your (Z0e, Z0o) are outside
  the buildable range (Z0e must exceed Z0o; extreme coupling wants s smaller
  than the fab can etch). Check module 2's end-vs-interior J formulas first.
- **Garbled symbols (Ω, °, λ) in the Windows console** — run `chcp 65001`
  first, or use Windows Terminal; the scripts also reconfigure stdout to UTF-8.
- **A plot window blocks the script** — that's `--sweep` doing its job (close
  the window to continue). For headless runs: `set MPLBACKEND=Agg` (Windows) /
  `MPLBACKEND=Agg python ...` (macOS/Linux); figures are always saved as PNG.
- **Smart App Control blocks numpy DLLs (Windows 11)** — this is why the course
  pins numpy 1.26.4; if you upgraded numpy, downgrade:
  `pip install numpy==1.26.4`.
