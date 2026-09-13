"""
Monster entity class (El Silbón) and behavioral state machine classes (Princess Boss FSM pattern).
The monster AI delegates decision making to modular state classes (Patrol, Knocking, Chase, Berserk, Stunned),
providing realistic stalking, room transitions, and proper hiding-spot evasion.
"""

import math
import random
from typing import List, Tuple, Optional, Dict
import pygame
from gale.animation import Animation
from gale import frames
from gale.state import BaseState, StateMachine

import settings
from src.entities.BaseEntity import BaseEntity


# ==============================================================================
# BEHAVIORAL STATE CLASSES (FSM inspired by The Legend of the Princess Boss)
# ==============================================================================

class SilbonBaseState(BaseState):
    def __init__(self, monster: "Monster", state_machine: StateMachine) -> None:
        super().__init__(state_machine)
        self.monster = monster

    def process_ai(self, house, player, dt: float) -> None:
        """Processes AI decisions each frame. Overridden by subclasses."""
        pass

    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        """Renders the entity sprite."""
        self.monster.render_sprite(surface, camera_offset)


class SilbonPatrolState(SilbonBaseState):
    """
    Patrols between waypoints within the current room.
    If the player is in another room or hidden, counts down to change rooms and leaves.
    """
    def enter(self, *args, **kwargs) -> None:
        self.monster.speed = settings.MONSTER_PATROL_SPEED
        # Longer room transition cooldown so player has breathing room to explore
        self.room_change_cooldown = random.uniform(2, 4)
        self.suspicion_timer = 0.0
        self.hidden_leave_timer = random.uniform(6,8)

    def process_ai(self, house, player, dt: float) -> None:
        player_room_name = house.current_room.name if house.current_room else "bedroom"
        monster_room_name = self.monster.current_room_name
        current_room = house.rooms.get(monster_room_name)

        # 1. Monster is in the SAME room as the player
        if monster_room_name == player_room_name:
            # If player is hidden in a wardrobe/table:
            if player.is_hidden:
                # The monster cannot see the player; counts down to give up and exit the room
                self.hidden_leave_timer -= dt
                if self.hidden_leave_timer <= 0.0:
                    self._leave_room(house)
                    return
                # In the meantime, patrol waypoints that are far from the player's hiding spot
                self._patrol_room(current_room, dt, avoid_pos=(player.x, player.y))
                return

            # Player is NOT hidden: check line-of-sight / flashlight detection
            if self.monster.can_detect_player(player):
                # Generous reaction delay before committing to a full sprint chase
                self.suspicion_timer += dt
                if self.suspicion_timer >= 0.3:
                    self.monster.change_state("chase")
                    return
            else:
                self.suspicion_timer = max(0.0, self.suspicion_timer - dt * 1.5)

            # Normal patrol in the room
            self._patrol_room(current_room, dt)

        # 2. Monster is in a DIFFERENT room from the player
        else:
            self.room_change_cooldown -= dt
            if self.room_change_cooldown <= 0.0:
                self.room_change_cooldown = random.uniform(5, 8)
                self._leave_room(house, target_room_preference=player_room_name)

    def _patrol_room(self, current_room, dt: float, avoid_pos: Optional[Tuple[float, float]] = None) -> None:
        if not current_room or not current_room.patrol_waypoints:
            return

        wp = current_room.patrol_waypoints[self.monster.current_wp_idx % len(current_room.patrol_waypoints)]
        
        # If an avoid position is provided (e.g. wardrobe where player hides), choose a waypoint far away
        if avoid_pos:
            dist_to_avoid = math.hypot(wp[0] - avoid_pos[0], wp[1] - avoid_pos[1])
            if dist_to_avoid < 90.0 and len(current_room.patrol_waypoints) > 1:
                self.monster.current_wp_idx = (self.monster.current_wp_idx + 1) % len(current_room.patrol_waypoints)
                wp = current_room.patrol_waypoints[self.monster.current_wp_idx % len(current_room.patrol_waypoints)]

        self.monster.target_x, self.monster.target_y = wp
        mx, my = self.monster.get_center()
        if math.hypot(wp[0] - mx, wp[1] - my) < 16:
            self.monster.current_wp_idx = (self.monster.current_wp_idx + 1) % len(current_room.patrol_waypoints)

        obstacles = current_room.get_obstacles()
        self.monster.move_towards(self.monster.target_x, self.monster.target_y, obstacles, dt)

    def _leave_room(self, house, target_room_preference: Optional[str] = None) -> None:
        current_room = house.rooms.get(self.monster.current_room_name)
        if not current_room:
            return

        # Ensure chosen doors lead only to rooms that actually exist in house.rooms
        valid_doors = [
            d for d in current_room.doors
            if not d.is_exit_door and not d.is_barred and not d.is_locked and not getattr(d, "is_bolted", False)
            and d.target_room_name in house.rooms
        ]
        if not valid_doors:
            return

        chosen_door = None
        # Prefer direct door to preferred room if available
        if target_room_preference:
            chosen_door = next(
                (d for d in valid_doors if d.target_room_name == target_room_preference),
                None
            )
        if not chosen_door and valid_doors:
            chosen_door = random.choice(valid_doors)

        if chosen_door:
            self.monster.change_state("moving_to_door", door=chosen_door, target_room=chosen_door.target_room_name)


