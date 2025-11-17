"""Translate parsed instruction lists into assembler units ready for linking."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AssemblyUnit:
    instructions: list[dict]
    label_table: dict[str, int]


def assemble(instructions: list[dict]) -> AssemblyUnit:
    """Prepare a parsed instruction list for linking."""

    label_table: dict[str, int] = {}
    for idx, instruction in enumerate(instructions):
        for label in instruction.get("labels", []):
            label_table[label] = idx
    return AssemblyUnit(instructions=instructions, label_table=label_table)
