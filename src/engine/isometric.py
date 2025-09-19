"""Helper functions for converting between grid and isometric screen coordinates."""

from __future__ import annotations

import math
from typing import Tuple

from .constants import TILE_HEIGHT, TILE_WIDTH


def grid_to_screen(x: float, y: float, offset_x: float = 0.0, offset_y: float = 0.0) -> Tuple[int, int]:
    """Convert grid coordinates to screen space using isometric projection."""

    iso_x = (x - y) * (TILE_WIDTH / 2)
    iso_y = (x + y) * (TILE_HEIGHT / 2)
    return int(iso_x + offset_x), int(iso_y + offset_y)


def screen_to_grid(screen_x: float, screen_y: float, offset_x: float = 0.0, offset_y: float = 0.0) -> Tuple[int, int]:
    """Map a screen coordinate to the underlying grid coordinate."""

    dx = screen_x - offset_x
    dy = screen_y - offset_y
    cart_x = (dx / (TILE_WIDTH / 2) + dy / (TILE_HEIGHT / 2)) / 2
    cart_y = (dy / (TILE_HEIGHT / 2) - dx / (TILE_WIDTH / 2)) / 2
    return math.floor(cart_x), math.floor(cart_y)


def tile_center(x: int, y: int, offset_x: float = 0.0, offset_y: float = 0.0) -> Tuple[int, int]:
    """Return the centre screen coordinate of a tile."""

    screen_x, screen_y = grid_to_screen(x + 0.5, y + 0.5, offset_x, offset_y)
    return screen_x, screen_y - TILE_HEIGHT // 2
