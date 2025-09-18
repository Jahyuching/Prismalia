"""Helper functions for converting between cartesian and isometric space."""

from __future__ import annotations

from typing import Tuple

from .constants import ISO_TILE_HEIGHT, ISO_TILE_WIDTH


def cartesian_to_isometric(x: float, y: float) -> Tuple[float, float]:
    """Convert cartesian grid coordinates to isometric screen coordinates."""

    iso_x = (x - y) * (ISO_TILE_WIDTH / 2)
    iso_y = (x + y) * (ISO_TILE_HEIGHT / 2)
    return iso_x, iso_y


def isometric_to_cartesian(iso_x: float, iso_y: float) -> Tuple[float, float]:
    """Inverse of :func:`cartesian_to_isometric`."""

    x = (iso_y / (ISO_TILE_HEIGHT / 2) + iso_x / (ISO_TILE_WIDTH / 2)) / 2
    y = (iso_y / (ISO_TILE_HEIGHT / 2) - iso_x / (ISO_TILE_WIDTH / 2)) / 2
    return x, y


def tile_to_screen(tile_x: int, tile_y: int, offset_x: float = 0, offset_y: float = 0) -> Tuple[int, int]:
    """Compute the pixel position of a tile in screen coordinates."""

    iso_x, iso_y = cartesian_to_isometric(tile_x, tile_y)
    return int(iso_x + offset_x), int(iso_y + offset_y)
