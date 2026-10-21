"""Phantom generator diff helpers.

Unified diffs between original and candidate source, and a way to strip the
Phantom instruction layer so the remaining host layer can be compared.
"""

from __future__ import annotations

import difflib

from phantom.lexer import TokenType, tokenize

_LAYER_TOKENS = frozenset(
    {
        TokenType.COMMENT_INSTRUCTION,
        TokenType.HYBRID_HEADER,
        TokenType.WS_BEGIN,
        TokenType.WS_END,
        TokenType.WS_DATA_LINE,
        TokenType.ZW_BEGIN,
        TokenType.ZW_END,
        TokenType.ZW_DATA_LINE,
    }
)


def unified_diff(
    original: str,
    candidate: str,
    from_name: str = "original",
    to_name: str = "candidate",
) -> str:
    """Return a unified diff between two source texts ('' when identical)."""
    return "".join(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            candidate.splitlines(keepends=True),
            fromfile=from_name,
            tofile=to_name,
        )
    )


def strip_phantom_layer(source: str) -> str:
    """Remove every line that belongs to the Phantom instruction layer."""
    drop = {tok.line for tok in tokenize(source) if tok.type in _LAYER_TOKENS}
    kept = [
        line for idx, line in enumerate(source.splitlines(keepends=True), start=1)
        if idx not in drop
    ]
    return "".join(kept)


def host_layer_diff(original: str, candidate: str) -> str:
    """Diff of only the host layers; empty when the host code is untouched."""
    return unified_diff(
        strip_phantom_layer(original),
        strip_phantom_layer(candidate),
        "original (host layer)",
        "candidate (host layer)",
    )
