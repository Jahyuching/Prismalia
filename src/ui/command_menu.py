"""Simple block command interface for the animal companion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional

import pygame

from ..engine.constants import COLOR_PANEL, COLOR_PANEL_BORDER, COLOR_TEXT, TILE_HEIGHT, TILE_WIDTH
from ..engine.isometric import grid_to_screen

if TYPE_CHECKING:
    from ..gameplay.world import World


@dataclass
class CommandDefinition:
    identifier: str
    title: str
    description: str
    requires_target: bool = False


COMMANDS: List[CommandDefinition] = [
    CommandDefinition("goto", "Aller à", "Déplacer l'animal vers une case", True),
    CommandDefinition("take", "Prendre", "Récolter une ressource", True),
    CommandDefinition("place", "Placer", "Poser un bloc", True),
]


class CommandMenu:
    def __init__(self) -> None:
        self.visible = False
        self.font = pygame.font.Font(None, 20)
        self.title_font = pygame.font.Font(None, 26)
        self.sequence: List[dict] = []
        self.pending: Optional[CommandDefinition] = None
        self.status_text: str = ""

    def handle_event(self, event: pygame.event.Event, world: "World") -> bool:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_l:
            self.visible = not self.visible
            if not self.visible:
                self.pending = None
                self.status_text = ""
            return True

        if not self.visible:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_1, pygame.K_KP1):
                self._start_command(COMMANDS[0])
                return True
            if event.key in (pygame.K_2, pygame.K_KP2):
                self._start_command(COMMANDS[1])
                return True
            if event.key in (pygame.K_3, pygame.K_KP3):
                self._start_command(COMMANDS[2])
                return True
            if event.key == pygame.K_RETURN:
                if self.sequence:
                    world.animal.enqueue_sequence(self.sequence.copy())
                    self.sequence.clear()
                    self.status_text = "Séquence envoyée !"
                else:
                    self.status_text = "Séquence vide"
                return True
            if event.key == pygame.K_BACKSPACE and self.sequence:
                self.sequence.pop()
                self.status_text = "Dernière commande retirée"
                return True
            if event.key == pygame.K_ESCAPE:
                self.pending = None
                self.status_text = "Commande annulée"
                return True

        if self.pending and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            tile = world.tile_from_screen(event.pos)
            if tile:
                command = {"type": self.pending.identifier, "target": (tile[0] + 0.5, tile[1] + 0.5)}
                if self.pending.identifier == "place":
                    command["block"] = world.player.selected_block
                self.sequence.append(command)
                self.status_text = f"Ajouté: {self.pending.title}"
                self.pending = None
            else:
                self.status_text = "En dehors de la carte"
            return True

        return False

    def _start_command(self, definition: CommandDefinition) -> None:
        if definition.requires_target:
            self.pending = definition
            self.status_text = "Cliquez sur la case cible"
        else:
            self.sequence.append({"type": definition.identifier})
            self.status_text = f"Ajouté: {definition.title}"

    def draw(self, surface: pygame.Surface, world: "World") -> None:
        if not self.visible:
            hint = self.font.render("Appuyez sur L pour les commandes", True, COLOR_TEXT)
            surface.blit(hint, (surface.get_width() - hint.get_width() - 20, surface.get_height() - 30))
            return

        panel_width = 320
        panel_height = 260
        panel_rect = pygame.Rect(surface.get_width() - panel_width - 20, 80, panel_width, panel_height)
        panel_surface = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        panel_surface.fill(COLOR_PANEL)
        pygame.draw.rect(panel_surface, COLOR_PANEL_BORDER, panel_surface.get_rect(), 1)

        title = self.title_font.render("Blocs de commande", True, COLOR_TEXT)
        panel_surface.blit(title, (14, 10))

        y = 50
        for idx, command in enumerate(COMMANDS, start=1):
            text = self.font.render(f"{idx}. {command.title} - {command.description}", True, COLOR_TEXT)
            panel_surface.blit(text, (14, y))
            y += 26

        sequence_title = self.font.render("Séquence en attente:", True, COLOR_TEXT)
        panel_surface.blit(sequence_title, (14, 140))
        y = 170
        if not self.sequence:
            panel_surface.blit(self.font.render("(vide)", True, COLOR_TEXT), (14, y))
        else:
            for command in self.sequence:
                label = command["type"]
                if command["type"] == "place":
                    label = f"place ({command['block']})"
                text = self.font.render(f"- {label}", True, COLOR_TEXT)
                panel_surface.blit(text, (14, y))
                y += 20

        status = self.font.render(self.status_text, True, COLOR_TEXT)
        panel_surface.blit(status, (14, panel_height - 34))

        help_text = self.font.render("Entrée: exécuter | Retour: retirer", True, COLOR_TEXT)
        panel_surface.blit(help_text, (14, panel_height - 58))

        surface.blit(panel_surface, panel_rect.topleft)

        if self.pending:
            mouse_pos = pygame.mouse.get_pos()
            tile = world.tile_from_screen(mouse_pos)
            if tile:
                self._draw_highlight(surface, tile, world)

    def _draw_highlight(self, surface: pygame.Surface, tile: tuple[int, int], world: "World") -> None:
        offset_x, offset_y = world.camera_offset
        x, y = tile
        top = grid_to_screen(x, y, offset_x, offset_y)
        half_w = TILE_WIDTH // 2
        half_h = TILE_HEIGHT // 2
        points = [
            (top[0], top[1] - half_h),
            (top[0] + half_w, top[1]),
            (top[0], top[1] + half_h),
            (top[0] - half_w, top[1]),
        ]
        pygame.draw.polygon(surface, (255, 255, 255, 160), points, 2)
