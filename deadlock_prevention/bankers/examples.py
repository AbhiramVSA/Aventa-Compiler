"""Curated example states for the Banker's Algorithm visualizer."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List

from .model import SystemState


def get_simple_example() -> SystemState:
    """Returns a simple safe example."""

    return SystemState(
        num_processes=3,
        num_resources=3,
        max_matrix=[
            [5, 3, 2],
            [3, 2, 2],
            [4, 3, 3],
        ],
        allocation_matrix=[
            [2, 1, 0],
            [2, 1, 1],
            [1, 1, 2],
        ],
        available=[1, 1, 1],
    )


def get_classic_example() -> SystemState:
    """Returns the textbook five-process safe example."""

    return SystemState(
        num_processes=5,
        num_resources=3,
        max_matrix=[
            [7, 5, 3],
            [3, 2, 2],
            [9, 0, 2],
            [2, 2, 2],
            [4, 3, 3],
        ],
        allocation_matrix=[
            [0, 1, 0],
            [2, 0, 0],
            [3, 0, 2],
            [2, 1, 1],
            [0, 0, 2],
        ],
        available=[3, 3, 2],
    )


def get_balanced_flow_example() -> SystemState:
    """Safe system with evenly distributed demand."""

    return SystemState(
        num_processes=4,
        num_resources=3,
        max_matrix=[
            [4, 3, 3],
            [2, 2, 2],
            [5, 3, 3],
            [3, 2, 2],
        ],
        allocation_matrix=[
            [1, 1, 0],
            [1, 0, 1],
            [2, 1, 1],
            [0, 0, 2],
        ],
        available=[2, 2, 2],
    )


def get_contention_example() -> SystemState:
    """Safe but high-contention system showing late unlocks."""

    return SystemState(
        num_processes=4,
        num_resources=3,
        max_matrix=[
            [5, 3, 2],
            [4, 2, 2],
            [4, 3, 3],
            [3, 3, 2],
        ],
        allocation_matrix=[
            [1, 0, 0],
            [2, 1, 1],
            [1, 2, 2],
            [0, 0, 1],
        ],
        available=[2, 1, 1],
    )


def get_unsafe_example() -> SystemState:
    """Configuration that immediately reveals an unsafe state."""

    return SystemState(
        num_processes=4,
        num_resources=2,
        max_matrix=[
            [3, 2],
            [4, 2],
            [2, 2],
            [4, 3],
        ],
        allocation_matrix=[
            [1, 0],
            [1, 1],
            [1, 1],
            [3, 1],
        ],
        available=[0, 0],
    )


def get_custom_blank(processes: int = 3, resources: int = 3) -> SystemState:
    """Zeroed template for users who want to input their own matrices."""

    return SystemState(
        num_processes=processes,
        num_resources=resources,
        max_matrix=[[0 for _ in range(resources)] for _ in range(processes)],
        allocation_matrix=[[0 for _ in range(resources)] for _ in range(processes)],
        available=[0 for _ in range(resources)],
    )


@dataclass(frozen=True)
class PresetDefinition:
    key: str
    title: str
    description: str
    builder: Callable[[], SystemState]
    badge: str


PRESET_LIBRARY: Dict[str, PresetDefinition] = {
    "simple": PresetDefinition(
        key="simple",
        title="Simple Safe (3×3)",
        description="Three processes and three resource types — great for walking through fundamentals.",
        builder=get_simple_example,
        badge="Safe",
    ),
    "classic": PresetDefinition(
        key="classic",
        title="Classic Textbook (5×3)",
        description="Five processes with overlapping needs; mirrors the example from operating-systems texts.",
        builder=get_classic_example,
        badge="Safe",
    ),
    "balanced": PresetDefinition(
        key="balanced",
        title="Balanced Flow (4×3)",
        description="Demonstrates how releasing resources mid-sequence unlocks others late in the run.",
        builder=get_balanced_flow_example,
        badge="Safe",
    ),
    "contention": PresetDefinition(
        key="contention",
        title="High Contention (4×3)",
        description="High demand relative to availability; shows non-trivial safe sequences.",
        builder=get_contention_example,
        badge="Safe",
    ),
    "unsafe": PresetDefinition(
        key="unsafe",
        title="Unsafe Demo (4×2)",
        description="No process can finish with the initial work vector, illustrating deadlock risk immediately.",
        builder=get_unsafe_example,
        badge="Unsafe",
    ),
}


def available_presets() -> List[PresetDefinition]:
    return list(PRESET_LIBRARY.values())


def get_preset(key: str) -> PresetDefinition | None:
    return PRESET_LIBRARY.get(key)


__all__ = [
    "available_presets",
    "get_preset",
    "get_simple_example",
    "get_classic_example",
    "get_balanced_flow_example",
    "get_contention_example",
    "get_unsafe_example",
    "get_custom_blank",
    "PresetDefinition",
]