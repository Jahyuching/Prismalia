"""Generate simple placeholder sprites for the MVP."""

from __future__ import annotations

from functools import lru_cache
from typing import Dict, Tuple

import pygame

from .constants import TILE_HEIGHT, TILE_WIDTH

TERRAIN_COLORS: Dict[str, Tuple[int, int, int]] = {
    "grass": (90, 150, 90),
    "dirt": (130, 100, 70),
    "rock": (110, 110, 110),
    "sand": (190, 170, 110),
    "water": (70, 120, 200),
    "wood_block": (140, 90, 50),
    "stone_block": (90, 90, 100),
    "campfire": (220, 120, 40),
}

RESOURCE_COLORS: Dict[str, Tuple[int, int, int]] = {
    "tree": (60, 100, 60),
    "rock": (90, 90, 110),
    "bush": (100, 150, 80),
}

ENTITY_COLORS: Dict[str, Tuple[int, int, int]] = {
    "player": (70, 160, 220),
    "animal": (230, 190, 90),
}


@lru_cache(maxsize=None)
def make_tile_surface(key: str) -> pygame.Surface:
    color = TERRAIN_COLORS.get(key, (200, 200, 200))
    surface = pygame.Surface((TILE_WIDTH, TILE_HEIGHT), pygame.SRCALPHA)
    points = [
        (TILE_WIDTH // 2, 0),
        (TILE_WIDTH, TILE_HEIGHT // 2),
        (TILE_WIDTH // 2, TILE_HEIGHT),
        (0, TILE_HEIGHT // 2),
    ]
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, (20, 20, 20), points, 1)
    return surface


@lru_cache(maxsize=None)
def make_resource_surface(key: str) -> pygame.Surface:
    color = RESOURCE_COLORS.get(key, (200, 80, 120))
    surface = pygame.Surface((TILE_WIDTH, TILE_HEIGHT), pygame.SRCALPHA)
    pygame.draw.circle(surface, color, (TILE_WIDTH // 2, TILE_HEIGHT // 2), TILE_HEIGHT // 2)
    pygame.draw.circle(surface, (0, 0, 0), (TILE_WIDTH // 2, TILE_HEIGHT // 2), TILE_HEIGHT // 2, 2)
    return surface


@lru_cache(maxsize=None)
def make_entity_surface(key: str) -> pygame.Surface:
    color = ENTITY_COLORS.get(key, (180, 180, 180))
    width = TILE_WIDTH // 2
    height = int(TILE_HEIGHT * 1.5)
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.ellipse(surface, color, (0, height // 3, width, height // 1.3))
    pygame.draw.ellipse(surface, (0, 0, 0), (0, height // 3, width, height // 1.3), 2)
    return surface
