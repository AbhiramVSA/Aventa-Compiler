import unittest
from deadlock_prevention.bankers.examples import get_simple_example
from deadlock_prevention.bankers.simulator import BankersSimulator

class TestBankersSimulator(unittest.TestCase):
    def test_describe_system(self):
        system_state = get_simple_example()
        simulator = BankersSimulator(system_state)
        description = simulator.describe_system()
        self.assertTrue(len(description) > 0)

    def test_check_safety(self):
        system_state = get_simple_example()
        simulator = BankersSimulator(system_state)
        is_safe, safe_sequence, explanation = simulator.check_safety()
        self.assertTrue(is_safe)
        self.assertIsNotNone(safe_sequence)
        self.assertTrue(len(explanation) > 0)

    def test_apply_request_granted(self):
        system_state = get_simple_example()
        simulator = BankersSimulator(system_state)
        process_id = 0
        request = [1, 0, 2]
        granted, explanation = simulator.apply_request(process_id, request)
        self.assertTrue(granted)
        self.assertTrue(len(explanation) > 0)

    def test_apply_request_denied(self):
        system_state = get_simple_example()
        simulator = BankersSimulator(system_state)
        process_id = 0
        request = [10, 0, 2]  # Exceeds available
        granted, explanation = simulator.apply_request(process_id, request)
        self.assertFalse(granted)
        self.assertTrue(len(explanation) > 0)

if __name__ == "__main__":
    unittest.main()