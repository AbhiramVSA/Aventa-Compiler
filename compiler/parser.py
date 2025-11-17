"""Lightweight parser for the Aventa Lumen instruction set (.av files)."""

from __future__ import annotations

import json
import shlex
import sys
from pathlib import Path
from typing import Sequence


class ParseError(RuntimeError):
    """Raised when a source line cannot be translated into bytecode."""


COMMENT_MARKERS = ("//", "#", ";")
LABEL_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.-"

OPCODE_TABLE = {
    "SIP": (),
    "EMBER": ("int",),
    "TWIST": ("int",),
    "DRIFT": ("label",),
    "GLINT.ZERO": ("label",),
    "GLINT.POS": ("label",),
    "FLASH": ("string",),
    "QUIET": (),
}


def strip_comments(line: str) -> str:
    """Remove inline comments while respecting quoted strings."""

    in_quote = False
    for idx, char in enumerate(line):
        if char == '"':
            in_quote = not in_quote
            continue
        if in_quote:
            continue
        for marker in COMMENT_MARKERS:
            if line.startswith(marker, idx):
                return line[:idx].rstrip()
    return line.rstrip()


def tokenize(line: str) -> list[str]:
    lexer = shlex.shlex(line, posix=True)
    lexer.commenters = ""
    lexer.whitespace_split = True
    try:
        return list(lexer)
    except ValueError as exc:  # pragma: no cover - shlex gives detail already
        raise ParseError(str(exc)) from exc


def parse_operand(raw: str, kind: str) -> object:
    if kind == "int":
        try:
            return int(raw, 10)
        except ValueError as exc:
            raise ParseError(f"Invalid integer literal '{raw}'") from exc
    if kind == "label":
        if not raw or any(ch not in LABEL_CHARS for ch in raw) or raw[0].isdigit():
            raise ParseError(f"Invalid label name '{raw}'")
        return raw
    if kind == "string":
        if raw == "":
            raise ParseError("String literal cannot be empty")
        return raw
    raise ParseError(f"Unsupported operand kind '{kind}'")


def split_labels(tokens: list[str], line_no: int) -> tuple[list[str], list[str]]:
    labels: list[str] = []
    remainder: list[str] = []
    defined_in_line: set[str] = set()

    for token in tokens:
        if token.endswith(":"):
            label = token[:-1]
            if not label:
                raise ParseError(f"Empty label on line {line_no}")
            if label[0].isdigit() or any(ch not in LABEL_CHARS for ch in label):
                raise ParseError(f"Invalid label '{label}' on line {line_no}")
            if label in defined_in_line:
                raise ParseError(f"Label '{label}' repeated on line {line_no}")
            labels.append(label)
            defined_in_line.add(label)
        else:
            remainder.append(token)
    return labels, remainder


def parse_program(source_path: Path) -> list[dict]:
    instructions: list[dict] = []
    pending_labels: list[tuple[str, int]] = []
    label_index: dict[str, int] = {}
    label_line: dict[str, int] = {}

    for line_no, raw_line in enumerate(source_path.read_text(encoding="utf-8").splitlines(), start=1):
        clean = strip_comments(raw_line).strip()
        if not clean:
            continue

        tokens = tokenize(clean)
        if not tokens:
            continue

        labels, payload = split_labels(tokens, line_no)
        pending_labels.extend((label, line_no) for label in labels)

        if not payload:
            continue

        opcode = payload[0]
        operand_kinds = OPCODE_TABLE.get(opcode)
        if operand_kinds is None:
            raise ParseError(f"Unknown opcode '{opcode}' on line {line_no}")
        operands = payload[1:]
        if len(operands) != len(operand_kinds):
            raise ParseError(
                f"Opcode '{opcode}' on line {line_no} expected {len(operand_kinds)} operand(s)"
            )

        parsed_operands = [parse_operand(raw, kind) for raw, kind in zip(operands, operand_kinds)]

        attached_labels = []
        for label, defined_line in pending_labels:
            if label in label_index:
                prev_line = label_line[label]
                raise ParseError(
                    f"Label '{label}' first defined on line {prev_line} and re-used on line {line_no}"
                )
            label_index[label] = len(instructions)
            label_line[label] = defined_line
            attached_labels.append(label)

        instruction = {
            "op": opcode,
            "args": parsed_operands,
            "line": line_no,
        }
        if attached_labels:
            instruction["labels"] = attached_labels
        instructions.append(instruction)
        pending_labels.clear()

    if pending_labels:
        dangling_label, _ = pending_labels[0]
        raise ParseError(f"Label '{dangling_label}' is not attached to any instruction")

    validate_labels(instructions)
    return instructions


def validate_labels(instructions: list[dict]) -> None:
    label_index = {}
    for idx, instr in enumerate(instructions):
        for label in instr.get("labels", []):
            label_index[label] = idx

    referenced: set[str] = set()
    for instr in instructions:
        operand_kinds = OPCODE_TABLE[instr["op"]]
        for kind, value in zip(operand_kinds, instr["args"]):
            if kind == "label":
                referenced.add(value)

    missing = referenced - set(label_index)
    if missing:
        raise ParseError(f"Undefined label reference(s): {', '.join(sorted(missing))}")


def build_payload(instructions: list[dict]) -> dict:
    label_index = {}
    for idx, instr in enumerate(instructions):
        for label in instr.get("labels", []):
            label_index[label] = idx
    return {
        "instructions": instructions,
        "labels": label_index,
        "instruction_count": len(instructions),
    }


def main(argv: Sequence[str]) -> int:
    if len(argv) != 2:
        print("Usage: python compiler.py <program.av>", file=sys.stderr)
        return 1

    source_path = Path(argv[1])
    if not source_path.exists():
        print(f"Source file '{source_path}' not found", file=sys.stderr)
        return 1

    try:
        instructions = parse_program(source_path)
    except ParseError as exc:
        print(f"[parse-error] {exc}", file=sys.stderr)
        return 1

    print(json.dumps(build_payload(instructions), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))