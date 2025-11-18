from .model import SystemState

def get_simple_example() -> SystemState:
    """
    Returns a simple example system state.

    Returns:
        SystemState: Example system state.
    """
    return SystemState(
        num_processes=3,
        num_resources=3,
        max_matrix=[
            [7, 5, 3],
            [3, 2, 2],
            [9, 0, 2]
        ],
        allocation_matrix=[
            [0, 1, 0],
            [2, 0, 0],
            [3, 0, 2]
        ],
        available=[3, 3, 2]
    )

def get_classic_example() -> SystemState:
    """
    Returns a classic example system state.

    Returns:
        SystemState: Example system state.
    """
    return SystemState(
        num_processes=5,
        num_resources=3,
        max_matrix=[
            [7, 5, 3],
            [3, 2, 2],
            [9, 0, 2],
            [2, 2, 2],
            [4, 3, 3]
        ],
        allocation_matrix=[
            [0, 1, 0],
            [2, 0, 0],
            [3, 0, 2],
            [2, 1, 1],
            [0, 0, 2]
        ],
        available=[3, 3, 2]
    )