"""Chapter 0 — Maxwell as Arrows: every number in tour.en.md, recomputed.

Run:  python tour_numbers.py all        # every section
      python tour_numbers.py 0.4        # one section

No solver library, no scikit-rf — numpy only. This chapter IS the
pre-software tool.
"""
import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np

E_CHARGE = 1.602176634e-19      # C
M_ELECTRON = 9.1093837015e-31   # kg
N_COPPER = 8.49e28              # free electrons / m^3 (one per atom)
SIGMA_COPPER = 5.96e7           # S/m
C_LIGHT = 2.99792458e8          # m/s
MU0 = 4e-7 * np.pi


def s01():
    print("== 0.1 three speeds of one ampere " + "=" * 30)
    I, A = 1.0, 1e-6                       # 1 A through 1 mm^2 of copper
    v_d = I / (N_COPPER * E_CHARGE * A)
    tau = M_ELECTRON * SIGMA_COPPER / (N_COPPER * E_CHARGE**2)
    v_fermi = 1.57e6                       # Cu Fermi velocity (settled value)
    Lp, Cp = 250e-9, 100e-12               # RG-58-class line, per meter
    v_wave = 1.0 / np.sqrt(Lp * Cp)
    print(f"drift    v_d   = I/(n q A)      = {v_d:.3e} m/s"
          f"   ({v_d*1e3:.4f} mm/s)")
    print(f"thermal  v_F   (copper, quoted) = {v_fermi:.2e} m/s")
    print(f"signal   v     = 1/sqrt(L'C')   = {v_wave:.3e} m/s"
          f"   ({v_wave/C_LIGHT:.3f} c)")
    print(f"Drude    tau   = m*sigma/(n q^2)= {tau:.2e} s"
          f"   (drift settles in ~5 tau = {5*tau*1e15:.0f} fs)")
    print(f"ratios: signal/drift = {v_wave/v_d:.1e}   "
          f"one meter of wire: signal {1/v_wave*1e9:.1f} ns, "
          f"an electron {1/v_d/3600:.1f} h")


def s02():
    print("== 0.2 flux is an integral, not a motion " + "=" * 24)
    J = 2e6                                # A/m^2 (2 A per mm^2), uniform, along z
    r = 1e-3
    A = np.pi * r**2
    for tilt in (0.0, 60.0):
        flux = J * A * np.cos(np.radians(tilt))
        print(f"disk r = 1 mm tilted {tilt:4.0f} deg:  I = J*A*cos = "
              f"{flux:.4f} A")
    print("same J, same disk, different orientation -> different flux:")
    print("flux measures field-through-surface geometry, not any new motion.")
    # numerical check of the tilted case by actual surface integration
    n = 400
    xs = np.linspace(-r, r, n)
    ys = np.linspace(-r, r, n)
    X, Y = np.meshgrid(xs, ys)
    inside = X**2 + Y**2 <= r**2
    dA = (xs[1] - xs[0]) * (ys[1] - ys[0])
    flux_num = J * np.cos(np.radians(60.0)) * inside.sum() * dA
    print(f"numerical surface integral (60 deg): {flux_num:.4f} A  "
          f"(closed form {J*A*0.5:.4f})")


