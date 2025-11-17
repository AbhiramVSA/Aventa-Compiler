# Aventa Lumen Toolchain

The project now ships a minimal end-to-end toolchain for the **Aventa Lumen** stack
language: parse the `.av` file, translate it into a linkable unit, resolve labels, and
execute the bytecode on a tiny virtual machine.

## Quick Start

```pwsh
python main.py code/test.av
```

The CLI now announces each compilation stage (`[parser] complete`, `[assembler] complete`,
`[linker] complete`, `[runtime] complete`) and then prints the queued `FLASH` output so
you can separate infrastructure logs from program output.

To inspect the intermediate JSON emitted by the parser directly, run
`python compiler/parser.py code/test.av`.

## Pipeline Overview

1. **Parser** (`compiler/parser.py`) cleans comments, validates syntax, and records
	labels.
2. **Assembler** (`compiler/assembler.py`) packages the raw instructions with a label
	table so they are easy to link.
3. **Linker** (`compiler/linker.py`) replaces label operands with instruction indexes.
4. **Runtime** (`compiler/runtime.py`) interprets the linked program using a compact
	stack machine.

## Instruction Set

| Opcode        | Description                                               | Operands |
|---------------|-----------------------------------------------------------|----------|
| `SIP`         | Reads an integer from input onto the stack                | –        |
| `EMBER n`     | Pushes the integer literal `n`                            | int      |
| `TWIST n`     | Conceptually subtracts `n` from the current stack head    | int      |
| `FLASH "txt"`| Emits a quoted string literal                             | string   |
| `DRIFT lbl`   | Unconditional branch to `lbl`                             | label    |
| `GLINT.ZERO lbl` | Branches when the stack head equals zero              | label    |
| `GLINT.POS lbl`  | Branches when the stack head is positive              | label    |
| `QUIET`       | Halts execution                                           | –        |

Labels use the syntax `label_name:` and can be stacked above a single instruction.
Inline comments support `//`, `#`, or `;` markers outside of quoted strings.

## Example Programs

- `code/test.av` – Classifies numbers as negative, zero, or positive and tests divisibility by three.
- `code/pulse_counter.av` – Demonstrates a countdown loop that prints "tick" until zero.
- `code/odd_even.av` – Reads an integer and reports whether it is odd or even.

Feel free to fork the opcode table inside `compiler/parser.py` to grow the language.
