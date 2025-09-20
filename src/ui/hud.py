"""Heads-up display elements for the MVP."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from ..engine.constants import COLOR_HUNGER_BACKGROUND, COLOR_HUNGER_BAR, COLOR_PANEL, COLOR_PANEL_BORDER, COLOR_TEXT
from ..gameplay.resources import BUILDABLE_BLOCKS, RESOURCE_DISPLAY_NAMES

if TYPE_CHECKING:
    from ..gameplay.world import World


class HUD:
    def __init__(self) -> None:
        self.font_small = pygame.font.Font(None, 20)
        self.font_large = pygame.font.Font(None, 26)
        self.message: str = ""
        self.message_timer = 0.0

    def update(self, dt: float) -> None:
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""

    def set_message(self, text: str) -> None:
        self.message = text
        self.message_timer = 2.5

    def draw(self, surface: pygame.Surface, world: "World") -> None:
        self._draw_bars(surface, world)
        self._draw_inventory(surface, world)
        self._draw_controls(surface, world)
        if self.message:
            text = self.font_large.render(self.message, True, COLOR_TEXT)
            rect = text.get_rect(center=(surface.get_width() // 2, 40))
            surface.blit(text, rect)

    def _draw_bars(self, surface: pygame.Surface, world: "World") -> None:
        bar_width = 180
        bar_height = 16
        padding = 10
        self._draw_bar(surface, (padding, padding), bar_width, bar_height, world.player.hunger, "Player Hunger")
        self._draw_bar(surface, (padding, padding + 28), bar_width, bar_height, world.animal.hunger, "Animal Hunger")

    def _draw_bar(
        self,
        surface: pygame.Surface,
        pos: tuple[int, int],
        width: int,
        height: int,
        value: float,
        label: str,
    ) -> None:
        x, y = pos
        pygame.draw.rect(surface, COLOR_HUNGER_BACKGROUND, (x, y, width, height))
        fill_width = int(width * max(0.0, min(1.0, value / 100.0)))
        pygame.draw.rect(surface, COLOR_HUNGER_BAR, (x, y, fill_width, height))
        pygame.draw.rect(surface, COLOR_PANEL_BORDER, (x, y, width, height), 1)
        text = self.font_small.render(label, True, COLOR_TEXT)
        surface.blit(text, (x, y - 18))

    def _draw_inventory(self, surface: pygame.Surface, world: "World") -> None:
        panel_width = 220
        panel_height = 160
        panel_rect = pygame.Rect(10, surface.get_height() - panel_height - 10, panel_width, panel_height)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill(COLOR_PANEL)
        pygame.draw.rect(panel_surface, COLOR_PANEL_BORDER, panel_surface.get_rect(), 1)

        title = self.font_large.render("Inventory", True, COLOR_TEXT)
        panel_surface.blit(title, (10, 8))
        y = 40
        if not world.player.inventory.stacks:
            panel_surface.blit(self.font_small.render("Empty", True, COLOR_TEXT), (10, y))
        else:
            for resource, amount in world.player.inventory.items():
                name = RESOURCE_DISPLAY_NAMES.get(resource, resource.title())
                text = self.font_small.render(f"{name}: {amount}", True, COLOR_TEXT)
                panel_surface.blit(text, (10, y))
                y += 20

        selected = world.player.selected_block
        selected_name = BUILDABLE_BLOCKS[selected]["display"]
        selected_text = self.font_small.render(f"Build: {selected_name}", True, COLOR_TEXT)
        panel_surface.blit(selected_text, (10, panel_rect.height - 28))

        surface.blit(panel_surface, panel_rect.topleft)

    def _draw_controls(self, surface: pygame.Surface, world: "World") -> None:
        lines = [
            "Controls:",
            "Move: WASD / Arrows",
            "Collect: E",
            "Feed animal: F",
            "Eat berries: G",
            "Cycle build: R",
            "Place block: Right click",
            "Command menu: L",
        ]
        x = surface.get_width() - 240
        y = 20
        for line in lines:
            text = self.font_small.render(line, True, COLOR_TEXT)
            surface.blit(text, (x, y))
            y += 20
