"""Tiny stack-based runtime for the Aventa instruction set."""

from __future__ import annotations

from typing import Callable, Sequence

from compiler.linker import Program

InputProvider = Callable[[], int]
OutputSink = Callable[[str], None]


class ExecutionError(RuntimeError):
    """Raised when the runtime encounters an illegal state."""


def _prompt_for_int() -> int:
    while True:
        raw = input("SIP> ")
        try:
            return int(raw, 10)
        except ValueError:
            print("Please enter an integer.")


def run_program(
    program: Program,
    input_provider: InputProvider | None = None,
    output_sink: OutputSink | None = None,
) -> list[str]:
    input_fn = input_provider or _prompt_for_int
    outputs: list[str] = []

    def emit(value: str) -> None:
        outputs.append(value)
        if output_sink is not None:
            output_sink(value)

    stack: list[int] = []
    ip = 0
    ops = program.operations

    while ip < len(ops):
        op = ops[ip]
        opcode = op.opcode

        if opcode == "SIP":
            stack.append(input_fn())
            ip += 1
        elif opcode == "EMBER":
            stack.append(_as_int(op.args, opcode, op.line, index=0))
            ip += 1
        elif opcode == "TWIST":
            if not stack:
                raise ExecutionError(f"TWIST on line {op.line} requires a stack value")
            stack[-1] -= _as_int(op.args, opcode, op.line, index=0)
            ip += 1
        elif opcode == "DRIFT":
            ip = _as_int(op.args, opcode, op.line, index=0)
        elif opcode == "GLINT.ZERO":
            top = stack[-1] if stack else 0
            target = _as_int(op.args, opcode, op.line, index=0)
            ip = target if top == 0 else ip + 1
        elif opcode == "GLINT.POS":
            top = stack[-1] if stack else 0
            target = _as_int(op.args, opcode, op.line, index=0)
            ip = target if top > 0 else ip + 1
        elif opcode == "FLASH":
            emit(_as_str(op.args, opcode, op.line, index=0))
            ip += 1
        elif opcode == "QUIET":
            break
        else:
            raise ExecutionError(f"Unknown opcode '{opcode}' on line {op.line}")

    return outputs


def _as_int(
    args: Sequence[object], opcode: str, line: int, *, index: int = 0
) -> int:
    try:
        value = args[index]
    except IndexError as exc:
        raise ExecutionError(f"{opcode} on line {line} is missing operand {index}") from exc

    if isinstance(value, (int, str)):
        try:
            return int(value)
        except ValueError as exc:  # pragma: no cover - sanity guard
            raise ExecutionError(f"{opcode} on line {line} expects an integer operand") from exc

    raise ExecutionError(
        f"{opcode} on line {line} expects an int-like operand, got {type(value).__name__}"
    )


def _as_str(
    args: Sequence[object], opcode: str, line: int, *, index: int = 0
) -> str:
    try:
        value = args[index]
    except IndexError as exc:
        raise ExecutionError(f"{opcode} on line {line} is missing operand {index}") from exc

    if isinstance(value, str):
        return value

    raise ExecutionError(f"{opcode} on line {line} expects a string operand")
