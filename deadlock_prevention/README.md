# Deadlock Prevention: Banker's Algorithm

This project demonstrates the Banker's Algorithm for deadlock avoidance in operating systems. It provides an interactive CLI to configure processes and resources, perform resource requests, and observe safety checks in real time.

## Features

- Configure processes and resources.
- Load example matrices (Max, Allocation, Available).
- Perform resource requests interactively.
- Step-by-step safety checks.
- Determine if the system is in a SAFE or UNSAFE state.

## Installation

1. Ensure Python 3.10+ is installed.
2. Clone or copy this project.

## Running the Project

Navigate to the `deadlock_prevention` directory and run one of the following:

### Interactive CLI

```bash
python -m deadlock_prevention.bankers.cli
```

### Visual Frontend (Tkinter)

```bash
python demo.py
```

The frontend lets you adjust matrices, load curated examples, and stream the algorithm
trace live for presentations.

## Example Interaction

1. Choose an example system.
2. Run a safety check.
3. Make a resource request or tweak the matrices.
4. Observe the results and explanations (CLI) or the animated trace (GUI).
