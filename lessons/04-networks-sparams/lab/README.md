# Lecture 4 lab — Microwave network theory: S-parameters

## Install (once, for the whole course)

Same environment as lecture 1 — nothing new this week. If you already have the
course venv, just verify it:

```
python setup_check.py           # must print SETUP OK
```

Fresh machine? **Python 3.12, exactly** (the course pins `numpy==1.26.4`, which has
no wheels for Python 3.13+). From the repo root (Windows shown; use `python3.12` and
`source .venv/bin/activate` on macOS/Linux):

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Files

| File | What it is |
|---|---|
| `setup_check.py` | pre-class environment verification → `SETUP OK` |
| `hour3_walkthrough.py` | hour 3's live-coding cells (`# %%` format) |
| `HOMEWORK.md` | the homework: story, modules, commands |
| `ANSWERS.md` | your answer sheet — two questions answered *before* running |
| `hw4_starter.py` | the only code file you edit and submit |
| `VERIFY.md` | instructor-side verification recipe |
| `solutions/` | instructor only |

No downloads this week: the three "measured" networks are planted by the toolkit,
deterministically (seeded), so everyone's `--check` sees identical data.

## Troubleshooting

- **`import skrf` fails with an error about `np.typing`** — you have scikit-rf 2.0.x
  installed. The course pins `scikit-rf==1.13.0` (2.0.x is incompatible with the
  course's numpy pin): `pip install scikit-rf==1.13.0`.
- **`from skrf.network import s2a` fails** — same cause as above, or a very old
  scikit-rf; `s2a`/`a2s`/`s2z`/`z2s` are verified present in the pinned 1.13.0.
- **numpy wheel errors on install** — you are on Python 3.13+. Install Python 3.12
  and recreate the venv.
- **Garbled symbols (Ω, λ, σ) in the Windows console** — run `chcp 65001` first, or
  use Windows Terminal; the scripts also reconfigure stdout to UTF-8 themselves.
- **A plot window blocks the script** — that's `--plot` doing its job (close the
  window to continue). For headless runs: `set MPLBACKEND=Agg` (Windows) /
  `MPLBACKEND=Agg python ...` (macOS/Linux); figures are always also saved as PNG.
- **Your residuals differ from HOMEWORK.md's in the last digit or two** — fine:
  BLAS libraries differ across OSes at the 1e-15 level. If a residual differs in the
  first digit, that's you, not the BLAS.
- **`LinAlgError: Singular matrix` from `s_to_z`** — you are inverting (I − S) for a
  network with S ≈ I (an open circuit at both ports). None of the planted networks
  do this; check that you built the matrix per frequency, not summed over frequency.
