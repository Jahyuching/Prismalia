"""High level world orchestration for the Prismalia MVP."""

from __future__ import annotations

from typing import List, Optional, Tuple

import pygame

from ..engine.constants import (
    CAMPFIRE_LIGHT_RADIUS,
    COLOR_SKY,
    PLAYER_LIGHT_RADIUS,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


from ..engine.constants import CAMPFIRE_LIGHT_RADIUS, COLOR_SKY, PLAYER_LIGHT_RADIUS, WINDOW_WIDTH
from ..engine.isometric import grid_to_screen, screen_to_grid
from ..engine.tilemap import TileMap

from .animal import Animal
from .player import Player
from .resources import BUILDABLE_BLOCKS, RESOURCE_DEFINITIONS, RESOURCE_DISPLAY_NAMES


class World:
    def __init__(self, size: Tuple[int, int] = (24, 24)) -> None:
        self.surface_size = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.tilemap = TileMap(*size)
        self.tilemap.generate()
        spawn = (size[0] // 2, size[1] // 2)
        self.player = Player((spawn[0] + 0.5, spawn[1] + 0.5))
        self.animal = Animal((spawn[0] + 2, spawn[1] + 0.5))
        self.campfires: List[pygame.Vector2] = []
        self.camera_offset = (0.0, 0.0)
        self.message: Optional[str] = None

    def set_surface_size(self, size: Tuple[int, int]) -> None:
        self.surface_size = size

    # --- Update & simulation -------------------------------------------------
    def update(self, dt: float, keys: pygame.key.ScancodeWrapper) -> None:
        self.player.update(keys, self.tilemap, dt)
        self.animal.update(self, dt)
        self.camera_offset = self._compute_camera_offset()

    def _compute_camera_offset(self) -> Tuple[float, float]:
        centre_x = self.surface_size[0] / 2
        centre_y = self.surface_size[1] / 2
        iso_x, iso_y = grid_to_screen(self.player.position.x, self.player.position.y)
        return centre_x - iso_x, centre_y - iso_y

    # --- Interaction helpers -------------------------------------------------
    def harvest_near_player(self) -> bool:
        px, py = int(self.player.position.x), int(self.player.position.y)
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                tx, ty = px + dx, py + dy
                if self.harvest_at(tx, ty, recipient="player"):
                    self.message = "Collected resource"
                    return True
        self.message = "Nothing to collect"
        return False

    def harvest_at(self, x: int, y: int, recipient: str = "player") -> bool:
        if not self.tilemap.in_bounds(x, y):
            return False
        tile = self.tilemap.get(x, y)
        if not tile.resource:
            return False
        definition = RESOURCE_DEFINITIONS[tile.resource]
        if recipient == "player":
            self.player.inventory.add(definition.yield_item, definition.yield_amount)
        else:
            self.player.inventory.add(definition.yield_item, definition.yield_amount)
        tile.resource = None
        self.message = f"Gained {definition.yield_amount} {RESOURCE_DISPLAY_NAMES[definition.yield_item]}"
        return True

    def place_block(self, x: int, y: int, block: str, actor: str = "player") -> bool:
        if block not in BUILDABLE_BLOCKS:
            return False
        cost = BUILDABLE_BLOCKS[block]["cost"]
        # Only the player's inventory is tracked; the animal borrows it
        for resource, amount in cost.items():
            if self.player.inventory.amount(resource) < amount:
                if actor == "player":
                    self.message = "Missing resources"
                return False
        if not self.tilemap.is_walkable(x, y):
            if actor == "player":
                self.message = "Tile not free"
            return False
        for resource, amount in cost.items():
            self.player.inventory.remove(resource, amount)
        placed = self.tilemap.place_block(x, y, block)
        if placed and block == "campfire":
            self.campfires.append(pygame.Vector2(x + 0.5, y + 0.5))
        if placed:
            self.message = f"Placed {BUILDABLE_BLOCKS[block]['display']}"
        return placed

    def feed_animal(self) -> bool:
        if self.player.inventory.remove("berries", 1):
            self.animal.feed()
            self.message = "Animal fed"
            return True
        self.message = "No food for the animal"
        return False

    # --- Event handling ------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self.harvest_near_player()
            elif event.key == pygame.K_f:
                self.feed_animal()
            elif event.key == pygame.K_g:
                if not self.player.eat_available_food():
                    self.message = "No food to eat"
            elif event.key == pygame.K_r:
                self.player.cycle_building()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            tile = self.tile_from_screen(event.pos)
            if tile:
                self.place_block(tile[0], tile[1], self.player.selected_block, actor="player")

    # --- Utility --------------------------------------------------------------
    def tile_from_screen(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        offset_x, offset_y = self.camera_offset
        tx, ty = screen_to_grid(pos[0], pos[1], offset_x, offset_y)
        if self.tilemap.in_bounds(tx, ty):
            return tx, ty
        return None

    # --- Rendering -----------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(COLOR_SKY)
        self.tilemap.screen_draw(surface, self.camera_offset)
        self.player.draw(surface, self.camera_offset)
        self.animal.draw(surface, self.camera_offset)
        self._draw_lighting(surface)

    def _draw_lighting(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        lights: List[Tuple[pygame.Vector2, int]] = []
        lights.append((self.player.position.copy(), PLAYER_LIGHT_RADIUS))
        lights.append((self.animal.position.copy(), PLAYER_LIGHT_RADIUS // 2))
        for campfire in self.campfires:
            lights.append((campfire.copy(), CAMPFIRE_LIGHT_RADIUS))
        offset_x, offset_y = self.camera_offset
        for position, radius in lights:
            screen_x, screen_y = grid_to_screen(position.x, position.y, offset_x, offset_y)
            pygame.draw.circle(overlay, (0, 0, 0, 0), (int(screen_x), int(screen_y)), radius)
        surface.blit(overlay, (0, 0))

    # --- Messaging -----------------------------------------------------------
    def consume_message(self) -> Optional[str]:
        message = self.message
        self.message = None
        return message
