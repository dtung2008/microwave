# Lecture 11 lab — Amplifier design & the LNA

## Install (once, for the whole course)

Same environment as lectures 1–10. **Python 3.12, exactly**; from the repo root:

```
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Then, from this directory:

```
python setup_check.py           # must print SETUP OK
```

## Step 0 — the vendor device (one download, ~0.6 MB)

This week's device is a real one: the **Mini-Circuits PGA-103+**, a 50 Ω
E-PHEMT MMIC low-noise amplifier, 0.05–4 GHz. Mini-Circuits publishes measured
S-parameters for it; the course never redistributes vendor files, so you fetch
your own copy:

1. Open the PGA-103+ product page:
   <https://www.minicircuits.com/WebStore/dashboard.html?model=PGA-103%2B>
2. Under **Data, Drawings & Downloads**, click **S-PARAMETERS**
   (file `PGA-103+_S2P.zip`). Use a browser — the site refuses plain
   `curl`/`wget`.
3. The zip holds 18 files (bias voltage × temperature). Extract exactly one
   into this `lab/` directory, keeping its name:

   ```
   PGA-103+_5V_Plus25DegC.s2p        (+5 V bias, +25 °C — the datasheet's case)
   ```

Everything degrades gracefully without it: the toolkit falls back to a
clearly-labeled **synthetic** device (`demo_device()`), and every command
still runs — with different numbers. `setup_check.py` tells you which state
you are in. Do the download; refereeing your design against the datasheet is
half the fun.

## Files

| File | What it is |
|---|---|
| `setup_check.py` | pre-class environment verification → `SETUP OK` |
| `hour3_walkthrough.py` | hour 3's live-coding cells (`# %%` format) |
| `HOMEWORK.md` | the homework: story, modules, commands |
| `ANSWERS.md` | your answer sheet — two questions answered *before* running |
| `hw11_starter.py` | the only code file you edit and submit |
| `VERIFY.md` | instructor-side verification recipe |
| `solutions/` | instructor only |

## Troubleshooting

- **The S-parameter download gives 403 / an error page** — Mini-Circuits
  blocks command-line fetches. Use a normal browser; if the page moved, search
  "PGA-103+ s2p" on minicircuits.com.
- **`file not found: PGA-103+_5V_Plus25DegC.s2p`** — the .s2p is not in
  `lab/` (or was renamed). The harness continues on the synthetic device;
  finish step 0 to get the real one.
- **Wrong file extracted** — the zip's other 17 files (3 V bias, −45 °C, …)
  load fine but give different numbers than the instructor's; use the 5 V,
  +25 °C file.
- **Garbled symbols (Ω, °, μ) in the Windows console** — run `chcp 65001`
  first, or use Windows Terminal; the scripts also reconfigure stdout to
  UTF-8 themselves.
- **A plot window blocks the script** — that's `--plot` doing its job (close
  the window to continue). For headless runs: `set MPLBACKEND=Agg` (Windows) /
  `MPLBACKEND=Agg python ...` (macOS/Linux); figures are always also saved as
  PNG.
- **`import skrf` fails with an error about `np.typing`** — you have
  scikit-rf 2.0.x; the course pins 1.13.0: `pip install scikit-rf==1.13.0`.
