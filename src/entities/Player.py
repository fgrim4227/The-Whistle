"""
Player class (Paramedic protagonist - Andreas).
Manages directional movement with collisions, spritesheet animations,
flashlight, battery consumption, stealth hiding state, and inner monologues.
"""

from typing import Optional, List, Dict, Tuple
import pygame
from gale.animation import Animation
from gale.command import CommandBindings
from gale.state import StateMachine

import settings
from src.commands import (
    CYCLE_ITEM,
    FLASHLIGHT,
    INTERACT,
    MOVE_DOWN,
    MOVE_LEFT,
    MOVE_RIGHT,
    MOVE_UP,
    RUN,
    SELECT_SLOT_1,
    SELECT_SLOT_2,
    SELECT_SLOT_3,
    SELECT_SLOT_4,
    SELECT_SLOT_5,
    STOP_MOVE_DOWN,
    STOP_MOVE_LEFT,
    STOP_MOVE_RIGHT,
    STOP_MOVE_UP,
    STOP_RUN,
    THROW,
)
from src.definitions import entity as entity_defs
from src.entities.BaseEntity import BaseEntity
from src.i18n import t
from src.states.entity.player.PlayerHidingState import PlayerHidingState
from src.states.entity.player.PlayerIdleState import PlayerIdleState
from src.states.entity.player.PlayerWalkState import PlayerWalkState


