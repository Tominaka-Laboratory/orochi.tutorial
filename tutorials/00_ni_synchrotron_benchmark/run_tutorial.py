"""Orochi 4.0 Tutorial 00: Standard Metallic Nickel Synchrotron Benchmark.

Reproduces Section 3.1 and Figure 3 of the Orochi manuscript:
- 1D Total scattering data reduction (`orochi.pdfget`) with
  diagonal corner sector integration up to Q_max = 29.0 A^-1.
- Flat-panel detector geometric edge cutoff (Q_edge = 23.94 A^-1) vs. diagonal sectors.
- Real-space Rietveld-grade PDF refinement (`orochi.phase`, `orochi.pdfsim`, `orochi.fit`):
  * Short-range coordination shells (2.0 <= r <= 15.0 A): Rw ≈ 3.30%
  * Long-range structural coherence (2.0 <= r <= 50.0 A): Rw ≈ 4.57%
  * Instrumental resolution calibration (Q_damp ≈ 0.026-0.030 A^-1, Q_broad ≈ 0.013-0.019 A^-1).
"""

import argparse
import glob
import json
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# Ensure local Orochi 4.0 packages are importable when running from repository checkout
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
for src_dir in glob.glob(os.path.join(REPO_ROOT, "orochi.*", "src")):
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

from orochi.pixia import Pixia
from orochi.pdfget import PDFget
from orochi.phase import Phase
from orochi.pdfsim import Simulator
from orochi.fit import LeastSquaresOptimizer


TUTORIAL_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(TUTORIAL_DIR, "data")
OUTPUT_DIR = os.path.join(TUTORIAL_DIR, "output")
README_PATH = os.path.join(TUTORIAL_DIR, "README.md")

DIAGONAL_1D_PATH = os.path.join(DATA_DIR, "ni_diagonal_1d.txt")
FULL_1D_PATH = os.path.join(DATA_DIR, "ni_full_1d.txt")
CIF_PATH = os.path.join(DATA_DIR, "ni.cif")


def find_raw_2d_dir(provided_dir=None):
    """Finds raw 2D TIFF directory from arguments, environment variables, or standard locations."""
    candidates = []
    if provided_dir:
        candidates.append(provided_dir)
    env_dir = os.environ.get("OROCHI_2D_DATA_DIR")
    if env_dir:
        candidates.append(env_dir)
    candidates.extend([
        os.path.join(DATA_DIR, "raw_2d"),
    ])
    for c in candidates:
        if c and os.path.isdir(c):
            return os.path.abspath(c)
    return None


