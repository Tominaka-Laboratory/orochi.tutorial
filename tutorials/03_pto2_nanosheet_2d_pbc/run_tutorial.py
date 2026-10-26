import argparse
import glob
import json
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# Ensure local Orochi 4.0 packages are importable
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
for src_dir in glob.glob(os.path.join(REPO_ROOT, "orochi.*", "src")):
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

from orochi.phase import Phase
from orochi.pdfsim import Simulator
from orochi.fit import LeastSquaresOptimizer

TUTORIAL_DIR = os.path.dirname(os.path.abspath(__file__))
README_PATH = os.path.join(TUTORIAL_DIR, "README.md")
OUTPUT_DIR = os.path.join(TUTORIAL_DIR, "output")

LOCAL_DATA_DIR = os.path.join(TUTORIAL_DIR, "data")
CIF_PATH = os.path.join(LOCAL_DATA_DIR, "PtO2_trigonal_single_layer.cif")
if not os.path.exists(CIF_PATH):
    CIF_PATH = os.path.join(
        REPO_ROOT, "orochi.example", "src", "orochi", "example", "cif", "PtO2_trigonal_single_layer.cif"
    )
EXP_GR_PATH = os.path.join(LOCAL_DATA_DIR, "PtO2_nanosheet.gr")
if not os.path.exists(EXP_GR_PATH):
    EXP_GR_PATH = os.path.join(
        REPO_ROOT, "orochi.example", "src", "orochi", "example", "data", "Gr", "PtO2_nanosheet.gr"
    )


def build_modules(pbc=(True, True, False), qmin=0.7, output_dir=None):
    """Initializes Phase, Simulator, and LeastSquaresOptimizer for the 2D PtO2 nanosheet."""
    out_dir = os.path.abspath(output_dir) if output_dir else OUTPUT_DIR
    os.makedirs(out_dir, exist_ok=True)

    phase = Phase()
    phase.work_dir = out_dir
    phase.study_name = "PtO2_Nanosheet"
    phase.read_file(CIF_PATH)
    phase["shape_type"] = "analytical"
    phase["pbc"] = list(pbc)
    phase["sphere"] = [35.0, 35.0, 35.0]
    phase.set_spherical_constraints()
    phase.set_lattice_constraints()
    phase.set_elemental_adp_constraints()

    lat0 = np.array(phase["lattice"], dtype=float)
    phase["lattice", "min"] = (lat0 - np.array([0.2, 0.2, 0.2, 1.0, 1.0, 1.0])).tolist()
    phase["lattice", "max"] = (lat0 + np.array([0.2, 0.2, 0.2, 1.0, 1.0, 1.0])).tolist()
    phase["lattice", "optimize"] = [True, False, False, False, False, False]

    phase["adp"] = [0.005, 0.008, 0.008]
    phase["adp", "min"] = [0.0005, 0.0005, 0.0005]
    phase["adp", "max"] = [0.05, 0.08, 0.08]
    phase["adp", "optimize"] = [True, True, False]

    phase["sphere", "optimize"] = [True, False, False]
    phase["sphere", "min"] = [10.0, 10.0, 10.0]
    phase["sphere", "max"] = [100.0, 100.0, 100.0]
    phase()

    sim = Simulator()
    sim.work_dir = out_dir
    sim.study_name = "PtO2_Nanosheet"
    sim.phase = phase
    sim["rambda"] = 0.18105
    sim["qmin"] = float(qmin)
    sim["qmax"] = 26.0
    sim["rmin"] = 1.2
    sim["rmax"] = 15.5
    sim["rstep"] = 0.01
    sim["qdepend"] = True

    sim["scale"] = 1.0
    sim["scale", "min"] = 0.2
    sim["scale", "max"] = 3.0
    sim["scale", "optimize"] = True

    sim["qdamp"] = 0.03
    sim["qdamp", "min"] = 0.005
    sim["qdamp", "max"] = 0.08
    sim["qdamp", "optimize"] = True

    sim["delta2"] = 2.0
    sim["delta2", "min"] = 0.0
    sim["delta2", "max"] = 6.0
    sim["delta2", "optimize"] = True

    ls = LeastSquaresOptimizer()
    ls.work_dir = out_dir
    ls.study_name = "PtO2_Nanosheet"
    ls.simulators = [sim]
    ls.read_file(EXP_GR_PATH)
    ls["fit_min"] = 1.5
    ls["fit_max"] = 15.0
    sim["rmin"] = 1.2
    sim["rmax"] = 15.5

    return phase, sim, ls


