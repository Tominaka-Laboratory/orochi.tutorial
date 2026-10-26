import argparse
import glob
import json
import os
import sys
import numpy as np
import matplotlib.pyplot as plt

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
CIF_PATH = os.path.join(LOCAL_DATA_DIR, "CeO2.cif")
if not os.path.exists(CIF_PATH):
    CIF_PATH = os.path.join(
        REPO_ROOT, "orochi.example", "src", "orochi", "example", "cif", "CeO2.cif"
    )


def make_simulator(shape_type="sphere", diameter=25.0, output_dir=None):
    """Creates a Phase + Simulator pair configured for either explicit or analytical nanoparticle PDF."""
    out_dir = os.path.abspath(output_dir) if output_dir else OUTPUT_DIR
    os.makedirs(out_dir, exist_ok=True)
    phase = Phase()
    phase.work_dir = out_dir
    phase.study_name = f"CeO2_{shape_type}"
    phase.read_file(CIF_PATH)
    phase["adp"] = [0.0035, 0.0085]
    phase["shape_type"] = shape_type
    phase["diameter"] = float(diameter)
    phase()

    sim = Simulator()
    sim.work_dir = out_dir
    sim.study_name = f"CeO2_{shape_type}"
    sim.phase = phase
    sim["rambda"] = 0.18105
    sim["qmin"] = 0.8
    sim["qmax"] = 25.0
    sim["rmin"] = 1.5
    sim["rmax"] = 26.0
    sim["rstep"] = 0.01
    sim["qdepend"] = True
    sim["scale"] = 1.0
    sim["qdamp"] = 0.03
    sim["qbroad"] = 0.012
    sim["delta2"] = 1.5
    return phase, sim


