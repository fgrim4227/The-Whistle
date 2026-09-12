"""
Door class for room interconnections, supporting locks and wooden barricades.
"""

from typing import Optional
import pygame


class Door:
    def __init__(
        self,
        x: float,
        y: float,
        target_room_name: str,
        target_spawn_x: float,
        target_spawn_y: float,
        width: int = 32,
        height: int = 32,
        is_locked: bool = False,
        is_barred: bool = False,
        required_key: Optional[str] = None,
        is_exit_door: bool = False,
    ) -> None:
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height
        self.target_room_name = target_room_name
        self.target_spawn_x = target_spawn_x
        self.target_spawn_y = target_spawn_y
        self.is_locked = is_locked
        self.is_barred = is_barred
        self.required_key = required_key
        self.is_exit_door = is_exit_door

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def can_open(self, player) -> bool:
        if self.is_barred:
            return False
        if self.is_locked:
            if player.equipped_item == self.required_key:
                return True
            return False
        return True

    def unlock(self) -> None:
        self.is_locked = False

    def unbar(self) -> None:
        self.is_barred = False

    def render(self, surface: pygame.Surface) -> None:
        rect = self.get_rect()
        # Door frame
        pygame.draw.rect(surface, (55, 40, 30), rect)
        
        if self.is_barred:
            # Draw diagonal wooden barricade planks
            pygame.draw.line(surface, (140, 95, 60), (rect.left + 2, rect.top + 4), (rect.right - 2, rect.bottom - 4), 4)
            pygame.draw.line(surface, (140, 95, 60), (rect.left + 2, rect.bottom - 4), (rect.right - 2, rect.top + 4), 4)
        elif self.is_locked:
            # Golden padlock
            pygame.draw.circle(surface, (230, 190, 40), (rect.centerx, rect.centery - 2), 4)
            pygame.draw.rect(surface, (230, 190, 40), (rect.centerx - 3, rect.centery, 6, 6))
        else:
            # Unlocked door leaf
            door_inner = rect.inflate(-6, -4)
            pygame.draw.rect(surface, (90, 60, 40), door_inner)
            pygame.draw.circle(surface, (220, 200, 80), (door_inner.right - 4, door_inner.centery), 2)
