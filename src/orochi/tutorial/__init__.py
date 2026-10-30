r"""
# Orochi 4.0 Tutorials Suite (`orochi.tutorial`)

Official CUI and GUI tutorials for the **Orochi 4.0** total scattering and Pair Distribution Function (PDF) analysis software suite.

This package bundles comprehensive, self-contained computational tutorials replicating benchmarks and key findings from the Orochi publication:
* S. Tominaka, *"Orochi: A Physics-Grounded Python Package for Pair Distribution Function Analysis of Crystalline and Low-Dimensional Materials"*, *ChemRxiv* (2026). DOI: [10.26434/chemrxiv.15010802/v2](https://doi.org/10.26434/chemrxiv.15010802/v2)

## Available Tutorials

1. **[`tutorial_00_ni_synchrotron_benchmark`](./tutorial/tutorial_00_ni_synchrotron_benchmark.html)**:
   - **Topic**: Standard metallic nickel (Ni) total scattering benchmark ($\lambda = 0.18033$ Å, $E = 68.48$ keV, $L_0 = 227.575$ mm).
   - **Key Concepts**: Flat-panel detector perimeter edge cutoff ($Q_\mathrm{edge} = 23.94$ Å$^{-1}$) vs. automated diagonal sector integration ($\beta = \pm 45^\circ \pm 18^\circ, \pm 135^\circ \pm 18^\circ$) up to $Q_\mathrm{max} = 29.0$ Å$^{-1}$, Faber–Ziman normalization, instrumental resolution calibration ($Q_\mathrm{damp}, Q_\mathrm{broad}$), and Rietveld-grade PDF refinements ($R_w \approx 3.30\%$ short-range, $4.57\%$ long-range).

2. **[`tutorial_01_ceo2_reduction_and_qdepend`](./tutorial/tutorial_01_ceo2_reduction_and_qdepend.html)**:
   - **Topic**: X-ray total scattering data reduction (`orochi.pdfget`) and $Q$-dependent complex form-factor PDF refinement (`orochi.phase`, `orochi.pdfsim`, `orochi.fit`) on fluorite $\mathrm{CeO}_2$.
   - **Key Concepts**: Faber–Ziman normalization, automated low-$r$ ripple minimization (`PDFget.tune`), and the necessity of exact $Q$-dependent scattering factor convolution (`qdepend = True`) vs. constant-$Z$ approximation (`qdepend = False`) under heavy/light $Z$-contrast ($Z_\mathrm{Ce} = 58, Z_\mathrm{O} = 8$).

3. **[`tutorial_02_ceo2_nanoparticle_explicit_vs_analytical`](./tutorial_02_ceo2_nanoparticle_explicit_vs_analytical.html)**:
   - **Topic**: Coordination-preserving explicit nanoparticle construction (`shape_type = "sphere"`) vs. uniform analytical spherical envelope approximation (`shape_type = "analytical"`) for $\mathrm{CeO}_2$ nanocrystals.
   - **Key Concepts**: Automated cation coordination polyhedra preservation (`trim_under_coordinated_ions`), O-terminated nanoparticle surface stoichiometry ($\mathrm{Ce}_{141}\mathrm{O}_{432}$ at $D = 25$ Å), spatially inhomogeneous radial distribution of $\mathrm{Ce}^{4+}$ core ($R_\mathrm{Ce,max} = 10.82$ Å) vs. $\mathrm{O}^{2-}$ termination shell ($R_\mathrm{O,max} = 12.33$ Å), and systematic bias in apparent diameter when fitting O-terminated nanoparticles with an analytical sphere model.

4. **[`tutorial_03_pto2_nanosheet_2d_pbc`](./tutorial_03_pto2_nanosheet_2d_pbc.html)**:
   - **Topic**: Anisotropic 2D periodic boundary conditions (`pbc = [True, True, False]`) and finite-$Q_\mathrm{min}$ baseline density filtering on 2D $\mathrm{PtO}_2$ nanosheets.
   - **Key Concepts**: Non-uniform continuum pair density $\rho_\mathrm{base}(r)$ in 2D nanosheets, low-pass sinc convolution at finite $Q_\mathrm{min}$, and structural refinement of experimental 2D $\mathrm{PtO}_2$ nanosheet X-ray PDF data.

## Running Tutorials

Run any tutorial in headless CUI mode:
```bash
python tutorials/00_ni_synchrotron_benchmark/run_tutorial.py
```

Launch interactive Gradio GUI mode:
```bash
python tutorials/00_ni_synchrotron_benchmark/run_tutorial.py --gui
```
"""

import os
from pathlib import Path

TUTORIALS_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "tutorials")
)

from . import tutorial_00_ni_synchrotron_benchmark
from . import tutorial_01_ceo2_reduction_and_qdepend
from . import tutorial_02_ceo2_nanoparticle_explicit_vs_analytical
from . import tutorial_03_pto2_nanosheet_2d_pbc

__all__ = [
    "TUTORIALS_DIR",
    "tutorial_00_ni_synchrotron_benchmark",
    "tutorial_01_ceo2_reduction_and_qdepend",
    "tutorial_02_ceo2_nanoparticle_explicit_vs_analytical",
    "tutorial_03_pto2_nanosheet_2d_pbc",
]
