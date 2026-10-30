.. image:: images/orochi_icon.png
   :align: center
   :width: 80px
   :target: https://github.com/Tominaka-Laboratory/orochi.tutorial
   :alt: Orochi Logo

===============
orochi.tutorial
===============

.. |title| replace:: orochi.tutorial
.. _title: https://github.com/Tominaka-Laboratory/orochi.tutorial

.. |Icon| image:: images/orochi_icon.png
   :target: https://github.com/Tominaka-Laboratory/orochi.tutorial
   :height: 100px

|PyPi| |Forge| |PythonVersion| |ChemRxiv| |PR|

|CI| |Codecov| |Black| |Tracking|

.. |ChemRxiv| image:: https://img.shields.io/badge/ChemRxiv-10.26434%2Fchemrxiv.15010802%2Fv2-blue.svg
        :target: https://doi.org/10.26434/chemrxiv.15010802/v2

.. |Black| image:: https://img.shields.io/badge/code_style-black-black
        :target: https://github.com/psf/black

.. |CI| image:: https://github.com/Tominaka-Laboratory/orochi.tutorial/actions/workflows/tests.yml/badge.svg
        :target: https://github.com/Tominaka-Laboratory/orochi.tutorial/actions/workflows/tests.yml

.. |Codecov| image:: https://codecov.io/gh/Tominaka-Laboratory/orochi.tutorial/branch/main/graph/badge.svg
        :target: https://codecov.io/gh/Tominaka-Laboratory/orochi.tutorial

.. |Forge| image:: https://img.shields.io/conda/vn/conda-forge/orochi.tutorial
        :target: https://anaconda.org/conda-forge/orochi.tutorial

.. |PR| image:: https://img.shields.io/badge/PR-Welcome-29ab47ff

.. |PyPi| image:: https://img.shields.io/pypi/v/orochi.tutorial
        :target: https://pypi.org/project/orochi.tutorial/

.. |PythonVersion| image:: https://img.shields.io/pypi/pyversions/orochi.tutorial
        :target: https://pypi.org/project/orochi.tutorial/

.. |Tracking| image:: https://img.shields.io/badge/issue_tracking-github-blue
        :target: https://github.com/Tominaka-Laboratory/orochi.tutorial/issues

Orochi 4.0 End-to-End Tutorials
===============================

The ``orochi.tutorial`` package provides self-contained, end-to-end computational tutorials for the **Orochi 4.0** total scattering and Pair Distribution Function (PDF) analysis suite.

Each tutorial directory contains:

* **``README.md``**: A single, unified guide explaining the physical background, mathematical formulation, and step-by-step workflow. This file is read directly in terminal/code hosting platforms and is automatically rendered inside the **Lesson Note / Instruction** tab when launched in the interactive Gradio web GUI.
* **``run_tutorial.py``**: A unified Python script that executes the complete computational workflow in headless CUI mode by default (saving quantitative numerical results and publication-quality figures) or launches the interactive Gradio GUI when invoked with ``--gui``.

Tutorial Index
--------------

0. **``tutorials/00_ni_synchrotron_benchmark/``**
   * **Topic**: Standard metallic nickel (Ni) total scattering benchmark (:math:`\lambda = 0.18033` Å, :math:`E = 68.48` keV, :math:`L_0 = 227.575` mm), matching **Section 3.1 and Figure 3** of the Orochi publication.
   * **Key Concepts**: Flat-panel detector perimeter edge cutoff (:math:`Q_\mathrm{edge} = 23.94` Å\ :sup:`-1`) vs. automated diagonal sector integration (:math:`\beta = \pm 45^\circ \pm 18^\circ, \pm 135^\circ \pm 18^\circ`) up to :math:`Q_\mathrm{max} = 29.0` Å\ :sup:`-1`, Faber–Ziman normalization, instrumental resolution calibration (:math:`Q_\mathrm{damp}, Q_\mathrm{broad}`), and Rietveld-grade PDF refinements (:math:`R_w \approx 3.30\%` short-range, :math:`4.57\%` long-range).

