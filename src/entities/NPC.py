"""
NPC class (Friendly cabin survivor / guide).
"""

import pygame
from src.entities.BaseEntity import BaseEntity


class NPC(BaseEntity):
    def __init__(self, x: float, y: float, name: str = "Elena", dialogue_keys: list = None) -> None:
        super().__init__(x, y, width=20, height=24, speed=0.0)
        self.name = name
        self.dialogue_keys = dialogue_keys or ["thought_silbon_whistle"]
        self.dialogue_index = 0

    def get_current_dialogue(self) -> str:
        key = self.dialogue_keys[self.dialogue_index]
        self.dialogue_index = (self.dialogue_index + 1) % len(self.dialogue_keys)
        return key

    def render(self, surface: pygame.Surface) -> None:
        rect = self.get_rect()
        # Light survivor clothing
        pygame.draw.rect(surface, (180, 160, 140), rect, border_radius=4)
        # Head
        pygame.draw.circle(surface, (235, 195, 170), (rect.centerx, rect.top + 5), 5)
        # Interaction indicator triangle above head
        pygame.draw.polygon(surface, (240, 220, 50), [
            (rect.centerx - 4, rect.top - 8),
            (rect.centerx + 4, rect.top - 8),
            (rect.centerx, rect.top - 3)
        ])
