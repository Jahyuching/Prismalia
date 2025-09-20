"""Definition of the world tile map and helper queries."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Iterable, List, Optional, Tuple

import pygame

from .constants import TILE_HEIGHT, TILE_WIDTH
from .isometric import grid_to_screen
from .sprites import make_resource_surface, make_tile_surface


@dataclass
class Tile:
    terrain: str
    walkable: bool = True
    resource: Optional[str] = None
    block: Optional[str] = None


RESOURCE_TERRAIN = {
    "tree": "grass",
    "rock": "rock",
    "bush": "grass",
}


class TileMap:
    """Simple grid storing terrain information and optional resources."""

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self.tiles: List[List[Tile]] = [
            [Tile("grass", True, None) for _ in range(width)] for _ in range(height)
        ]

    def generate(self, seed: int | None = None) -> None:
        rng = random.Random(seed)
        for y in range(self.height):
            for x in range(self.width):
                roll = rng.random()
                if roll < 0.65:
                    terrain = "grass"
                elif roll < 0.78:
                    terrain = "dirt"
                elif roll < 0.9:
                    terrain = "rock"
                elif roll < 0.97:
                    terrain = "sand"
                else:
                    terrain = "water"
                walkable = terrain != "water"
                resource = self._maybe_spawn_resource(rng, terrain)
                self.tiles[y][x] = Tile(terrain=terrain, walkable=walkable, resource=resource)

    def _maybe_spawn_resource(self, rng: random.Random, terrain: str) -> Optional[str]:
        if terrain in {"grass", "dirt"} and rng.random() < 0.1:
            return rng.choice(["tree", "bush"])
        if terrain == "rock" and rng.random() < 0.12:
            return "rock"
        return None

    def get(self, x: int, y: int) -> Tile:
        return self.tiles[y][x]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_walkable(self, x: int, y: int) -> bool:
        if not self.in_bounds(x, y):
            return False
        tile = self.tiles[y][x]
        if tile.block in {"wood_block", "stone_block", "campfire"}:
            return False
        return tile.walkable

    def screen_draw(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        offset_x, offset_y = camera_offset
        for y in range(self.height):
            for x in range(self.width):
                tile = self.tiles[y][x]
                sprite = make_tile_surface(tile.block or tile.terrain)
                draw_x, draw_y = grid_to_screen(x, y, offset_x, offset_y)
                draw_x -= TILE_WIDTH // 2
                draw_y -= TILE_HEIGHT // 2
                surface.blit(sprite, (draw_x, draw_y))
                if tile.resource:
                    resource_sprite = make_resource_surface(tile.resource)
                    res_rect = resource_sprite.get_rect()
                    res_rect.midbottom = (draw_x + TILE_WIDTH // 2, draw_y + TILE_HEIGHT)
                    surface.blit(resource_sprite, res_rect)


                    res_x = draw_x
                    res_y = draw_y - TILE_HEIGHT // 2
                    surface.blit(resource_sprite, (res_x, res_y))

    def iter_tiles(self) -> Iterable[Tuple[int, int, Tile]]:
        for y in range(self.height):
            for x in range(self.width):
                yield x, y, self.tiles[y][x]

    def remove_resource(self, x: int, y: int) -> None:
        if self.in_bounds(x, y):
            self.tiles[y][x].resource = None

    def place_block(self, x: int, y: int, block: str) -> bool:
        if not self.in_bounds(x, y):
            return False
        tile = self.tiles[y][x]
        if not tile.walkable:
            return False
        tile.block = block
        tile.resource = None
        return True

    def clear_block(self, x: int, y: int) -> None:
        if self.in_bounds(x, y):
            self.tiles[y][x].block = None