def run_cui(output_dir=None):
    """Executes Tutorial 03 in CUI mode, comparing 3D PBC vs 2D PBC + finite-Qmin baseline on PtO2 nanosheets."""
    out_dir = os.path.abspath(output_dir) if output_dir else OUTPUT_DIR
    os.makedirs(out_dir, exist_ok=True)
    print("=" * 76)
    print("Tutorial 03: 2D PtO2 Nanosheet PBC & Finite-Qmin Baseline Density Refinement")
    print("=" * 76)

    # 1. Refine with 2D Nanosheet PBC (pbc = [True, True, False])
    print("\n[1/2] Running Least-Squares Refinement with 2D PBC (pbc = [True, True, False])...")
    phase_2d, sim_2d, ls_2d = build_modules(pbc=(True, True, False), qmin=0.7, output_dir=out_dir)
    ls_2d()
    rw_2d = float(np.sqrt(np.sum((ls_2d.obsy - ls_2d.simy) ** 2) / np.sum(ls_2d.obsy ** 2)))
    r_grid = np.array(ls_2d.obsx, dtype=float)
    obs_gr = np.array(ls_2d.obsy, dtype=float)
    sim_gr_2d = np.array(ls_2d.simy, dtype=float)
    density_2d = sim_2d.density.copy()
    sim_r_2d = sim_2d.r.copy()

    a_2d = float(phase_2d["lattice"][0])
    uiso_pt_2d = float(phase_2d["adp"][0])
    uiso_o_2d = float(phase_2d["adp"][1])
    d_2d = float(phase_2d["sphere"][0])
    scale_2d = float(sim_2d["scale"])
    qdamp_2d = float(sim_2d["qdamp"])
    delta2_2d = float(sim_2d["delta2"])

    print(f"  -> 2D PBC: Rw = {rw_2d:.4f} ({rw_2d*100:.2f}%), "
          f"a = {a_2d:.4f} A, D = {d_2d:.2f} A, Uiso(Pt) = {uiso_pt_2d:.5f} A^2")

    # 2. Refine with 3D periodic assumption (pbc = [True, True, True])
    print("\n[2/2] Running Least-Squares Refinement with 3D PBC (pbc = [True, True, True])...")
    phase_3d, sim_3d, ls_3d = build_modules(pbc=(True, True, True), qmin=0.7, output_dir=out_dir)
    ls_3d()
    rw_3d = float(np.sqrt(np.sum((ls_3d.obsy - ls_3d.simy) ** 2) / np.sum(ls_3d.obsy ** 2)))
    sim_gr_3d = np.array(ls_3d.simy, dtype=float)
    density_3d = sim_3d.density.copy()
    print(f"  -> 3D PBC: Rw = {rw_3d:.4f} ({rw_3d*100:.2f}%), "
          f"a = {phase_3d['lattice'][0]:.4f} A, D = {phase_3d['sphere'][0]:.2f} A")

    summary = {
        "pbc_2D": {
            "Rw": rw_2d,
            "a": a_2d,
            "diameter_A": d_2d,
            "Uiso_Pt": uiso_pt_2d,
            "Uiso_O": uiso_o_2d,
            "scale": scale_2d,
            "qdamp": qdamp_2d,
            "delta2": delta2_2d,
        },
        "pbc_3D": {
            "Rw": rw_3d,
            "a": float(phase_3d["lattice"][0]),
            "c": float(phase_3d["lattice"][2]),
            "diameter_A": float(phase_3d["sphere"][0]),
            "Uiso_Pt": float(phase_3d["adp"][0]),
            "scale": float(sim_3d["scale"]),
        },
    }
    with open(os.path.join(out_dir, "tutorial_03_results.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Save publication-quality 2-panel figure
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), dpi=300)

    # Panel (a): Pair correlation g(r) and baseline density rho_base(r)
    ax0 = axes[0]
    ax0.plot(sim_r_2d, sim_2d.gr, color="#7f7f7f", lw=0.9, alpha=0.7, label=r"Unnormalized $g(r)$ (2D monolayer)")
    ax0.plot(sim_r_2d, density_3d, color="#d62728", ls="--", lw=1.2,
             label=r"3D linear baseline $4\pi r \rho_0$ (`pbc=[T,T,T]`)")
    ax0.plot(sim_r_2d, density_2d, color="#1f77b4", lw=1.3,
             label=r"2D finite-$Q_{\mathrm{min}}$ sinc baseline (`pbc=[T,T,F]`)")
    ax0.set_xlim(1.5, 15.0)
    ax0.set_xlabel(r"Interatomic distance $r$ ($\mathrm{\AA}$)")
    ax0.set_ylabel(r"$g(r)$ and baseline $\rho_{\mathrm{base}}(r)$ ($\mathrm{\AA^{-2}}$)")
    ax0.set_title(r"(a) 2D $\mathrm{PtO_2}$ Nanosheet Baseline Density Filtering")
    ax0.legend(loc="upper right", frameon=False, fontsize=8.0)
    ax0.grid(True, alpha=0.25)

    # Panel (b): Experimental vs Refined G(r) for 2D PtO2 nanosheet
    ax1 = axes[1]
    ax1.plot(r_grid, obs_gr, "ko", ms=2.4, mfc="none", alpha=0.7, label=r"Experimental $\mathrm{PtO_2}$ nanosheet $G(r)$")
    ax1.plot(r_grid, sim_gr_3d, color="#d62728", ls="--", lw=1.0, alpha=0.85,
             label=rf"3D PBC fit (`pbc=[T,T,T]`, $R_w={rw_3d*100:.1f}\%$)")
    ax1.plot(r_grid, sim_gr_2d, color="#1f77b4", lw=1.2,
             label=rf"2D PBC fit (`pbc=[T,T,F]`, $R_w={rw_2d*100:.1f}\%$)")
    offset = -6.0
    ax1.plot(r_grid, (obs_gr - sim_gr_2d) + offset, color="#2ca02c", lw=0.9,
             label=r"Diff ($G_{\mathrm{obs}} - G_{2\mathrm{D}}$)")
    ax1.axhline(offset, color="gray", ls="--", lw=0.6)
    ax1.set_xlim(1.5, 15.0)
    ax1.set_xlabel(r"Interatomic distance $r$ ($\mathrm{\AA}$)")
    ax1.set_ylabel(r"$G(r)$ ($\mathrm{\AA^{-2}}$)")
    ax1.set_title(r"(b) 2D $\mathrm{PtO_2}$ Nanosheet PDF Refinement")
    ax1.legend(loc="upper right", frameon=False, fontsize=8.0)
    ax1.grid(True, alpha=0.25)

    fig.tight_layout()
    fig_path = os.path.join(out_dir, "tutorial_03_pto2_nanosheet.pdf")
    fig.savefig(fig_path)
    fig.savefig(fig_path.replace(".pdf", ".png"))
    plt.close(fig)
    print(f"\nSaved figure to {fig_path}")
    return summary


