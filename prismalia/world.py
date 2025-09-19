"""High level world orchestration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

import pygame

from .assets import AssetManager
from .constants import GRID_TILE_SIZE, LOGIC_BLOCKS, WINDOW_HEIGHT, WINDOW_WIDTH
from .entities import CompanionAnimal, Player
from .input import InputState
from .isoutils import cartesian_to_isometric
from .tilemap import MapTile, TileMap


@dataclass
class Camera:
    position: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(0, 0))

    def world_to_screen(self, world_pos: pygame.Vector2) -> Tuple[int, int]:
        iso_x, iso_y = cartesian_to_isometric(world_pos.x, world_pos.y)
        screen_x = iso_x + self.position.x
        screen_y = iso_y + self.position.y
        return int(screen_x), int(screen_y)


class World:
    """Container for all world related systems."""

    def __init__(self, asset_manager: AssetManager) -> None:
        self.asset_manager = asset_manager
        self.tilemap = TileMap(width=48, height=48)
        self.tilemap.generate()
        spawn_x, spawn_y = self.tilemap.find_spawn()
        companion_x, companion_y = self.tilemap.find_walkable_near(
            spawn_x,
            spawn_y,
            exclude={(spawn_x, spawn_y)},
        )
        self.player = Player(position=(spawn_x, spawn_y))
        self.animal = CompanionAnimal(position=(companion_x, companion_y))
        self.tilemap = TileMap(width=32, height=32)
        self.tilemap.generate()
        self.player = Player(position=(5, 5))
        self.animal = CompanionAnimal(position=(7, 6))
        self.camera = Camera()
        self.logic_unlocks: set[str] = set()
        self.pending_notifications: list[str] = []
        self._load_default_animations()

    def _load_default_animations(self) -> None:
        player_idle = self.asset_manager.load_animation("player:idle", GRID_TILE_SIZE)
        player_walk = self.asset_manager.load_animation("player:walk", GRID_TILE_SIZE)
        self.player.add_animation("idle", player_idle)
        self.player.add_animation("walk", player_walk)
        animal_idle = self.asset_manager.load_animation("animal:idle", GRID_TILE_SIZE)
        animal_walk = self.asset_manager.load_animation("animal:walk", GRID_TILE_SIZE)
        self.animal.add_animation("idle", animal_idle)
        self.animal.add_animation("walk", animal_walk)

    def update(self, dt: float, input_state: InputState) -> None:
        self.player.update(dt, self.tilemap, input_state)
        self.animal.update(dt, self.tilemap, self.player)

        if input_state.interact:
            self._handle_interaction()
        if input_state.feed_animal:
            self._handle_feed()
        if input_state.toggle_logic:
            self._handle_logic_ui_toggle()

        self._update_camera()
        self._update_unlocks()

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((20, 25, 40))
        offset = (self.camera.position.x, self.camera.position.y)
        self.tilemap.draw(surface, self.asset_manager, offset)
        self.animal.draw(surface, self.asset_manager, offset)
        self.player.draw(surface, self.asset_manager, offset)
        self._draw_hud(surface)

    def _update_camera(self) -> None:
        iso_x, iso_y = cartesian_to_isometric(self.player.state.position.x, self.player.state.position.y)
        self.camera.position.x = WINDOW_WIDTH / 2 - iso_x
        self.camera.position.y = WINDOW_HEIGHT / 2 - iso_y - GRID_TILE_SIZE[1]

    def _handle_interaction(self) -> None:
        tile_x = int(round(self.player.state.position.x))
        tile_y = int(round(self.player.state.position.y))
        if not (0 <= tile_x < self.tilemap.width and 0 <= tile_y < self.tilemap.height):
            return
        tile = self.tilemap.get(tile_x, tile_y)
        if tile.resource:
            self.player.inventory.add(tile.resource)
            self.pending_notifications.append(f"Collected {tile.resource}")
            tile.resource = None

    def _handle_feed(self) -> None:
        for food in ("grass", "fruit", "fish", "meat_cooked", "meat_raw"):
            if self.player.inventory.has(food):
                self.player.inventory.remove(food)
                self.animal.consume_food(food)
                self.pending_notifications.append("Fed companion")
                break

    def _handle_logic_ui_toggle(self) -> None:
        # Placeholder hook where future UI logic editor will be toggled
        self.pending_notifications.append("Logic interface toggled")

    def _update_unlocks(self) -> None:
        thresholds = {
            "sequence": 1,
            "loop": 5,
            "condition": 10,
            "memory": 15,
            "function": 25,
        }
        total = self.player.inventory.total_items()
        for block, requirement in thresholds.items():
            if total >= requirement and block not in self.logic_unlocks:
                self.logic_unlocks.add(block)
                self.pending_notifications.append(f"Unlocked {LOGIC_BLOCKS[block]}")

    def _draw_hud(self, surface: pygame.Surface) -> None:
        font = pygame.font.Font(None, 20)
        lines = ["Inventory:"] + self.player.inventory.to_lines()
        for idx, line in enumerate(lines):
            text = font.render(line, True, (240, 240, 240))
            surface.blit(text, (20, 20 + idx * 18))

        notif_y = WINDOW_HEIGHT - 20
        for message in reversed(self.pending_notifications[-5:]):
            text = font.render(message, True, (200, 220, 255))
            rect = text.get_rect(bottomleft=(20, notif_y))
            surface.blit(text, rect)
            notif_y -= 20

    def debug_pick_tile(self, screen_pos: Tuple[int, int]) -> MapTile | None:
        # Placeholder for later development: convert screen to world and pick tile
        return None
