"""Resolve label references and produce executable programs."""

from __future__ import annotations

from dataclasses import dataclass

from compiler.assembler import AssemblyUnit
from compiler.parser import OPCODE_TABLE


class LinkError(RuntimeError):
    """Raised when the linker cannot resolve symbol references."""


@dataclass(frozen=True)
class Operation:
    opcode: str
    args: tuple[object, ...]
    line: int


@dataclass(frozen=True)
class Program:
    operations: list[Operation]


def _resolve_operand(kind: str, value: object, labels: dict[str, int]) -> object:
    if kind != "label":
        return value
    target = labels.get(value)  # type: ignore[arg-type]
    if target is None:
        raise LinkError(f"Undefined label '{value}' during linking")
    return target


def link(unit: AssemblyUnit) -> Program:
    operations: list[Operation] = []
    for instruction in unit.instructions:
        opcode = instruction["op"]
        operand_kinds = OPCODE_TABLE[opcode]
        resolved_args = tuple(
            _resolve_operand(kind, value, unit.label_table)
            for kind, value in zip(operand_kinds, instruction["args"])
        )
        operations.append(
            Operation(opcode=opcode, args=resolved_args, line=instruction["line"])
        )
    return Program(operations=operations)
