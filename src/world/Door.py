import os
from typing import Any, Optional, Tuple
import pygame

import settings

_DOOR_SPRITES_LOADED = False
_SPRITE_DOOR_LOCKED: Optional[pygame.Surface] = None
_SPRITE_DOOR_UNLOCKED: Optional[pygame.Surface] = None
_SPRITE_ESCAPE_SENSOR: Optional[pygame.Surface] = None
_SPRITE_ESCAPE_CHAINS: Optional[pygame.Surface] = None
_SPRITE_ESCAPE_CLEAR: Optional[pygame.Surface] = None


def _load_door_sprites() -> None:
    global _DOOR_SPRITES_LOADED, _SPRITE_DOOR_LOCKED, _SPRITE_DOOR_UNLOCKED
    global _SPRITE_ESCAPE_SENSOR, _SPRITE_ESCAPE_CHAINS, _SPRITE_ESCAPE_CLEAR
    if _DOOR_SPRITES_LOADED:
        return
    _DOOR_SPRITES_LOADED = True
    sheet_path = os.path.join(settings.BASE_DIR, "assets", "graphics", "environment", "spritesheet.png")
    if os.path.exists(sheet_path):
        try:
            sheet = pygame.image.load(sheet_path).convert_alpha()
            _SPRITE_DOOR_LOCKED = sheet.subsurface(pygame.Rect(704, 64, 16, 64))
            _SPRITE_DOOR_UNLOCKED = sheet.subsurface(pygame.Rect(640, 64, 16, 64))
            _SPRITE_ESCAPE_SENSOR = sheet.subsurface(pygame.Rect(688, 32, 32, 32))
            _SPRITE_ESCAPE_CHAINS = sheet.subsurface(pygame.Rect(656, 32, 32, 32))
            _SPRITE_ESCAPE_CLEAR = sheet.subsurface(pygame.Rect(624, 32, 32, 32))
        except Exception as e:
            print(f"Notice: Failed to load door sprites: {e}")


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
        is_bolted: bool = False,
        required_key: Optional[str] = None,
        is_exit_door: bool = False,
        render_graphic: bool = True,
        is_stairs: bool = False,
        planks_remaining: int = 3,
        lock_type: Optional[str] = None,
        passcode: Optional[str] = None,
        unlocked: bool = False,
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
        self.is_bolted = is_bolted
        self.required_key = required_key
        self.is_exit_door = is_exit_door
        self.render_graphic = render_graphic
        self.is_stairs = is_stairs
        self.planks_remaining = planks_remaining if is_barred else 0
        self.lock_type = lock_type
        self.passcode = passcode
        self.unlocked = unlocked

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def can_open(self, player) -> bool:
        if self.is_barred or self.is_bolted:
            return False
        if self.is_locked:
            if hasattr(player, "has_item"):
                return player.has_item(self.required_key)
            return player.equipped_item == self.required_key
        return True

    def unlock(self) -> None:
        self.is_locked = False

    def unbar(self) -> None:
        self.planks_remaining = 0
        self.is_barred = False

    def unbolt(self) -> None:
        self.is_bolted = False

    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0), house: Optional[Any] = None) -> None:
        _load_door_sprites()
        rect = self.get_rect().move(-camera_offset[0], -camera_offset[1])

        # 1. Master Bedroom vertical door from Upper Hallway (replace yellow overlay with real top-down door sprites)
        is_mb_door = self.target_room_name.lower() in ("master_bedroom", "masterbedroom")
        if is_mb_door and _SPRITE_DOOR_LOCKED is not None:
            if self.is_locked:
                # Snap to tile grid (16x16) for seamless doorway alignment
                draw_x = int(self.x // 16) * 16 - camera_offset[0]
                draw_y = int(self.y // 16) * 16 - camera_offset[1]
                surface.blit(_SPRITE_DOOR_LOCKED, (draw_x, draw_y))
            # When unlocked, the base tilemap already has the clean door authored without padlock!
            return

        # 2. Escape door (Living Room exit) with 3 reactive sprite states
        if self.is_exit_door and _SPRITE_ESCAPE_SENSOR is not None:
            is_powered = getattr(house, "power_restored", False) if house else False
            draw_x = rect.x + (self.width - 32) // 2
            draw_y = rect.y + (self.height - 32)
            if not is_powered:
                # State 1: Active security sensor (red beam)
                surface.blit(_SPRITE_ESCAPE_SENSOR, (draw_x, draw_y))
            elif self.is_locked:
                # State 2: Power restored, chained door with padlock
                surface.blit(_SPRITE_ESCAPE_CHAINS, (draw_x, draw_y))
            else:
                # State 3: Unlocked / free access
                surface.blit(_SPRITE_ESCAPE_CLEAR, (draw_x, draw_y))
            return

        # 3. Barricaded door planks
        if self.is_barred:
            if self.render_graphic:
                pygame.draw.rect(surface, (55, 40, 30), rect)

            # Planks rendered according to planks_remaining
            if self.planks_remaining >= 1:
                pygame.draw.line(surface, (140, 95, 60), (rect.left + 2, rect.top + 4), (rect.right - 2, rect.bottom - 4), 4)
            if self.planks_remaining >= 2:
                pygame.draw.line(surface, (140, 95, 60), (rect.left + 2, rect.bottom - 4), (rect.right - 2, rect.top + 4), 4)
            if self.planks_remaining >= 3:
                pygame.draw.line(surface, (155, 105, 65), (rect.left + 2, rect.centery), (rect.right - 2, rect.centery), 4)
            return

        if not self.render_graphic:
            return

        # 4. Fallback procedural door
        pygame.draw.rect(surface, (55, 40, 30), rect)
        door_inner = rect.inflate(-6, -4)
        pygame.draw.rect(surface, (90, 60, 40), door_inner)
        pygame.draw.circle(surface, (220, 200, 80), (door_inner.right - 4, door_inner.centery), 2)
