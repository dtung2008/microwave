# %% Lecture 5, Hour 3 — Tools walkthrough (mirrors script.en.md cell-for-cell)
# Run whole:  python hour3_walkthrough.py        (figures saved, not shown)
# Or cell-by-cell in VS Code (# %% cells).
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.constants import c
from scipy.optimize import brentq

# %% 3.1 Setup verification
import scipy, skrf  # noqa: E401

print("python ", sys.version.split()[0])
print("numpy  ", np.__version__, " scipy", scipy.__version__,
      " matplotlib", matplotlib.__version__, " scikit-rf", skrf.__version__)
try:
    import fdtd
    print("fdtd   ", fdtd.__version__, " (optional, for cell 3.5)")
except ImportError:
    print("fdtd    not installed (optional: pip install fdtd; cell 3.5 will skip)")

# %% 3.2 Hammerstad by hand — the board designed in four lines
# The course stackup: RO4350B, 20-mil core, 1-oz copper (the homework's board).
RO = dict(name="RO4350B", ep_r=3.48, h_m=0.508e-3, tand=0.0037, t_m=35e-6)
FR4 = dict(name="FR-4", ep_r=4.4, h_m=0.508e-3, tand=0.02, t_m=35e-6)

def w_eff_m(w_m, sub):                 # Wheeler: thickness -> a wider thin strip
    return w_m + sub["t_m"] / np.pi * (1 + np.log(2 * sub["h_m"] / sub["t_m"]))

def eps_eff(w_m, sub):                 # Hammerstad filling-factor formula
    u = w_eff_m(w_m, sub) / sub["h_m"]
    er = sub["ep_r"]
    return (er + 1) / 2 + (er - 1) / 2 / np.sqrt(1 + 12 / u)

def z0_ohm(w_m, sub):                  # Hammerstad impedance, both regimes
    u = w_eff_m(w_m, sub) / sub["h_m"]
    ee = eps_eff(w_m, sub)
    if u <= 1:
        return 60 / np.sqrt(ee) * np.log(8 / u + u / 4)
    return 120 * np.pi / (np.sqrt(ee) * (u + 1.393 + 0.667 * np.log(u + 1.444)))

def width_for(z_target, sub):          # synthesis = a root on the analysis
    return brentq(lambda w: z0_ohm(w, sub) - z_target,
                  0.02 * sub["h_m"], 20 * sub["h_m"], xtol=1e-12)

for sub in (RO, FR4):
    w50 = width_for(50.0, sub)
    ee = eps_eff(w50, sub)
    lam_g = c / (10e9 * np.sqrt(ee))
    print(f"{sub['name']:8s}: 50-ohm width = {w50*1e3:.4f} mm "
          f"(w/h = {w50/sub['h_m']:.3f}), eps_eff = {ee:.4f}, "
          f"lam_g(10 GHz) = {lam_g*1e3:.3f} mm")
print("eps_eff sits between (er+1)/2 and er — the fields live half in air,"
      " half in the board, and eps_eff is the exact bookkeeping.")

# %% 3.3 The referee: skrf MLine — an independent implementation WITH dispersion
from skrf.media import MLine

w50 = width_for(50.0, RO)
freq = skrf.Frequency(1, 20, 191, "ghz")
ml = MLine(frequency=freq, w=w50, h=RO["h_m"], t=RO["t_m"], ep_r=RO["ep_r"],
           tand=RO["tand"], rho=1.68e-8, model="hammerstadjensen",
           disp="kirschningjansen", f_epr_tand=10e9)
z_sk = ml.z0_characteristic.real
e_sk = ml.ep_reff_f.real
dz = np.abs(z0_ohm(w50, RO) - z_sk) / z_sk * 100
de = np.abs(eps_eff(w50, RO) - e_sk) / e_sk * 100
print(f"hand z0 = {z0_ohm(w50, RO):.4f} ohm (flat — quasi-static has no f)")
print(f"skrf z0 at 1 / 10 / 20 GHz = {z_sk[0]:.3f} / "
      f"{z_sk[95]:.3f} / {z_sk[-1]:.3f} ohm")
