# Aventa Lumen Parser

Parses `.av` source files written in the custom **Aventa Lumen** stack language and emits
a structured program listing. The focus is on quick validation of syntax, labels, and
operand types rather than executing the code.

## Quick Start

```pwsh
python compiler/compiler.py code/test.av
```

The command prints JSON that contains each instruction, its operands, source line, and
any labels targeting that instruction.

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

Feel free to fork the opcode table inside `compiler/compiler.py` to grow the language.
