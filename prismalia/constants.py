"""Centralised constants for the Prismalia project."""

from __future__ import annotations

import pygame

# General window configuration
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# Isometric grid configuration
ISO_TILE_WIDTH = 64
ISO_TILE_HEIGHT = 32
GRID_TILE_SIZE = (ISO_TILE_WIDTH, ISO_TILE_HEIGHT)

# Entity defaults
PLAYER_SPEED = 200  # tiles per second converted in cartesian space
ANIMAL_SPEED = 160
PLAYER_COLLISION_RADIUS = 0.4
ANIMAL_COLLISION_RADIUS = 0.35

# Layers for drawing order
LAYER_FLOOR = 0
LAYER_OBJECTS = 1
LAYER_ENTITIES = 2

# Colours (RGB) used for placeholder visuals
COLOR_DEBUG_GRID = (50, 50, 50)
COLOR_SKY = (15, 20, 35)
COLOR_TEXT = (240, 240, 240)
COLOR_PLACEHOLDERS = {
    "player": (66, 135, 245),
    "animal": (245, 188, 66),
    "grass": (100, 150, 90),
    "dirt": (134, 94, 69),
    "rock": (110, 110, 110),
    "water": (40, 90, 160),
    "sand": (170, 160, 100),
    "tree": (80, 100, 60),
    "bush": (70, 120, 60),
    "resource": (120, 60, 120),
}

# Font configuration
DEFAULT_FONT_NAME = "fira code"
DEFAULT_FONT_SIZE = 16

# Resource identifiers used by the inventory system
RESOURCE_TYPES = {
    "grass": "Grass",
    "fruit": "Wild Fruit",
    "fish": "Fish",
    "meat_raw": "Raw Meat",
    "meat_cooked": "Cooked Meat",
    "bread": "Bread",
    "root": "Tubers",
    "wood": "Wood Log",
    "stick": "Stick",
    "stone": "Stone",
    "pebble": "Pebble",
    "fiber": "Fiber",
    "fat": "Animal Fat",
    "crystal": "Glow Crystal",
}

# Logic block identifiers placeholder
LOGIC_BLOCKS = {
    "sequence": "Sequence",
    "loop": "Loop",
    "condition": "Condition",
    "memory": "Memory",
    "function": "Function",
}


def init_fonts() -> None:
    """Initialise pygame fonts ensuring fallback when unavailable."""

    pygame.font.init()
    # Attempt to find the preferred font; fall back to default pygame font
    if not pygame.font.match_font(DEFAULT_FONT_NAME):
        # pygame will fallback automatically when using None
        pass
