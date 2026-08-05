# Lecture 3 lab — The Smith chart & impedance matching

## Install

Nothing new: the course environment from lecture 1 covers everything
(**Python 3.12 exactly**, `numpy==1.26.4`, scipy, matplotlib,
`scikit-rf==1.13.0`). If you skipped lecture 1's setup, do it now from the
repo root:

```
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Optional extra for this lecture (standalone Smith-chart axes for your own
projects; the course draws its charts with scikit-rf either way):

```
pip install pysmithchart
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
| `hw3_starter.py` | the only code file you edit and submit |
| `VERIFY.md` | instructor-side verification recipe |
| `solutions/` | instructor only |

## Troubleshooting

- **`--check` says an edge is `edge-limited` / your module returns `None`** —
  not a bug: the unmatched antenna already sits at 10.90 dB return loss, so
  some matched sweeps never cross the 10-dB threshold inside the window.
  Q5 in ANSWERS.md is about exactly this.
- **Your |Γ(f₀)| is ~1e-5 instead of ~1e-16** — you rounded a design value
  before handing it to the referee. Keep full-precision floats end-to-end;
  round only in what you *print*.
- **Your stub "solution" makes the match worse** — you are probably standing
  on the impedance chart while attaching a shunt element. Re-run hour 3's
  cell 3.7 (`hour3_bug.png`) and compare your intermediate point against the
  g = 1 circle in `--smith`.
- **A negative line/stub length** — take the other arctan branch: add half a
  wavelength. Every length must land in [0, 0.5) λ.
- **`import skrf` fails with an error about `np.typing`** — you have
  scikit-rf 2.0.x installed; the course pins `scikit-rf==1.13.0`:
  `pip install scikit-rf==1.13.0`.
- **Garbled symbols (Ω, °, λ) in the Windows console** — run `chcp 65001`
  first, or use Windows Terminal; the scripts also reconfigure stdout to
  UTF-8 themselves.
- **A plot window blocks the script** — that's `--smith` doing its job
  (close the window to continue). For headless runs: `set MPLBACKEND=Agg`
  (Windows) / `MPLBACKEND=Agg python ...` (macOS/Linux); figures are always
  also saved as PNG.
