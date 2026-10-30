<p align="center">
  <img src="images/orochi_icon.png" alt="Orochi Logo" width="80">
</p>

# Orochi 4.0 Tutorials (`orochi.tutorial`)

This package provides self-contained, end-to-end tutorials for the **Orochi 4.0** total scattering and Pair Distribution Function (PDF) analysis suite.

Each tutorial directory contains:
- **`README.md`**: A single, unified Markdown guide explaining the physical background, mathematical formulation, and step-by-step workflow. This same `README.md` can be read directly by command-line (CUI) users, on code hosting platforms (GitHub / GitLab), and is automatically rendered inside the **Lesson Note / Instruction** tab when launched in the Gradio web GUI (`ui.tab.instruction(markdown_file="README.md")`).
- **`run_tutorial.py`**: A unified Python script that executes the complete computational workflow in headless CUI mode by default (saving quantitative results and publication-quality figures) or launches the interactive Gradio GUI when invoked with `--gui` (or `LAUNCH_GUI = True`).

## Tutorial Index

0. **`tutorials/00_ni_synchrotron_benchmark/`**
   - **Topic**: Standard metallic nickel (Ni) total scattering benchmark (λ = 0.18033 Å, E = 68.48 keV, L₀ = 227.575 mm), matching **Section 3.1 and Figure 3** of the Orochi publication.
   - **Key Concepts**: Flat-panel detector perimeter edge cutoff (Q_edge = 23.94 Å⁻¹) vs. automated diagonal sector integration (β = ±45° ± 18°, ±135° ± 18°) up to Q_max = 29.0 Å⁻¹, Faber–Ziman normalization, instrumental resolution calibration (Q_damp, Q_broad), and Rietveld-grade PDF refinements (Rw ≈ 3.30% short-range, 4.57% long-range).

1. **`tutorials/01_ceo2_reduction_and_qdepend/`**
   - **Topic**: X-ray total scattering data reduction (`orochi.pdfget`) and Q-dependent complex form-factor PDF refinement (`orochi.phase`, `orochi.pdfsim`, `orochi.fit`) on fluorite CeO₂.
   - **Key Concepts**: Faber–Ziman normalization, automated low-r ripple minimization (`PDFget.tune`), and the necessity of exact Q-dependent scattering factor convolution (`qdepend = True`) vs. the constant-Z approximation (`qdepend = False`) under heavy/light Z-contrast (Z_Ce = 58, Z_O = 8).

2. **`tutorials/02_ceo2_nanoparticle_explicit_vs_analytical/`**
   - **Topic**: Coordination-preserving explicit nanoparticle construction (`shape_type = "sphere"`) vs. uniform analytical spherical envelope approximation (`shape_type = "analytical"`) for CeO₂ nanocrystals.
   - **Key Concepts**: Automated cation coordination polyhedra preservation (`trim_under_coordinated_ions`), O-terminated nanoparticle surface stoichiometry (Ce₁₄₁O₄₃₂ at D = 25 Å), spatially inhomogeneous radial distribution of Ce⁴⁺ core (R_Ce,max = 10.82 Å) vs. O²⁻ termination shell (R_O,max = 12.33 Å), and systematic bias in apparent diameter when fitting O-terminated nanoparticles with a uniform analytical sphere model.

3. **`tutorials/03_pto2_nanosheet_2d_pbc/`**
   - **Topic**: Anisotropic 2D periodic boundary conditions (`pbc = [True, True, False]`) and finite-Q_min baseline density filtering on 2D PtO₂ nanosheets.
   - **Key Concepts**: Non-uniform continuum pair density ρ_base(r) in 2D nanosheets, low-pass sinc convolution at finite Q_min, and structural refinement of experimental 2D PtO₂ nanosheet X-ray PDF data.

## Usage

Run any tutorial in headless CUI mode:
```bash
python tutorials/00_ni_synchrotron_benchmark/run_tutorial.py
python tutorials/01_ceo2_reduction_and_qdepend/run_tutorial.py
python tutorials/02_ceo2_nanoparticle_explicit_vs_analytical/run_tutorial.py
python tutorials/03_pto2_nanosheet_2d_pbc/run_tutorial.py
```

Launch any tutorial in interactive Gradio GUI mode:
```bash
python tutorials/00_ni_synchrotron_benchmark/run_tutorial.py --gui
python tutorials/01_ceo2_reduction_and_qdepend/run_tutorial.py --gui
python tutorials/02_ceo2_nanoparticle_explicit_vs_analytical/run_tutorial.py --gui
python tutorials/03_pto2_nanosheet_2d_pbc/run_tutorial.py --gui
```

---

## License

This package and all tutorials are licensed under the **GNU General Public License v3.0 (GPLv3)**. See `LICENSE.rst` for details.

This ensures that the computational workflows remain completely open, transparent, and legally protected against proprietary enclosure for future generations of researchers.

---

## Academic Citation Policy

If you use Orochi in academic research leading to a publication or thesis, please cite:

```bibtex
@article{tominaka2026orochi,
  title   = {Orochi: A Physics-Grounded Python Package for Pair Distribution Function Analysis of Crystalline and Low-Dimensional Materials},
  author  = {Tominaka, Satoshi},
  journal = {ChemRxiv},
  year    = {2026},
  doi     = {10.26434/chemrxiv.15010802},
  url     = {https://doi.org/10.26434/chemrxiv.15010802}
}
```
