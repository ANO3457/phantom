"""The documented examples must behave exactly as the documentation shows."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "docs" / "examples"


def _phantom(*args: str) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONPATH=str(ROOT / "src"), PYTHONUTF8="1")
    return subprocess.run(
        [sys.executable, "-m", "phantom", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=ROOT,
        env=env,
        timeout=60,
    )


def _python(path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(path)], capture_output=True, text=True, encoding="utf-8", timeout=60
    )


@pytest.mark.parametrize("name", ["hello", "comments", "whitespace", "unicode", "hybrid", "events"])
def test_plain_python_runs_every_example(name):
    result = _python(EXAMPLES / f"{name}.py")
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize(
    "name", ["hello", "comments", "whitespace", "unicode", "hybrid", "events"]
)
def test_examples_check_clean_even_in_strict_mode(name):
    result = _phantom("check", "--strict", f"docs/examples/{name}.py")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "0 error(s), 0 warning(s)" in result.stdout


def test_comments_run_output():
    result = _phantom("run", "docs/examples/comments.py")
    assert result.returncode == 0
    assert result.stdout.splitlines() == [
        "=== Phantom Runtime v0.1.0 ===",
        "[OK] Validation passed (5 instruction(s), 0 warning(s))",
        "Hello, World!",
        "",
        "--- Phantom Diagnostics ---",
        "[INFO] [docs/examples/comments.py:18:0 [comment]] Greeting counter initialised",
    ]


def test_events_run_output():
    result = _phantom("run", "docs/examples/events.py")
    assert result.stdout.splitlines() == [
        "=== Phantom Runtime v0.1.0 ===",
        "[OK] Validation passed (2 instruction(s), 0 warning(s))",
        "[hook] about to run events.py",
        "[hook] finished with exit code 0",
        "Doing the work.",
    ]


@pytest.mark.parametrize(
    "name,encoding,message",
    [
        ("whitespace", "whitespace", "hidden in whitespace"),
        ("unicode", "unicode", "hidden in zero-width characters"),
    ],
)
def test_encoded_example_diagnostics(name, encoding, message):
    result = _phantom("run", f"docs/examples/{name}.py")
    assert result.returncode == 0
    assert f"[{encoding}]] {message}" in result.stdout
    assert "Executing core Python logic!" in result.stdout


def test_hybrid_example_has_three_instructions_in_three_encodings():
    result = _phantom("inspect", "--json", "docs/examples/hybrid.py")
    import json

    data = json.loads(result.stdout)
    assert [i["encoding"] for i in data["instructions"]] == ["comment", "whitespace", "unicode"]


def test_invalid_example_is_rejected_in_line_order():
    result = _phantom("check", "docs/examples/invalid.py")
    assert result.returncode == 2
    assert "3 error(s), 0 warning(s)" in result.stdout
    lines = [ln for ln in result.stderr.splitlines() if ln.startswith("  -->")]
    assert [ln.rsplit(":", 2)[1] for ln in lines] == ["5", "6", "7"]
    # nothing in the invalid file was executed or imported
    assert "handlers" not in sys.modules


def test_build_examples_is_reproducible(tmp_path):
    before = {p.name: p.read_bytes() for p in EXAMPLES.glob("*.py")}
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_examples.py")],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    after = {p.name: p.read_bytes() for p in EXAMPLES.glob("*.py")}
    assert before == after
