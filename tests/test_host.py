"""Tests for Phantom host execution."""

from __future__ import annotations

from pathlib import Path

from phantom.host import HostResult, execute_host_program

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_execute_host_program_success():
    target = FIXTURES_DIR / "valid_plain.py"
    res = execute_host_program(str(target))

    assert isinstance(res, HostResult)
    assert res.exit_code == 0
    assert "Hello, World!" in res.stdout
    assert res.stderr == ""
    assert res.duration_ms >= 0


def test_execute_host_program_with_args(tmp_path):
    script = tmp_path / "args_test.py"
    script.write_text("import sys; print(' '.join(sys.argv[1:]))")

    res = execute_host_program(str(script), args=["alpha", "beta", "gamma"])
    assert res.exit_code == 0
    assert res.stdout.strip() == "alpha beta gamma"


def test_execute_host_program_not_found():
    res = execute_host_program("non_existent_file_xyz.py")
    assert res.exit_code == 1
    assert "not found" in res.stderr.lower()
    assert res.exception is not None


def test_execute_host_program_timeout(tmp_path):
    script = tmp_path / "hang.py"
    script.write_text("import time; time.sleep(5)")

    res = execute_host_program(str(script), timeout=0.2)
    assert res.exit_code == 124
    assert "timed out" in res.stderr.lower()
