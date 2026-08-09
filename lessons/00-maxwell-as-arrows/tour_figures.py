"""Chapter 0 — Maxwell as Arrows: regenerate every figure in tour.en.md.

Run:  python tour_figures.py        # writes figures/fig01..fig06 (PNG)
"""
import os
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.special import j0, j1

os.makedirs("figures", exist_ok=True)
DPI = 130


def save(fig, name):
    path = os.path.join("figures", name)
    fig.tight_layout()
    fig.savefig(path, dpi=DPI)
    plt.close(fig)
    print("wrote", path)


# --- fig01: three speeds, and the wavefront that turns current on -----------
def fig01():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 3.9))
    speeds = {"drift $v_d$": 7.35e-5, "thermal $v_F$": 1.57e6,
              "signal $1/\\sqrt{L'C'}$": 2.0e8}
    names = list(speeds)
    ax1.barh(names, [speeds[n] for n in names],
             color=["#888", "#5b9bd5", "#c0504d"], log=True)
    ax1.set_xlabel("speed (m/s, log scale)")
    ax1.set_title("three speeds of one ampere — 12 orders of magnitude")
    ax1.grid(True, axis="x", alpha=0.3)

    # x-t diagram: the switch-on front moves at v; drift onset follows it
    v = 2.0e8
    x = np.linspace(0, 10, 200)             # meters of line
    ax2.plot(x, x / v * 1e9, "k", lw=2, label="field front  t = x/v")
    ax2.fill_between(x, x / v * 1e9, 60, color="#f4f6f9",
                     label="no field yet — no drift")
    ax2.fill_between(x, 0, x / v * 1e9, color="#dbe8ff",
                     label="drifting (started ~fs after front)")
    ax2.set_xlabel("position along line (m)")
    ax2.set_ylabel("time (ns)")
    ax2.set_title("current 'turns on' at wave speed, in sequence")
    ax2.legend(loc="upper left", fontsize=8)
    save(fig, "fig01_speeds.png")


# --- fig02: flux = field through a surface, orientation included ------------
def fig02():
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.0))
    y, z = np.meshgrid(np.linspace(-1.4, 1.4, 8), np.linspace(-1.4, 1.4, 8))
    for ax, tilt, flux in ((axes[0], 0, 6.2832), (axes[1], 60, 3.1416)):
        ax.quiver(np.full_like(y, -1.5), y, np.ones_like(y), np.zeros_like(y),
                  angles="xy", scale_units="xy", scale=1.4, color="#5b9bd5",
                  width=0.006)
        t = np.radians(tilt)
        ax.plot([np.sin(t), -np.sin(t)], [-np.cos(t), np.cos(t)],
                "k", lw=4)
        ax.set_xlim(-1.8, 1.8)
        ax.set_ylim(-1.8, 1.8)
        ax.set_aspect("equal")
        ax.set_title(f"disk tilted {tilt}° — flux = {flux:.4f} A")
        ax.axis("off")
    fig.suptitle("same J (2 A/mm², r = 1 mm disk): flux counts field "
                 "THROUGH the surface — cos(tilt)", y=1.0)
    save(fig, "fig02_flux.png")


# --- fig03: curl — shear vs vortex, paddle wheels ---------------------------
def fig03():
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.4))
    g = np.linspace(-1, 1, 13)
    X, Y = np.meshgrid(g, g)
    axes[0].quiver(X, Y, 2 * Y, np.zeros_like(X), color="#5b9bd5",
                   scale=18, width=0.005)
    axes[0].set_title("shear v = (2y, 0): straight lines,\n"
                      "circulation/area = −2.0000 everywhere (SPINS)")
    r2 = X**2 + Y**2 + 1e-9
    mask = r2 > 0.08
    axes[1].quiver(X[mask], Y[mask], (-Y / r2)[mask], (X / r2)[mask],
                   color="#c0504d", scale=30, width=0.005)
    axes[1].set_title("vortex v = φ̂/r: visibly circling,\n"
                      "curl = 0 off-axis; loop around axis: 2π (any R)")
    for ax in axes:
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
    save(fig, "fig03_curl.png")


