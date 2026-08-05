# Lecture 7 lab — Power dividers & couplers

## Install

Nothing new this week — the course venv from lecture 1 (Python 3.12 exactly,
`pip install -r requirements.txt` from the repo root: numpy 1.26.4, scipy,
matplotlib, scikit-rf 1.13.0) is all this lab uses.

Then, from this directory:

```
python setup_check.py           # must print SETUP OK
```

The smoke test assembles a small Wilkinson in `skrf.Circuit` — if it passes, every
API this week's homework touches works on your machine.

## Files

| File | What it is |
|---|---|
| `setup_check.py` | pre-class environment verification → `SETUP OK` |
| `hour3_walkthrough.py` | hour 3's live-coding cells (`# %%` format) |
| `HOMEWORK.md` | the homework: story, modules, commands |
| `ANSWERS.md` | your answer sheet — two questions answered *before* running |
| `hw7_starter.py` | the only code file you edit and submit |
| `VERIFY.md` | instructor-side verification recipe |
| `solutions/` | instructor only |

## Troubleshooting

- **`AttributeError: ... appears twice in the connection description`** — two
  networks in your `Circuit` share a `.name`. Every element (and every port)
  needs a unique, non-empty name; pass `name=` to every builder call.
- **`All Networks must have a name`** — you called a raw `media.line(...)`
  without `name=`. Use the toolkit's `tem_line(...)`, which requires one.
- **Your feed's outputs land in the wrong rows of S** — skrf `Circuit` orders
  external ports by *first appearance in the connections list*. List your port
  connections first, in the order you want (in, out1..out4).
- **`np.tan` overflow / garbage at f₀ in module 1** — you evaluated tan(π/2)
  numerically. The closed form takes the quarter-wave limit on paper; there is
  no `tan` left in the final formulas.
- **Garbled symbols (Ω, °, λ) in the Windows console** — run `chcp 65001` first,
  or use Windows Terminal; the scripts also reconfigure stdout to UTF-8.
- **A plot window blocks the script** — that's `--plot` doing its job (close the
  window to continue). For headless runs: `set MPLBACKEND=Agg` (Windows) /
  `MPLBACKEND=Agg python ...` (macOS/Linux); figures are always also saved as PNG.