def s03():
    print("== 0.3 divergence is flux density " + "=" * 31)
    # point-charge field E = r_hat / r^2  (units: q/4pi*eps0 = 1)
    def flux_through_cube(center, half, n=500):
        """Net outward flux of r_hat/r^2 through a cube's six faces."""
        c = np.asarray(center, float)
        u = np.linspace(-half, half, n, endpoint=False) + half / n
        U, V = np.meshgrid(u, u)
        dA = (2 * half / n) ** 2
        total = 0.0
        for axis in range(3):
            for sign in (+1.0, -1.0):
                pts = np.zeros((3, n, n))
                others = [a for a in range(3) if a != axis]
                pts[axis] = c[axis] + sign * half
                pts[others[0]] = c[others[0]] + U
                pts[others[1]] = c[others[1]] + V
                r = np.sqrt((pts**2).sum(0))
                En = pts[axis] / r**3          # (r_hat/r^2) . axis_hat
                total += sign * np.sum(En) * dA
        return total

    print("field of a point charge at the origin, E = r_hat/r^2:")
    for center, half, label in [((0, 0, 0), 0.5, "enclosing, side 1"),
                                ((0, 0, 0), 2.0, "enclosing, side 4"),
                                ((3, 0, 0), 0.5, "NOT enclosing")]:
        f = flux_through_cube(center, half)
        print(f"  cube at {center}, {label:18s}: net flux = {f:8.4f}"
              f"   (4*pi = {4*np.pi:.4f})")
    # divergence as the limit flux/volume, away from the charge
    print("divergence = flux/volume as the box shrinks, at point (2,0,0):")
    for half in (0.2, 0.05):
        f = flux_through_cube((2, 0, 0), half)
        print(f"  box half-size {half:4.2f}: flux/volume = "
              f"{f/(2*half)**3:+.2e}   (-> 0: no source here)")
    print("the most diverging-LOOKING field in physics has zero divergence")
    print("everywhere except the charge: spreading is exactly cancelled by")
    print("1/r^2 weakening. All 4*pi of it lives AT the charge -> Gauss.")


def s04():
    print("== 0.4 curl is circulation density " + "=" * 30)
    # circulation/area on shrinking square loops, computed by walking the loop
    def circulation(field, half, n=4000):
        # square loop centered at (0.5, 0.5), walked counterclockwise;
        # midpoint sampling: n segments per side, sample at segment centers
        dl = 2 * half / n
        s = np.linspace(-half, half, n, endpoint=False) + dl / 2
        cx, cy = 0.5, 0.5
        top = np.stack([cx + s, np.full(n, cy + half)], 1)
        left = np.stack([np.full(n, cx - half), cy + s[::-1]], 1)
        bot = np.stack([cx + s[::-1], np.full(n, cy - half)], 1)
        right = np.stack([np.full(n, cx + half), cy + s], 1)
        circ = 0.0
        for seg, dvec in ((right, (0, 1)), (top, (-1, 0)),
                          (left, (0, -1)), (bot, (1, 0))):
            v = field(seg[:, 0], seg[:, 1])
            circ += np.sum(v[0] * dvec[0] + v[1] * dvec[1]) * dl
        return circ

    k = 2.0
    shear = lambda x, y: (k * y, np.zeros_like(x))         # noqa: E731
    print("shear flow v = (k*y, 0), k = 2  (straight streamlines):")
    for half in (0.4, 0.1, 0.01):
        c = circulation(shear, half)
        print(f"  loop half-size {half:5.2f}: circulation/area = "
              f"{c/(2*half)**2:+.4f}   (curl_z = -k = -2)")

    print("vortex  v = (1/r) phi_hat  (visibly circling):")

    def vortex(x, y):
        r2 = x**2 + y**2
        return (-y / r2, x / r2)
    # loop NOT containing the axis: center (0.5, 0.5)
    for half in (0.2, 0.05):
        c = circulation(vortex, half)
        print(f"  off-axis loop half {half:4.2f}: circulation/area = "
              f"{c/(2*half)**2:+.2e}   (curl = 0 away from axis)")
    # loop containing the axis: walk a circle of radius R around origin
    for R in (0.3, 1.0):
        th = np.linspace(0, 2 * np.pi, 20000)
        x, y = R * np.cos(th), R * np.sin(th)
        vx, vy = vortex(x, y)
        dl = np.stack([-np.sin(th), np.cos(th)], 1) * (2 * np.pi * R / len(th))
        circ = np.sum(vx * dl[:, 0] + vy * dl[:, 1])
        print(f"  axis-enclosing loop R = {R:.1f}: circulation = "
              f"{circ:.5f}   (2*pi = {2*np.pi:.5f}, any R)")
    print("straight flow can curl; circling flow can be curl-free:")
    print("curl = does a paddle wheel SPIN here, not do paths bend.")


