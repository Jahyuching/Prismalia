"""Central constants used across the Prismalia MVP prototype."""

from __future__ import annotations

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60

# Isometric tile configuration
TILE_WIDTH = 64
TILE_HEIGHT = 32

# Gameplay pacing
PLAYER_MOVE_SPEED = 3.5  # tiles per second
ANIMAL_MOVE_SPEED = 3.0
PLAYER_HUNGER_DECAY = 3.0  # hunger points per minute
ANIMAL_HUNGER_DECAY = 4.0
PLAYER_HUNGER_REPLENISH = 30.0
ANIMAL_HUNGER_REPLENISH = 40.0

# Inventory limits
MAX_STACK_SIZE = 99

# Colours
COLOR_SKY = (25, 32, 48)
COLOR_TEXT = (238, 238, 238)
COLOR_PANEL = (20, 20, 24, 200)
COLOR_PANEL_BORDER = (120, 120, 150)
COLOR_HUNGER_BAR = (220, 140, 60)
COLOR_HUNGER_BACKGROUND = (60, 48, 40)

# Lighting
CAMPFIRE_LIGHT_RADIUS = 220
PLAYER_LIGHT_RADIUS = 120
