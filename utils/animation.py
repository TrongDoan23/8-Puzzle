from __future__ import annotations
from typing import Dict


# Speed multiplier -> animation duration in milliseconds per step
SPEED_PRESETS: Dict[str, float] = {
    "0.25x": 0.25,
    "0.5x": 0.5,
    "1x": 1.0,
    "2x": 2.0,
    "3x": 3.0,
    "5x": 5.0,
}

BASE_ANIMATION_MS = 400  # Base duration for one tile slide at 1x speed


def get_animation_duration(speed_multiplier: float) -> int:
    """
    Get animation duration in milliseconds for a given speed multiplier.

    Args:
        speed_multiplier: Speed factor (e.g. 2.0 = twice as fast).

    Returns:
        Duration in milliseconds.
    """
    return max(50, int(BASE_ANIMATION_MS / speed_multiplier))
