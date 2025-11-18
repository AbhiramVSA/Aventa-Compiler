import sys
from .examples import get_simple_example, get_classic_example
from .simulator import BankersSimulator
from .model import SystemState

def main():
    """
    Interactive CLI for the Banker's Algorithm demo.
    """
    print("Welcome to the Banker's Algorithm Demo!")

    examples = {
        "1": get_simple_example,
        "2": get_classic_example
    }

    system_state = None
    original_state = None

    while True:
        print("\nMenu:")
        print("1. Load an example system")
        print("2. Configure a new system")
        print("3. Show current system")
        print("4. Run safety check")
        print("5. Make a resource request")
        print("6. Reset to original configuration")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            print("\nChoose an example:")
            print("1. Simple Example")
            print("2. Classic Example")
            example_choice = input("Enter your choice: ")
            if example_choice in examples:
                system_state = examples[example_choice]()
                original_state = examples[example_choice]()
                print("Example system loaded.")
            else:
                print("Invalid choice.")

        elif choice == "2":
            try:
                num_processes = int(input("Enter number of processes: "))
                num_resources = int(input("Enter number of resources: "))

                print("Enter Max matrix (space-separated rows):")
                max_matrix = [list(map(int, input().split())) for _ in range(num_processes)]

                print("Enter Allocation matrix (space-separated rows):")
                allocation_matrix = [list(map(int, input().split())) for _ in range(num_processes)]

                print("Enter Available vector (space-separated):")
                available = list(map(int, input().split()))

                system_state = SystemState(
                    num_processes=num_processes,
                    num_resources=num_resources,
                    max_matrix=max_matrix,
                    allocation_matrix=allocation_matrix,
                    available=available
                )

                if not system_state.validate():
                    print("Invalid system configuration.")
                    system_state = None
                else:
                    original_state = SystemState(
                        num_processes=num_processes,
                        num_resources=num_resources,
                        max_matrix=max_matrix,
                        allocation_matrix=allocation_matrix,
                        available=available
                    )
                    print("System configured successfully.")

            except ValueError:
                print("Invalid input. Please try again.")

        elif choice == "3":
            if system_state:
                simulator = BankersSimulator(system_state)
                print(simulator.describe_system())
            else:
                print("No system loaded.")

        elif choice == "4":
            if system_state:
                simulator = BankersSimulator(system_state)
                is_safe, safe_sequence, explanation = simulator.check_safety()
                print(explanation)
            else:
                print("No system loaded.")

        elif choice == "5":
            if system_state:
                try:
                    process_id = int(input("Enter process ID: "))
                    request = list(map(int, input("Enter request vector (space-separated): ").split()))

                    simulator = BankersSimulator(system_state)
                    granted, explanation = simulator.apply_request(process_id, request)
                    print(explanation)
                except ValueError:
                    print("Invalid input. Please try again.")
            else:
                print("No system loaded.")

        elif choice == "6":
            if original_state:
                system_state = original_state
                print("System reset to original configuration.")
            else:
                print("No original configuration to reset to.")

        elif choice == "7":
            print("Exiting. Goodbye!")
            sys.exit()

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()