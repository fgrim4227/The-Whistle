"""
Monster entity class (El Silbón). AI decision-making lives in the
per-state classes under src/states/entity/ (Patrol, MovingToDoor,
Knocking, Chase, Investigate, Berserk, Stunned); this class only holds
the entity's own data and the movement/animation/rendering it exposes
to those states.
"""

import math
import random
from typing import Dict, List, Tuple

import pygame
from gale.animation import Animation
from gale.state import StateMachine

import settings
from src.definitions import entity as entity_defs
from src.entities.BaseEntity import BaseEntity
from src.states.entity.MonsterBerserkState import MonsterBerserkState
from src.states.entity.MonsterChaseState import MonsterChaseState
from src.states.entity.MonsterInvestigateState import MonsterInvestigateState
from src.states.entity.MonsterKnockingState import MonsterKnockingState
from src.states.entity.MonsterMovingToDoorState import MonsterMovingToDoorState
from src.states.entity.MonsterPatrolState import MonsterPatrolState
from src.states.entity.MonsterStunnedState import MonsterStunnedState


class Monster(BaseEntity):
    def __init__(self, x: float, y: float, start_room: str = "hallway") -> None:
        width, height = entity_defs.MONSTER_SIZE
        super().__init__(x, y, width=width, height=height, speed=settings.MONSTER_PATROL_SPEED)
        self.current_room_name = start_room
        self.target_x = x
        self.target_y = y
        self.current_wp_idx = 0
        self.distance_to_player = 9999.0
        self.is_moving = False

        self.animations: Dict[str, Animation]
        self._animation_textures: Dict[str, str]
        self.animations, self._animation_textures = self._create_animations()
        self.current_animation = self.animations.get("idle-down")
        self.current_texture = self._animation_textures.get("idle-down")

        self.state_machine = StateMachine({
            "patrol": lambda sm: MonsterPatrolState(self, sm),
            "moving_to_door": lambda sm: MonsterMovingToDoorState(self, sm),
            "investigate": lambda sm: MonsterInvestigateState(self, sm),
            "knocking": lambda sm: MonsterKnockingState(self, sm),
            "chase": lambda sm: MonsterChaseState(self, sm),
            "berserk": lambda sm: MonsterBerserkState(self, sm),
            "stunned": lambda sm: MonsterStunnedState(self, sm),
        })
        self.ai_state = "patrol"
        self.state_machine.change(self.ai_state)

    def change_state(self, state_name: str, *args, **kwargs) -> None:
        self.state_machine.change(state_name, *args, **kwargs)
        self.ai_state = state_name

    def _create_animations(self) -> Tuple[Dict[str, Animation], Dict[str, str]]:
        return entity_defs.build_animations(
            entity_defs.MONSTER_ANIMATIONS, entity_defs.MONSTER_FALLBACK_COLOR, entity_defs.MONSTER_SPRITE_SIZE
        )

    def change_animation(self, anim_name: str) -> None:
        if anim_name in self.animations and self.current_animation != self.animations[anim_name]:
            self.current_animation = self.animations[anim_name]
            self.current_animation.reset()
            self.current_texture = self._animation_textures.get(anim_name)

    def hear_noise(self, noise_x: float, noise_y: float, radius: float = 280.0) -> None:
        """Alerts the monster of a sound if within audio radius."""
        if self.ai_state in ("stunned", "berserk", "knocking"):
            return

        dist = math.hypot(noise_x - self.x, noise_y - self.y)
        if dist <= radius:
            self.change_state("investigate", target_x=noise_x, target_y=noise_y)

    def receive_throw_hit(self) -> str:
        """Applies 75% Stun / 25% Berserk probability."""
        roll = random.random()
        if roll < settings.THROW_BERSERK_CHANCE:
            self.change_state("berserk")
            return "berserk"
        else:
            duration = random.uniform(3.0, 4.5)
            self.change_state("stunned", duration=duration)
            return "stunned"

    def can_detect_player(self, player) -> bool:
        """Checks whether the player is currently detected by line of sight or flashlight."""
        if player.is_hidden:
            return False
        px, py = player.get_center()
        mx, my = self.get_center()
        self.distance_to_player = math.hypot(px - mx, py - my)
        view_distance = 210.0 if player.flashlight_on else 85.0
        return self.distance_to_player <= view_distance

    def move_towards(self, target_x: float, target_y: float, obstacles: List[pygame.Rect], dt: float) -> None:
        """Moves towards target coordinate with obstacle avoidance."""
        mx, my = self.get_center()
        dx = target_x - mx
        dy = target_y - my
        dist = math.hypot(dx, dy)

        if dist < 6.0:
            self.vx = 0.0
            self.vy = 0.0
            self.is_moving = False
            self.change_animation(f"idle-{self.direction}")
            return

        self.is_moving = True
        nx = dx / dist
        ny = dy / dist

        if abs(nx) > abs(ny):
            self.direction = "right" if nx > 0 else "left"
        else:
            self.direction = "down" if ny > 0 else "up"

        self.change_animation(f"walk-{self.direction}")

        new_x = self.x + nx * self.speed * dt
        rect_x = pygame.Rect(int(new_x), int(self.y + 16), self.width, self.height - 16)
        if not any(rect_x.colliderect(obs) for obs in obstacles):
            self.x = new_x

        new_y = self.y + ny * self.speed * dt
        rect_y = pygame.Rect(int(self.x), int(new_y + 16), self.width, self.height - 16)
        if not any(rect_y.colliderect(obs) for obs in obstacles):
            self.y = new_y

    def update_ai(self, player, house, dt: float) -> None:
        self.state_machine.current.process_ai(house, player, dt)

        if self.current_animation:
            self.current_animation.update(dt)

    def render_sprite(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        """Renders the 64x64 frame centered over the entity's position."""
        ox, oy = camera_offset
        offset_x, offset_y = entity_defs.MONSTER_SPRITE_OFFSET
        sprite_x = int(self.x + offset_x - ox)
        sprite_y = int(self.y + offset_y - oy)

        if self.current_animation:
            frame = self.current_animation.get_current_frame()
            if isinstance(frame, pygame.Rect):
                surface.blit(settings.TEXTURES[self.current_texture], (sprite_x, sprite_y), frame)
            elif isinstance(frame, pygame.Surface):
                surface.blit(frame, (sprite_x, sprite_y))
            else:
                pygame.draw.rect(surface, entity_defs.MONSTER_FALLBACK_COLOR, self.get_rect().move(-ox, -oy))
        else:
            pygame.draw.rect(surface, entity_defs.MONSTER_FALLBACK_COLOR, self.get_rect().move(-ox, -oy))

        if self.ai_state == "berserk":
            pygame.draw.circle(surface, (255, 0, 0), (int(self.x + 8 - ox), int(self.y - 2 - oy)), 3)
            pygame.draw.circle(surface, (255, 0, 0), (int(self.x + 16 - ox), int(self.y - 2 - oy)), 3)

    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        self.state_machine.current.render(surface, camera_offset)