print(f"skrf eps_eff at 1 / 10 / 20 GHz = {e_sk[0]:.4f} / {e_sk[95]:.4f} / "
      f"{e_sk[-1]:.4f}   <- dispersion: the field retreats into the dielectric")
print(f"worst disagreement 1-20 GHz: z0 {dz.max():.2f}%  eps_eff {de.max():.2f}%"
      "   (syllabus bars: 2% and 3% — the hand formula holds)")

fig, ax = plt.subplots(figsize=(7.2, 4.2))
ax.plot(freq.f / 1e9, e_sk, label="skrf MLine (Kirschning-Jansen)")
ax.axhline(eps_eff(w50, RO), color="C1", ls="--", label="hand quasi-static")
ax.set_xlabel("frequency (GHz)"), ax.set_ylabel(r"$\epsilon_{\rm eff}$")
ax.set_title("the quasi-TEM lie, measured")
ax.legend(), ax.grid(alpha=0.3)
fig.tight_layout(), fig.savefig("microstrip_referee.png", dpi=130)
print("wrote microstrip_referee.png")

# %% 3.4 The hollow pipe: skrf RectangularWaveguide dispersion
from skrf.media import RectangularWaveguide

WGS = {"WR-90": (22.86e-3, 10.16e-3), "WR-75": (19.05e-3, 9.525e-3),
       "WR-62": (15.7988e-3, 7.8994e-3)}
fig, ax = plt.subplots(figsize=(7.2, 4.4))
f = np.linspace(5e9, 20e9, 800)
for name, (a, b) in WGS.items():
    fc = c / (2 * a)                       # the analytic cutoff, c/2a
    wg = RectangularWaveguide(frequency=skrf.Frequency(9.9, 10.1, 3, "ghz"),
                              a=a, b=b, rho=1.68e-8)
    tau = 0.30 / (c * np.sqrt(1 - (fc / 10e9) ** 2))   # 30 cm group delay
    print(f"{name}: fc = {fc/1e9:.6f} GHz (skrf f_cutoff agrees: "
          f"{wg.f_cutoff/1e9:.6f}); 30 cm at 10 GHz takes {tau*1e9:.4f} ns"
          f"  (light in air: {0.30/c*1e9:.4f} ns)")
    fs = f[f > fc * 1.001]
    beta = 2 * np.pi / c * np.sqrt(fs**2 - fc**2)
    ax.plot(beta, fs / 1e9, label=name)
ax.plot(2 * np.pi * f / c, f / 1e9, "k--", alpha=0.5, label="light line")
ax.axhline(10, color="gray", ls=":")
ax.set_xlabel(r"$\beta$ (rad/m)"), ax.set_ylabel("f (GHz)")
ax.set_title(r"$\omega$-$\beta$: the slope IS the group velocity")
ax.legend(), ax.grid(alpha=0.3)
fig.tight_layout(), fig.savefig("omega_beta.png", dpi=130)
print("wrote omega_beta.png")
print("WR-62 'works' at 10 GHz (9.49 < 10) — and pays 3.17 ns and a curve"
      " so steep the 200 MHz window smears by ~0.6 ns/30cm. The picker says WR-90.")

