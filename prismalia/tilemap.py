"""Tile map generation and rendering."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional, Tuple

import pygame

from .assets import AssetManager
from .constants import GRID_TILE_SIZE
from .isoutils import tile_to_screen


@dataclass
class MapTile:
    """Represents a single tile in the world grid."""

    terrain: str
    resource: Optional[str] = None
    walkable: bool = True


TERRAIN_TO_SPRITE: Dict[str, str] = {
    "grass": "tiles:grass",
    "dirt": "tiles:dirt",
    "rock": "tiles:rock",
    "sand": "tiles:sand",
    "water": "tiles:water",
}


class TileMap:
    """Simple isometric tile map with naive random generation."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.tiles: List[List[MapTile]] = [
            [MapTile("grass") for _ in range(width)] for _ in range(height)
        ]

    def generate(self, seed: int | None = None) -> None:
        rng = random.Random(seed)
        for y in range(self.height):
            for x in range(self.width):
                roll = rng.random()
                if roll < 0.65:
                    terrain = "grass"
                elif roll < 0.75:
                    terrain = "dirt"
                elif roll < 0.85:
                    terrain = "sand"
                elif roll < 0.95:
                    terrain = "rock"
                else:
                    terrain = "water"
                walkable = terrain != "water"
                resource = self._choose_resource_for_terrain(terrain, rng)
                self.tiles[y][x] = MapTile(terrain=terrain, resource=resource, walkable=walkable)

    def _choose_resource_for_terrain(self, terrain: str, rng: random.Random) -> Optional[str]:
        if terrain == "grass" and rng.random() < 0.1:
            return rng.choice(["grass", "fruit", "root"])
        if terrain == "dirt" and rng.random() < 0.15:
            return rng.choice(["root", "fiber"])
        if terrain == "rock" and rng.random() < 0.2:
            return rng.choice(["stone", "pebble", "crystal"])
        if terrain == "water" and rng.random() < 0.3:
            return "fish"
        if terrain == "sand" and rng.random() < 0.1:
            return "stick"
        return None

    def get(self, x: int, y: int) -> MapTile:
        return self.tiles[y][x]

    def is_walkable(self, x: int, y: int) -> bool:
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x].walkable
        return False

    def draw(self, surface: pygame.Surface, asset_manager: AssetManager, camera_offset: Tuple[float, float]) -> None:
        offset_x, offset_y = camera_offset
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                sprite_name = TERRAIN_TO_SPRITE.get(tile.terrain, "tiles:grass")
                sprite = asset_manager.load_image(sprite_name, GRID_TILE_SIZE)
                screen_x, screen_y = tile_to_screen(x, y, offset_x, offset_y)
                draw_x = screen_x - sprite.get_width() // 2
                draw_y = screen_y - GRID_TILE_SIZE[1] // 2
                surface.blit(sprite, (draw_x, draw_y))

    def iter_sorted_coordinates(self) -> Iterator[Tuple[int, int]]:
        for y in range(self.height):
            for x in range(self.width):
                yield x, y
