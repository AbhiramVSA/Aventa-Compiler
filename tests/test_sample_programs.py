"""Regression checks for the checked-in Aventa sample programs."""

from pathlib import Path
import unittest

from compiler.assembler import assemble
from compiler.linker import link
from compiler.parser import parse_program
from compiler.runtime import run_program


ROOT = Path(__file__).resolve().parents[1]


class SampleProgramTests(unittest.TestCase):
    def test_integer_classification_and_divisibility_example(self) -> None:
        source = ROOT / "code" / "test.av"

        cases = (
            (9, "positive and divisible by three"),
            (10, "positive but not divisible by three"),
            (0, "zero"),
            (-2, "negative value"),
        )

        for value, expected in cases:
            with self.subTest(value=value):
                instructions = parse_program(source)
                program = link(assemble(instructions))
                outputs = run_program(program, input_provider=lambda value=value: value)

                self.assertEqual(outputs, [expected])


if __name__ == "__main__":
    unittest.main()
