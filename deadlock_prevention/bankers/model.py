from dataclasses import dataclass
from typing import List

@dataclass
class SystemState:
    num_processes: int
    num_resources: int
    max_matrix: List[List[int]]
    allocation_matrix: List[List[int]]
    available: List[int]

    @property
    def need_matrix(self) -> List[List[int]]:
        """
        Computes the need matrix as Max - Allocation.

        Returns:
            List[List[int]]: The need matrix.
        """
        return [
            [self.max_matrix[i][j] - self.allocation_matrix[i][j] for j in range(self.num_resources)]
            for i in range(self.num_processes)
        ]

    def validate(self) -> bool:
        """
        Validates the system state.

        Returns:
            bool: True if the state is valid, False otherwise.
        """
        if len(self.max_matrix) != self.num_processes or len(self.allocation_matrix) != self.num_processes:
            return False
        if any(len(row) != self.num_resources for row in self.max_matrix):
            return False
        if any(len(row) != self.num_resources for row in self.allocation_matrix):
            return False
        if len(self.available) != self.num_resources:
            return False
        if any(self.max_matrix[i][j] < self.allocation_matrix[i][j] for i in range(self.num_processes) for j in range(self.num_resources)):
            return False
        return True

    def pretty_print(self) -> str:
        """
        Returns a string representation of the matrices.

        Returns:
            str: Formatted matrices.
        """
        def format_matrix(matrix):
            return "\n".join(" ".join(map(str, row)) for row in matrix)

        return (
            f"Max Matrix:\n{format_matrix(self.max_matrix)}\n\n"
            f"Allocation Matrix:\n{format_matrix(self.allocation_matrix)}\n\n"
            f"Need Matrix:\n{format_matrix(self.need_matrix)}\n\n"
            f"Available Vector:\n{' '.join(map(str, self.available))}"
        )