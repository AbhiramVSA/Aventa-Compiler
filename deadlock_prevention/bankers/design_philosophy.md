# Design Philosophy

## What is the Banker's Algorithm?

The Banker's Algorithm is a deadlock avoidance algorithm that ensures a system remains in a safe state. It simulates resource allocation for processes and determines whether granting a resource request will leave the system in a safe state.

### Key Concepts

- **Processes**: Independent units of execution requiring resources.
- **Resource Types**: Categories of resources (e.g., CPU, memory).
- **Max Matrix**: Maximum resources each process may need.
- **Allocation Matrix**: Resources currently allocated to each process.
- **Need Matrix**: Resources each process still needs (Max - Allocation).
- **Available Vector**: Resources currently available.
- **Safe State**: A state where all processes can complete without deadlock.
- **Safety Algorithm**: Checks if the system is in a safe state.
- **Resource-Request Algorithm**: Determines if a resource request can be safely granted.

## Design Goals

1. **Clarity**: Prioritize readability and maintainability.
2. **Separation of Concerns**: Distinct modules for data, logic, simulation, and CLI.
3. **Testability**: Ensure all components are unit-testable.
4. **Extensibility**: Allow future enhancements (e.g., GUI).

## Module Interaction

```
+----------------+
| model.py       |
| Data structures|
+----------------+
        |
        v
+----------------+
| core.py        |
| Algorithm logic|
+----------------+
        |
        v
+----------------+
| simulator.py   |
| Scenario runner|
+----------------+
        |
        v
+----------------+
| cli.py         |
| User interface |
+----------------+
        ^
        |
+----------------+
| examples.py    |
| Sample configs |
+----------------+
```
