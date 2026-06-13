import os
import sys
import subprocess
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "example_file", ["beartyped_columns", "default_typed", "default_untyped", "tqdm_swifter", "vectorized_validate"]
)
def test_examples_run(example_file: str):
    project_root = Path(__file__).resolve().parent.parent
    examples_dir = project_root / "examples"
    assert examples_dir.exists(), "examples directory missing"

    py = sys.executable
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root)
    p = examples_dir.joinpath(Path(example_file).with_suffix(".py"))
    # Run each example as a subprocess from the project root so imports work
    proc = subprocess.run(
        [py, str(p)],
        cwd=str(project_root),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=15,
    )
    out = proc.stdout.decode(errors="ignore")
    assert proc.returncode == 0, f"Example {p.name} failed (exit {proc.returncode}):\n{out}"