# --- fig04: coax read by arrows — E radial, H azimuthal, S = E×H axial ------
def fig04():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.2))
    a, b = 1.0, np.exp(5.0 / 6.0)
    th = np.linspace(0, 2 * np.pi, 200)
    for R, c in ((a, "k"), (b, "k")):
        ax1.plot(R * np.cos(th), R * np.sin(th), c, lw=2)
    ang = np.linspace(0, 2 * np.pi, 12, endpoint=False)
    rr = np.linspace(a * 1.15, b * 0.9, 3)
    for R in rr:
        x, y = R * np.cos(ang), R * np.sin(ang)
        r_hat = np.stack([np.cos(ang), np.sin(ang)])
        phi_hat = np.stack([-np.sin(ang), np.cos(ang)])
        ax1.quiver(x, y, *(r_hat / R), color="#c0504d", scale=9,
                   width=0.006)
        ax1.quiver(x, y, *(phi_hat / R), color="#5b9bd5", scale=9,
                   width=0.006)
    ax1.plot([], [], color="#c0504d", label="E (radial, +V to ground)")
    ax1.plot([], [], color="#5b9bd5", label="H (wraps the center current)")
    ax1.scatter([0], [0], s=60, c="k", zorder=5)
    ax1.annotate("S = E×H: out of the page,\ndown the cable", (0.02, -2.6),
                 ha="center", fontsize=9)
    ax1.set_aspect("equal")
    ax1.axis("off")
    ax1.set_title("coax by arrows: three sentences, no integral")
    ax1.legend(loc="upper right", fontsize=8)

    r = np.linspace(a, b, 300)
    S = 1.0 / (r**2 * np.log(b / a) ** 2 * 2 * np.pi) * 10 * 0.2 * np.log(b/a)
    # plot normalized axial Poynting density profile
    ax2.plot(r, S / S[0], "#c0504d", lw=2)
    ax2.set_xlabel("radius r (in units of a)")
    ax2.set_ylabel("S(r) / S(a)")
    ax2.set_title("Poynting density ∝ 1/r²; its integral = VI = 2.00000 W")
    ax2.grid(True, alpha=0.3)
    save(fig, "fig04_coax.png")


# --- fig05: the barber pole — H tilts, curl H does not ----------------------
def fig05():
    fig = plt.figure(figsize=(10.5, 4.0))
    r0 = 1.0
    z = np.linspace(0, 12, 800)
    for i, (hz_ratio, label) in enumerate(
            [(0.0, "solenoid off: pitch 90°"),
             (1.0, "H_z = H_φ: pitch 45°"),
             (3.0, "H_z = 3H_φ: pitch 18.4°")]):
        ax = fig.add_subplot(1, 3, i + 1, projection="3d")
        phi = z * (1.0 / (1.0 + 1e-12)) if hz_ratio == 0 else z / hz_ratio
        if hz_ratio == 0:
            phi = np.linspace(0, 4 * np.pi, 800)
            zz = np.zeros_like(phi)
        else:
            zz = z
        ax.plot(r0 * np.cos(phi), r0 * np.sin(phi), zz, "#5b9bd5", lw=2)
        ax.plot([0, 0], [0, 0], [-1, 13], "k", lw=3)
        ax.set_title(label, fontsize=9)
        ax.set_axis_off()
    fig.suptitle("field line at r = 5 mm around a 1 A wire: adding a curl-free "
                 "H_z rotates H into a helix — J (the axis) never moves")
    save(fig, "fig05_barberpole.png")


