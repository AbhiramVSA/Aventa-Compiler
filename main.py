from __future__ import annotations

import sys
from pathlib import Path

from compiler import parser
from compiler.assembler import assemble
from compiler.linker import LinkError, link
from compiler.runtime import ExecutionError, run_program


def main(argv: list[str] | None = None) -> int:
    args = list(argv or sys.argv[1:])
    if not args or args[0] in {"-h", "--help"}:
        print("Usage: python main.py <program.av>")
        return 1

    source = Path(args[0])
    if not source.exists():
        print(f"Source file '{source}' not found")
        return 1

    try:
        instructions = parser.parse_program(source)
    except parser.ParseError as exc:
        print(f"[parse-error] {exc}")
        return 1
    print("[parser] complete")

    assembly = assemble(instructions)
    print("[assembler] complete")

    try:
        program = link(assembly)
    except LinkError as exc:
        print(f"[link-error] {exc}")
        return 1
    print("[linker] complete")

    try:
        outputs = run_program(program)
    except ExecutionError as exc:
        print(f"[runtime-error] {exc}")
        return 1

    print("[runtime] complete")
    for line in outputs:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
