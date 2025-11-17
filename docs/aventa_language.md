# Aventa Lumen Language & Toolchain Guide

This document explains every moving part of the **Aventa Lumen** stack-based language
and the companion compiler pipeline shipped in this repository. It is intended as a
presentation-ready reference that covers syntax, opcodes, build stages, and extension
points.

---

## 1. System Overview

Aventa Lumen programs are plain-text `.av` files. Each file is parsed into a list of
instructions, converted into a linkable unit, resolved into bytecode-style operations,
and finally interpreted by a compact runtime. The entire toolchain lives in this repo
and is driven through `python main.py <program.av>`.

Key traits:

- **Stack machine**: All calculations read and mutate the stack head (the last pushed
  integer). Strings exist only inside `FLASH` literals.
- **Structured jumps**: Labels are resolved to instruction indexes during linking, so
  runtime jumps are integer offsets instead of textual tags.
- **Single data type for arithmetic**: Integers are the only numeric type. Input is read
  from stdin and converted with Python's `int` function.
- **Deterministic pipeline**: Each stage emits a `[stage] complete` message so you can
  narrate compilation progress during demos.

---

## 2. Repository Layout

| Path | Purpose |
|------|---------|
| `main.py` | CLI entry point (parser → assembler → linker → runtime) |
| `compiler/parser.py` | Tokenizer, syntax checker, and JSON emitter |
| `compiler/assembler.py` | Builds label tables from parsed instructions |
| `compiler/linker.py` | Resolves label operands into numeric instruction indexes |
| `compiler/runtime.py` | Executes linked programs on a stack VM |
| `code/*.av` | Sample source programs |
| `docs/aventa_language.md` | This reference guide |

---

## 3. Language Syntax Rules

1. **Instructions**: One per line, consisting of an opcode followed by zero or more
   operands separated by whitespace.
2. **Labels**: `label_name:` placed before an instruction. Multiple labels can precede a
   single instruction; they all resolve to that instruction's index.
3. **Comments**: Begin with `//`, `#`, or `;` when not inside a quoted string. The parser
   ignores everything from the comment marker to end of line.
4. **String literals**: Wrap text in double quotes, e.g., `FLASH "hello"`. Spaces inside
   the quotes are preserved.
5. **Numeric literals**: Base-10 integers only (e.g., `EMBER 42`).
6. **Whitespace**: Tabs or spaces are interchangeable. Blank lines are ignored.

The parser validates that every referenced label exists, that opcodes receive the proper
number of operands, and that integer literals are well-formed.

---

## 4. Instruction Reference

| Opcode | Operands | Effect |
|--------|----------|--------|
| `SIP` | – | Read an integer from stdin and push it on the stack. |
| `EMBER <int>` | int literal | Push the literal value on the stack. |
| `TWIST <int>` | int literal | Subtract the literal from the current stack head. |
| `FLASH "text"` | string literal | Queue a string for output (printed after runtime completes). |
| `DRIFT <label>` | label | Jump unconditionally to the instruction tagged by `<label>`. |
| `GLINT.ZERO <label>` | label | Jump to `<label>` if the current stack head is zero; otherwise continue. |
| `GLINT.POS <label>` | label | Jump to `<label>` if the stack head is positive; otherwise continue. |
| `QUIET` | – | Halt execution immediately. |

Runtime stack discipline:

- `TWIST` requires at least one value on the stack; otherwise the runtime raises an
  `ExecutionError` and quits.
- `GLINT.*` reads the stack head if present; if the stack is empty the value defaults to
  `0`, which allows zero checks to behave predictably for initialization sequences.

---

## 5. Toolchain Pipeline

1. **Parser (`compiler/parser.py`)**
   - Strips comments using quote-aware scanning.
   - Tokenizes each line with `shlex`, ensuring string literals stay intact.
   - Validates opcodes, operand counts, and label definitions.
   - Emits JSON-like dictionaries for each instruction.

2. **Assembler (`compiler/assembler.py`)**
   - Accepts the parsed instruction list.
   - Builds a label → instruction index table.
   - Emits an `AssemblyUnit` dataclass containing both structures.

3. **Linker (`compiler/linker.py`)**
   - Resolves every operand tagged as a `label` into the numeric instruction index.
   - Produces a `Program` object with ready-to-execute `Operation` dataclasses.

4. **Runtime (`compiler/runtime.py`)**
   - Executes the program, prompting for integers when `SIP` is encountered.
   - Collects `FLASH` output and returns it to the CLI, which then prints the strings.

Each stage emits a `[stage] complete` log message so audiences can follow progress when
running demos live.

---

## 6. Running Programs

```pwsh
python main.py code/odd_even.av
```

Example session:

```
[parser] complete
[assembler] complete
[linker] complete
SIP> 233
[runtime] complete
odd
```

Tips:

- Programs with multiple `SIP` instructions will prompt for each value sequentially.
- You can still pipe input for automation: `7 | python main.py code/odd_even.av`.
- To inspect the parser output alone, run `python compiler/parser.py <file.av>`.

---

## 7. Sample Programs

| File | Concept Demonstrated |
|------|----------------------|
| `code/test.av` | Number classification (negative/zero/positive) plus divisibility by 3 loops. |
| `code/pulse_counter.av` | Countdown loop that emits "tick" until a zero check triggers `FLASH "liftoff"`. |
| `code/odd_even.av` | Runtime input plus parity detection using repeated subtraction and branching. |

Use these as templates when presenting features such as labels, loops, and string output.

---

## 8. Extending the Language

1. **Add opcode spec**: Edit `OPCODE_TABLE` in `compiler/parser.py` to define operand
   counts and kinds (`"int"`, `"label"`, or `"string"`).
2. **Update runtime**: Handle the new opcode inside the `while` loop in
   `compiler/runtime.py`. Throw `ExecutionError` with descriptive text for invalid stack
   states.
3. **Document**: Append the new opcode to the table in this guide and in `README.md`.
4. **Add sample**: Create a `.av` file that showcases the new instruction.

Because labels resolve to instruction indexes automatically, new opcodes that need jumps
should simply declare a `"label"` operand in the opcode table.

---

## 9. Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `[parse-error] Unknown opcode 'FOO'` | Opcode not listed in `OPCODE_TABLE`. | Add the opcode entry or fix the typo. |
| `[parse-error] Label 'L0' re-defined` | Same label reused before another instruction. | Rename the duplicate label. |
| `[link-error] Undefined label 'bar' during linking` | Jump references a label that was never defined. | Add the label or correct the reference. |
| `[runtime-error] TWIST on line N requires a stack value` | Attempted arithmetic on an empty stack. | Push a value (`SIP` or `EMBER`) before calling `TWIST`. |
| Program prints output before `[runtime] complete` | `FLASH` is inside a loop before `QUIET`. This is expected—the CLI prints queued strings after runtime completes. |

---

## 10. Presenting the Toolchain

When demoing:

1. Introduce the language using the table in §4.
2. Walk through the pipeline using §5, pointing to the corresponding modules.
3. Run `python main.py code/odd_even.av`, type a value, and highlight the stage logs.
4. Show how to extend the language by pointing to `OPCODE_TABLE` and the runtime
   handler.

With this reference, you now have a single document that covers both the language design
and the implementation strategy behind the Aventa Lumen compiler.
