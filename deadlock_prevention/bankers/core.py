from .model import SystemState

class BankersAlgorithm:
    """
    Implements the Banker's Algorithm for deadlock avoidance.
    """
    def __init__(self, system_state: SystemState):
        self.system_state = system_state

    def is_safe_state(self) -> tuple[bool, list[int] | None]:
        """
        Determines if the system is in a safe state.

        Returns:
            tuple[bool, list[int] | None]: (is_safe, safe_sequence)
        """
        work = self.system_state.available[:]
        finish = [False] * self.system_state.num_processes
        safe_sequence = []

        while len(safe_sequence) < self.system_state.num_processes:
            found = False
            for i in range(self.system_state.num_processes):
                if not finish[i] and all(
                    self.system_state.need_matrix[i][j] <= work[j]
                    for j in range(self.system_state.num_resources)
                ):
                    # Process i can finish
                    work = [work[j] + self.system_state.allocation_matrix[i][j] for j in range(self.system_state.num_resources)]
                    finish[i] = True
                    safe_sequence.append(i)
                    found = True
                    break

            if not found:
                return False, None

        return True, safe_sequence

    def request_resources(self, process_id: int, request: list[int]) -> bool:
        """
        Handles a resource request from a process.

        Args:
            process_id (int): The ID of the process making the request.
            request (list[int]): The resource request vector.

        Returns:
            bool: True if the request is granted, False otherwise.
        """
        if any(request[j] > self.system_state.need_matrix[process_id][j] for j in range(self.system_state.num_resources)):
            return False  # Request exceeds need

        if any(request[j] > self.system_state.available[j] for j in range(self.system_state.num_resources)):
            return False  # Request exceeds available resources

        # Provisionally allocate resources
        self.system_state.available = [
            self.system_state.available[j] - request[j] for j in range(self.system_state.num_resources)
        ]
        self.system_state.allocation_matrix[process_id] = [
            self.system_state.allocation_matrix[process_id][j] + request[j] for j in range(self.system_state.num_resources)
        ]

        safe, _ = self.is_safe_state()
        if safe:
            return True

        # Rollback allocation
        self.system_state.available = [
            self.system_state.available[j] + request[j] for j in range(self.system_state.num_resources)
        ]
        self.system_state.allocation_matrix[process_id] = [
            self.system_state.allocation_matrix[process_id][j] - request[j] for j in range(self.system_state.num_resources)
        ]
        return False