# %% 3.5 fdtd: watch the wave refuse to propagate below cutoff
# 2D FDTD (finite-difference time-domain), WR-90 width between conducting
# walls. Above fc the mode travels; below fc it dies exponentially — the
# same physics as beta = sqrt(k^2 - (pi/a)^2) going imaginary.
try:
    import fdtd

    fdtd.set_backend("numpy")
    A_M = 22.86e-3
    FC = c / (2 * A_M)
    DX = A_M / 40
    NWALL = 3
    NX, NY = 320, 40 + 2 * NWALL

    def wave_in_pipe(f_hz, steps):
        grid = fdtd.Grid(shape=(NX, NY, 1), grid_spacing=DX)
        grid[0:12, :, :] = fdtd.PML(name="pml_lo")       # absorbing ends
        grid[-12:, :, :] = fdtd.PML(name="pml_hi")
        grid[:, 0:NWALL, :] = fdtd.AbsorbingObject(       # metal walls
            permittivity=1.0, conductivity=1e6, name="wall_lo")
        grid[:, -NWALL:, :] = fdtd.AbsorbingObject(
            permittivity=1.0, conductivity=1e6, name="wall_hi")
        grid[30, NWALL:-NWALL, 0] = fdtd.LineSource(period=1.0 / f_hz,
                                                    name="src")
        grid.run(steps, progress_bar=False)
        return np.asarray(grid.E[:, :, 0, 2])            # Ez snapshot

    ez_hi = wave_in_pipe(10e9, steps=2600)               # above fc = 6.557
    ez_lo = wave_in_pipe(4.5e9, steps=5200)              # below fc

    # measure the guided wavelength at 10 GHz off the field itself
    row = ez_hi[:, NY // 2][60:296]
    F = np.fft.rfft(row * np.hanning(len(row)), n=len(row) * 16)
    kax = np.fft.rfftfreq(len(row) * 16, DX)
    lam_meas = 1.0 / kax[np.abs(F).argmax()]
    lam_th = c / (10e9 * np.sqrt(1 - (FC / 10e9) ** 2))
    print(f"lambda_g at 10 GHz: FDTD measures {lam_meas*1e3:.2f} mm, "
          f"theory says {lam_th*1e3:.2f} mm "
          f"({abs(lam_meas-lam_th)/lam_th*100:.1f}% apart)")

    # measure the evanescent decay at 4.5 GHz (fit 0.6-2.9 cm from the source)
    mid = np.abs(ez_lo[:, NY // 2])
    x = np.arange(NX) * DX
    slope = np.polyfit(x[40:80], np.log(mid[40:80] + 1e-30), 1)[0]
    kappa_th = 2 * np.pi / c * np.sqrt(FC**2 - 4.5e9**2)
    print(f"below cutoff at 4.5 GHz: field decays at {-slope:.1f} Np/m; "
          f"analytic kappa = sqrt(kc^2-k^2) = {kappa_th:.1f} Np/m "
          f"({abs(-slope-kappa_th)/kappa_th*100:.1f}% apart)")
    print("no loss anywhere in that pipe — the wave below cutoff is REFUSED,"
          " not absorbed. Reactive, like a too-small door.")

    fig, axs = plt.subplots(2, 1, figsize=(9, 4.8), sharex=True)
    # color scale from the traveling wave itself, not the hot source cells
    vmax = np.abs(ez_hi[100:296, NWALL:-NWALL]).max()
    for ax_, ez, lab in [(axs[0], ez_hi, "10 GHz  >  fc = 6.56 GHz : travels"),
                         (axs[1], ez_lo, "4.5 GHz  <  fc = 6.56 GHz : dies in ~1 cm")]:
        ax_.imshow(ez.T, aspect="auto", cmap="RdBu", vmin=-vmax, vmax=vmax,
                   extent=[0, NX * DX * 100, 0, (NY * DX) * 1e3],
                   origin="lower")
        ax_.set_title(lab, fontsize=10)
        ax_.set_ylabel("y (mm)")
    axs[1].set_xlabel("x (cm)   [source at 1.7 cm; PML absorbers at both ends]")
    fig.tight_layout(), fig.savefig("fdtd_cutoff.png", dpi=130)
    print("wrote fdtd_cutoff.png")
except ImportError:
    print("fdtd not installed — skipping (pip install fdtd to see the demo)")

# %% 3.6 The openEMS case study — post-processing a full-wave Touchstone
# openEMS is a full-wave FDTD field solver (instructor-run only; students
# never install it). The instructor exports a Touchstone file of a 30 mm
# 50-ohm RO4350B line; this cell post-processes WHATEVER file sits at
# CASE_FILE the same way, and falls back to a clearly-labeled scikit-rf
# placeholder so the pipeline can be rehearsed before the real file lands.
import os

CASE_FILE = "openems_microstrip.s2p"        # <- instructor's export goes here
L_CASE_M = 0.030                            # the case-study line is 30 mm

if os.path.exists(CASE_FILE):
    case = skrf.Network(CASE_FILE)
    src = f"instructor openEMS export ({CASE_FILE})"
else:
    line = ml.line(L_CASE_M, unit="m", name="mline_placeholder")
    line.write_touchstone("PLACEHOLDER_mline.s2p", r_ref=50.0)
    case = skrf.Network("PLACEHOLDER_mline.s2p")
    src = ("PLACEHOLDER (skrf MLine model — NOT field-solved; drop the real "
           f"openEMS export at {CASE_FILE} and rerun)")
print(f"case study source: {src}")

fghz = case.frequency.f / 1e9
s21_db = 20 * np.log10(np.abs(case.s[:, 1, 0]))
phi = np.unwrap(np.angle(case.s[:, 1, 0]))
beta_meas = -phi / L_CASE_M
ee_meas = (beta_meas * c / (2 * np.pi * case.frequency.f)) ** 2
i10 = np.argmin(np.abs(fghz - 10.0))
print(f"at 10 GHz: |S21| = {s21_db[i10]:.4f} dB over 30 mm "
      f"-> {-s21_db[i10]/L_CASE_M:.3f} dB/m")
print(f"eps_eff from the S21 phase slope: {ee_meas[i10]:.4f} "
      f"(hand quasi-static said {eps_eff(w50, RO):.4f})")

fig, axs = plt.subplots(1, 2, figsize=(10.5, 4.0))
axs[0].plot(fghz, s21_db)
axs[0].set_xlabel("f (GHz)"), axs[0].set_ylabel("|S21| (dB)")
axs[0].set_title("loss of the 30 mm case-study line")
axs[0].grid(alpha=0.3)
axs[1].plot(fghz, ee_meas)
axs[1].axhline(eps_eff(w50, RO), color="C1", ls="--",
               label="hand quasi-static")
axs[1].set_xlabel("f (GHz)"), axs[1].set_ylabel(r"$\epsilon_{\rm eff}$")
axs[1].set_title("eps_eff extracted from the phase")
axs[1].legend(), axs[1].grid(alpha=0.3)
fig.suptitle(f"source: {src}", fontsize=8)
fig.tight_layout(), fig.savefig("openems_case.png", dpi=130)
print("wrote openems_case.png  (same code, any Touchstone — that is the point)")

# %% 3.7 Deliberate bug — the wavelength that used the wrong epsilon
# Design the homework's lambda/4 transformer (70.71 ohm, 10 GHz, RO4350B),
# but compute the guided wavelength with er = 3.48 instead of eps_eff.
# Nothing crashes. The board gets made.
zt = np.sqrt(50.0 * 100.0)
wt = width_for(zt, RO)
ee_t = eps_eff(wt, RO)
L_right = c / (10e9 * np.sqrt(ee_t)) / 4
L_bug = c / (10e9 * np.sqrt(RO["ep_r"])) / 4       # <- the bug: er, not eps_eff
theta_bug = 90.0 * L_bug / L_right                  # electrical length at f0
f_res_bug = 10e9 * L_right / L_bug                  # where the bug stub is 90 deg
print(f"BUG: lam/4 with er = 3.48       -> L = {L_bug*1e3:.4f} mm")
print(f"     lam/4 with eps_eff = {ee_t:.3f} -> L = {L_right*1e3:.4f} mm"
      f"   (the truth is {L_right/L_bug:.4f}x longer)")
print(f"the bugged stub at 10 GHz is only {theta_bug:.1f} deg of the 90 needed;"
      f" it becomes a quarter wave at {f_res_bug/1e9:.2f} GHz instead")
print("every stub, transformer, and coupled-line filter in lectures 6-9 dies"
      " the same death: eps_eff owns the wavelength; er only owns the board.")
