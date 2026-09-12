"""
House class managing all cabin rooms, door interconnections, and Tiled JSON level loading.
"""

import json
from typing import Dict, Optional, Tuple
import pygame

import settings
from src.world.Room import Room
from src.world.Door import Door
from src.world.GameObject import GameObject
from src.world.HidingSpot import HidingSpot
from src.entities.NPC import NPC


class House:
    def __init__(self) -> None:
        self.rooms: Dict[str, Room] = {}
        self.current_room: Optional[Room] = None
        self.is_shifting = False
        self.shift_timer = 0.0
        self._build_default_cabin()

    def _build_default_cabin(self) -> None:
        """
        Builds the cabin layout with 4 interconnected rooms:
        Bedroom, Central Hallway, Kitchen, and Main Living Room (Exit).
        """
        # 1. Bedroom (Starting room where Andreas wakes up)
        bedroom = Room("bedroom", "Dormitorio Sombrío")
        # Wardrobe hiding spot
        bedroom.hiding_spots.append(HidingSpot("wardrobe", 64, 40))
        # Flashlight battery on the floor
        bedroom.items.append(GameObject("battery", 140, 100, "Batería"))
        # Door to hallway (right wall)
        bedroom.doors.append(
            Door(
                x=settings.VIRTUAL_WIDTH - settings.TILE_SIZE,
                y=settings.VIRTUAL_HEIGHT // 2 - 16,
                target_room_name="hallway",
                target_spawn_x=48,
                target_spawn_y=settings.VIRTUAL_HEIGHT // 2 - 12,
            )
        )
        bedroom.patrol_waypoints = [(100, 100), (250, 150)]
        self.rooms["bedroom"] = bedroom

        # 2. Central Hallway (Dangerous transit zone)
        hallway = Room("hallway", "Pasillo Principal")
        # Door back to bedroom
        hallway.doors.append(
            Door(
                x=0,
                y=settings.VIRTUAL_HEIGHT // 2 - 16,
                target_room_name="bedroom",
                target_spawn_x=settings.VIRTUAL_WIDTH - 64,
                target_spawn_y=settings.VIRTUAL_HEIGHT // 2 - 12,
            )
        )
        # Door to kitchen (top wall)
        hallway.doors.append(
            Door(
                x=settings.VIRTUAL_WIDTH // 2 - 16,
                y=0,
                target_room_name="kitchen",
                target_spawn_x=settings.VIRTUAL_WIDTH // 2 - 10,
                target_spawn_y=settings.VIRTUAL_HEIGHT - 64,
            )
        )
        # Door to Living Room (right wall, barred with planks)
        hallway.doors.append(
            Door(
                x=settings.VIRTUAL_WIDTH - settings.TILE_SIZE,
                y=settings.VIRTUAL_HEIGHT // 2 - 16,
                target_room_name="living_room",
                target_spawn_x=48,
                target_spawn_y=settings.VIRTUAL_HEIGHT // 2 - 12,
                is_barred=True,
            )
        )
        # Throwable object (stone / brick) in the hallway
        hallway.items.append(GameObject("throwable", 200, 120, "Piedra"))
        hallway.patrol_waypoints = [(80, 140), (240, 140), (400, 140)]
        self.rooms["hallway"] = hallway

        # 3. Kitchen (Contains the crowbar to unbar the door)
        kitchen = Room("kitchen", "Cocina Abandonada")
        # Door back to hallway
        kitchen.doors.append(
            Door(
                x=settings.VIRTUAL_WIDTH // 2 - 16,
                y=settings.VIRTUAL_HEIGHT - settings.TILE_SIZE,
                target_room_name="hallway",
                target_spawn_x=settings.VIRTUAL_WIDTH // 2 - 10,
                target_spawn_y=48,
            )
        )
        # Crowbar item
        kitchen.items.append(GameObject("crowbar", 380, 70, "Palanca"))
        kitchen.items.append(GameObject("throwable", 120, 180, "Botella"))
        kitchen.hiding_spots.append(HidingSpot("table", 200, 80, 48, 32))
        # Survivor NPC in the corner of the kitchen
        kitchen.npc = NPC(64, 64, name="Elena", dialogue_keys=["thought_silbon_whistle", "thought_door_locked"])
        kitchen.patrol_waypoints = [(150, 100), (320, 160)]
        self.rooms["kitchen"] = kitchen

        # 4. Main Living Room (Exit room)
        living_room = Room("living_room", "Sala Principal")
        # Door back to hallway
        living_room.doors.append(
            Door(
                x=0,
                y=settings.VIRTUAL_HEIGHT // 2 - 16,
                target_room_name="hallway",
                target_spawn_x=settings.VIRTUAL_WIDTH - 64,
                target_spawn_y=settings.VIRTUAL_HEIGHT // 2 - 12,
            )
        )
        # Master escape key
        living_room.items.append(GameObject("key", 100, 80, "Llave de Salida"))
        # Escape door into dark forest (locked with key)
        living_room.doors.append(
            Door(
                x=settings.VIRTUAL_WIDTH // 2 - 16,
                y=0,
                target_room_name="exit",
                target_spawn_x=0,
                target_spawn_y=0,
                is_locked=True,
                required_key="key",
                is_exit_door=True,
            )
        )
        living_room.hiding_spots.append(HidingSpot("wardrobe", 380, 40))
        living_room.patrol_waypoints = [(120, 120), (360, 120)]
        self.rooms["living_room"] = living_room

        # Start game inside bedroom
        self.current_room = bedroom

    def load_from_tiled(self, json_path: str) -> None:
        """Loads and parses collision layers and objects from exported Tiled JSON."""
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Process Tiled layers
            for layer in data.get("layers", []):
                if layer.get("type") == "objectgroup":
                    room_name = layer.get("name", "custom_room")
                    room = Room(room_name, room_name.capitalize())
                    for obj in layer.get("objects", []):
                        x, y = obj["x"], obj["y"]
                        w, h = obj["width"], obj["height"]
                        otype = obj.get("type") or obj.get("properties", {}).get("type")
                        if otype == "wall":
                            room.solid_tiles.append(pygame.Rect(x, y, w, h))
                        elif otype == "door":
                            target = obj.get("properties", {}).get("target", "hallway")
                            room.doors.append(Door(x, y, target, 48, 48))
                        elif otype == "hiding":
                            room.hiding_spots.append(HidingSpot("wardrobe", x, y, w, h))
                    self.rooms[room_name] = room
        except Exception as e:
            print(f"Notice: could not load Tiled JSON '{json_path}' ({e}), using default cabin.")

    def change_room(self, target_room_name: str, spawn_x: float, spawn_y: float, player) -> None:
        if target_room_name in self.rooms:
            self.current_room = self.rooms[target_room_name]
            player.x = spawn_x
            player.y = spawn_y

    def render(self, surface: pygame.Surface) -> None:
        if self.current_room:
            self.current_room.render(surface)
