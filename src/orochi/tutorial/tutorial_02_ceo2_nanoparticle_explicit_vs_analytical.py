from pathlib import Path
import os
import subprocess
import sys

_readme_path = Path(__file__).resolve().parent.parent.parent.parent / "tutorials" / "02_ceo2_nanoparticle_explicit_vs_analytical" / "README.md"
if _readme_path.exists():
    __doc__ = _readme_path.read_text(encoding="utf-8")
else:
    __doc__ = """Tutorial 02: Coordination-Preserving Explicit Nanoparticle Modeling vs. Analytical Spherical Envelope for CeO2"""

TUTORIAL_DIR = Path(__file__).resolve().parent.parent.parent.parent / "tutorials" / "02_ceo2_nanoparticle_explicit_vs_analytical"

def run(gui: bool = False):
    """Execute 02_ceo2_nanoparticle_explicit_vs_analytical workflow.

    Parameters
    ----------
    gui : bool, default=False
        If True, launches the interactive Gradio web GUI.
        If False, executes the workflow in headless CUI mode.
    """
    script = TUTORIAL_DIR / "run_tutorial.py"
    cmd = [sys.executable, str(script)]
    if gui:
        cmd.append("--gui")
    return subprocess.run(cmd)

__all__ = ["run", "TUTORIAL_DIR"]