def run_gui(output_dir=None):
    """Launches the interactive Gradio GUI for Tutorial 03."""
    from orochi.ui.ui import BaseUI as UI
    from orochi.view.model_viewer import ModelViewer

    out_dir = os.path.abspath(output_dir) if output_dir else OUTPUT_DIR
    os.makedirs(out_dir, exist_ok=True)

    phase, sim, ls = build_modules(pbc=(True, True, False), output_dir=out_dir)
    viewer = ModelViewer()
    viewer.phase = phase
    phase.viewer = viewer
    phase()

    ui = UI(theme="Orochi")
    ui.work_dir = out_dir
    ui.study_name = "Tutorial03_PtO2_Nanosheet"
    ui["server"] = "127.0.0.1"

    ui.add_instruction_panel(title="Lesson Note", markdown_file=README_PATH)
    ui.add_phase_panel(
        module=phase,
        keys=["shape_type", "pbc", "sphere"],
        const_keys=["spherical_constraints", "lattice_constraints", "symmetry_constraints"],
        title="2D Nanosheet (Phase)",
    )
    ui.add_simulation_panel(
        module=sim,
        keys=["rmin", "rmax", "rstep", "qmax", "qmin", "scale", "qdamp", "delta2", "rambda", "qdepend"],
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
    parser = argparse.ArgumentParser(description="Orochi 4.0 Tutorial 03: 2D PtO2 Nanosheet PDF Refinement")
    parser.add_argument("--gui", action="store_true", help="Launch interactive web GUI")
    parser.add_argument("--output-dir", "-o", type=str, default=None, help="Directory to save output figures, data, and logs (defaults to ./output)")
    args = parser.parse_args()

    if args.gui:
        run_gui(output_dir=args.output_dir)
    else:
        run_cui(output_dir=args.output_dir)


