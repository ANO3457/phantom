"""Phantom Host Program Execution.

Executes host Python programs in isolated subprocesses with timeout
and resource management.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from dataclasses import dataclass


@dataclass
class HostResult:
    """Result of executing a host program."""

    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    exception: str | None = None


def execute_host_program(
    filepath: str,
    args: list[str] | None = None,
    timeout: float = 30.0,
    env: dict[str, str] | None = None,
) -> HostResult:
    """Execute a Python program in a subprocess.

    Uses sys.executable to run the same Python.
    Captures stdout, stderr, exit code.
    Applies timeout.
    Never modifies the host file.
    """
    if not os.path.isfile(filepath):
        return HostResult(
            exit_code=1,
            stdout="",
            stderr=f"Error: Host file not found: '{filepath}'",
            duration_ms=0.0,
            exception=f"FileNotFoundError: '{filepath}'",
        )

    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)

    # Ensure unbuffered and UTF-8 output
    merged_env["PYTHONUNBUFFERED"] = "1"
    merged_env["PYTHONIOENCODING"] = "utf-8"

    cmd = [sys.executable, filepath]
    if args:
        cmd.extend(args)

    start_time = time.perf_counter()
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=merged_env,
            encoding="utf-8",
            errors="replace",
        )
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        return HostResult(
            exit_code=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            duration_ms=duration_ms,
        )
    except subprocess.TimeoutExpired as exc:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        stdout_str = (
            exc.stdout
            if isinstance(exc.stdout, str)
            else (exc.stdout or b"").decode("utf-8", errors="replace")
        )
        stderr_str = (
            exc.stderr
            if isinstance(exc.stderr, str)
            else (exc.stderr or b"").decode("utf-8", errors="replace")
        )
        timeout_msg = f"\n[HostExecution] Process timed out after {timeout} seconds."
        return HostResult(
            exit_code=124,
            stdout=stdout_str,
            stderr=stderr_str + timeout_msg,
            duration_ms=duration_ms,
            exception=f"TimeoutExpired: Process timed out after {timeout} seconds",
        )
    except Exception as exc:
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        return HostResult(
            exit_code=1,
            stdout="",
            stderr=f"Execution error: {exc}",
            duration_ms=duration_ms,
            exception=str(exc),
        )
