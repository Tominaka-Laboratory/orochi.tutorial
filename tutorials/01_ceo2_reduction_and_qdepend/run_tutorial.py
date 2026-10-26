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
README_PATH = os.path.join(TUTORIAL_DIR, "README.md")
OUTPUT_DIR = os.path.join(TUTORIAL_DIR, "output")

LOCAL_DATA_DIR = os.path.join(TUTORIAL_DIR, "data")
PIXIA_1D_PATH = os.path.join(LOCAL_DATA_DIR, "ceo2_diagonal_1d.txt")
if not os.path.exists(PIXIA_1D_PATH):
    PIXIA_1D_PATH = os.path.join(REPO_ROOT, "orochi.pdfget", "check", "BL22XU_23A", "ceo2_pixia_data.txt")

CIF_PATH = os.path.join(LOCAL_DATA_DIR, "CeO2.cif")
if not os.path.exists(CIF_PATH):
    CIF_PATH = os.path.join(REPO_ROOT, "orochi.example", "src", "orochi", "example", "cif", "CeO2.cif")

EXP_GR_PATH = os.path.join(LOCAL_DATA_DIR, "CeO2.gr")
if not os.path.exists(EXP_GR_PATH):
    EXP_GR_PATH = os.path.join(REPO_ROOT, "orochi.example", "src", "orochi", "example", "data", "Gr", "CeO2.gr")


