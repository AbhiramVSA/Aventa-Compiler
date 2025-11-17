"""Parser for the Aventa Lumen instruction set (.av files)."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
import shlex
import sys
from pathlib import Path
from typing import Callable, Sequence, Tuple, cast


class ParseError(RuntimeError):
    """Raised when the source file violates the instruction format."""


OperandParser = Callable[[str], object]


@dataclass(frozen=True)
class OpcodeSpec:
    name: str
    operand_parsers: Tuple[OperandParser, ...]
    operand_kinds: Tuple[str, ...]
    description: str


@dataclass(frozen=True)
class Instruction:
    opcode: str
    operands: Tuple[object, ...]
    labels: Tuple[str, ...]
    line: int

    def as_program_entry(self) -> dict:
        entry = {
            "op": self.opcode,
            "args": list(self.operands),
            "line": self.line,
        }
        if self.labels:
            entry["labels"] = list(self.labels)
        return entry


LABEL_PATTERN = re.compile(r"^[A-Za-z_][\w.-]*$")
COMMENT_TOKENS = ("//", "#", ";")


def parse_int(token: str) -> int:
    try:
        return int(token, 10)
    except ValueError as exc:  # pragma: no cover - defensive
        raise ParseError(f"Invalid integer literal '{token}'") from exc


def parse_label_reference(token: str) -> str:
    if not LABEL_PATTERN.match(token):
        raise ParseError(f"Invalid label name '{token}'")
    return token


def parse_string_literal(token: str) -> str:
    if token == "":
        raise ParseError("String literal cannot be empty")
    return token


OPCODE_SPECS = {
    # Input / stack operations
    "SIP": OpcodeSpec(
        name="SIP",
        operand_parsers=(),
        operand_kinds=(),
        description="Reads an integer from STDIN onto the stack",
    ),
    "EMBER": OpcodeSpec(
        name="EMBER",
        operand_parsers=(parse_int,),
        operand_kinds=("int",),
        description="Pushes an integer literal",
    ),
    "TWIST": OpcodeSpec(
        name="TWIST",
        operand_parsers=(parse_int,),
        operand_kinds=("int",),
        description="Subtracts an integer literal from the stack head",
    ),
    # Flow control
    "DRIFT": OpcodeSpec(
        name="DRIFT",
        operand_parsers=(parse_label_reference,),
        operand_kinds=("label",),
        description="Unconditional jump",
    ),
    "GLINT.ZERO": OpcodeSpec(
        name="GLINT.ZERO",
        operand_parsers=(parse_label_reference,),
        operand_kinds=("label",),
        description="Jump when the stack head equals zero",
    ),
    "GLINT.POS": OpcodeSpec(
        name="GLINT.POS",
        operand_parsers=(parse_label_reference,),
        operand_kinds=("label",),
        description="Jump when the stack head is positive",
    ),
    # Output / termination
    "FLASH": OpcodeSpec(
        name="FLASH",
        operand_parsers=(parse_string_literal,),
        operand_kinds=("string",),
        description="Writes a quoted string",
    ),
    "QUIET": OpcodeSpec(
        name="QUIET",
        operand_parsers=(),
        operand_kinds=(),
        description="Halts execution",
    ),
}


def strip_comments(line: str) -> str:
    in_quotes = False
    idx = 0
    while idx < len(line):
        char = line[idx]
        if char == '"':
            in_quotes = not in_quotes
            idx += 1
            continue
        if not in_quotes:
            for marker in COMMENT_TOKENS:
                if line.startswith(marker, idx):
                    return line[:idx].rstrip()
        idx += 1
    return line.rstrip()


def tokenize(line: str) -> list[str]:
    lexer = shlex.shlex(line, posix=True)
    lexer.commenters = ""
    lexer.whitespace_split = True
    try:
        return list(lexer)
    except ValueError as exc:
        raise ParseError(str(exc)) from exc


def parse_program(source_path: Path) -> list[Instruction]:
    raw_lines = source_path.read_text(encoding="utf-8").splitlines()
    instructions: list[Instruction] = []
    pending_labels: list[tuple[str, int]] = []
    defined_labels: dict[str, int] = {}

    for line_no, raw_line in enumerate(raw_lines, start=1):
        cleaned = strip_comments(raw_line).strip()
        if not cleaned:
            continue

        tokens = tokenize(cleaned)
        if not tokens:
            continue

        actual_tokens: list[str] = []
        for token in tokens:
            if token.endswith(":"):
                label = token[:-1]
                if not LABEL_PATTERN.match(label):
                    raise ParseError(f"Invalid label '{label}' on line {line_no}")
                if label in defined_labels:
                    first_line = defined_labels[label]
                    raise ParseError(
                        f"Label '{label}' re-defined on line {line_no} (first seen on line {first_line})"
                    )
                defined_labels[label] = line_no
                pending_labels.append((label, line_no))
            else:
                actual_tokens.append(token)

        if not actual_tokens:
            continue

        opcode = actual_tokens[0]
        spec = OPCODE_SPECS.get(opcode)
        if spec is None:
            raise ParseError(f"Unknown opcode '{opcode}' on line {line_no}")

        operand_tokens = actual_tokens[1:]
        if len(operand_tokens) != len(spec.operand_parsers):
            raise ParseError(
                f"Opcode '{opcode}' on line {line_no} expected {len(spec.operand_parsers)} operand(s)"
            )

        operands: list[object] = []
        for idx, (token, converter) in enumerate(zip(operand_tokens, spec.operand_parsers), start=1):
            try:
                operands.append(converter(token))
            except ParseError as exc:
                raise ParseError(f"Line {line_no}, operand {idx}: {exc}") from exc

        instruction_labels = tuple(label for label, _ in pending_labels)
        pending_labels.clear()

        instructions.append(
            Instruction(
                opcode=opcode,
                operands=tuple(operands),
                labels=instruction_labels,
                line=line_no,
            )
        )

    if pending_labels:
        label, label_line = pending_labels[0]
        raise ParseError(
            f"Label '{label}' declared on line {label_line} is not attached to an instruction"
        )

    validate_label_references(instructions)
    return instructions


def validate_label_references(instructions: Sequence[Instruction]) -> None:
    defined = build_label_index(instructions)
    referenced: set[str] = set()

    for instruction in instructions:
        spec = OPCODE_SPECS[instruction.opcode]
        for kind, value in zip(spec.operand_kinds, instruction.operands):
            if kind == "label":
                referenced.add(cast(str, value))

    missing = referenced - set(defined)
    if missing:
        missing_text = ", ".join(sorted(missing))
        raise ParseError(f"Undefined label reference(s): {missing_text}")


def build_label_index(instructions: Sequence[Instruction]) -> dict[str, int]:
    index: dict[str, int] = {}
    for idx, instruction in enumerate(instructions):
        for label in instruction.labels:
            index[label] = idx
    return index


def program_payload(instructions: Sequence[Instruction]) -> dict:
    return {
        "instructions": [instr.as_program_entry() for instr in instructions],
        "labels": build_label_index(instructions),
        "instruction_count": len(instructions),
    }


def main(argv: Sequence[str]) -> int:
    if len(argv) != 2:
        print("Usage: python compiler.py path/to/program.av", file=sys.stderr)
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

    payload = program_payload(instructions)
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))