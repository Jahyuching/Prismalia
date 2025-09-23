"""Overlay menu displayed when the game is paused."""

from __future__ import annotations

from typing import Optional

import pygame

from ..engine.constants import COLOR_PANEL, COLOR_PANEL_BORDER, COLOR_TEXT


class PauseMenu:
    def __init__(self) -> None:
        self.title_font = pygame.font.Font(None, 56)
        self.button_font = pygame.font.Font(None, 32)
        self._buttons = [
            ("Reprendre", "resume"),
            ("Sauvegarder et quitter", "save_quit"),
        ]
        self._button_rects: list[tuple[pygame.Rect, str]] = []

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "save_quit"
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return "resume"
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, action in self._button_rects:
                if rect.collidepoint(event.pos):
                    return action
        return None

    def draw(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        panel_width = 420
        panel_height = 260
        panel_rect = pygame.Rect(
            (surface.get_width() - panel_width) // 2,
            (surface.get_height() - panel_height) // 2,
            panel_width,
            panel_height,
        )
        panel_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        panel_surface.fill(COLOR_PANEL)
        pygame.draw.rect(panel_surface, COLOR_PANEL_BORDER, panel_surface.get_rect(), 2)

        title = self.title_font.render("Pause", True, COLOR_TEXT)
        title_rect = title.get_rect(center=(panel_rect.width // 2, 60))
        panel_surface.blit(title, title_rect)

        self._button_rects = []
        button_width = panel_rect.width - 120
        button_height = 50
        start_y = 110
        mouse_pos = pygame.mouse.get_pos()
        for index, (label, action) in enumerate(self._buttons):
            rect = pygame.Rect(
                (panel_rect.width - button_width) // 2,
                start_y + index * (button_height + 24),
                button_width,
                button_height,
            )
            absolute_rect = rect.move(panel_rect.topleft)
            hovered = absolute_rect.collidepoint(mouse_pos)
            fill_color = (90, 96, 128, 240) if hovered else (48, 54, 78, 230)
            pygame.draw.rect(panel_surface, fill_color, rect, border_radius=8)
            pygame.draw.rect(panel_surface, COLOR_PANEL_BORDER, rect, 2, border_radius=8)
            text = self.button_font.render(label, True, COLOR_TEXT)
            text_rect = text.get_rect(center=rect.center)
            panel_surface.blit(text, text_rect)
            self._button_rects.append((absolute_rect, action))

        surface.blit(panel_surface, panel_rect)
