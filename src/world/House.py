"""
House class managing all cabin rooms, door interconnections, and Tiled JSON level loading.
"""

import os
from typing import Dict, Optional, Tuple
import pygame

from src.definitions import rooms as room_defs
from src.world.Room import Room
from src.world.Door import Door
from src.world.GameObject import GameObject
from src.world.HidingSpot import HidingSpot
from src.world.TiledLevelLoader import TiledLevelLoader


class House:
    def __init__(self) -> None:
        self.rooms: Dict[str, Room] = {}
        self.current_room: Optional[Room] = None
        self.power_restored: bool = False

        # Attempt to load newly authored Tiled levels, fallback to default procedural cabin
        if not self._build_tiled_cabin():
            self._build_default_cabin()

    def _register_room(self, room_key: str, room: Room, aliases: list) -> None:
        room.house = self
        self.rooms[room_key] = room
        for alias in aliases:
            self.rooms[alias] = room

    def _apply_room_fallbacks(self, room: Room, spec: dict) -> None:
        """
        Fills in whatever a room's Tiled map didn't already author itself,
        using room_defs.TILED_ROOMS' fallback data -- a door/hiding
        spot/item is only added if nothing already targets/matches it, so
        a room can mix Tiled-authored and fallback content freely.
        """
        if not room.player_spawn and spec.get("player_spawn"):
            room.player_spawn = spec["player_spawn"]

        if not room.hiding_spots:
            for hs in spec.get("hiding_spots", []):
                room.hiding_spots.append(HidingSpot(**hs))

        if not room.patrol_waypoints:
            room.patrol_waypoints = list(spec.get("patrol_waypoints", []))

        existing_targets = {d.target_room_name for d in room.doors}
        for d in spec.get("doors", []):
            if d["target_room_name"] not in existing_targets:
                room.doors.append(Door(**d))
                existing_targets.add(d["target_room_name"])

        existing_types = {it.obj_type for it in room.items}
        for it in spec.get("items", []):
            if it["obj_type"] not in existing_types:
                room.items.append(GameObject(**it))
                existing_types.add(it["obj_type"])

    def _build_tiled_cabin(self) -> bool:
        """
        Loads every room in room_defs.TILED_ROOMS from its Tiled JSON map,
        patches in fallback content it didn't author, and registers it
        (and its aliases) in self.rooms.
        """
        start_spec = room_defs.TILED_ROOMS[room_defs.TILED_START_ROOM]
        hallway_spec = room_defs.TILED_ROOMS["UpperHallway"]
        if not os.path.exists(start_spec["path"]) or not os.path.exists(hallway_spec["path"]):
            return False

        try:
            built: Dict[str, Room] = {}

            for room_key, spec in room_defs.TILED_ROOMS.items():
                room = TiledLevelLoader.load_room(
                    json_path=spec["path"],
                    room_name=room_key,
                    display_name=spec["display_name"],
                )
                self._apply_room_fallbacks(room, spec)
                built[room_key] = room
                self._register_room(room_key, room, spec.get("aliases", []))

            self._sync_reciprocal_doors()
            self.current_room = built[room_defs.TILED_START_ROOM]
            return True

        except Exception as e:
            print(f"Error loading Tiled cabin: {e}. Falling back to default cabin layout.")
            return False

    def _sync_reciprocal_doors(self) -> None:
        """Ensures that reciprocal doors share lock states and required keys."""
        for rname, room in self.rooms.items():
            for door in room.doors:
                if door.is_locked:
                    target_rm = self.rooms.get(door.target_room_name)
                    if target_rm:
                        for d in target_rm.doors:
                            if d.target_room_name in (rname, room.display_name):
                                d.is_locked = True
                                if door.required_key and not d.required_key:
                                    d.required_key = door.required_key

    def _build_default_cabin(self) -> None:
        """Builds the fully procedural fallback house from room_defs.DEFAULT_CABIN_ROOMS."""
        built: Dict[str, Room] = {}

        for room_key, spec in room_defs.DEFAULT_CABIN_ROOMS.items():
            room = Room(room_key, spec["display_name"])

            for hs in spec.get("hiding_spots", []):
                room.hiding_spots.append(HidingSpot(**hs))
            for it in spec.get("items", []):
                room.items.append(GameObject(**it))
            for d in spec.get("doors", []):
                room.doors.append(Door(**d))
            room.patrol_waypoints = list(spec.get("patrol_waypoints", []))

            built[room_key] = room
            self.rooms[room_key] = room

        self.current_room = built[room_defs.DEFAULT_START_ROOM]

    def change_room(self, target_room_name: str, spawn_x: float, spawn_y: float, player) -> None:
        if target_room_name in self.rooms:
            self.current_room = self.rooms[target_room_name]
            player.x = spawn_x
            player.y = spawn_y
        else:
            # Target room is pending authoring (e.g. lower_hallway during WIP)
            player.set_thought("thought_stairs_blocked", 3.0)

    def render(self, surface: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)) -> None:
        if self.current_room:
            self.current_room.render(surface, camera_offset)
