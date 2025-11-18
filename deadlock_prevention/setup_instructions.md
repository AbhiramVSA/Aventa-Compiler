# Setup Instructions

## Prerequisites

- Python 3.10 or higher.

## Steps

1. Clone or copy the project to your local machine.
2. Navigate to the `deadlock_prevention` directory.
3. Run the CLI:
   ```bash
   python -m deadlock_prevention.bankers.cli
   ```
4. To run tests:
   ```bash
   python -m unittest discover -s deadlock_prevention/tests
   ```

## Directory Layout

- `bankers/`: Core logic and CLI for the Banker's Algorithm.
- `tests/`: Unit tests for the project.
- `README.md`: Project overview and usage instructions.
- `requirements.txt`: Notes on dependencies (none required).