class SilbonMovingToDoorState(SilbonBaseState):
    """
    State where El Silbón physically pathfinds and walks to a chosen door
    before transitioning rooms. Eliminates visual teleportation across the map.
    """
    def enter(self, door, target_room: str, *args, **kwargs) -> None:
        self.door = door
        self.target_room = target_room
        self.monster.speed = settings.MONSTER_PATROL_SPEED
        self.timeout = 8.0  # Failsafe timer so geometry snags don't trap the monster
        # Target the center of the door
        self.target_x = self.door.x + self.door.width / 2.0
        self.target_y = self.door.y + self.door.height / 2.0

    def process_ai(self, house, player, dt: float) -> None:
        player_room_name = house.current_room.name if house.current_room else "FirstRoom"
        current_room = house.rooms.get(self.monster.current_room_name)

        # 1. If player is in the same room and unhidden, detect and chase!
        if self.monster.current_room_name == player_room_name and not player.is_hidden:
            if self.monster.can_detect_player(player):
                self.monster.change_state("chase")
                return

        # 2. Move towards the doorway
        self.timeout -= dt
        obstacles = current_room.get_obstacles() if current_room else []
        door_rect = self.door.get_rect()
        # Exclude the target door itself from blocking movement
        obstacles = [obs for obs in obstacles if not obs.colliderect(door_rect)]

        self.monster.move_towards(self.target_x, self.target_y, obstacles, dt)

        # 3. Check if arrived at the doorway
        mx, my = self.monster.get_center()
        dist_to_door = math.hypot(mx - self.target_x, my - self.target_y)

        # Arrived at door or timed out (to prevent geometry wedge)
        if dist_to_door < 16 or self.timeout <= 0.0:
            # Case A: If El Silbón is in a DIFFERENT room and intends to invade the PLAYER'S room:
            # Knock loudly on the door from outside so the player hears it and has time to hide!
            if self.monster.current_room_name != player_room_name and self.target_room == player_room_name:
                self.monster.change_state("knocking", door=self.door, target_room=self.target_room)
            else:
                # Case B: Leaving player's room or wandering between other rooms:
                # Open door, play creak audio, and transition to destination room
                settings.play_sound("door_creak", loops=0, volume=3, channel_name="sfx")
                self.monster.current_room_name = self.target_room
                self.monster.x = self.door.target_spawn_x
                self.monster.y = self.door.target_spawn_y
                self.monster.current_wp_idx = 0
                self.monster.vx = 0.0
                self.monster.vy = 0.0
                self.monster.is_moving = False

                if self.monster.current_room_name == player_room_name and self.monster.can_detect_player(player):
                    self.monster.change_state("chase")
                else:
                    self.monster.change_state("patrol")


class SilbonKnockingState(SilbonBaseState):
    """
    State when El Silbón knocks loudly on a door before entering the target room.
    Provides sound effects and on-screen warnings so the player has time to hide.
    """
    def enter(self, door, target_room: str, *args, **kwargs) -> None:
        self.door = door
        self.target_room = target_room
        self.timer = random.randint(2, 3) 
        self.monster.vx = 0.0
        self.monster.vy = 0.0
        self.monster.is_moving = False
        self.monster.change_animation(f"idle-{self.monster.direction}")
        # Trigger door knock audio
        settings.play_sound("knock_door", loops=0, volume=1.0, channel_name="knock")

    def process_ai(self, house, player, dt: float) -> None:
        player_room_name = house.current_room.name if house.current_room else "FirstRoom"

        # If the player is in the same room as the monster and unhidden:
        # El Silbón immediately cancels knocking and attacks/chases (no zombie state)
        if self.monster.current_room_name == player_room_name and not player.is_hidden:
            dist = math.hypot(player.x - self.monster.x, player.y - self.monster.y)
            if self.monster.can_detect_player(player) or dist < 140.0:
                self.monster.change_state("chase")
                return

        self.timer -= dt
        if self.timer <= 0.0:
            # Step through the door into the destination room
            self.monster.current_room_name = self.target_room
            self.monster.x = self.door.target_spawn_x
            self.monster.y = self.door.target_spawn_y
            self.monster.current_wp_idx = 0

            # If player is in this room and visible, begin chasing
            if self.monster.current_room_name == player_room_name and self.monster.can_detect_player(player):
                self.monster.change_state("chase")
            else:
                self.monster.change_state("patrol")


