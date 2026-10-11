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
        process_id = 1
        request = [0, 0, 1]
        granted, explanation = simulator.apply_request(process_id, request)
        self.assertTrue(granted)
        self.assertEqual(explanation, "Request granted.")
        self.assertEqual(system_state.available, [1, 1, 0])
        self.assertEqual(system_state.allocation_matrix[process_id], [2, 1, 2])

    def test_apply_request_denied(self):
        system_state = get_simple_example()
        simulator = BankersSimulator(system_state)
        process_id = 0
        request = [10, 0, 2]  # Exceeds available
        original_available = system_state.available[:]
        original_allocation = [row[:] for row in system_state.allocation_matrix]
        granted, explanation = simulator.apply_request(process_id, request)
        self.assertFalse(granted)
        self.assertEqual(explanation, "Request denied.")
        self.assertEqual(system_state.available, original_available)
        self.assertEqual(system_state.allocation_matrix, original_allocation)

    def test_apply_negative_request_is_denied_without_state_change(self):
        system_state = get_simple_example()
        simulator = BankersSimulator(system_state)
        original_available = system_state.available[:]
        original_allocation = [row[:] for row in system_state.allocation_matrix]

        granted, explanation = simulator.apply_request(0, [-1, 0, 0])

        self.assertFalse(granted)
        self.assertEqual(explanation, "Request denied.")
        self.assertEqual(system_state.available, original_available)
        self.assertEqual(system_state.allocation_matrix, original_allocation)

if __name__ == "__main__":
    unittest.main()