# --- fig06: the force-free rope — curl B parallel to B ----------------------
def fig06():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 3.9))
    r = np.linspace(0, 2.404, 400)
    ax1.plot(r, j0(r), "#c0504d", lw=2, label="$B_z = J_0(r)$ (axial)")
    ax1.plot(r, j1(r), "#5b9bd5", lw=2, label="$B_φ = J_1(r)$ (azimuthal)")
    ax1.axhline(0, color="k", lw=0.5)
    ax1.set_xlabel("radius r")
    ax1.set_title("Lundquist flux rope: ∇×B = B (checked to 1e-4)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    pitch = np.degrees(np.arctan2(j1(r), j0(r)))
    ax2.plot(r, pitch, "k", lw=2)
    ax2.set_xlabel("radius r")
    ax2.set_ylabel("field pitch from axis (deg)")
    ax2.set_title("axial at the core → azimuthal at the rim;\n"
                  "J is parallel to B the whole way")
    ax2.grid(True, alpha=0.3)
    save(fig, "fig06_lundquist.png")


# --- fig07: divergence — 3-D geometry, and why the constancy is 3-D ---------
def _cube_edges(ax, c, half, color, lw=1.8):
    s = [-half, half]
    for i in s:
        for j in s:
            ax.plot([c[0]+s[0], c[0]+s[1]], [c[1]+i]*2, [c[2]+j]*2,
                    color=color, lw=lw)
            ax.plot([c[0]+i]*2, [c[1]+s[0], c[1]+s[1]], [c[2]+j]*2,
                    color=color, lw=lw)
            ax.plot([c[0]+i]*2, [c[1]+j]*2, [c[2]+s[0], c[2]+s[1]],
                    color=color, lw=lw)


def fig07():
    fig = plt.figure(figsize=(11.0, 4.6))
    # left: the real 3-D geometry — radial field, two spherical shells of
    # arrows (length falling as 1/r^2), an enclosing cube, a non-enclosing one
    ax = fig.add_subplot(1, 2, 1, projection="3d")
    for R, scale in ((1.0, 0.55), (2.0, 0.55 / 4)):
        n = 90
        # near-uniform points on the sphere (golden spiral)
        k = np.arange(n) + 0.5
        th = np.arccos(1 - 2 * k / n)
        ph = np.pi * (1 + 5**0.5) * k
        x, y, z = (R * np.sin(th) * np.cos(ph), R * np.sin(th) * np.sin(ph),
                   R * np.cos(th))
        ax.quiver(x, y, z, x / R * scale, y / R * scale, z / R * scale,
                  color="#5b9bd5", lw=1, arrow_length_ratio=0.35)
    _cube_edges(ax, (0, 0, 0), 1.5, "#c0504d")
    _cube_edges(ax, (3.1, 0, 0), 0.6, "#4a7c3f")
    ax.scatter([0], [0], [0], s=50, c="k")
    ax.set_box_aspect((1.3, 1, 1))
    ax.set_axis_off()
    ax.set_title("the 3-D geometry: E = r̂/r², arrows weakening as 1/r²;\n"
                 "red cube (6 faces) nets 4π, green cube nets 0", fontsize=10)
    # right: the constancy is a 3-D fact — flux vs enclosing radius,
    # 3-D sphere (area ~ r^2) vs a 2-D circle (perimeter ~ r)
    ax2 = fig.add_subplot(1, 2, 2)
    R = np.linspace(0.5, 4, 200)
    ax2.plot(R, np.full_like(R, 4 * np.pi), "#c0504d", lw=2,
             label="3-D: sphere area 4πR² × field 1/R² = 4π, any R")
    ax2.plot(R, 2 * np.pi / R, "#5b9bd5", lw=2, ls="--",
             label="same 1/R² field in a 2-D world: 2πR × 1/R² = 2π/R")
    ax2.axhline(0, color="k", lw=0.5)
    ax2.set_xlabel("enclosing radius R")
    ax2.set_ylabel("net outward flux")
    ax2.set_title("size-independence is the 3-D balance\n"
                  "(in 2-D the divergence-free radial field is 1/r, not 1/r²)",
                  fontsize=10)
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)
    save(fig, "fig07_divergence.png")


if __name__ == "__main__":
    for f in (fig01, fig02, fig03, fig04, fig05, fig06, fig07):
        f()
