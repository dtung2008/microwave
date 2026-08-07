# Lecture 13 lab — Antennas & arrays

## Install (once, for the whole course)

Same environment as lecture 1 — nothing new this week. **Python 3.12, exactly**,
with the course venv (`numpy==1.26.4`, `scipy`, `matplotlib`, `scikit-rf==1.13.0`).
If you have been running lectures 1–12, you are done; otherwise see
`lessons/01-systems-panorama/lab/README.md` for the per-OS install.

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
| `hw13_starter.py` | the only code file you edit and submit |
| `VERIFY.md` | instructor-side verification recipe |
| `solutions/` | instructor only |

## Troubleshooting

- **`chebwin` prints "This window is not suitable for spectral analysis"** — scipy
  warns that the −30 dB Chebyshev window's *noise bandwidth* misbehaves for PSD
  estimation. We are pointing antennas, not estimating PSDs; the equal-ripple
  sidelobe guarantee holds. The starter and walkthrough silence this warning with a
  comment saying why; if you import `chebwin` in your own scratch files you will see
  it once — it is safe to ignore here.
- **Your pattern shows dozens of identical beams spaced ~3.14° apart** — you fed
  degrees to `np.sin`. That spacing is π showing up on a degrees axis; hour 3's
  deliberate bug is exactly this. Convert: `np.sin(np.radians(theta_deg))`.
- **Your steered beam or the scene's drone lands at the mirror angle (−15° instead
  of +15°)** — sign convention. Element `n` sits at `x = n·d` with geometric phase
  `+k·d·n·sin(theta)`; steering phases are `-k·d·n·sin(theta0)`.
- **`hpbw_deg` disagrees with the closed form by ~0.2% and refuses to improve** —
  you are reading the −3 dB edge at the nearest grid sample. Interpolate linearly
  between the two samples that straddle half power.
- **Garbled symbols (Ω, °, λ) in the Windows console** — run `chcp 65001` first, or
  use Windows Terminal; the scripts also reconfigure stdout to UTF-8 themselves.
- **A plot window blocks the script** — that's `--plot` doing its job (close the
  window to continue). For headless runs: `set MPLBACKEND=Agg` (Windows) /
  `MPLBACKEND=Agg python ...` (macOS/Linux); figures are always also saved as PNG.