def run_cui(output_dir=None):
    """Executes Tutorial 02 in CUI mode, comparing explicit O-terminated vs analytical spherical CeO2 nanoparticles."""
    out_dir = os.path.abspath(output_dir) if output_dir else OUTPUT_DIR
    os.makedirs(out_dir, exist_ok=True)
    print("=" * 76)
    print("Tutorial 02: Explicit O-Terminated Nanoparticle vs. Analytical Sphere (CeO2)")
    print("=" * 76)

    nominal_diameter = 25.0

    # 1. Explicit O-terminated nanoparticle (shape_type = "sphere")
    print(f"\n[1/3] Building explicit coordination-preserving CeO2 nanoparticle (D = {nominal_diameter:.1f} A)...")
    phase_exp, sim_exp = make_simulator(shape_type="sphere", diameter=nominal_diameter, output_dir=out_dir)
    sim_exp()

    symbols = phase_exp.model["symbol"]
    xyz = phase_exp.model["xyz"]
    radii_from_center = np.linalg.norm(xyz, axis=1)
    r_ce = radii_from_center[symbols == "Ce"]
    r_o = radii_from_center[symbols == "O"]
    comp = {str(k): float(v) for k, v in phase_exp.get_model_composition().items()}
    n_ce = int(comp.get("Ce", 0))
    n_o = int(comp.get("O", 0))

    print(f"  -> Explicit cluster composition: Ce_{n_ce} O_{n_o} ({n_ce + n_o} atoms, O/Ce = {n_o/n_ce:.3f})")
    print(f"  -> Max radial distance from center: R_Ce,max = {r_ce.max():.2f} A (D_Ce = {2*r_ce.max():.2f} A), "
          f"R_O,max = {r_o.max():.2f} A (D_O = {2*r_o.max():.2f} A)")

    # 2. Analytical uniform sphere at the same nominal diameter (D = 25.0 A)
    print(f"\n[2/3] Simulating analytical uniform sphere at identical nominal diameter (D = {nominal_diameter:.1f} A)...")
    phase_ana_fixed, sim_ana_fixed = make_simulator(shape_type="analytical", diameter=nominal_diameter, output_dir=out_dir)
    sim_ana_fixed()

    r_grid = sim_exp.r
    gr_exp = sim_exp.Gr.copy()
    gr_ana_fixed = sim_ana_fixed.Gr.copy()

    # Compute unrefined Rw between explicit nanoparticle and nominal D=25 A analytical sphere
    rw_nominal = float(np.sqrt(np.sum((gr_exp - gr_ana_fixed) ** 2) / np.sum(gr_exp ** 2)))
    print(f"  -> Direct comparison at nominal D = {nominal_diameter:.1f} A: Rw = {rw_nominal:.4f} ({rw_nominal*100:.2f}%)")

    # 3. Fit the explicit O-terminated nanoparticle PDF using the analytical sphere model
    print("\n[3/3] Fitting explicit O-terminated nanoparticle PDF using analytical spherical model...")
    np_gr_path = os.path.join(out_dir, "ceo2_explicit_np25A.gr")
    np.savetxt(np_gr_path, np.column_stack([r_grid, gr_exp]), fmt="%.6f",
               header="Explicit O-terminated CeO2 nanoparticle (nominal D=25.0 A)\nr(A) G(r)")

    phase_fit, sim_fit = make_simulator(shape_type="analytical", diameter=nominal_diameter, output_dir=out_dir)
    phase_fit.set_spherical_constraints()
    phase_fit["sphere", "optimize"] = [True, False, False]
    phase_fit["sphere", "min"] = [10.0, 10.0, 10.0]
    phase_fit["sphere", "max"] = [40.0, 40.0, 40.0]
    sim_fit["scale", "optimize"] = True
    sim_fit["scale", "min"] = 0.5
    sim_fit["scale", "max"] = 1.5

    ls = LeastSquaresOptimizer()
    ls.work_dir = out_dir
    ls.study_name = "CeO2_NP_AnalyticalFit"
    ls.simulators = [sim_fit]
    ls["fit_min"] = 1.5
    ls["fit_max"] = 25.0
    ls.read_file(np_gr_path)
    ls()

    apparent_diameter = float(phase_fit["sphere"][0])
    apparent_scale = float(sim_fit["scale"])
    rw_fitted = float(ls.Rw)
    gr_ana_fitted = np.array(ls.simy, dtype=float)
    print(f"  -> Analytical sphere fit to O-terminated NP: refined apparent diameter D_app = {apparent_diameter:.2f} A "
          f"(vs. outer O diameter {2*r_o.max():.2f} A and Ce core diameter {2*r_ce.max():.2f} A)")
    print(f"  -> Refined scale = {apparent_scale:.3f}, residual Rw = {rw_fitted:.4f} ({rw_fitted*100:.2f}%)")

    summary = {
        "nominal_diameter_A": nominal_diameter,
        "explicit_total_atoms": int(n_ce + n_o),
        "explicit_n_Ce": n_ce,
        "explicit_n_O": n_o,
        "O_to_Ce_ratio": float(n_o / n_ce),
        "R_Ce_max_A": float(r_ce.max()),
        "D_Ce_core_A": float(2.0 * r_ce.max()),
        "R_O_max_A": float(r_o.max()),
        "D_O_outer_A": float(2.0 * r_o.max()),
        "Rw_nominal_D25": rw_nominal,
        "analytical_fit_apparent_diameter_A": apparent_diameter,
        "analytical_fit_scale": apparent_scale,
        "Rw_analytical_fit": rw_fitted,
    }
    with open(os.path.join(out_dir, "tutorial_02_results.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # Generate publication-quality 2-panel figure
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), dpi=300)

    # Panel (a): Radial atomic distribution (Ce core vs O-terminated shell)
    ax0 = axes[0]
    bins = np.linspace(0.0, 13.5, 19)
    ax0.hist(r_o, bins=bins, color="#ff7f0e", alpha=0.65, edgecolor="black", lw=0.6,
             label=rf"$\mathrm{{O^{{2-}}}}$ ($N={n_o}$, $R_{{\max}}={r_o.max():.2f}\ \mathrm{{\AA}}$)")
    ax0.hist(r_ce, bins=bins, color="#1f77b4", alpha=0.80, edgecolor="black", lw=0.6,
             label=rf"$\mathrm{{Ce^{{4+}}}}$ ($N={n_ce}$, $R_{{\max}}={r_ce.max():.2f}\ \mathrm{{\AA}}$)")
    ax0.axvline(r_ce.max(), color="#1f77b4", ls="--", lw=1.1, label=r"$\mathrm{Ce^{4+}}$ core boundary")
    ax0.axvline(r_o.max(), color="#ff7f0e", ls=":", lw=1.2, label=r"$\mathrm{O^{2-}}$ surface boundary")
    ax0.set_xlim(0.0, 13.5)
    ax0.set_xlabel(r"Radial distance from nanoparticle center $R$ ($\mathrm{\AA}$)")
    ax0.set_ylabel("Number of atoms per radial shell")
    ax0.set_title(r"(a) Explicit O-Terminated $\mathrm{Ce_{141}O_{432}}$ Radial Distribution")
    ax0.legend(loc="upper left", frameon=False, fontsize=8.0)
    ax0.grid(True, alpha=0.25)

    # Panel (b): Explicit O-terminated G(r) vs Analytical Sphere (nominal & fitted)
    ax1 = axes[1]
    ax1.plot(r_grid, gr_exp, "k-", lw=1.3,
             label=r"Explicit O-terminated $\mathrm{Ce_{141}O_{432}}$ ($D_{\mathrm{O}}=24.7\ \mathrm{\AA}$)")
    ax1.plot(r_grid, gr_ana_fixed, color="#2ca02c", ls="--", lw=1.0, alpha=0.85,
             label=rf"Analytical sphere ($D=25.0\ \mathrm{{\AA}}$, $R_w={rw_nominal*100:.1f}\%$)")
    ax1.plot(ls.obsx, gr_ana_fitted, color="#d62728", lw=1.1,
             label=rf"Analytical fit ($D_{{\mathrm{{app}}}}={apparent_diameter:.1f}\ \mathrm{{\AA}}$, $R_w={rw_fitted*100:.1f}\%$)")
    offset = -3.2
    ax1.plot(ls.obsx, (ls.obsy - gr_ana_fitted) + offset, color="#d62728", lw=0.9,
             label="Diff (Explicit $-$ Analytical fit)")
    ax1.axhline(offset, color="gray", ls="--", lw=0.6)
    ax1.set_xlim(1.5, 25.0)
    ax1.set_xlabel(r"Interatomic distance $r$ ($\mathrm{\AA}$)")
    ax1.set_ylabel(r"$G(r)$ ($\mathrm{\AA^{-2}}$)")
    ax1.set_title(r"(b) Breakdown of Uniform Spherical Approximation")
    ax1.legend(loc="upper right", frameon=False, fontsize=7.8)
    ax1.grid(True, alpha=0.25)

    fig.tight_layout()
    fig_path = os.path.join(out_dir, "tutorial_02_ceo2_nanoparticle.pdf")
    fig.savefig(fig_path)
    fig.savefig(fig_path.replace(".pdf", ".png"))
    plt.close(fig)
    print(f"\nSaved figure to {fig_path}")
    return summary


