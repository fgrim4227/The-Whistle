"""
Main gameplay state (PlayState).
Coordinates the cabin house, player (Andreas), El Silbón (inter-room wandering & door knocking),
dynamic lighting system, HUD, and game over / victory conditions.
"""

import math
from typing import Dict, List, Optional
import pygame
from gale.input_handler import InputData

import settings
from src.i18n import t
from src.states.BaseState import BaseState
from src.states.PauseState import PauseState
from src.states.ObjectiveState import ObjectiveState
from src.states.GameOverState import GameOverState
from src.states.VictoryState import VictoryState
from src.world.House import House
from src.entities.Player import Player
from src.entities.Monster import Monster, SilbonStunnedState, SilbonKnockingState
from src.world.GameObject import ThrowableProjectile
from src.systems.LightingSystem import LightingSystem
from src.systems.AudioManager import AudioManager
from src.ui.HUD import HUD


class PlayState(BaseState):
    def __init__(self, state_stack) -> None:
        super().__init__(state_stack)
        self.house = House()
        self.player = Player(x=80, y=120)
        # El Silbón starts patrolling in the central hallway of the cabin
        self.monster = Monster(x=220, y=140, start_room="hallway")
        
        self.lighting = LightingSystem()
        self.audio = AudioManager()
        self.hud = HUD()

        self.projectiles: List[ThrowableProjectile] = []
        self.pressed_inputs: Dict[str, bool] = {}
        self.prompt_text = ""

        self.objectives_progress = {
            "flashlight": True,
            "explore": False,
            "crowbar": False,
            "key": False,
            "escape": False,
        }

    def enter(self, *args, **kwargs) -> None:
        self.pressed_inputs.clear()
        # Start atmospheric cabin ambient background music
        self.audio.start_ambient()

    def exit(self) -> None:
        # Stop continuous channels on exit
        settings.stop_channel("silbon_breath")

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id in ("move_left", "move_right", "move_up", "move_down"):
            self.pressed_inputs[input_id] = input_data.pressed
            return

        if not input_data.pressed:
            return

        if input_id == "pause":
            self.state_stack.push(PauseState(self.state_stack))
        elif input_id == "objectives":
            self.state_stack.push(ObjectiveState(self.state_stack, self.objectives_progress))
        elif input_id == "flashlight":
            self.player.toggle_flashlight()
        elif input_id in ("throw", "action"):
            self._handle_throw()
        elif input_id == "interact":
            self._handle_interaction()

    def _handle_throw(self) -> None:
        if self.player.equipped_item in ("throwable", "crowbar"):
            px, py = self.player.get_center()
            self.projectiles.append(ThrowableProjectile(px, py, self.player.direction))
            self.player.equipped_item = None
            # Loud crash alerts El Silbón if in the same room
            if self.monster.current_room_name == self.house.current_room.name:
                self.monster.hear_noise(px, py, radius=320.0)

    def _handle_interaction(self) -> None:
        room = self.house.current_room
        if not room:
            return

        # 1. Exit hiding spot if currently concealed
        if self.player.is_hidden:
            self.player.exit_hide()
            return

        player_rect = self.player.get_rect()
        interact_zone = player_rect.inflate(20, 20)

        # 2. Check nearby hiding spots (wardrobes / tables)
        for spot in room.hiding_spots:
            if interact_zone.colliderect(spot.get_rect()):
                self.player.hide(spot)
                return

        # 3. Check nearby floor items
        for item in room.items:
            if not item.is_picked and interact_zone.colliderect(item.get_rect()):
                item.is_picked = True
                if item.obj_type == "battery":
                    self.player.recharge_battery()
                    self.player.set_thought("thought_dark", 3.0)
                else:
                    self.player.equipped_item = item.obj_type
                    if item.obj_type == "crowbar":
                        self.objectives_progress["crowbar"] = True
                    elif item.obj_type == "key":
                        self.objectives_progress["key"] = True
                return

        # 4. Check nearby doors
        for door in room.doors:
            if interact_zone.colliderect(door.get_rect()):
                if door.is_barred:
                    if self.player.equipped_item == "crowbar":
                        door.unbar()
                        self.player.set_thought("thought_door_locked", 3.0)
                    else:
                        self.player.set_thought("prompt_door_barred", 3.0)
                    return

                if door.is_locked:
                    if door.can_open(self.player):
                        door.unlock()
                        if door.is_exit_door:
                            self.objectives_progress["escape"] = True
                            self.state_stack.push(VictoryState(self.state_stack))
                            return
                    else:
                        self.player.set_thought("prompt_door_locked", 3.0)
                    return

                if door.is_exit_door:
                    self.state_stack.push(VictoryState(self.state_stack))
                    return

                # Walk through door into target room
                self.house.change_room(door.target_room_name, door.target_spawn_x, door.target_spawn_y, self.player)
                self.objectives_progress["explore"] = True
                return

        # 5. Check nearby NPC
        if room.npc and interact_zone.colliderect(room.npc.get_rect()):
            dialogue_key = room.npc.get_current_dialogue()
            self.player.set_thought(dialogue_key, 4.5)

    def update(self, dt: float) -> None:
        room = self.house.current_room
        if not room:
            return

        obstacles = room.get_obstacles()

        # Update player
        self.player.update_movement_from_input(self.pressed_inputs, obstacles, dt)
        self.player.update(dt)

        # Update El Silbón (delegating to FSM state machine with house navigation)
        monster_in_same_room = (self.monster.current_room_name == room.name)
        self.monster.update_ai(self.player, self.house, dt)

        # Update thrown projectiles and hit collisions
        if monster_in_same_room:
            for p in self.projectiles:
                p.update(dt)
                if p.active and p.get_rect().colliderect(self.monster.get_rect()):
                    p.active = False
                    result = self.monster.receive_throw_hit()
                    if result == "stunned":
                        self.player.set_thought("thought_monster_stunned", 3.0)
                    else:
                        self.player.set_thought("thought_monster_enraged", 3.0)
        else:
            for p in self.projectiles:
                p.update(dt)

        self.projectiles = [p for p in self.projectiles if p.active]

        # Update dynamic audio system and proximity cues
        self.audio.update(
            self.player.get_center(),
            self.monster.get_center(),
            self.player.is_hidden,
            monster_in_same_room=monster_in_same_room,
            dt=dt,
        )

        # Update HUD and contextual action prompts
        self._update_contextual_prompt()
        self.hud.update(dt)

        # Game Over Condition: caught by El Silbón in the same room while unhidden
        is_safe_state = isinstance(self.monster.state_machine.current, (SilbonStunnedState, SilbonKnockingState))
        if monster_in_same_room and not self.player.is_hidden and not is_safe_state:
            if self.player.get_rect().colliderect(self.monster.get_rect()):
                self.state_stack.push(GameOverState(self.state_stack))

    def _update_contextual_prompt(self) -> None:
        room = self.house.current_room
        if not room:
            self.prompt_text = ""
            return

        # Special door banging warning when El Silbón is knocking on the room's door
        current_state = self.monster.state_machine.current
        if isinstance(current_state, SilbonKnockingState):
            target_room = getattr(current_state, "target_room", "")
            if target_room == room.name:
                self.prompt_text = t("prompt_door_banging")
                return

        if self.player.is_hidden:
            self.prompt_text = t("prompt_exit_hide")
            return

        zone = self.player.get_rect().inflate(20, 20)
        
        for spot in room.hiding_spots:
            if zone.colliderect(spot.get_rect()):
                self.prompt_text = t("prompt_hide")
                return

        for item in room.items:
            if not item.is_picked and zone.colliderect(item.get_rect()):
                item_label = t(f"item_{item.obj_type}")
                self.prompt_text = f"{t('prompt_pickup')} ({item_label})"
                return

        for door in room.doors:
            if zone.colliderect(door.get_rect()):
                if door.is_barred:
                    self.prompt_text = t("prompt_door_barred")
                elif door.is_locked:
                    self.prompt_text = t("prompt_door_locked")
                else:
                    self.prompt_text = t("prompt_open_door")
                return

        if room.npc and zone.colliderect(room.npc.get_rect()):
            self.prompt_text = t("prompt_talk_npc", name=room.npc.name)
            return

        self.prompt_text = ""

    def render(self, surface: pygame.Surface) -> None:
        # 1. Draw current cabin room
        self.house.render(surface)

        # 2. Draw room entities
        self.player.render(surface)
        
        # El Silbón only renders when inside the player's room
        if self.monster.current_room_name == self.house.current_room.name:
            self.monster.render(surface)

        # 3. Draw projectiles
        for p in self.projectiles:
            p.render(surface)

        # 4. Draw darkness and dynamic flashlight beam
        active_monster = self.monster if (self.monster.current_room_name == self.house.current_room.name) else None
        self.lighting.render(surface, self.player, active_monster)

        # 5. Draw top HUD and prompts
        self.hud.render(surface, self.player, self.audio, self.prompt_text)
