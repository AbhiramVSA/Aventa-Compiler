from .model import SystemState
from .core import BankersAlgorithm

class BankersSimulator:
    def __init__(self, system_state: SystemState):
        self.system_state = system_state
        self.algorithm = BankersAlgorithm(system_state)

    def describe_system(self) -> str:
        """
        Returns a description of the current system state.

        Returns:
            str: Formatted system state.
        """
        return self.system_state.pretty_print()

    def check_safety(self) -> tuple[bool, list[int] | None, str]:
        """
        Checks if the system is in a safe state.

        Returns:
            tuple[bool, list[int] | None, str]: (is_safe, safe_sequence, explanation)
        """
        is_safe, safe_sequence = self.algorithm.is_safe_state()
        explanation = "Safe sequence found: " + ", ".join(map(str, safe_sequence)) if is_safe else "System is in an unsafe state."
        return is_safe, safe_sequence, explanation

    def apply_request(self, process_id: int, request: list[int]) -> tuple[bool, str]:
        """
        Applies a resource request and returns the result.

        Args:
            process_id (int): The ID of the process making the request.
            request (list[int]): The resource request vector.

        Returns:
            tuple[bool, str]: (granted, explanation)
        """
        granted = self.algorithm.request_resources(process_id, request)
        explanation = "Request granted." if granted else "Request denied."
        return granted, explanation