class Player(BaseEntity):
    def __init__(self, x: float, y: float) -> None:
        width, height = entity_defs.PLAYER_SIZE
        super().__init__(x, y, width=width, height=height, speed=settings.PLAYER_SPEED)
        self.flashlight_on = True
        self.battery = 100.0
        self.is_hidden = False
        self.current_hiding_spot = None

        # Multi-slot inventory system (stores collected tools & keys)
        self.inventory: List[str] = []
        self.selected_item_index: int = 0

        self.panic_meter = 0.0
        self.is_running = False
        self.step_timer = 0.0
        self.footstep_taken = False

        # Movement intent, updated by MOVE_*/STOP_MOVE_* commands and
        # resolved into actual movement by update_movement() every frame.
        self.held: Dict[str, bool] = {
            "move_left": False,
            "move_right": False,
            "move_up": False,
            "move_down": False,
        }

        # Edge-triggered intent: interact/throw are one-shot actions
        # resolved (and cleared) by PlayState.update(), since they need
        # access to the current room/house/monster to resolve.
        self.interact_requested = False
        self.throw_requested = False

        self.command_bindings = CommandBindings()
        self.command_bindings.bind("move_left", press=MOVE_LEFT, release=STOP_MOVE_LEFT)
        self.command_bindings.bind("move_right", press=MOVE_RIGHT, release=STOP_MOVE_RIGHT)
        self.command_bindings.bind("move_up", press=MOVE_UP, release=STOP_MOVE_UP)
        self.command_bindings.bind("move_down", press=MOVE_DOWN, release=STOP_MOVE_DOWN)
        self.command_bindings.bind("run", press=RUN, release=STOP_RUN)
        self.command_bindings.bind("interact", press=INTERACT)
        self.command_bindings.bind("throw", press=THROW)
        self.command_bindings.bind("action", press=THROW)
        self.command_bindings.bind("flashlight", press=FLASHLIGHT)
        self.command_bindings.bind("cycle_item", press=CYCLE_ITEM)
        self.command_bindings.bind("slot_1", press=SELECT_SLOT_1)
        self.command_bindings.bind("slot_2", press=SELECT_SLOT_2)
        self.command_bindings.bind("slot_3", press=SELECT_SLOT_3)
        self.command_bindings.bind("slot_4", press=SELECT_SLOT_4)
        self.command_bindings.bind("slot_5", press=SELECT_SLOT_5)
        
        # Directional animations
        self.animations: Dict[str, Animation]
        self._animation_textures: Dict[str, str]
        self.animations, self._animation_textures = self._create_animations()
        self.current_animation = self.animations.get("idle-down")
        self.current_texture = self._animation_textures.get("idle-down")
        self.is_moving = False

        self.state_machine = StateMachine({
            "idle": lambda sm: PlayerIdleState(self, sm),
            "walk": lambda sm: PlayerWalkState(self, sm),
            "hiding": lambda sm: PlayerHidingState(self, sm),
        })
        self.state_name = "idle"
        self.state_machine.change(self.state_name)

        # Internal thought / monologue system
        self.current_thought: Optional[str] = "thought_intro"
        self.thought_timer = 5.0

    @property
    def equipped_item(self) -> Optional[str]:
        """Returns the currently selected item in the inventory, if any."""
        if 0 <= self.selected_item_index < len(self.inventory):
            return self.inventory[self.selected_item_index]
        return None

    @equipped_item.setter
    def equipped_item(self, item: Optional[str]) -> None:
        if item is None:
            return
        if item not in self.inventory:
            if len(self.inventory) < 6:
                self.inventory.append(item)
                self.selected_item_index = len(self.inventory) - 1
            else:
                self.inventory[self.selected_item_index] = item
        else:
            self.selected_item_index = self.inventory.index(item)

    def add_item(self, item: str) -> bool:
        """Adds an item to inventory without overwriting existing items."""
        if item not in self.inventory:
            if len(self.inventory) < 6:
                self.inventory.append(item)
                self.selected_item_index = len(self.inventory) - 1
                return True
            return False
        self.selected_item_index = self.inventory.index(item)
        return True

    def remove_item(self, item: str) -> bool:
        """Removes an item from inventory (e.g. consumed keys)."""
        if item in self.inventory:
            self.inventory.remove(item)
            if self.selected_item_index >= len(self.inventory):
                self.selected_item_index = max(0, len(self.inventory) - 1)
            return True
        return False

    def has_item(self, item: Optional[str]) -> bool:
        """Checks if player possesses the given item in any inventory slot."""
        if not item:
            return False
        return item in self.inventory

    def select_slot(self, index: int) -> None:
        """Selects an active inventory slot by index (0-4)."""
        if 0 <= index < len(self.inventory):
            self.selected_item_index = index

    def cycle_item(self) -> None:
        """Cycles to the next item in inventory."""
        if self.inventory:
            self.selected_item_index = (self.selected_item_index + 1) % len(self.inventory)

    def _create_animations(self) -> Tuple[Dict[str, Animation], Dict[str, str]]:
        return entity_defs.build_animations(
            entity_defs.PLAYER_ANIMATIONS, entity_defs.PLAYER_FALLBACK_COLOR, entity_defs.PLAYER_SIZE
        )

    def change_animation(self, anim_name: str) -> None:
        if anim_name in self.animations and self.current_animation != self.animations[anim_name]:
            self.current_animation = self.animations[anim_name]
            self.current_animation.reset()
            self.current_texture = self._animation_textures.get(anim_name)

    def change_state(self, state_name: str, *args, **kwargs) -> None:
        if state_name == self.state_name:
            return
        self.state_machine.change(state_name, *args, **kwargs)
        self.state_name = state_name

    def get_collision_rect(self) -> pygame.Rect:
        # Feet collision rect (bottom 16x16 area) for natural top-down perspective
        return pygame.Rect(int(self.x), int(self.y + 16), 16, 16)

    def toggle_flashlight(self) -> None:
        if self.battery > 0:
            self.flashlight_on = not self.flashlight_on
        else:
            self.flashlight_on = False

    def recharge_battery(self, amount: float = settings.BATTERY_RECHARGE_AMOUNT) -> None:
        self.battery = min(100.0, self.battery + amount)
        self.flashlight_on = True

    def set_thought(self, text_key: str, duration: float = 4.0) -> None:
        self.current_thought = text_key
        self.thought_timer = duration

    def hide(self, spot) -> None:
        self.is_hidden = True
        self.current_hiding_spot = spot
        self.flashlight_on = False
        self.change_state("hiding")

    def exit_hide(self) -> None:
        self.is_hidden = False
        self.current_hiding_spot = None
        self.change_state("idle")

    def clear_movement(self) -> None:
        """Completely halts movement and clears all held directional inputs, running status, and velocity."""
        for key in self.held:
            self.held[key] = False
        self.is_running = False
        self.is_moving = False
        self.vx = 0.0
        self.vy = 0.0
        self.step_timer = 0.0
        self.footstep_taken = False
        self.interact_requested = False
        self.throw_requested = False
        if not self.is_hidden:
            self.change_state("idle")
            if self.direction:
                self.change_animation(f"idle-{self.direction}")

    def clear_held(self) -> None:
        self.clear_movement()

    def sync_movement_keys(self) -> None:
        """Synchronizes movement and run states with actual physical keyboard state."""
        keys = pygame.key.get_pressed()
        get_k = (lambda k: keys.get(k, False)) if isinstance(keys, dict) else (lambda k: keys[k])
        self.held["move_left"] = bool(get_k(pygame.K_LEFT) or get_k(pygame.K_a))
        self.held["move_right"] = bool(get_k(pygame.K_RIGHT) or get_k(pygame.K_d))
        self.held["move_up"] = bool(get_k(pygame.K_UP) or get_k(pygame.K_w))
        self.held["move_down"] = bool(get_k(pygame.K_DOWN) or get_k(pygame.K_s))
        self.is_running = bool(get_k(pygame.K_LSHIFT) or get_k(pygame.K_RSHIFT))
        self.is_moving = any(self.held.values())
        if not self.is_moving:
            self.vx = 0.0
            self.vy = 0.0
            self.step_timer = 0.0
            self.footstep_taken = False
            if not self.is_hidden:
                self.change_state("idle")
                if self.direction:
                    self.change_animation(f"idle-{self.direction}")

    def update_movement(self, obstacles: List[pygame.Rect], dt: float) -> None:
        if self.is_hidden:
            return

        dx = 0.0
        dy = 0.0

        if self.held["move_left"]:
            dx -= 1.0
            self.direction = "left"
        if self.held["move_right"]:
            dx += 1.0
            self.direction = "right"
        if self.held["move_up"]:
            dy -= 1.0
            self.direction = "up"
        if self.held["move_down"]:
            dy += 1.0
            self.direction = "down"

        self.is_moving = (dx != 0.0 or dy != 0.0)
        self.change_state("walk" if self.is_moving else "idle")
        if self.is_moving:
            self.change_animation(f"walk-{self.direction}")

        current_speed = settings.PLAYER_RUN_SPEED if self.is_running else self.speed

        if self.is_moving:
            step_interval = 0.25 if self.is_running else 0.44
            self.step_timer += dt
            if self.step_timer >= step_interval:
                self.step_timer = 0.0
                self.footstep_taken = True
        else:
            self.step_timer = 0.0
            self.footstep_taken = False

        if dx != 0.0 and dy != 0.0:
            inv = 0.70710678
            dx *= inv
            dy *= inv

        # Collision resolution per axis on character feet
        new_x = self.x + dx * current_speed * dt
        feet_rect_x = pygame.Rect(int(new_x), int(self.y + 16), 16, 16)
        if not any(feet_rect_x.colliderect(obs) for obs in obstacles):
            self.x = new_x

        new_y = self.y + dy * current_speed * dt
        feet_rect_y = pygame.Rect(int(self.x), int(new_y + 16), 16, 16)
        if not any(feet_rect_y.colliderect(obs) for obs in obstacles):
            self.y = new_y

    def update(self, dt: float) -> None:
        # Update active animation frame
        if self.current_animation:
            self.current_animation.update(dt)

        # Flashlight battery drain
        if self.flashlight_on:
            self.battery = max(0.0, self.battery - settings.BATTERY_DRAIN_RATE * dt)
            if self.battery <= 0.0:
                self.flashlight_on = False

        # Thought display timer
        if self.thought_timer > 0.0:
            self.thought_timer -= dt
            if self.thought_timer <= 0.0:
                self.current_thought = None

    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        if self.is_hidden:
            return  # Hidden inside wardrobe/table

        ox, oy = camera_offset
        draw_x = int(self.x - ox)
        draw_y = int(self.y - oy)

        # 1. Draw Andreas current animation frame
        if self.current_animation:
            frame = self.current_animation.get_current_frame()
            if isinstance(frame, pygame.Rect):
                surface.blit(settings.TEXTURES[self.current_texture], (draw_x, draw_y), frame)
            elif isinstance(frame, pygame.Surface):
                surface.blit(frame, (draw_x, draw_y))
            else:
                pygame.draw.rect(surface, entity_defs.PLAYER_FALLBACK_COLOR, self.get_rect().move(-ox, -oy))
        else:
            pygame.draw.rect(surface, entity_defs.PLAYER_FALLBACK_COLOR, self.get_rect().move(-ox, -oy))

        # 2. Flashlight origin indicator light if active
        if self.flashlight_on and self.battery > 0:
            beam_offsets = {
                "down": (draw_x + 8, draw_y + 20),
                "up": (draw_x + 8, draw_y + 10),
                "left": (draw_x + 2, draw_y + 18),
                "right": (draw_x + 14, draw_y + 18),
            }
            bx, by = beam_offsets.get(self.direction, (draw_x + 8, draw_y + 20))
            pygame.draw.circle(surface, (255, 250, 200), (int(bx), int(by)), 2)

    def render_thought(self, surface: pygame.Surface, prompt_active: bool = False) -> None:
        """Renders character thoughts and dialogue banners in screen space on top of lighting."""
        if not self.current_thought:
            return

        thought_text = t(self.current_thought)
        font = settings.FONTS.get("dialogue", settings.FONTS["small"])
        max_w = settings.VIRTUAL_WIDTH - 48

        # Word wrap into lines if text exceeds canvas width
        words = f'"{thought_text}"'.split(" ")
        lines = []
        cur_line = []
        for word in words:
            test_line = " ".join(cur_line + [word])
            if font.size(test_line)[0] <= max_w:
                cur_line.append(word)
            else:
                if cur_line:
                    lines.append(" ".join(cur_line))
                cur_line = [word]
        if cur_line:
            lines.append(" ".join(cur_line))

        if not lines:
            return

        rendered_lines = [font.render(l, True, (245, 245, 245)) for l in lines]
        total_h = sum(r.get_height() for r in rendered_lines) + (len(rendered_lines) - 1) * 3
        max_line_w = max(r.get_width() for r in rendered_lines)

        base_y = settings.VIRTUAL_HEIGHT - 44 if prompt_active else settings.VIRTUAL_HEIGHT - 24
        bg_rect = pygame.Rect(0, 0, max_line_w + 20, total_h + 10)
        bg_rect.center = (settings.VIRTUAL_WIDTH // 2, base_y - (total_h - rendered_lines[0].get_height()) // 2)

        pygame.draw.rect(surface, (12, 12, 18, 225), bg_rect, border_radius=5)
        pygame.draw.rect(surface, (120, 110, 85), bg_rect, width=1, border_radius=5)

        cur_y = bg_rect.top + 5
        for r in rendered_lines:
            r_rect = r.get_rect(centerx=bg_rect.centerx, top=cur_y)
            surface.blit(r, r_rect)
            cur_y += r.get_height() + 3
