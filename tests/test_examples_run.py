import os
import sys
import subprocess
from pathlib import Path


def test_examples_run():
    project_root = Path(__file__).resolve().parent.parent
    examples_dir = project_root / "examples"
    assert examples_dir.exists(), "examples directory missing"

    py = sys.executable
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)
    for p in sorted(examples_dir.glob("*.py")):
        # Run each example as a subprocess from the project root so imports work
        proc = subprocess.run(
            [py, str(p.relative_to(project_root))],
            cwd=str(project_root),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=15,
        )
        out = proc.stdout.decode(errors="ignore")
        assert proc.returncode == 0, f"Example {p.name} failed (exit {proc.returncode}):\n{out}"