class SilbonChaseState(SilbonBaseState):
    """Active pursuit of the player."""
    def enter(self, *args, **kwargs) -> None:
        self.monster.speed = settings.MONSTER_CHASE_SPEED

    def process_ai(self, house, player, dt: float) -> None:
        player_room_name = house.current_room.name if house.current_room else "bedroom"
        
        # If the player fled into another room
        if self.monster.current_room_name != player_room_name:
            self.monster.change_state("patrol")
            return

        # If player successfully hides inside wardrobe/table during chase:
        # El Silbón loses visual contact, does NOT walk to the wardrobe, and soon gives up
        if player.is_hidden:
            self.monster.change_state("patrol")
            return

        px, py = player.get_center()
        current_room = house.rooms.get(self.monster.current_room_name)
        obstacles = current_room.get_obstacles() if current_room else []
        self.monster.move_towards(px, py, obstacles, dt)


class SilbonInvestigateState(SilbonBaseState):
    """Investigates a thrown object noise or disturbance."""
    def enter(self, target_x: float, target_y: float, *args, **kwargs) -> None:
        self.target_x = target_x
        self.target_y = target_y
        self.timer = 4.0
        self.monster.speed = settings.MONSTER_PATROL_SPEED

    def process_ai(self, house, player, dt: float) -> None:
        player_room_name = house.current_room.name if house.current_room else "bedroom"
        if self.monster.current_room_name != player_room_name:
            self.monster.change_state("patrol")
            return

        if self.monster.can_detect_player(player):
            self.monster.change_state("chase")
            return

        self.timer -= dt
        mx, my = self.monster.get_center()
        dist = math.hypot(self.target_x - mx, self.target_y - my)
        if dist < 16.0 or self.timer <= 0.0:
            self.monster.change_state("patrol")
            return

        current_room = house.rooms.get(self.monster.current_room_name)
        obstacles = current_room.get_obstacles() if current_room else []
        self.monster.move_towards(self.target_x, self.target_y, obstacles, dt)


class SilbonBerserkState(SilbonBaseState):
    """Berserk state triggered by 25% chance when hit by thrown object."""
    def enter(self, *args, **kwargs) -> None:
        self.timer = 6.0
        self.monster.speed = settings.MONSTER_BERSERK_SPEED

    def process_ai(self, house, player, dt: float) -> None:
        self.timer -= dt
        if self.timer <= 0.0:
            self.monster.change_state("patrol")
            return

        player_room_name = house.current_room.name if house.current_room else "bedroom"
        if self.monster.current_room_name == player_room_name and not player.is_hidden:
            px, py = player.get_center()
            current_room = house.rooms.get(self.monster.current_room_name)
            obstacles = current_room.get_obstacles() if current_room else []
            self.monster.move_towards(px, py, obstacles, dt)
        else:
            self.monster.change_state("patrol")


class SilbonStunnedState(SilbonBaseState):
    """Stunned state triggered by 75% chance when hit by thrown object."""
    def enter(self, duration: float = 3.5, *args, **kwargs) -> None:
        self.timer = duration
        self.monster.vx = 0.0
        self.monster.vy = 0.0
        self.monster.is_moving = False
        self.monster.change_animation(f"idle-{self.monster.direction}")

    def process_ai(self, house, player, dt: float) -> None:
        self.timer -= dt
        if self.timer <= 0.0:
            # Enrages upon recovering from stun
            self.monster.change_state("berserk")


# ==============================================================================
# MAIN MONSTER CLASS (EL SILBÓN)
# ==============================================================================

