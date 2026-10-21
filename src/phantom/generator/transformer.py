"""Apply a validated TransformationPlan to source text.

The transformer only ever inserts whole lines. It never edits, moves, or
removes existing lines, and it refuses insertion points inside multi-line
strings, brackets, or backslash continuations.
"""

from __future__ import annotations

import io
import tokenize

from phantom.encoding import encode_instruction
from phantom.generator.models import PlannedInstruction, TransformationPlan
from phantom.ir import (
    Argument,
    ArgumentType,
    EncodingMode,
    InstructionType,
    PhantomInstruction,
    SourceLocation,
)

_MODES = {
    "comment": EncodingMode.COMMENT,
    "whitespace": EncodingMode.WHITESPACE,
    "unicode": EncodingMode.UNICODE,
}


class TransformError(ValueError):
    """Raised when a plan cannot be applied safely."""


def unsafe_insertion_lines(source: str) -> set[int]:
    """Line numbers before which inserting a new line would change the program."""
    unsafe: set[int] = set()
    lines = source.splitlines()
    try:
        depth = 0
        for tok in tokenize.generate_tokens(io.StringIO(source).readline):
            if tok.type == tokenize.OP:
                if tok.string in "([{":
                    depth += 1
                elif tok.string in ")]}":
                    depth = max(0, depth - 1)
            if tok.start[0] < tok.end[0]:
                unsafe.update(range(tok.start[0] + 1, tok.end[0] + 1))
            if depth > 0 and tok.type in (tokenize.NL, tokenize.NEWLINE):
                unsafe.add(tok.start[0] + 1)
    except (tokenize.TokenError, IndentationError, SyntaxError) as exc:
        raise TransformError(f"Source cannot be tokenized: {exc}") from exc
    for idx, line in enumerate(lines, start=1):
        if line.endswith("\\"):
            unsafe.add(idx + 1)
    return unsafe


def _to_instruction(planned: PlannedInstruction) -> PhantomInstruction:
    args = tuple(
        Argument(ArgumentType(a["type"]), a["value"]) for a in planned.arguments
    )
    return PhantomInstruction(
        InstructionType(planned.instruction_type),
        args,
        SourceLocation("<plan>", planned.placement_line, 0, _MODES[planned.encoding]),
    )


def apply_plan(source: str, plan: TransformationPlan) -> str:
    """Return `source` with the plan's instructions inserted."""
    if not plan.valid:
        raise TransformError("Plan is not valid: " + "; ".join(plan.validation_errors))

    newline = "\r\n" if "\r\n" in source else "\n"
    lines = source.splitlines()
    unsafe = unsafe_insertion_lines(source)
    total = len(lines)

    inserts: dict[int, list[str]] = {}
    for planned in plan.instructions:
        at = min(planned.placement_line, total + 1)
        if at in unsafe:
            raise TransformError(
                f"Line {planned.placement_line} is inside a multi-line construct; "
                "instructions cannot be inserted there"
            )
        text = encode_instruction(_to_instruction(planned), _MODES[planned.encoding])
        inserts.setdefault(at, []).extend(text.split("\n"))

    out: list[str] = []
    for lineno in range(1, total + 2):
        out.extend(inserts.get(lineno, []))
        if lineno <= total:
            out.append(lines[lineno - 1])
    trailing = newline if source.endswith(("\n", "\r")) or not source else ""
    return newline.join(out) + trailing


def resolve_placement(source: str, placement: str) -> int:
    """Resolve a placement spec to a 1-based insertion line.

    Accepted: 'beginning', 'end', 'line:N', 'near:NAME' (before the single
    function or class called NAME).

    Raises:
        TransformError: If the spec is unknown or ambiguous.
    """
    import ast

    total = len(source.splitlines())
    spec = placement.strip()
    if spec in ("", "beginning"):
        return 1
    if spec == "end":
        return total + 1
    if spec.startswith("line:"):
        try:
            line = int(spec[5:])
        except ValueError:
            raise TransformError(f"Invalid line placement: '{spec}'") from None
        if not 1 <= line <= total + 1:
            raise TransformError(f"Line {line} is outside the file (1-{total + 1})")
        return line
    if spec.startswith("near:"):
        name = spec[5:].strip()
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            raise TransformError(f"Cannot resolve '{spec}': {exc.msg}") from exc
        hits = [
            n for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and n.name == name
        ]
        if not hits:
            raise TransformError(f"No function or class named '{name}' found")
        if len(hits) > 1:
            lines = ", ".join(str(n.lineno) for n in hits)
            raise TransformError(
                f"'{name}' is ambiguous (defined at lines {lines}); use line:N instead"
            )
        node = hits[0]
        first = min([node.lineno] + [d.lineno for d in node.decorator_list])
        return first
    raise TransformError(f"Unknown placement '{placement}'")