def run_gui(output_dir=None):
    """Launches the interactive Gradio GUI for Tutorial 02."""
    from orochi.ui.ui import BaseUI as UI
    from orochi.view.model_viewer import ModelViewer

    out_dir = os.path.abspath(output_dir) if output_dir else OUTPUT_DIR
    os.makedirs(out_dir, exist_ok=True)
    phase, sim = make_simulator(shape_type="sphere", diameter=25.0, output_dir=out_dir)
    viewer = ModelViewer()
    viewer.phase = phase
    phase.viewer = viewer
    phase()

    ui = UI(theme="Orochi")
    ui.work_dir = out_dir
    ui.study_name = "Tutorial02_CeO2_Nanoparticle"
    ui["server"] = "127.0.0.1"

    ui.add_instruction_panel(title="Lesson Note", markdown_file=README_PATH)
    ui.add_phase_panel(
        module=phase,
        keys=["shape_type", "diameter", "sphere", "pbc"],
        const_keys=["spherical_constraints", "lattice_constraints", "symmetry_constraints"],
        title="Nanoparticle Structure (Phase)",
    )
    ui.add_simulation_panel(
        module=sim,
        keys=["rmin", "rmax", "rstep", "qmax", "qmin", "scale", "qdamp", "qbroad", "delta2", "rambda", "qdepend"],
        title="Simulation (PDFsim)",
    )
    ui.add_log_panel(title="Execution Log")
    ui()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Orochi 4.0 Tutorial 02: Explicit vs Analytical CeO2 Nanoparticle")
    parser.add_argument("--gui", action="store_true", help="Launch interactive Gradio GUI")
    parser.add_argument("--output-dir", "-o", type=str, default=None, help="Directory to save output figures, data, and logs (defaults to ./output)")
    args = parser.parse_args()
    if args.gui:
        run_gui(output_dir=args.output_dir)
    else:
        run_cui(output_dir=args.output_dir)


