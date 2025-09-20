"""Base entity helpers for rendering and movement."""

from __future__ import annotations

from typing import Tuple

import pygame

from .isometric import grid_to_screen
from .constants import TILE_HEIGHT
from .sprites import make_entity_surface


class Entity:
    def __init__(self, kind: str, position: Tuple[float, float]) -> None:
        self.kind = kind
        self.position = pygame.Vector2(position)
        self.velocity = pygame.Vector2(0, 0)

    def draw(self, surface: pygame.Surface, camera_offset: Tuple[float, float]) -> None:
        sprite = make_entity_surface(self.kind)
        screen_x, screen_y = grid_to_screen(self.position.x, self.position.y, *camera_offset)
        rect = sprite.get_rect()
        rect.midbottom = (
            int(screen_x),
            int(screen_y + TILE_HEIGHT // 2),
        )
        surface.blit(sprite, rect)


        draw_x, draw_y = grid_to_screen(self.position.x, self.position.y, *camera_offset)
        draw_x -= sprite.get_width() // 2
        draw_y -= sprite.get_height() - sprite.get_height() // 3
        surface.blit(sprite, (draw_x, draw_y))

    def move_towards(self, target: pygame.Vector2, speed: float, dt: float) -> float:
        direction = target - self.position
        distance = direction.length()
        if distance < 1e-3:
            self.position.update(target)
            return distance
        direction.scale_to_length(min(distance, speed * dt))
        self.position += direction
        return distance
