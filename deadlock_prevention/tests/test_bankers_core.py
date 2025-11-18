import unittest
from deadlock_prevention.bankers.model import SystemState
from deadlock_prevention.bankers.core import BankersAlgorithm
from deadlock_prevention.bankers.examples import get_simple_example, get_classic_example

class TestBankersCore(unittest.TestCase):
    def test_is_safe_state_simple(self):
        system_state = get_simple_example()
        algorithm = BankersAlgorithm(system_state)
        is_safe, safe_sequence = algorithm.is_safe_state()
        self.assertTrue(is_safe)
        self.assertIsNotNone(safe_sequence)

    def test_is_safe_state_classic(self):
        system_state = get_classic_example()
        algorithm = BankersAlgorithm(system_state)
        is_safe, safe_sequence = algorithm.is_safe_state()
        self.assertTrue(is_safe)
        self.assertIsNotNone(safe_sequence)

    def test_request_resources_safe(self):
        system_state = get_simple_example()
        algorithm = BankersAlgorithm(system_state)
        request = [1, 0, 2]
        process_id = 0
        self.assertTrue(algorithm.request_resources(process_id, request))

    def test_request_resources_unsafe(self):
        system_state = get_simple_example()
        algorithm = BankersAlgorithm(system_state)
        request = [10, 0, 2]  # Exceeds available
        process_id = 0
        self.assertFalse(algorithm.request_resources(process_id, request))

if __name__ == "__main__":
    unittest.main()