def find_raw_2d_dir(provided_dir=None):
    """Finds raw 2D TIFF directory from arguments, environment variables, or standard locations."""
    candidates = []
    if provided_dir:
        candidates.append(provided_dir)
    env_dir = os.environ.get("OROCHI_2D_DATA_DIR")
    if env_dir:
        candidates.append(env_dir)
    candidates.extend([
        os.path.join(TUTORIAL_DIR, "data", "raw_2d"),
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

    # 0. Pixia (CeO2 2D Detector Image Integration)
    pix = Pixia()
    pix.work_dir = out_dir
    pix.study_name = "CeO2_Pixia"
    pix["rambda"] = 0.18033
    pix["distance"] = 227.6026
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
        for fname in ["ceo2_sample_2d.tif", "ceo2.tif", "sample.tif"]:
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
        if pix["sample_file"] and os.path.exists(str(pix["sample_file"])):
            try:
                pix.read()
            except Exception as e:
                print(f"Notice: pre-reading 2D data: {e}")

    # 1. PDFget (1D Total Scattering -> S(Q), F(Q), G(r))
    pdfget = PDFget()
    pdfget.work_dir = out_dir
    pdfget.study_name = "CeO2_Reduction"
    if os.path.exists(PIXIA_1D_PATH):
        pdfget.read_file(PIXIA_1D_PATH, target="sample")
    pdfget["composition"] = "CeO2"
    pdfget["rambda"] = 0.1777
    pdfget["qmin"] = 1.0
    pdfget["qmax"] = 25.0
    pdfget["fitmin"] = 12.0
    pdfget["fitmax"] = 25.0
    pdfget["rmin"] = 0.0
    pdfget["rmax"] = 50.0

    # 2. Phase (Fluorite CeO2, Fm-3m)
    phase = Phase()
    phase.work_dir = out_dir
    phase.study_name = "CeO2_Qdepend"
    phase.read_file(CIF_PATH)
    phase["shape_type"] = "analytical"
    phase["sphere"] = [1000.0, 1000.0, 1000.0]
    phase["lattice", "min"] = [5.35, 5.35, 5.35, 89.0, 89.0, 89.0]
    phase["lattice", "max"] = [5.48, 5.48, 5.48, 91.0, 91.0, 91.0]
    phase["lattice", "optimize"] = [True, False, False, False, False, False]
    phase.set_lattice_constraints()
    phase["adp"] = [0.003, 0.008]
    phase["adp", "min"] = [0.0005, 0.0005]
    phase["adp", "max"] = [0.03, 0.05]
    phase["adp", "optimize"] = [True, True]
    phase()

    # 3. Simulator
    sim = Simulator()
    sim.work_dir = out_dir
    sim.study_name = "CeO2_Qdepend"
    sim.phase = phase
    sim["rambda"] = 0.18105
    sim["qmin"] = 0.8
    sim["qmax"] = 25.0
    sim["rmin"] = 1.5
    sim["rmax"] = 30.0
    sim["rstep"] = 0.01

    sim["scale"] = 0.85
    sim["scale", "min"] = 0.3
    sim["scale", "max"] = 1.5
    sim["scale", "optimize"] = True

    sim["qdamp"] = 0.035
    sim["qdamp", "min"] = 0.005
    sim["qdamp", "max"] = 0.08
    sim["qdamp", "optimize"] = True

    sim["qbroad"] = 0.015
    sim["qbroad", "min"] = 0.0001
    sim["qbroad", "max"] = 0.06
    sim["qbroad", "optimize"] = True

    sim["delta2"] = 1.5
    sim["delta2", "min"] = 0.0
    sim["delta2", "max"] = 4.0
    sim["delta2", "optimize"] = True

    # 4. Least-Squares Optimizer
    ls = LeastSquaresOptimizer()
    ls.work_dir = out_dir
    ls.study_name = "CeO2_Qdepend"
    ls.simulators = [sim]
    ls["fit_min"] = 1.5
    ls["fit_max"] = 30.0
    ls.read_file(EXP_GR_PATH)

    return pix, pdfget, phase, sim, ls


def run_cui(raw_2d_dir=None, output_dir=None):
    """Executes Tutorial 01 in headless CUI mode and saves figures + JSON summary."""
    out_dir = os.path.abspath(output_dir) if output_dir else OUTPUT_DIR
    os.makedirs(out_dir, exist_ok=True)
    print("=" * 72)
    print("Tutorial 01: CeO2 Data Reduction & Q-Dependent Scattering Factor Refinement")
    print("=" * 72)

    pix, pdfget, phase, sim, ls = build_modules(raw_2d_dir=raw_2d_dir, output_dir=out_dir)

    raw_dir = find_raw_2d_dir(raw_2d_dir)
    if raw_dir and pix["sample_file"] and os.path.exists(str(pix["sample_file"])):
        print(f"\n[Stage 0/3] Processing raw 2D detector images via orochi.pixia from:\n   {raw_dir}")
        print("   Running pixel corrections & diagonal sector azimuthal integration...")
        pix.run()
        integrated_1d = os.path.join(out_dir, "ceo2_pixia_integrated_1d.txt")
        pix.save_file(integrated_1d)
        print(f"   -> Successfully integrated 2D image into 1D profile ({len(pix.tt1d)} points).")
        pdfget.read_file(integrated_1d, target="sample")
    else:
        print("\n[Stage 0/3] Using pre-integrated 1D profile.")

    # Part A: Run PDFget reduction
    print("\n[1/3] Running orochi.pdfget data reduction on CeO2 total scattering data...")
    pdfget()
    pdfget.save_file(os.path.join(out_dir, "ceo2_reduced.gr"))
    print(pdfget.explain())

    # Part B: Refinement with qdepend = False (constant-Z approximation)
    print("\n[2/3] Running Least-Squares Refinement with qdepend = False (Constant-Z)...")
    sim["qdepend"] = False
    ls()
    rw_const = float(ls.Rw)
    r_grid = np.array(ls.obsx, dtype=float)
    obs_gr = np.array(ls.obsy, dtype=float)
    sim_const = np.array(ls.simy, dtype=float)
    res_const = {
        "Rw": rw_const,
        "a": float(phase["lattice"][0]),
        "Uiso_Ce": float(phase["adp"][0]),
        "Uiso_O": float(phase["adp"][1]),
        "scale": float(sim["scale"]),
        "qdamp": float(sim["qdamp"]),
        "qbroad": float(sim["qbroad"]),
        "delta2": float(sim["delta2"]),
    }
    print(f"  -> qdepend=False: Rw = {rw_const:.4f} ({rw_const*100:.2f}%), "
          f"a = {res_const['a']:.5f} A, Uiso(Ce) = {res_const['Uiso_Ce']:.5f} A^2, "
          f"Uiso(O) = {res_const['Uiso_O']:.5f} A^2")

    # Reset initial parameters before running qdepend = True
    phase["lattice"] = [5.411, 5.411, 5.411, 90.0, 90.0, 90.0]
    phase["adp"] = [0.003, 0.008]
    sim["scale"] = 0.85
    sim["qdamp"] = 0.035
    sim["qbroad"] = 0.015
    sim["delta2"] = 1.5

    # Part C: Refinement with qdepend = True (exact Q-dependent scattering factors)
    print("\n[3/3] Running Least-Squares Refinement with qdepend = True (Q-dependent DCT)...")
    sim["qdepend"] = True
    ls()
    rw_qdep = float(ls.Rw)
    sim_qdep = np.array(ls.simy, dtype=float)
    res_qdep = {
        "Rw": rw_qdep,
        "a": float(phase["lattice"][0]),
        "Uiso_Ce": float(phase["adp"][0]),
        "Uiso_O": float(phase["adp"][1]),
        "scale": float(sim["scale"]),
        "qdamp": float(sim["qdamp"]),
        "qbroad": float(sim["qbroad"]),
        "delta2": float(sim["delta2"]),
    }
    print(f"  -> qdepend=True : Rw = {rw_qdep:.4f} ({rw_qdep*100:.2f}%), "
          f"a = {res_qdep['a']:.5f} A, Uiso(Ce) = {res_qdep['Uiso_Ce']:.5f} A^2, "
          f"Uiso(O) = {res_qdep['Uiso_O']:.5f} A^2")

    summary = {"qdepend_False": res_const, "qdepend_True": res_qdep}
    with open(os.path.join(out_dir, "tutorial_01_results.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Save publication figure
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), dpi=300)

    # Panel (a): PDFget F(Q) and G(r)
    ax0 = axes[0]
    q_fq = pdfget.data["q_fq"]
    fq = pdfget.data["fq"]
    ax0.plot(q_fq, fq, color="#1f77b4", lw=1.0, label=r"Reduced $F(Q)$ (`orochi.pdfget`)")
    ax0.set_xlim(0.8, 25.0)
    ax0.set_xlabel(r"Momentum transfer $Q$ ($\mathrm{\AA^{-1}}$)")
    ax0.set_ylabel(r"$F(Q)$ ($\mathrm{\AA^{-1}}$)")
    ax0.set_title(r"(a) $\mathrm{CeO_2}$ Total Scattering $F(Q)$")
    ax0.legend(loc="upper right", frameon=False, fontsize=8.5)
    ax0.grid(True, alpha=0.25)

    # Panel (b): Constant-Z vs Q-dependent PDF refinement
    ax1 = axes[1]
    ax1.plot(r_grid, obs_gr, "ko", ms=2.2, mfc="none", alpha=0.65, label=r"Experimental $G(r)$")
    ax1.plot(r_grid, sim_const, color="#d62728", lw=1.1, alpha=0.85,
             label=rf"Constant-$Z$ (`qdepend=False`, $R_w={rw_const*100:.1f}\%$)")
    ax1.plot(r_grid, sim_qdep, color="#1f77b4", lw=1.2,
             label=rf"$Q$-dependent (`qdepend=True`, $R_w={rw_qdep*100:.1f}\%$)")
    offset = -5.5
    ax1.plot(r_grid, (obs_gr - sim_const) + offset, color="#d62728", lw=0.9, alpha=0.75,
             label="Diff (Constant-$Z$)")
    ax1.plot(r_grid, (obs_gr - sim_qdep) + offset - 2.5, color="#1f77b4", lw=0.9,
             label="Diff ($Q$-dependent)")
    ax1.axhline(offset, color="gray", ls="--", lw=0.6)
    ax1.axhline(offset - 2.5, color="gray", ls="--", lw=0.6)
    ax1.set_xlim(1.5, 30.0)
    ax1.set_xlabel(r"Interatomic distance $r$ ($\mathrm{\AA}$)")
    ax1.set_ylabel(r"$G(r)$ ($\mathrm{\AA^{-2}}$)")
    ax1.set_title(r"(b) $\mathrm{CeO_2}$ PDF Refinement: Constant-$Z$ vs. $Q$-Dependent")
    ax1.legend(loc="upper right", frameon=False, fontsize=7.8)
    ax1.grid(True, alpha=0.25)

    fig.tight_layout()
    fig_path = os.path.join(out_dir, "tutorial_01_ceo2_qdepend.pdf")
    fig.savefig(fig_path)
    fig.savefig(fig_path.replace(".pdf", ".png"))
    plt.close(fig)
    print(f"\nSaved figure to {fig_path}")
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
    ui.study_name = "Tutorial01_CeO2"
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
    parser = argparse.ArgumentParser(description="Orochi 4.0 Tutorial 01: CeO2 PDF Reduction & Q-dependence")
    parser.add_argument("--gui", action="store_true", help="Launch interactive Gradio GUI")
    parser.add_argument("--raw-2d", type=str, default=None, help="Path to raw 2D TIFF directory (ceo2.tif, empty.tif, mask.tif)")
    parser.add_argument("--output-dir", "-o", type=str, default=None, help="Directory to save output figures, data, and logs (defaults to ./output)")
    args = parser.parse_args()
    if args.gui:
        run_gui(raw_2d_dir=args.raw_2d, output_dir=args.output_dir)
    else:
        run_cui(raw_2d_dir=args.raw_2d, output_dir=args.output_dir)