class Monster(BaseEntity):
    def __init__(self, x: float, y: float, start_room: str = "hallway") -> None:
        super().__init__(x, y, width=24, height=44, speed=settings.MONSTER_PATROL_SPEED)
        self.current_room_name = start_room
        self.target_x = x
        self.target_y = y
        self.current_wp_idx = 0
        self.distance_to_player = 9999.0
        self.is_moving = False

        # Animations
        self.animations: Dict[str, Animation] = self._create_animations()
        self.current_animation = self.animations.get("idle-down")

        # Behavioral state machine (Princess Boss FSM pattern)
        self.state_machine = StateMachine({
            "patrol": lambda sm: SilbonPatrolState(self, sm),
            "moving_to_door": lambda sm: SilbonMovingToDoorState(self, sm),
            "investigate": lambda sm: SilbonInvestigateState(self, sm),
            "knocking": lambda sm: SilbonKnockingState(self, sm),
            "chase": lambda sm: SilbonChaseState(self, sm),
            "berserk": lambda sm: SilbonBerserkState(self, sm),
            "stunned": lambda sm: SilbonStunnedState(self, sm),
        })
        self.state_machine.change("patrol")

    @property
    def ai_state(self) -> str:
        """Returns the current state name for compatibility with HUD and systems."""
        for name, state in self.state_machine.states.items():
            if isinstance(self.state_machine.current, state if isinstance(state, type) else SilbonBaseState):
                return name
        return "patrol"

    def change_state(self, state_name: str, *args, **kwargs) -> None:
        self.state_machine.change(state_name, *args, **kwargs)

    def _create_animations(self) -> Dict[str, Animation]:
        """
        Loads and slices directional animations with exact row mappings:
        silbon_walk: Row 0=up, Row 1=left, Row 2=right, Row 3=down
        silbon_idle: Row 0=down, Row 1=up, Row 2=left, Row 3=right
        """
        anims = {}
        tex = settings.TEXTURES
        walk_img = tex.get("silbon_walk")
        idle_img = tex.get("silbon_idle")

        if walk_img:
            # 10 frames of 64x64 per row
            anims["walk-up"] = Animation([walk_img.subsurface((c * 64, 0 * 64, 64, 64)) for c in range(10)], 0.10)
            anims["walk-left"] = Animation([walk_img.subsurface((c * 64, 1 * 64, 64, 64)) for c in range(10)], 0.10)
            anims["walk-right"] = Animation([walk_img.subsurface((c * 64, 2 * 64, 64, 64)) for c in range(10)], 0.10)
            anims["walk-down"] = Animation([walk_img.subsurface((c * 64, 3 * 64, 64, 64)) for c in range(10)], 0.10)

        if idle_img:
            # 7 frames of 64x64 per row
            anims["idle-down"] = Animation([idle_img.subsurface((c * 64, 0 * 64, 64, 64)) for c in range(7)], 0.16)
            anims["idle-up"] = Animation([idle_img.subsurface((c * 64, 1 * 64, 64, 64)) for c in range(7)], 0.16)
            anims["idle-left"] = Animation([idle_img.subsurface((c * 64, 2 * 64, 64, 64)) for c in range(7)], 0.16)
            anims["idle-right"] = Animation([idle_img.subsurface((c * 64, 3 * 64, 64, 64)) for c in range(7)], 0.16)

        return anims

    def change_animation(self, anim_name: str) -> None:
        if anim_name in self.animations and self.current_animation != self.animations[anim_name]:
            self.current_animation = self.animations[anim_name]
            self.current_animation.reset()

    def hear_noise(self, noise_x: float, noise_y: float, radius: float = 280.0) -> None:
        """Alerts the monster of a sound if within audio radius."""
        if isinstance(self.state_machine.current, (SilbonStunnedState, SilbonBerserkState, SilbonKnockingState)):
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
        # Flashlight significantly increases detection distance
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

        # Determine dominant direction
        if abs(nx) > abs(ny):
            self.direction = "right" if nx > 0 else "left"
        else:
            self.direction = "down" if ny > 0 else "up"

        self.change_animation(f"walk-{self.direction}")

        # Collision check on lower feet rect
        new_x = self.x + nx * self.speed * dt
        rect_x = pygame.Rect(int(new_x), int(self.y + 16), self.width, self.height - 16)
        if not any(rect_x.colliderect(obs) for obs in obstacles):
            self.x = new_x

        new_y = self.y + ny * self.speed * dt
        rect_y = pygame.Rect(int(self.x), int(new_y + 16), self.width, self.height - 16)
        if not any(rect_y.colliderect(obs) for obs in obstacles):
            self.y = new_y

    def update_ai(self, player, house, dt: float) -> None:
        # 1. Delegate decision making to current state in StateMachine
        self.state_machine.current.process_ai(house, player, dt)
        
        # 2. Update active animation frame
        if self.current_animation:
            self.current_animation.update(dt)

    def render_sprite(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        """Renders the 64x64 frame centered over the entity's position."""
        ox, oy = camera_offset
        sprite_x = int(self.x - 20 - ox)
        sprite_y = int(self.y - 12 - oy)

        if self.current_animation:
            frame = self.current_animation.get_current_frame()
            if isinstance(frame, pygame.Surface):
                surface.blit(frame, (sprite_x, sprite_y))
            else:
                pygame.draw.rect(surface, (160, 40, 40), self.get_rect().move(-ox, -oy))
        else:
            pygame.draw.rect(surface, (160, 40, 40), self.get_rect().move(-ox, -oy))

        # Berserk visual effect: glowing crimson eyes
        if isinstance(self.state_machine.current, SilbonBerserkState):
            pygame.draw.circle(surface, (255, 0, 0), (int(self.x + 8 - ox), int(self.y - 2 - oy)), 3)
            pygame.draw.circle(surface, (255, 0, 0), (int(self.x + 16 - ox), int(self.y - 2 - oy)), 3)

    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        self.state_machine.current.render(surface, camera_offset)