def s05():
    print("== 0.5 arrows at work: coax, barber pole, tilted loop " + "=" * 12)
    # --- Poynting through a 50-ohm air coax carries exactly V*I -------------
    a, b = 1e-3, 1e-3 * np.exp(5.0 / 6.0)   # 60*ln(b/a) = 50 ohm (air)
    V, Z0 = 10.0, 60.0 * np.log(b / a)
    I = V / Z0
    r = np.linspace(a, b, 200000)
    E = V / (r * np.log(b / a))             # V/m, radial
    H = I / (2 * np.pi * r)                 # A/m, azimuthal
    S = E * H                               # W/m^2, axial (E x H)
    P = np.trapz(S * 2 * np.pi * r, r)
    print(f"air coax a = 1 mm, b = {b*1e3:.3f} mm -> Z0 = {Z0:.3f} ohm")
    print(f"V = {V} V, I = V/Z0 = {I:.5f} A -> circuit P = VI = {V*I:.5f} W")
    print(f"integral of (E x H) over the DIELECTRIC cross-section = {P:.5f} W")
    print(f"difference = {abs(P - V*I):.2e} W -> the power rides the field")
    # --- barber pole: wire H_phi + solenoid H_z -> pitch angle --------------
    Iw, r0 = 1.0, 5e-3
    Hphi = Iw / (2 * np.pi * r0)
    print(f"wire 1 A at r = 5 mm: H_phi = {Hphi:.2f} A/m; add solenoid H_z:")
    for Hz in (0.0, Hphi, 3 * Hphi):
        ang = np.degrees(np.arctan2(Hphi, Hz))
        print(f"  H_z = {Hz:6.2f} A/m -> field pitch {ang:5.1f} deg off axis"
              f"   (J still purely axial)")
    print("curl(H) unchanged (solenoid field is curl-free here); H rotated.")
    # --- tilted loop: same arrow, new components ----------------------------
    R, Il = 0.05, 1.0
    B = MU0 * Il / (2 * R)
    for tilt in (0.0, 45.0):
        t = np.radians(tilt)
        comp = (B * np.sin(t), 0.0, B * np.cos(t))
        print(f"loop R = 5 cm, I = 1 A, tilt {tilt:4.1f} deg: "
              f"B = ({comp[0]*1e6:5.2f}, {comp[1]*1e6:4.2f}, "
              f"{comp[2]*1e6:5.2f}) uT, |B| = {B*1e6:.2f} uT")
    print("components rotate with the bookkeeping; the arrow stays on the axis.")


def s06():
    print("== 0.6 the empty slot, and the field that shares it " + "=" * 14)
    # Lundquist force-free rope: B = (0, J1(alpha r), J0(alpha r)), alpha = 1
    from scipy.special import j0, j1        # scipy allowed for Bessel only
    alpha = 1.0
    r = np.linspace(1e-6, 2.404, 6001)
    Bz, Bphi = j0(alpha * r), j1(alpha * r)
    # curl in cylindrical coords for (0, Bphi(r), Bz(r)):
    curl_phi = -np.gradient(Bz, r)
    curl_z = np.gradient(r * Bphi, r) / r
    ok = r > 0.05                          # keep away from the r=0 grid singularity
    res_phi = np.max(np.abs(curl_phi - alpha * Bphi)[ok])
    res_z = np.max(np.abs(curl_z - alpha * Bz)[ok])
    print("Lundquist flux rope  B = (0, J1(r), J0(r)),  testing curl B = B:")
    print(f"  max |curl_phi - B_phi| = {res_phi:.2e}"
          f"   max |curl_z - B_z| = {res_z:.2e}"
          "   (finite differences, r > 0.05)")
    for rr in (0.0, 1.0, 2.0, 2.404):
        th = np.degrees(np.arctan2(j1(alpha * rr), j0(alpha * rr)))
        print(f"  r = {rr:5.3f}: field pitch from axis = {th:6.1f} deg")
    print("curl B is PARALLEL to B everywhere -> J || B: the force-free rope.")
    print("perpendicularity was a habit of simple geometry, never a law.")


SECTIONS = {"0.1": s01, "0.2": s02, "0.3": s03,
            "0.4": s04, "0.5": s05, "0.6": s06}


def main():
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which == "all":
        for key in SECTIONS:
            SECTIONS[key]()
            print()
    elif which in SECTIONS:
        SECTIONS[which]()
    else:
        print(f"unknown section {which}; choose from {list(SECTIONS)} or all")


if __name__ == "__main__":
    main()
