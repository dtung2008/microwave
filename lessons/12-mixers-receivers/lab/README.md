# Lecture 12 lab — Mixers, detectors & receiver architectures

## Install

Same course environment as lecture 1 (**Python 3.12, exactly**; numpy 1.26.4,
scipy, matplotlib, scikit-rf 1.13.0). If you have been following the course, there
is nothing new to install. Fresh machine — from the repo root (Windows shown; use
`python3.12` on macOS/Linux):

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
| `hw12_starter.py` | the only code file you edit and submit |
| `VERIFY.md` | instructor-side verification recipe |
| `solutions/` | instructor only |

## Troubleshooting

- **Everything is deterministic** — `--check`, the walkthrough, and the plots use
  fixed seeds. If your numbers differ from HOMEWORK.md's measured values *after*
  you implement a module, the difference is signal, not noise.
- **Module 3 feels slow** — the Doppler scene is 64 s of samples at 4096 Hz
  (262 144 points) so the Welch-averaged skirt is smooth; the whole `--check` runs
  in a few seconds. If it takes minutes, you are probably re-synthesizing the
  scene inside a loop — call `doppler_psd()` once.
- **Garbled symbols (Ω, °, λ) in the Windows console** — run `chcp 65001` first,
  or use Windows Terminal; the scripts also reconfigure stdout to UTF-8.
- **A plot window blocks the script** — that's `--plot` doing its job (close the
  window to continue). For headless runs: `set MPLBACKEND=Agg` (Windows) /
  `MPLBACKEND=Agg python ...` (macOS/Linux); figures are always also saved as PNG.
- **`import skrf` fails with an error about `np.typing`** — you have scikit-rf
  2.0.x; the course pins `scikit-rf==1.13.0`: `pip install scikit-rf==1.13.0`.
  (This lab only uses skrf in `setup_check.py`, but keep the course env intact.)