def build_modules(raw_2d_dir=None, output_dir=None):
    """Initializes and configures Pixia, PDFget, Phase, Simulator, and LeastSquaresOptimizer."""
    out_dir = os.path.abspath(output_dir) if output_dir else OUTPUT_DIR
    os.makedirs(out_dir, exist_ok=True)
    raw_dir = find_raw_2d_dir(raw_2d_dir)

    # 0. Pixia (2D Detector Image Integration)
    pix = Pixia()
    pix.work_dir = out_dir
    pix.study_name = "Ni_Pixia"
    pix["rambda"] = 0.18033
    pix["distance"] = 227.575
    pix["x0"] = 1025.6
    pix["y0"] = 1053.13
    pix["tiltx"] = 0.0041
    pix["tilty"] = 0.0891
    pix["background_scale"] = 1.0
    pix.set_azimuthal_mode("diagonals", width=18.0)
    pix["ttmin"] = 0.78
    pix["ttmax"] = 50.0
    pix["ttstep"] = 0.002
    if raw_dir:
        for fname in ["ni_sample_2d.tif", "ni.tif", "sample.tif"]:
            p = os.path.join(raw_dir, fname)
            if os.path.exists(p):
                pix["sample_file"] = p
                break
        for fname in ["empty_background_2d.tif", "empty.tif", "background.tif"]:
            p = os.path.join(raw_dir, fname)
            if os.path.exists(p):
                pix["background_file"] = p
                break
        for fname in ["detector_mask_2d.tif", "mask.tif"]:
            p = os.path.join(raw_dir, fname)
            if os.path.exists(p):
                pix["mask_file"] = p
                break

    # 1. PDFget (1D Total Scattering -> S(Q), F(Q), G(r))
    pdfget = PDFget()
    pdfget.work_dir = out_dir
    pdfget.study_name = "Ni_Reduction"
    if os.path.exists(DIAGONAL_1D_PATH):
        pdfget.read_file(DIAGONAL_1D_PATH, target="sample")
    pdfget["composition"] = "Ni"
    pdfget["rambda"] = 0.18033
    pdfget["qmin"] = 0.8
    pdfget["qmax"] = 29.0
    pdfget["fitmin"] = 18.0
    pdfget["fitmax"] = 28.5
    pdfget["rmin"] = 0.0
    pdfget["rmax"] = 50.0
    pdfget["padding"] = 5
    pdfget["lorch"] = 5.0
    pdfget["number_density"] = 0.069206

    # 2. Phase (FCC Ni, Fm-3m, a = 3.5238 A)
    phase = Phase()
    phase.work_dir = out_dir
    phase.study_name = "Ni_Benchmark"
    if os.path.exists(CIF_PATH):
        phase.read_file(CIF_PATH)
    phase["shape_type"] = "analytical"
    phase["sphere"] = [1000.0, 1000.0, 1000.0]
    phase["lattice", "min"] = [3.4, 3.4, 3.4, 89.0, 89.0, 89.0]
    phase["lattice", "max"] = [3.6, 3.6, 3.6, 91.0, 91.0, 91.0]
    phase["lattice", "optimize"] = [True, False, False, False, False, False]
    phase.set_lattice_constraints()
    phase["adp"] = [0.004]
    phase["adp", "min"] = [0.0005]
    phase["adp", "max"] = [0.03]
    phase["adp", "optimize"] = [True]
    phase()

    # 3. Simulator (Exact Q-dependent scattering factors and Correlated Motion)
    sim = Simulator()
    sim.work_dir = out_dir
    sim.study_name = "Ni_Benchmark"
    sim.phase = phase
    sim["rambda"] = 0.18033
    sim["rambda", "min"] = 0.1
    sim["rambda", "max"] = 2.0
    sim["rambda", "optimize"] = False

    sim["qmin"] = 0.8
    sim["qmax"] = 29.0
    sim["rmin"] = 0.0
    sim["rmax"] = 15.0
    sim["rstep"] = 0.01
    sim["qdepend"] = True

    sim["scale"] = 0.93
    sim["scale", "min"] = 0.5
    sim["scale", "max"] = 1.5
    sim["scale", "optimize"] = True

    sim["qdamp"] = 0.03
    sim["qdamp", "min"] = 0.005
    sim["qdamp", "max"] = 0.08
    sim["qdamp", "optimize"] = True

    sim["qbroad"] = 0.018
    sim["qbroad", "min"] = 0.0001
    sim["qbroad", "max"] = 0.06
    sim["qbroad", "optimize"] = True

    sim["delta1"] = 0.0
    sim["delta1", "min"] = 0.0
    sim["delta1", "max"] = 5.0
    sim["delta1", "optimize"] = False

    sim["delta2"] = 2.2
    sim["delta2", "min"] = 0.0
    sim["delta2", "max"] = 5.0
    sim["delta2", "optimize"] = True

    # 4. Least-Squares Optimizer
    ls = LeastSquaresOptimizer()
    ls.work_dir = out_dir
    ls.study_name = "Ni_Benchmark"
    ls.simulators = [sim]
    ls["fit_min"] = 2.0
    ls["fit_max"] = 15.0

    return pix, pdfget, phase, sim, ls