1. **``tutorials/01_ceo2_reduction_and_qdepend/``**
   * **Topic**: X-ray total scattering data reduction (``orochi.pdfget``) and :math:`Q`-dependent complex form-factor PDF refinement (``orochi.phase``, ``orochi.pdfsim``, ``orochi.fit``) on fluorite CeO\ :sub:`2`.
   * **Key Concepts**: Faber–Ziman normalization, automated low-:math:`r` ripple minimization (``PDFget.tune``), and the necessity of exact :math:`Q`-dependent scattering factor convolution (``qdepend = True``) vs. the constant-:math:`Z` approximation (``qdepend = False``) under heavy/light :math:`Z`-contrast (:math:`Z_\mathrm{Ce} = 58, Z_\mathrm{O} = 8`).

2. **``tutorials/02_ceo2_nanoparticle_explicit_vs_analytical/``**
   * **Topic**: Coordination-preserving explicit nanoparticle construction (``shape_type = "sphere"``) vs. uniform analytical spherical envelope approximation (``shape_type = "analytical"``) for CeO\ :sub:`2` nanocrystals.
   * **Key Concepts**: Automated cation coordination polyhedra preservation (``trim_under_coordinated_ions``), O-terminated nanoparticle surface stoichiometry (Ce\ :sub:`141`\ O\ :sub:`432` at :math:`D = 25` Å), spatially inhomogeneous radial distribution of Ce\ :sup:`4+` core (:math:`R_\mathrm{Ce,max} = 10.82` Å) vs. O\ :sup:`2-` termination shell (:math:`R_\mathrm{O,max} = 12.33` Å), and systematic bias in apparent diameter when fitting O-terminated nanoparticles with a uniform analytical sphere model.

3. **``tutorials/03_pto2_nanosheet_2d_pbc/``**
   * **Topic**: Anisotropic 2D periodic boundary conditions (``pbc = [True, True, False]``) and finite-:math:`Q_\mathrm{min}` baseline density filtering on 2D PtO\ :sub:`2` nanosheets.
   * **Key Concepts**: Non-uniform continuum pair density :math:`\rho_\mathrm{base}(r)` in 2D nanosheets, low-pass sinc convolution at finite :math:`Q_\mathrm{min}`, and structural refinement of experimental 2D PtO\ :sub:`2` nanosheet X-ray PDF data.

Usage
-----

Run any tutorial in headless CUI mode:

.. code-block:: bash

    python tutorials/00_ni_synchrotron_benchmark/run_tutorial.py
    python tutorials/01_ceo2_reduction_and_qdepend/run_tutorial.py
    python tutorials/02_ceo2_nanoparticle_explicit_vs_analytical/run_tutorial.py
    python tutorials/03_pto2_nanosheet_2d_pbc/run_tutorial.py

Launch any tutorial in interactive Gradio GUI mode:

.. code-block:: bash

    python tutorials/00_ni_synchrotron_benchmark/run_tutorial.py --gui
    python tutorials/01_ceo2_reduction_and_qdepend/run_tutorial.py --gui
    python tutorials/02_ceo2_nanoparticle_explicit_vs_analytical/run_tutorial.py --gui
    python tutorials/03_pto2_nanosheet_2d_pbc/run_tutorial.py --gui

Installation
------------

The preferred method is to install using ``pip``:

.. code-block:: bash

    pip install orochi.tutorial

License
-------

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**. See the `LICENSE.rst` file for details.

This copyleft license guarantees that Orochi remains freely accessible, open, and transparent to the entire scientific community, and that all derivative works must likewise remain open source.

Citation
--------

If you use this package in academic research, please cite the Orochi preprint:

.. code-block:: bibtex

    @article{tominaka2026orochi,
      title   = {Orochi: A Physics-Grounded Python Package for Pair Distribution Function Analysis of Crystalline and Low-Dimensional Materials},
      author  = {Tominaka, Satoshi},
      journal = {ChemRxiv},
      year    = {2026},
      doi     = {10.26434/chemrxiv.15010802/v2},
      url     = {https://doi.org/10.26434/chemrxiv.15010802/v2}
    }

Contact
-------

For more information on orochi.tutorial, please visit the project `web-page <https://github.com/Tominaka-Laboratory/orochi>`_ or email Dr. Satoshi Tominaka at tominaka.satoshi@nims.go.jp.

