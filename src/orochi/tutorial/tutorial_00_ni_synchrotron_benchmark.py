from pathlib import Path
import os
import subprocess
import sys

_readme_path = Path(__file__).resolve().parent.parent.parent.parent / "tutorials" / "00_ni_synchrotron_benchmark" / "README.md"
if _readme_path.exists():
    __doc__ = _readme_path.read_text(encoding="utf-8")
else:
    __doc__ = """Tutorial 00: Standard Metallic Nickel Benchmark: Instrumental Calibration"""

TUTORIAL_DIR = Path(__file__).resolve().parent.parent.parent.parent / "tutorials" / "00_ni_synchrotron_benchmark"

def run(gui: bool = False):
    """Execute 00_ni_synchrotron_benchmark workflow.

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
