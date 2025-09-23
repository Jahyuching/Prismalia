"""Simple text-based main menu for selecting and creating worlds."""

from __future__ import annotations

import random
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import pygame

from ..engine.constants import COLOR_PANEL_BORDER, COLOR_TEXT
from ..storage import save_manager


class MainMenu:
    def __init__(self) -> None:
        self.title_font = pygame.font.Font(None, 68)
        self.entry_font = pygame.font.Font(None, 32)
        self.detail_font = pygame.font.Font(None, 22)
        self.selection = 0
        self.worlds: List[Dict[str, Any]] = []
        self._entry_rects: List[Tuple[pygame.Rect, int]] = []
        self.refresh()

    def refresh(self) -> None:
        self.worlds = save_manager.list_worlds()
        if self.selection > len(self.worlds):
            self.selection = len(self.worlds)

    def handle_event(self, event: pygame.event.Event) -> Optional[Tuple[str, Dict[str, Any]]]:
        total_options = len(self.worlds) + 1
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selection = (self.selection - 1) % total_options
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selection = (self.selection + 1) % total_options
            elif event.key == pygame.K_RETURN:
                return self._activate_selection()
            elif event.key == pygame.K_r:
                self.refresh()
        elif event.type == pygame.MOUSEMOTION:
            option = self._option_at(event.pos)
            if option is not None:
                self.selection = option
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            option = self._option_at(event.pos)
            if option is not None:
                self.selection = option
                return self._activate_selection()
        return None

    def _option_at(self, pos: Tuple[int, int]) -> Optional[int]:
        for rect, index in self._entry_rects:
            if rect.collidepoint(pos):
                return index
        return None

    def _activate_selection(self) -> Optional[Tuple[str, Dict[str, Any]]]:
        if self.selection == 0:
            return "new_world", self._build_new_world_payload()
        if 0 < self.selection <= len(self.worlds):
            metadata = self.worlds[self.selection - 1]
            return "load_world", metadata
        return None

    def _build_new_world_payload(self) -> Dict[str, Any]:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        base_name = f"monde-{timestamp}"
        slot_name = base_name
        existing = {world.get("slot_name") for world in self.worlds}
        counter = 1
        while slot_name in existing:
            slot_name = f"{base_name}-{counter}"
            counter += 1
        seed = random.randrange(0, 2**31)
        return {
            "slot_name": slot_name,
            "title": f"Monde {timestamp}",
            "seed": seed,
        }

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill((16, 18, 28))
        title = self.title_font.render("Prismalia", True, COLOR_TEXT)
        title_rect = title.get_rect(center=(surface.get_width() // 2, 120))
        surface.blit(title, title_rect)

        subtitle = self.entry_font.render("Sélectionnez un monde", True, COLOR_TEXT)
        subtitle_rect = subtitle.get_rect(center=(surface.get_width() // 2, 180))
        surface.blit(subtitle, subtitle_rect)

        self._entry_rects = []
        start_y = 240
        option_width = 520
        option_height = 54
        total_options = len(self.worlds) + 1

        for index in range(total_options):
            rect = pygame.Rect(
                surface.get_width() // 2 - option_width // 2,
                start_y + index * (option_height + 16),
                option_width,
                option_height,
            )
            is_selected = index == self.selection
            color = (80, 90, 130, 220) if is_selected else (48, 54, 78, 200)
            panel = pygame.Surface(rect.size, pygame.SRCALPHA)
            panel.fill(color)
            pygame.draw.rect(panel, COLOR_PANEL_BORDER, panel.get_rect(), 2)

            if index == 0:
                label = self.entry_font.render("+ Nouveau monde", True, COLOR_TEXT)
                panel.blit(label, (20, panel.get_height() // 2 - label.get_height() // 2))
            else:
                metadata = self.worlds[index - 1]
                title_text = metadata.get("title") or metadata.get("slot_name") or "Monde"
                label = self.entry_font.render(str(title_text), True, COLOR_TEXT)
                panel.blit(label, (20, 10))
                updated = metadata.get("updated_at", "")
                details = metadata.get("player_hunger")
                detail_lines = [f"Dernière sauvegarde : {updated}"]
                if details is not None:
                    player_hunger = float(details)
                    animal_hunger = float(metadata.get("animal_hunger", 0.0))
                    detail_lines.append(
                        f"Faim joueur : {player_hunger:.0f} | Faim animal : {animal_hunger:.0f}"
                    )
                size_meta = metadata.get("size")
                if isinstance(size_meta, (list, tuple)) and len(size_meta) >= 2:
                    detail_lines.append(f"Taille : {size_meta[0]} x {size_meta[1]}")
                for i, line in enumerate(detail_lines):
                    detail = self.detail_font.render(line, True, COLOR_TEXT)
                    panel.blit(detail, (20, 28 + i * 18))

            surface.blit(panel, rect)
            self._entry_rects.append((rect, index))

        hint_text = self.detail_font.render(
            "Entrée: valider | R: rafraîchir | Échap: quitter", True, COLOR_TEXT
        )
        surface.blit(hint_text, (surface.get_width() // 2 - hint_text.get_width() // 2, surface.get_height() - 60))
