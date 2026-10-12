<p align="center">
  <img src="assets/aventa-lumen-toolchain-logo.png" alt="Amber and navy symbols for the Aventa Lumen toolchain" width="160">
</p>

<h1 align="center">Aventa Lumen Toolchain</h1>

<p align="center">A Python toolchain for the Aventa Lumen stack language.</p>

<div align="center">

[Overview](#overview) · [Install](#install) · [Run](#run) · [Language](#language) · [Examples](#examples) · [Tests](#tests)

</div>

## Overview

The toolchain parses `.av` source files, assembles instructions, links labels, and runs bytecode on a stack machine. The command-line program reports each completed stage and prints the program output.

## Install

Use `Python 3.13+` for the root project. Install [uv](https://docs.astral.sh/uv/), then run these commands from the repository root:

```sh
uv sync --frozen
```

The lock file lists each project dependency and version.

## Run

Run a source file with the command-line program:

```sh
uv run --frozen python main.py code/test.av
```

The `SIP` instruction reads an integer from standard input. This command sends the value `9` to the sample program:

```sh
printf '9\n' | uv run --frozen python main.py code/test.av
```

The program reports each compilation stage, then prints the result:

```text
[parser] complete
[assembler] complete
[linker] complete
SIP> [runtime] complete
positive and divisible by three
```

Run the parser to print its JSON output:

```sh
uv run --frozen python compiler/parser.py code/test.av
```

## Language

The parser accepts labels in the form `label_name:`. It uses `//`, `#`, and `;` as comment markers. It does not read these marks as comments in a quoted string.

| Opcode | Action | Operand |
| --- | --- | --- |
| `SIP` | Read an integer onto the stack. | None |
| `EMBER n` | Push integer `n` onto the stack. | Integer |
| `TWIST n` | Subtract `n` from the top stack value. | Integer |
| `FLASH "text"` | Add a text value to program output. | Text |
| `DRIFT label` | Jump to a label. | Label |
| `GLINT.ZERO label` | Jump when the top stack value equals zero. | Label |
| `GLINT.POS label` | Jump when the top stack value is positive. | Label |
| `QUIET` | Stop the program. | None |

Read the [Aventa Lumen language guide](docs/aventa_language.md) for syntax details.

## Examples

- `code/test.av` reports whether an input is negative, zero, or positive. For positive inputs, it also checks divisibility by three.
- `code/pulse_counter.av` prints one `tick` for each positive count, then prints `liftoff`. For `0`, it prints `already at zero`.
- `code/odd_even.av` reports if an integer is odd or even.

## Tests

Run the toolchain tests from the repository root:

```sh
uv run --frozen python -m unittest discover -s tests
```

## Related project

The [`deadlock_prevention` project](deadlock_prevention/README.md) shows the Banker's Algorithm. It has a command-line interface and a Tkinter visualizer.
