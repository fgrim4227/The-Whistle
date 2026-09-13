"""
NPC class (Friendly cabin survivor / guide).
"""

from typing import Tuple, List, Optional
import pygame
from src.entities.BaseEntity import BaseEntity


class NPC(BaseEntity):
    def __init__(self, x: float, y: float, name: str = "Elena", dialogue_keys: list = None, item_to_give: Optional[str] = "lockpick") -> None:
        super().__init__(x, y, width=20, height=24, speed=0.0)
        self.name = name
        self.dialogue_keys = dialogue_keys or ["elena_dialogue_intro"]
        self.dialogue_index = 0
        self.item_to_give = item_to_give
        self.has_given_item = False

    def interact_with_player(self, player) -> Tuple[str, Optional[str]]:
        """
        Interacts with the player.
        Returns a tuple: (dialogue_key, item_given_or_None).
        """
        item_given = None
        if not self.has_given_item and self.item_to_give:
            item_given = self.item_to_give
            self.has_given_item = True
            player.add_item(item_given)
            return ("elena_dialogue_intro", item_given)

        # Context-sensitive narrative hints based on player inventory
        if player.has_item("key"):
            return ("elena_dialogue_escape", None)
        if player.has_item("crowbar"):
            return ("elena_dialogue_crowbar", None)
        if player.has_item("old_key"):
            return ("elena_dialogue_bedroom", None)
        if player.has_item("lockpick"):
            return ("elena_dialogue_dining", None)

        # Fallback to standard cycled dialogue
        if not self.dialogue_keys:
            return ("", None)
        key = self.dialogue_keys[self.dialogue_index]
        self.dialogue_index = (self.dialogue_index + 1) % len(self.dialogue_keys)
        return (key, None)

    def get_next_dialogue(self) -> str:
        if not self.dialogue_keys:
            return ""
        key = self.dialogue_keys[self.dialogue_index]
        self.dialogue_index = (self.dialogue_index + 1) % len(self.dialogue_keys)
        return key

    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        rect = self.get_rect().move(-camera_offset[0], -camera_offset[1])
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
