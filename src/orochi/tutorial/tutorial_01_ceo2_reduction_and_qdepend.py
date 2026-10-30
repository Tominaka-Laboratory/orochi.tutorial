from pathlib import Path
import os
import subprocess
import sys

_readme_path = Path(__file__).resolve().parent.parent.parent.parent / "tutorials" / "01_ceo2_reduction_and_qdepend" / "README.md"
if _readme_path.exists():
    __doc__ = _readme_path.read_text(encoding="utf-8")
else:
    __doc__ = """Tutorial 01: Total Scattering Data Reduction and Q-Dependent Form-Factor PDF Refinement of Bulk CeO2"""

TUTORIAL_DIR = Path(__file__).resolve().parent.parent.parent.parent / "tutorials" / "01_ceo2_reduction_and_qdepend"

def run(gui: bool = False):
    """Execute 01_ceo2_reduction_and_qdepend workflow.

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