def run_cui(raw_2d_dir=None, output_dir=None):
    """Executes Tutorial 00 in headless CUI mode and saves figures + JSON summary."""
    out_dir = os.path.abspath(output_dir) if output_dir else OUTPUT_DIR
    os.makedirs(out_dir, exist_ok=True)
    print("=" * 76)
    print("Tutorial 00: Standard Metallic Nickel Benchmark: Instrumental Calibration")
    print("=" * 76)

    pix, pdfget, phase, sim, ls = build_modules(raw_2d_dir=raw_2d_dir, output_dir=out_dir)

    raw_dir = find_raw_2d_dir(raw_2d_dir)
    if raw_dir and pix["sample_file"] and os.path.exists(str(pix["sample_file"])):
        print(f"\n[Stage 0/3] Processing raw 2D detector images via orochi.pixia from:\n   {raw_dir}")
        print("   Running pixel corrections & diagonal sector azimuthal integration...")
        pix.run()
        integrated_1d = os.path.join(out_dir, "ni_pixia_integrated_1d.txt")
        pix.save_file(integrated_1d)
        print(f"   -> Successfully integrated 2D image into 1D profile ({len(pix.tt1d)} points).")
        pdfget.read_file(integrated_1d, target="sample")
    else:
        print("\n[Stage 0/3] Using pre-integrated 1D profile (data/ni_diagonal_1d.txt).")

    # Part A: Run PDFget reduction on diagonal sector profile
    print("\n[1/3] Running orochi.pdfget data reduction on diagonal sector profile...")
    pdfget()
    reduced_gr_path = os.path.join(out_dir, "ni_reduced.gr")
    pdfget.save_file(reduced_gr_path)
    ls.read_file(reduced_gr_path)

    # Also run reduction on full 360-deg integration profile for edge cutoff comparison
    q_full, fq_full = None, None
    if os.path.exists(FULL_1D_PATH):
        pdfget_full = PDFget()
        pdfget_full.read_file(FULL_1D_PATH, target="sample")
        pdfget_full["composition"] = "Ni"
        pdfget_full["rambda"] = 0.18033
        pdfget_full["qmin"] = 0.8
        pdfget_full["qmax"] = 29.0
        pdfget_full["fitmin"] = 18.0
        pdfget_full["fitmax"] = 28.5
        pdfget_full["padding"] = 5
        pdfget_full["lorch"] = 5.0
        pdfget_full["number_density"] = 0.069206
        pdfget_full()
        q_full = np.array(pdfget_full.data.get("q_fq", []))
        fq_full = np.array(pdfget_full.data.get("fq", []))

    q_diag = np.array(pdfget.data.get("q_fq", []))
    fq_diag = np.array(pdfget.data.get("fq", []))
    r_full = np.array(ls.obsx, dtype=float)
    gr_full = np.array(ls.obsy, dtype=float)

    # Part B: Short-range refinement (2.0 <= r <= 15.0 A)
    print("\n[2/3] Running Short-Range Rietveld-Grade PDF Refinement (2.0 <= r <= 15.0 A)...")
    sim["rmin"] = 2.0
    sim["rmax"] = 15.0
    sim["rstep"] = 0.01
    ls["fit_min"] = 2.0
    ls["fit_max"] = 15.0
    ls()

    rw_short = float(ls.Rw)
    r_short = np.array(ls.obsx, dtype=float)
    obs_short = np.array(ls.obsy, dtype=float)
    calc_short = np.array(ls.simy, dtype=float)

    res_short = {
        "Rw_percent": rw_short * 100.0,
        "lattice_a_A": float(phase["lattice"][0]),
        "Uiso_A2": float(phase["adp"][0]),
        "scale": float(sim["scale"]),
        "qdamp_A_inv": float(sim["qdamp"]),
        "qbroad_A_inv": float(sim["qbroad"]),
        "delta2": float(sim["delta2"]),
    }
    print(f"  -> Short-Range Refinement (2.0 - 15.0 A):")
    print(f"     Rw     = {res_short['Rw_percent']:.2f}% (manuscript: 3.30%)")
    print(f"     a      = {res_short['lattice_a_A']:.5f} A (NIST certified: 3.5238 A)")
    print(f"     Uiso   = {res_short['Uiso_A2']:.5f} A^2")
    print(f"     Qdamp  = {res_short['qdamp_A_inv']:.4f} A^-1")
    print(f"     Qbroad = {res_short['qbroad_A_inv']:.4f} A^-1")
    print(f"     delta2 = {res_short['delta2']:.2f}")

    # Part C: Long-range structural coherence refinement (2.0 <= r <= 50.0 A)
    print("\n[3/3] Running Long-Range Structural Coherence Refinement (2.0 <= r <= 50.0 A)...")
    sim["rmin"] = 2.0
    sim["rmax"] = 50.0
    sim["rstep"] = 0.02
    ls["fit_min"] = 2.0
    ls["fit_max"] = 50.0

    # Start from calibrated short-range parameters
    phase["lattice"] = [res_short["lattice_a_A"]] * 3 + [90.0] * 3
    phase["adp"] = [res_short["Uiso_A2"]]
    sim["scale"] = 0.915
    sim["qdamp"] = 0.026
    sim["qbroad"] = 0.013
    sim["delta2"] = 2.5
    ls()

    rw_long = float(ls.Rw)
    r_long = np.array(ls.obsx, dtype=float)
    obs_long = np.array(ls.obsy, dtype=float)
    calc_long = np.array(ls.simy, dtype=float)

    res_long = {
        "Rw_percent": rw_long * 100.0,
        "lattice_a_A": float(phase["lattice"][0]),
        "Uiso_A2": float(phase["adp"][0]),
        "scale": float(sim["scale"]),
        "qdamp_A_inv": float(sim["qdamp"]),
        "qbroad_A_inv": float(sim["qbroad"]),
        "delta2": float(sim["delta2"]),
    }
    print(f"  -> Long-Range Refinement (2.0 - 50.0 A):")
    print(f"     Rw     = {res_long['Rw_percent']:.2f}% (manuscript: 4.57%)")
    print(f"     a      = {res_long['lattice_a_A']:.5f} A")
    print(f"     Uiso   = {res_long['Uiso_A2']:.5f} A^2")
    print(f"     Qdamp  = {res_long['qdamp_A_inv']:.4f} A^-1")
    print(f"     Qbroad = {res_long['qbroad_A_inv']:.4f} A^-1")
    print(f"     delta2 = {res_long['delta2']:.2f}")

    # Save summary JSON
    summary = {
        "standard": "Metallic Nickel (Ni)",
        "measurement_type": "Synchrotron high-energy X-ray total scattering",
        "incident_wavelength_A": 0.18033,
        "incident_energy_keV": 68.48,
        "detector_edge_cutoff_Q_A_inv": 23.94,
        "diagonal_Qmax_A_inv": 29.0,
        "short_range_refinement": res_short,
        "long_range_refinement": res_long,
    }
    summary_path = os.path.join(out_dir, "tutorial_00_results.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Plot publication figure reproducing Figure 3 of the manuscript
    fig, axes = plt.subplots(3, 1, figsize=(8.5, 9.8), dpi=300)

    # Theoretical average density slope: -4 * pi * rho0 * r (rho0 = 0.0914 A^-3 for FCC Ni)
    rho0 = 0.0914
    r_dense = np.linspace(0.0, 50.0, 1000)
    density_slope = -4.0 * np.pi * rho0 * r_dense

    # Panel (a): F(Q) comparison
    ax0 = axes[0]
    if q_full is not None and fq_full is not None:
        ax0.plot(q_full, fq_full, color="#1f77b4", lw=0.9, alpha=0.8,
                 label=r"Full azimuthal integration ($360^\circ$, edge truncation)")
    ax0.plot(q_diag, fq_diag, color="#d62728", lw=1.0,
             label=r"Automated diagonal sector selection ($\beta = \pm 45^\circ \pm 18^\circ$)")
    ax0.axvline(23.94, color="gray", ls=":", lw=1.2, label=r"Sensor edge boundary $Q_{\mathrm{edge}} = 23.94\ \mathrm{\AA}^{-1}$")
    ax0.set_xlim(0.8, 30.0)
    ax0.set_xlabel(r"Momentum transfer $Q$ ($\mathrm{\AA^{-1}}$)", fontsize=9.5)
    ax0.set_ylabel(r"$F(Q)$ ($\mathrm{\AA^{-1}}$)", fontsize=9.5)
    ax0.set_title(r"(a) Structure factor $F(Q)$ on Flat-Panel Area Detector", fontsize=10.5, fontweight="bold")
    ax0.legend(loc="upper right", frameon=False, fontsize=8.0)
    ax0.grid(True, alpha=0.25)

    # Panel (b): Short-range refinement (2.0 - 15.0 A)
    ax1 = axes[1]
    # Observed profile plotted from r = 0 to evaluate low-r baseline
    mask_disp_short = r_full <= 15.0
    ax1.plot(r_full[mask_disp_short], gr_full[mask_disp_short], "bo", ms=2.2, mfc="none", alpha=0.6, label="Observed $G(r)$ (from $r=0$)")
    ax1.plot(r_dense[r_dense <= 15.0], density_slope[r_dense <= 15.0], color="gray", ls="--", lw=1.0, label=r"Density baseline ($-4\pi\rho_0 r$)")
    ax1.plot(r_short, calc_short, color="#d62728", lw=1.1, label=rf"Refined model ($R_w = {res_short['Rw_percent']:.2f}\%$)")
    offset = -18.0
    diff_short = obs_short - calc_short
    ax1.plot(r_short, diff_short + offset, color="#2ca02c", lw=0.9, label=r"Difference ($G_{\mathrm{obs}} - G_{\mathrm{calc}}$)")
    ax1.axhline(offset, color="gray", ls=":", lw=0.7)
    ax1.set_xlim(0.0, 15.0)
    ax1.set_xlabel(r"Interatomic distance $r$ ($\mathrm{\AA}$)", fontsize=9.5)
    ax1.set_ylabel(r"$G(r)$ ($\mathrm{\AA^{-2}}$)", fontsize=9.5)
    ax1.set_title(r"(b) Short-range coordination profile refinement ($r \in [2.0, 15.0]\ \mathrm{\AA}$)", fontsize=10.5, fontweight="bold")
    ax1.legend(loc="upper right", frameon=False, fontsize=8.0)
    ax1.grid(True, alpha=0.25)

    # Panel (c): Long-range refinement (2.0 - 50.0 A)
    ax2 = axes[2]
    mask_disp_long = r_full <= 50.0
    ax2.plot(r_full[mask_disp_long], gr_full[mask_disp_long], "bo", ms=1.6, mfc="none", alpha=0.45, label="Observed $G(r)$")
    ax2.plot(r_dense[r_dense <= 50.0], density_slope[r_dense <= 50.0], color="gray", ls="--", lw=1.0, label=r"Density baseline ($-4\pi\rho_0 r$)")
    ax2.plot(r_long, calc_long, color="#d62728", lw=1.0, label=rf"Refined model ($R_w = {res_long['Rw_percent']:.2f}\%$)")
    diff_long = obs_long - calc_long
    ax2.plot(r_long, diff_long + offset, color="#2ca02c", lw=0.8, label=r"Difference ($G_{\mathrm{obs}} - G_{\mathrm{calc}}$)")
    ax2.axhline(offset, color="gray", ls=":", lw=0.7)
    ax2.set_xlim(0.0, 50.0)
    ax2.set_xlabel(r"Interatomic distance $r$ ($\mathrm{\AA}$)", fontsize=9.5)
    ax2.set_ylabel(r"$G(r)$ ($\mathrm{\AA^{-2}}$)", fontsize=9.5)
    ax2.set_title(r"(c) Long-range macroscopic structural coherence ($r \in [2.0, 50.0]\ \mathrm{\AA}$)", fontsize=10.5, fontweight="bold")
    ax2.legend(loc="upper right", frameon=False, fontsize=8.0)
    ax2.grid(True, alpha=0.25)

    fig.tight_layout()
    fig_path = os.path.join(out_dir, "tutorial_00_ni_benchmark.pdf")
    fig.savefig(fig_path)
    fig.savefig(fig_path.replace(".pdf", ".png"))
    plt.close(fig)
    print(f"\nSaved publication figure to {fig_path}")

    return summary


def run_gui(raw_2d_dir=None, output_dir=None):
    """Launches the interactive Gradio GUI with the shared README.md in the Lesson Note tab."""
    from orochi.ui.ui import BaseUI as UI
    from orochi.view.model_viewer import ModelViewer

    out_dir = os.path.abspath(output_dir) if output_dir else OUTPUT_DIR
    os.makedirs(out_dir, exist_ok=True)

    pix, pdfget, phase, sim, ls = build_modules(raw_2d_dir=raw_2d_dir, output_dir=out_dir)
    viewer = ModelViewer()
    viewer.phase = phase
    phase.viewer = viewer
    phase()

    ui = UI(theme="Orochi")
    ui.work_dir = out_dir
    ui.study_name = "Tutorial00_Ni_Benchmark"
    ui["server"] = "127.0.0.1"

    ui.add_instruction_panel(title="Lesson Note", markdown_file=README_PATH)
    ui.add_pixia_panel(
        module=pix,
        keys=[
            "rambda", "distance", "x0", "y0", "tiltx", "tilty",
            "ttmin", "ttmax", "ttstep", "outlier", "background_scale"
        ],
        title="2D -> 1D (Pixia)",
        downstream_pdfget=pdfget,
    )
    ui.add_pdfget_panel(module=pdfget, title="1D -> PDF (PDFget)")
    ui.add_phase_panel(
        module=phase,
        keys=["sphere", "pbc"],
        const_keys=["spherical_constraints", "lattice_constraints", "symmetry_constraints"],
        title="Structure (Phase)",
    )
    ui.add_simulation_panel(
        module=sim,
        keys=["rmin", "rmax", "rstep", "qmax", "qmin", "scale", "qdamp", "qbroad", "delta1", "delta2", "rambda", "qdepend"],
        title="Simulation (PDFsim)",
    )
    ui.add_least_squares_panel(
        module=ls,
        keys=["fit_min", "fit_max", "max_nfev", "ftol"],
        title="Least Squares (Fit)",
    )
    ui.add_log_panel(title="Execution Log")
    ui()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Orochi 4.0 Tutorial 00: Standard Metallic Nickel Synchrotron Benchmark"
    )
    parser.add_argument("--gui", action="store_true", help="Launch interactive Gradio GUI")
    parser.add_argument("--raw-2d", type=str, default=None, help="Path to raw 2D TIFF directory (ni.tif, empty.tif, mask.tif)")
    parser.add_argument("--output-dir", "-o", type=str, default=None, help="Directory to save output figures, data, and logs (defaults to ./output)")
    args = parser.parse_args()
    if args.gui:
        run_gui(raw_2d_dir=args.raw_2d, output_dir=args.output_dir)
    else:
        run_cui(raw_2d_dir=args.raw_2d, output_dir=args.output_dir)

