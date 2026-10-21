"""Tests for Phantom CLI."""

from __future__ import annotations

import json
from pathlib import Path

from phantom.cli import main
from phantom.version import __version__

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_cli_version(capsys):
    ret = main(["--version"])
    assert ret == 0
    out, _ = capsys.readouterr()
    assert __version__ in out


def test_cli_help(capsys):
    ret = main(["--help"])
    assert ret == 0
    out, _ = capsys.readouterr()
    assert "usage:" in out.lower() or "phantom" in out


def test_cli_no_args(capsys):
    ret = main([])
    assert ret == 0
    out, _ = capsys.readouterr()
    assert "usage:" in out.lower() or "phantom" in out


def test_cli_check_valid(capsys):
    target = FIXTURES_DIR / "valid_comments.py"
    ret = main(["check", str(target)])
    assert ret == 0
    out, _ = capsys.readouterr()
    assert "0 error(s)" in out


def test_cli_check_invalid(capsys):
    target = FIXTURES_DIR / "invalid_instructions.py"
    ret = main(["check", str(target)])
    assert ret == 2
    out, err = capsys.readouterr()
    combined = out + err
    assert "error(s)" in combined


def test_cli_check_not_found(capsys):
    ret = main(["check", "not_real_file.py"])
    assert ret == 1
    _, err = capsys.readouterr()
    assert "not found" in err.lower()


def test_cli_inspect_text(capsys):
    target = FIXTURES_DIR / "valid_comments.py"
    ret = main(["inspect", str(target)])
    assert ret == 0
    out, _ = capsys.readouterr()
    assert "Instructions:" in out
    assert "event.declare" in out
    assert "Capabilities:" in out


def test_cli_inspect_json(capsys):
    target = FIXTURES_DIR / "valid_comments.py"
    ret = main(["inspect", str(target), "--json"])
    assert ret == 0
    out, _ = capsys.readouterr()
    parsed = json.loads(out)
    assert parsed["instruction_count"] > 0
    assert len(parsed["instructions"]) > 0
    first = parsed["instructions"][0]
    assert "type" in first
    assert "required_capabilities" in first


def test_cli_run_valid(capsys):
    target = FIXTURES_DIR / "valid_plain.py"
    ret = main(["run", str(target)])
    assert ret == 0
    out, _ = capsys.readouterr()
    assert "=== Phantom Runtime" in out
    assert "Hello, World!" in out


def test_cli_run_with_phantom_instructions(capsys):
    target = FIXTURES_DIR / "hello_phantom.py"
    ret = main(["run", str(target)])
    assert ret == 0
    out, _ = capsys.readouterr()
    assert "=== Phantom Runtime" in out
    assert "Validation passed" in out
    assert "Hello, World!" in out


def test_cli_run_invalid(capsys):
    target = FIXTURES_DIR / "invalid_instructions.py"
    ret = main(["run", str(target)])
    assert ret == 2
    _, err = capsys.readouterr()
    assert "Validation failed" in err


def test_cli_generate_requires_intent_noninteractive(capsys):
    target = FIXTURES_DIR / "valid_plain.py"
    ret = main(["generate", str(target)])
    assert ret == 1
    _, err = capsys.readouterr()
    assert "--intent is required" in err


def test_cli_generate_requires_remote_consent(capsys, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    target = FIXTURES_DIR / "valid_plain.py"
    ret = main(["generate", "--intent", "note startup", str(target)])
    assert ret == 1
    _, err = capsys.readouterr()
    assert "not authorized" in err


def test_cli_diff(capsys, tmp_path):
    f1 = tmp_path / "a.py"
    f2 = tmp_path / "b.py"
    f1.write_text("print('hello')\n")
    f2.write_text("print('world')\n")

    ret = main(["diff", str(f1), str(f2)])
    assert ret == 0
    out, _ = capsys.readouterr()
    assert "-print('hello')" in out
    assert "+print('world')" in out


def test_cli_verify_match(capsys):
    target = FIXTURES_DIR / "valid_plain.py"
    ret = main(["verify", str(target), str(target)])
    assert ret == 0
    out, _ = capsys.readouterr()
    assert "Tested equivalence" in out


def test_cli_verify_mismatch(capsys, tmp_path):
    f1 = tmp_path / "p1.py"
    f2 = tmp_path / "p2.py"
    f1.write_text("print('A')\n")
    f2.write_text("print('B')\n")

    ret = main(["verify", str(f1), str(f2)])
    assert ret == 1
    _, err = capsys.readouterr()
    assert "stdout differs" in err
