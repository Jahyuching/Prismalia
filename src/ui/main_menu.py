"""Main menu overlay handling game navigation."""

from __future__ import annotations

import random
from typing import Callable, Sequence

import pygame

from ..engine.constants import COLOR_PANEL, COLOR_PANEL_BORDER, COLOR_TEXT

MenuCallback = Callable[[], None]
NewWorldCallback = Callable[[int | None], None]
LoadWorldCallback = Callable[[str], None]


class MainMenu:
    """Simple keyboard-driven main menu for the prototype."""

    def __init__(
        self,
        *,
        on_new_world: NewWorldCallback,
        on_load_world: LoadWorldCallback,
        on_quit: MenuCallback,
    ) -> None:
        self.on_new_world = on_new_world
        self.on_load_world = on_load_world
        self.on_quit = on_quit

        self.selection = 0
        self.mode: str = "root"
        self.active = False
        self.saves: list[str] = []
        self.status_message: str = ""
        self.random = random.Random()

        self.title_font = pygame.font.Font(None, 54)
        self.option_font = pygame.font.Font(None, 30)
        self.small_font = pygame.font.Font(None, 22)

    # ------------------------------------------------------------------ state
    def set_saves(self, saves: Sequence[str]) -> None:
        self.saves = list(saves)
        self._clamp_selection()

    def open(self, saves: Sequence[str] | None = None) -> None:
        """Show the menu and optionally refresh the available saves."""

        if saves is not None:
            self.set_saves(saves)
        self.selection = 0
        self.mode = "root"
        self.active = True
        self.status_message = ""
        self._clamp_selection()

    def close(self) -> None:
        self.active = False

    def set_status(self, message: str) -> None:
        self.status_message = message

    # ---------------------------------------------------------------- controls
    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self._move_selection(-1)
                return True
            if event.key in (pygame.K_DOWN, pygame.K_s):
                self._move_selection(1)
                return True
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                self._activate_selection()
                return True
            if event.key == pygame.K_ESCAPE:
                if self.mode == "load":
                    self.mode = "root"
                    self.selection = 1 if self.saves else 0
                    self._clamp_selection()
                else:
                    self.on_quit()
                return True

        return False

    # ----------------------------------------------------------------- drawing
    def draw(self, surface: pygame.Surface) -> None:
        if not self.active:
            return

        options = self._current_options()
        self._clamp_selection()

        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        surface.blit(overlay, (0, 0))

        option_area = max(1, len(options)) * 40
        if self.mode == "load" and not self.saves:
            option_area += 30
        panel_width = 520
        panel_height = 170 + option_area
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill(COLOR_PANEL)
        pygame.draw.rect(panel_surface, COLOR_PANEL_BORDER, panel_surface.get_rect(), 1)

        title = self.title_font.render("Prismalia", True, COLOR_TEXT)
        panel_surface.blit(title, (32, 26))

        subtitle_text = "Menu principal" if self.mode == "root" else "Charger une sauvegarde"
        subtitle = self.small_font.render(subtitle_text, True, COLOR_TEXT)
        panel_surface.blit(subtitle, (34, 80))

        y = 120
        for index, label in enumerate(options):
            selected = index == self.selection
            color = COLOR_TEXT if not selected else (255, 255, 255)
            text = self.option_font.render(label, True, color)
            panel_surface.blit(text, (74, y))
            if selected:
                indicator = self.option_font.render("▶", True, color)
                panel_surface.blit(indicator, (40, y))
            y += 40

        if self.mode == "load" and not self.saves:
            info = self.small_font.render(
                "Aucune sauvegarde disponible", True, COLOR_TEXT
            )
            panel_surface.blit(info, (74, y))
            y += 30

        if self.status_message:
            status = self.small_font.render(self.status_message, True, COLOR_TEXT)
            panel_surface.blit(status, (34, panel_height - 70))

        hint = self.small_font.render(
            "↑/↓ pour naviguer · Entrée pour valider · Échap pour quitter",
            True,
            COLOR_TEXT,
        )
        hint_rect = hint.get_rect()
        hint_rect.bottomleft = (34, panel_height - 28)
        panel_surface.blit(hint, hint_rect)

        panel_rect = panel_surface.get_rect(center=surface.get_rect().center)
        surface.blit(panel_surface, panel_rect.topleft)

    # ----------------------------------------------------------------- helpers
    def _move_selection(self, delta: int) -> None:
        count = len(self._current_options())
        if count == 0:
            self.selection = 0
            return
        self.selection = (self.selection + delta) % count

    def _activate_selection(self) -> None:
        if self.mode == "root":
            if self.selection == 0:
                seed = self.random.randrange(0, 2**31)
                self.on_new_world(seed)
            elif self.selection == 1:
                if self.saves:
                    self.mode = "load"
                    self.selection = 0
                else:
                    self.set_status("Aucune sauvegarde détectée")
            elif self.selection == 2:
                self.on_quit()
        elif self.mode == "load":
            if self.selection < len(self.saves):
                self.on_load_world(self.saves[self.selection])
            else:
                self.mode = "root"
                self.selection = 1 if self.saves else 0
        self._clamp_selection()

    def _clamp_selection(self) -> None:
        count = len(self._current_options())
        if count == 0:
            self.selection = 0
        else:
            self.selection = max(0, min(self.selection, count - 1))

    def _current_options(self) -> list[str]:
        if self.mode == "root":
            return [
                "Nouveau monde",
                "Charger une sauvegarde",
                "Quitter",
            ]

        options = list(self.saves)
        options.append("Retour")
        return options
