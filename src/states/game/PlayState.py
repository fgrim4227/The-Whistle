"""
Main gameplay state (PlayState).
Coordinates the cabin house, player (Andreas), El Silbón (inter-room wandering & door knocking),
dynamic lighting system, HUD, and game over / victory conditions.
"""

import math
import random
from typing import List, Optional, Tuple
import pygame
from gale.input_handler import InputData

import settings
from src.i18n import t
from gale.state import BaseState
from src.states.game.PauseState import PauseState
from src.states.game.ObjectiveState import ObjectiveState
from src.states.game.GameOverState import GameOverState
from src.states.game.VictoryState import VictoryState
from src.states.game.NoteState import NoteState
from src.world.House import House
from src.entities.Player import Player
from src.entities.Monster import Monster
from src.world.GameObject import ThrowableProjectile
from src.systems.LightingSystem import Light, LightingSystem
from src.systems.AudioManager import AudioManager
from src.ui.HUD import HUD


class PlayState(BaseState):
    def __init__(self, state_machine) -> None:
        super().__init__(state_machine)
        self.house = House()

        # Andreas spawns at the authored player_spawn in FirstRoom (defaulting to 94, 129)
        spawn_pos = (94.0, 129.0)
        if self.house.current_room and self.house.current_room.player_spawn:
            spawn_pos = self.house.current_room.player_spawn
        self.player = Player(x=spawn_pos[0], y=spawn_pos[1])

        # El Silbón spawns stalking in UpperHallway (as requested by level design)
        self.monster = Monster(x=380.0, y=116.0, start_room="UpperHallway")
        
        self.lighting = LightingSystem()
        self.audio = AudioManager()
        self.hud = HUD()

        self.projectiles: List[ThrowableProjectile] = []
        self.prompt_text = ""

        self.objectives_progress = {
            "flashlight": True,
            "explore": False,
            "crowbar": False,
            "key": False,
            "escape": False,
        }

    def enter(self, *args, **kwargs) -> None:
        self.player.clear_held()
        # Start atmospheric cabin ambient background music
        self.audio.start_ambient()

    def exit(self) -> None:
        # Stop continuous channels on exit
        settings.stop_channel("silbon_breath")

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_data.pressed:
            if input_id == "pause":
                self.player.clear_movement()
                self.state_machine.push(PauseState(self.state_machine, on_close=self.player.sync_movement_keys))
                return
            elif input_id == "objectives":
                self.player.clear_movement()
                self.state_machine.push(ObjectiveState(self.state_machine, self.objectives_progress, on_close=self.player.sync_movement_keys))
                return

        self.player.command_bindings.dispatch(self.player, input_id, input_data)

    def _handle_throw(self) -> None:
        if self.player.equipped_item in ("throwable", "crowbar"):
            item_thrown = self.player.equipped_item
            px, py = self.player.get_center()
            self.projectiles.append(ThrowableProjectile(px, py, self.player.direction))
            self.player.remove_item(item_thrown)
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
        interact_zone = player_rect.inflate(24, 24)

        # 2. Check nearby hiding spots (wardrobes / tables)
        for spot in room.hiding_spots:
            if interact_zone.colliderect(spot.get_rect()):
                self.player.hide(spot)
                return

        # 3. Check nearby floor items & interactables (cabinets, safes, keys, tools, notes)
        for item in room.items:
            if not item.is_picked and interact_zone.colliderect(item.get_rect()):
                if item.obj_type == "battery":
                    item.is_picked = True
                    self.player.recharge_battery()
                    self.player.set_thought("thought_dark", 3.0)
                    return
                elif item.obj_type == "cabinet":
                    # Vintage cabinet in DiningRoom requiring lockpick
                    if self.player.has_item("lockpick"):
                        item.is_picked = True
                        self.player.add_item("old_key")
                        self.player.set_thought("thought_got_old_key", 4.5)
                    else:
                        self.player.set_thought("prompt_cabinet_locked", 3.5)
                    return
                elif item.obj_type == "safe":
                    # Master Bedroom safe containing exit key
                    item.is_picked = True
                    self.player.add_item("key")
                    self.objectives_progress["key"] = True
                    self.player.set_thought("thought_got_exit_key", 4.5)
                    return
                elif item.obj_type == "note":
                    note_id = getattr(item, "note_id", "note_kitchen")
                    title_key = f"{note_id}_title"
                    body_key = f"{note_id}_body"
                    attached_item = getattr(item, "yields", None)

                    self.player.clear_movement()

                    def on_note_closed():
                        if attached_item and not item.is_picked:
                            item.is_picked = True
                            self.player.add_item(attached_item)
                            if attached_item == "lockpick":
                                self.player.set_thought("thought_note_got_lockpick", 4.5)
                        self.player.sync_movement_keys()

                    self.state_machine.push(
                        NoteState(
                            self.state_machine,
                            title_key,
                            body_key,
                            attached_item=attached_item if not item.is_picked else None,
                            on_close=on_note_closed,
                        )
                    )
                    return
                else:
                    item.is_picked = True
                    self.player.add_item(item.obj_type)
                    if item.obj_type == "crowbar":
                        self.objectives_progress["crowbar"] = True
                    elif item.obj_type == "key":
                        self.objectives_progress["key"] = True
                    return

        # 5. Check nearby doors
        for door in room.doors:
            if interact_zone.colliderect(door.get_rect()):
                # Unboltable passage between LivingRoom and DiningRoom
                if door.is_bolted:
                    if room.name in ("living_room", "LivingRoom"):
                        door.unbolt()
                        # Also unbolt reverse door in dining_room to complete the loop
                        dining_room = self.house.rooms.get("dining_room")
                        if dining_room:
                            for d in dining_room.doors:
                                if d.target_room_name in ("living_room", "LivingRoom"):
                                    d.unbolt()
                        self.player.set_thought("thought_unbolted", 4.0)
                    else:
                        self.player.set_thought("prompt_door_bolted", 3.5)
                    return

                if door.is_barred:
                    if self.player.has_item("crowbar"):
                        door.unbar()
                        self.player.set_thought("thought_door_unbarred", 3.5)
                    else:
                        self.player.set_thought("prompt_door_barred", 3.5)
                    return

                if door.is_locked:
                    if door.can_open(self.player):
                        door.unlock()
                        if door.is_exit_door:
                            self.objectives_progress["escape"] = True
                            self.state_machine.push(VictoryState(self.state_machine))
                            return
                    else:
                        self.player.set_thought("prompt_door_locked", 3.0)
                    return

                if door.is_exit_door:
                    self.state_machine.push(VictoryState(self.state_machine))
                    return

                # Walk through door into target room
                self.house.change_room(door.target_room_name, door.target_spawn_x, door.target_spawn_y, self.player)
                self.objectives_progress["explore"] = True
                return

    def update(self, dt: float) -> None:
        room = self.house.current_room
        if not room:
            return

        obstacles = room.get_obstacles()

        # Update player
        self.player.update_movement(obstacles, dt)
        self.player.update(dt)

        monster_in_same_room = (self.monster.current_room_name == room.name)

        # Footstep acoustics: footsteps can alert El Silbón to investigate
        if self.player.footstep_taken:
            self.player.footstep_taken = False
            if monster_in_same_room:
                px, py = self.player.get_center()
                if self.player.is_running:
                    # Running footsteps: 75% chance within 320 px
                    if random.random() < 0.75:
                        self.monster.hear_noise(px, py, radius=320.0)
                else:
                    # Walking footsteps: 20% chance within 140 px
                    if random.random() < 0.20:
                        self.monster.hear_noise(px, py, radius=140.0)

        if self.player.interact_requested:
            self.player.interact_requested = False
            self._handle_interaction()

        if self.player.throw_requested:
            self.player.throw_requested = False
            self._handle_throw()

        # Update El Silbón (delegating to FSM state machine with house navigation)
        self.monster.update_ai(self.player, self.house, dt)

        # Update thrown projectiles, obstacle collisions, and monster hit collisions
        for p in self.projectiles:
            impacted = p.update(dt, obstacles)
            if monster_in_same_room and p.active and p.get_rect().colliderect(self.monster.get_rect()):
                p.active = False
                result = self.monster.receive_throw_hit()
                if result == "stunned":
                    self.player.set_thought("thought_monster_stunned", 3.0)
                else:
                    self.player.set_thought("thought_monster_enraged", 3.0)
            elif impacted:
                # Projectile crashed against a wall/obstacle or reached ground, generating noise distraction
                settings.play_sound("knock_door", volume=0.55, channel_name="sfx")
                self.monster.hear_noise(p.x, p.y, radius=320.0)
                self.player.set_thought("thought_projectile_crash", 2.5)

        self.projectiles = [p for p in self.projectiles if p.active]

        # Calculate door-listening proximity: Andreas hears heavy breathing through the door
        door_listening_proximity = 0.0
        px, py = self.player.get_center()
        for door in room.doors:
            d_cx = door.x + door.width / 2.0
            d_cy = door.y + door.height / 2.0
            p_dist = math.hypot(px - d_cx, py - d_cy)
            if p_dist < 50.0 and self.monster.current_room_name == door.target_room_name:
                mx, my = self.monster.get_center()
                m_dist = math.hypot(mx - door.target_spawn_x, my - door.target_spawn_y)
                if m_dist < 180.0:
                    prox = (1.0 - p_dist / 50.0) * (1.0 - m_dist / 180.0)
                    door_listening_proximity = max(door_listening_proximity, prox)

        # Update dynamic audio system and proximity cues
        self.audio.update(
            self.player.get_center(),
            self.monster.get_center(),
            self.player.is_hidden,
            monster_in_same_room=monster_in_same_room,
            door_listening_proximity=door_listening_proximity,
            dt=dt,
            monster_is_moving=self.monster.is_moving,
            monster_ai_state=self.monster.ai_state,
        )

        # Update HUD and contextual action prompts
        self._update_contextual_prompt()
        self.hud.update(dt)

        # Game Over Condition: caught by El Silbón in the same room while unhidden
        is_safe_state = self.monster.ai_state == "stunned"
        if monster_in_same_room and not self.player.is_hidden and not is_safe_state:
            if self.player.get_rect().colliderect(self.monster.get_rect()):
                self.state_machine.push(GameOverState(self.state_machine))

    def _update_contextual_prompt(self) -> None:
        room = self.house.current_room
        if not room:
            self.prompt_text = ""
            return

        # Special door banging warning when El Silbón is knocking on the room's door
        current_state = self.monster.state_machine.current
        if self.monster.ai_state == "knocking":
            target_room = getattr(current_state, "target_room", "")
            if target_room == room.name:
                self.prompt_text = t("prompt_door_banging")
                return

        if self.player.is_hidden:
            self.prompt_text = t("prompt_exit_hide")
            return

        zone = self.player.get_rect().inflate(24, 24)
        
        for spot in room.hiding_spots:
            if zone.colliderect(spot.get_rect()):
                self.prompt_text = t("prompt_hide")
                return

        for item in room.items:
            if not item.is_picked and zone.colliderect(item.get_rect()):
                if item.obj_type == "cabinet":
                    if self.player.has_item("lockpick"):
                        self.prompt_text = t("prompt_pick_cabinet")
                    else:
                        self.prompt_text = t("prompt_cabinet_locked")
                elif item.obj_type == "safe":
                    self.prompt_text = t("prompt_open_safe")
                elif item.obj_type == "note":
                    self.prompt_text = t("prompt_read_note")
                else:
                    item_label = t(f"item_{item.obj_type}")
                    self.prompt_text = f"{t('prompt_pickup')} ({item_label})"
                return

        for door in room.doors:
            if zone.colliderect(door.get_rect()):
                # Check if El Silbón is lurking on the other side of this door
                is_danger = False
                if self.monster.current_room_name == door.target_room_name:
                    mx, my = self.monster.get_center()
                    m_dist = math.hypot(mx - door.target_spawn_x, my - door.target_spawn_y)
                    if m_dist < 180.0:
                        is_danger = True

                if door.is_bolted:
                    if room.name in ("living_room", "LivingRoom"):
                        self.prompt_text = t("prompt_unbolt_door")
                    else:
                        self.prompt_text = t("prompt_door_bolted")
                elif door.is_barred:
                    self.prompt_text = t("prompt_door_barred")
                elif door.is_locked:
                    self.prompt_text = t("prompt_door_locked")
                elif is_danger:
                    self.prompt_text = t("prompt_open_door_danger")
                elif getattr(door, "is_stairs", False):
                    self.prompt_text = t("prompt_use_stairs")
                else:
                    self.prompt_text = t("prompt_open_door")
                return

        self.prompt_text = ""

    def get_camera_offset(self) -> Tuple[int, int]:
        room = self.house.current_room
        if not room:
            return (0, 0)
        px, py = self.player.get_center()
        cam_x = int(px - settings.VIRTUAL_WIDTH / 2.0)
        cam_y = int(py - settings.VIRTUAL_HEIGHT / 2.0)
        max_cam_x = max(0, room.width - settings.VIRTUAL_WIDTH)
        max_cam_y = max(0, room.height - settings.VIRTUAL_HEIGHT)
        cam_x = max(0, min(cam_x, max_cam_x))
        cam_y = max(0, min(cam_y, max_cam_y))
        return (cam_x, cam_y)

    def _collect_lights(self, active_monster) -> List[Light]:
        """
        Builds this frame's list of active lights -- the player's
        flashlight (or a dim residual glow while it's off) and El
        Silbón's always-on red eyes today. A future light source (a
        thrown lit lantern, say) is just another entry appended here;
        LightingSystem itself doesn't need to know it exists.
        """
        lights: List[Light] = []

        if not self.player.is_hidden:
            px, py = self.player.get_center()
            if self.player.flashlight_on and self.player.battery > 0:
                # Colorless: a real flashlight just reveals, it doesn't tint the room.
                lights.append(
                    Light(px, py, settings.FLASHLIGHT_LIGHT_RADIUS, settings.COLOR_FLASHLIGHT, intensity=0.0, reveal=0.6)
                )
            else:
                lights.append(Light(px, py, 26.0, settings.COLOR_GRAY, intensity=0.0, reveal=0.3))

        if active_monster:
            mx, my = active_monster.get_center()
            lights.append(
                Light(
                    mx, my - 32, settings.MONSTER_EYE_LIGHT_RADIUS, settings.COLOR_MONSTER_EYES,
                    intensity=0.1, reveal=0.1,
                )
            )

        return lights

    def render(self, surface: pygame.Surface) -> None:
        camera_offset = self.get_camera_offset()

        # 1. Draw current cabin room
        self.house.render(surface, camera_offset)

        # 2. Draw room entities
        self.player.render(surface, camera_offset)
        
        # El Silbón only renders when inside the player's room
        if self.monster.current_room_name == self.house.current_room.name:
            self.monster.render(surface, camera_offset)

        # 3. Draw projectiles
        for p in self.projectiles:
            p.render(surface, camera_offset)

        # 4. Draw darkness with every active light carved out of it
        active_monster = self.monster if (self.monster.current_room_name == self.house.current_room.name) else None
        self.lighting.render(surface, self._collect_lights(active_monster), camera_offset)

        # 5. Draw top HUD and prompts
        self.hud.render(surface, self.player, self.audio, self.prompt_text)
