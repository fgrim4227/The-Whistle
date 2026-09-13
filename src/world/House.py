"""
House class managing all cabin rooms, door interconnections, and Tiled JSON level loading.
"""

import json
import os
from typing import Dict, Optional, Tuple
import pygame

import settings
from src.world.Room import Room
from src.world.Door import Door
from src.world.GameObject import GameObject
from src.world.HidingSpot import HidingSpot
from src.entities.NPC import NPC
from src.world.TiledLevelLoader import TiledLevelLoader


class House:
    def __init__(self) -> None:
        self.rooms: Dict[str, Room] = {}
        self.current_room: Optional[Room] = None
        self.is_shifting = False
        self.shift_timer = 0.0

        # Attempt to load newly authored Tiled levels, fallback to default procedural cabin
        if not self._build_tiled_cabin():
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

    def _build_tiled_cabin(self) -> bool:
        """
        Loads the authoring Tiled maps (FirstRoom.json and UpperHallway.json),
        bakes their graphical tile layers, sets up solid collision rectangles,
        and establishes robust inter-room door connections.
        """
        first_room_path = "assets/tilemaps/FirstRoom.json"
        upper_hallway_path = "assets/tilemaps/UpperHallway.json"

        if not os.path.exists(first_room_path) or not os.path.exists(upper_hallway_path):
            return False

        try:
            # 1. Load FirstRoom (Starting bedroom where Andreas wakes up)
            first_room = TiledLevelLoader.load_room(
                json_path=first_room_path,
                room_name="FirstRoom",
                display_name="Habitación Sombría",
            )

            # Ensure player spawn fallback if missing in Tiled interest_points
            if not first_room.player_spawn:
                first_room.player_spawn = (94.0, 129.0)

            # Wardrobe hiding spot in FirstRoom (top-left)
            if not first_room.hiding_spots:
                first_room.hiding_spots.append(
                    HidingSpot("wardrobe", 32, 16, width=48, height=48, render_graphic=False, is_solid=False)
                )

            # Door to UpperHallway on the right wall
            if not first_room.doors:
                first_room.doors.append(
                    Door(
                        x=464,
                        y=104,
                        target_room_name="UpperHallway",
                        target_spawn_x=48,
                        target_spawn_y=116,
                        width=32,
                        height=48,
                        render_graphic=False,
                    )
                )

            # 2. Load UpperHallway (Transit corridor where El Silbón stalks)
            upper_hallway = TiledLevelLoader.load_room(
                json_path=upper_hallway_path,
                room_name="UpperHallway",
                display_name="Pasillo Superior",
            )

            # Door back to FirstRoom on the left wall
            if not upper_hallway.doors:
                upper_hallway.doors.append(
                    Door(
                        x=0,
                        y=96,
                        target_room_name="FirstRoom",
                        target_spawn_x=440,
                        target_spawn_y=120,
                        width=32,
                        height=54,
                        render_graphic=False,
                    )
                )

            # Stairs to lower hallway (ground floor)
            upper_hallway.doors.append(
                Door(
                    x=224,
                    y=16,
                    target_room_name="lower_hallway",
                    target_spawn_x=190,
                    target_spawn_y=60,
                    width=80,
                    height=40,
                    render_graphic=False,
                    is_stairs=True,
                )
            )

            # Table hiding spots along the hallway
            if not upper_hallway.hiding_spots:
                upper_hallway.hiding_spots.append(
                    HidingSpot("table", 64, 48, width=48, height=28, render_graphic=False, is_solid=False)
                )
                upper_hallway.hiding_spots.append(
                    HidingSpot("table", 464, 144, width=48, height=28, render_graphic=False, is_solid=False)
                )

            # Waypoints along the hallway corridor for El Silbón's patrol
            if not upper_hallway.patrol_waypoints:
                upper_hallway.patrol_waypoints = [(80, 116), (200, 116), (340, 116), (460, 116)]

            # Throwable defensive item on hallway floor
            upper_hallway.items.append(GameObject("throwable", 440, 150, "Botella"))

            # 3. Load LowerHallway (Long 1024px ground floor corridor)
            lower_hallway = TiledLevelLoader.load_room(
                json_path="assets/tilemaps/LowerHallway.json",
                room_name="lower_hallway",
                display_name="Pasillo Inferior",
            )
            # Ensure stairs back up to UpperHallway if missing
            if not any(d.target_room_name == "UpperHallway" for d in lower_hallway.doors):
                lower_hallway.doors.append(
                    Door(
                        x=160,
                        y=16,
                        target_room_name="UpperHallway",
                        target_spawn_x=260,
                        target_spawn_y=60,
                        width=80,
                        height=32,
                        is_stairs=True,
                        render_graphic=False,
                    )
                )
            if not lower_hallway.hiding_spots:
                lower_hallway.hiding_spots.extend([
                    HidingSpot("table", 80, 64, width=48, height=32, render_graphic=False, is_solid=False),
                    HidingSpot("table", 448, 192, width=48, height=32, render_graphic=False, is_solid=False),
                    HidingSpot("table", 768, 80, width=48, height=32, render_graphic=False, is_solid=False),
                    HidingSpot("wardrobe", 928, 48, width=48, height=48, render_graphic=False, is_solid=False),
                ])
            if not lower_hallway.patrol_waypoints:
                lower_hallway.patrol_waypoints = [(80, 112), (190, 80), (330, 112), (480, 140), (620, 112), (780, 80), (940, 112)]

            # 4. Load Kitchen (Contains Elena survivor NPC and door to DiningRoom)
            kitchen = TiledLevelLoader.load_room(
                json_path="assets/tilemaps/Kitchen.json",
                room_name="kitchen",
                display_name="Cocina Abandonada",
            )
            if not kitchen.hiding_spots:
                kitchen.hiding_spots.append(
                    HidingSpot("table", 224, 112, width=64, height=32, render_graphic=False, is_solid=False)
                )
            if not any(d.target_room_name in ("dining_room", "DiningRoom") for d in kitchen.doors):
                kitchen.doors.append(
                    Door(x=488, y=96, target_room_name="dining_room", target_spawn_x=48, target_spawn_y=116, width=24, height=48, render_graphic=False)
                )
            if not kitchen.patrol_waypoints:
                kitchen.patrol_waypoints = [(100, 120), (380, 140)]

            # 5. Load Dining Room (NEW - Center ground floor connector forming circular loop)
            dining_room = TiledLevelLoader.load_room(
                json_path="assets/tilemaps/DiningRoom.json",
                room_name="dining_room",
                display_name="Comedor Principal",
            )
            if not dining_room.hiding_spots:
                dining_room.hiding_spots.append(
                    HidingSpot("table", 12 * 16, 7 * 16, width=8 * 16, height=2 * 16, render_graphic=False, is_solid=False)
                )
            if not any(it.obj_type == "cabinet" for it in dining_room.items):
                dining_room.items.append(GameObject("cabinet", 22 * 16, 2 * 16, "Vitrina"))
            if not any(d.target_room_name in ("kitchen", "Kitchen") for d in dining_room.doors):
                dining_room.doors.append(
                    Door(x=0, y=96, target_room_name="kitchen", target_spawn_x=440, target_spawn_y=116, width=24, height=48, render_graphic=False)
                )
            if not any(d.target_room_name in ("living_room", "LivingRoom") for d in dining_room.doors):
                dining_room.doors.append(
                    Door(x=488, y=96, target_room_name="living_room", target_spawn_x=48, target_spawn_y=192, width=24, height=48, is_bolted=True, render_graphic=False)
                )
            if not dining_room.patrol_waypoints:
                dining_room.patrol_waypoints = [(100, 120), (256, 160), (420, 120)]

            # 6. Load Living Room (Exit room with locked forest exit door and unboltable passage to DiningRoom)
            living_room = TiledLevelLoader.load_room(
                json_path="assets/tilemaps/LivingRoom.json",
                room_name="living_room",
                display_name="Sala Principal",
            )
            if not any(d.target_room_name in ("dining_room", "DiningRoom") for d in living_room.doors):
                living_room.doors.append(
                    Door(x=0, y=180, target_room_name="dining_room", target_spawn_x=450, target_spawn_y=116, width=24, height=48, is_bolted=True, render_graphic=False)
                )
            if not living_room.hiding_spots:
                living_room.hiding_spots.append(
                    HidingSpot("wardrobe", 432, 48, width=48, height=48, render_graphic=False, is_solid=False)
                )
            if not living_room.patrol_waypoints:
                living_room.patrol_waypoints = [(120, 120), (360, 120)]

            # 7. Load Storage Room (Contains crowbar tool, battery, and electrical breaker)
            storage_room = TiledLevelLoader.load_room(
                json_path="assets/tilemaps/StorageRoom.json",
                room_name="storage_room",
                display_name="Almacén Oscuro",
            )
            if not any(it.obj_type == "crowbar" for it in storage_room.items):
                storage_room.items.append(GameObject("crowbar", 380, 80, "Palanca"))
            if not any(it.obj_type == "battery" for it in storage_room.items):
                storage_room.items.append(GameObject("battery", 180, 90, "Batería"))
            if not storage_room.hiding_spots:
                storage_room.hiding_spots.append(
                    HidingSpot("wardrobe", 400, 48, width=48, height=48, render_graphic=False, is_solid=False)
                )
            if not storage_room.patrol_waypoints:
                storage_room.patrol_waypoints = [(120, 130), (360, 130)]

            # 8. Load Master Bedroom (NEW - Upper floor room with Safe containing Forest Exit Key)
            master_bedroom = TiledLevelLoader.load_room(
                json_path="assets/tilemaps/MasterBedroom.json",
                room_name="master_bedroom",
                display_name="Dormitorio Principal",
            )
            if not master_bedroom.hiding_spots:
                master_bedroom.hiding_spots.append(
                    HidingSpot("wardrobe", 26 * 16, 2 * 16, width=32, height=48, render_graphic=False, is_solid=False)
                )
            if not any(it.obj_type == "safe" for it in master_bedroom.items):
                master_bedroom.items.append(GameObject("safe", 9 * 16, 3 * 16, "Caja Fuerte"))
            if not any(d.target_room_name in ("UpperHallway", "upper_hallway") for d in master_bedroom.doors):
                master_bedroom.doors.append(
                    Door(x=0, y=96, target_room_name="UpperHallway", target_spawn_x=440, target_spawn_y=116, width=24, height=48, render_graphic=False)
                )
            if not master_bedroom.patrol_waypoints:
                master_bedroom.patrol_waypoints = [(120, 130), (256, 140), (380, 130)]

            # Ensure UpperHallway has locked door to master_bedroom
            if not any(d.target_room_name in ("master_bedroom", "MasterBedroom") for d in upper_hallway.doors):
                upper_hallway.doors.append(
                    Door(x=488, y=96, target_room_name="master_bedroom", target_spawn_x=48, target_spawn_y=116, width=24, height=48, is_locked=True, required_key="old_key", render_graphic=False)
                )

            # Register all 8 rooms and aliases for case-insensitivity and backward compatibility
            self.rooms["FirstRoom"] = first_room
            self.rooms["first_room"] = first_room
            self.rooms["bedroom"] = first_room

            self.rooms["UpperHallway"] = upper_hallway
            self.rooms["upper_hallway"] = upper_hallway
            self.rooms["hallway"] = upper_hallway

            self.rooms["MasterBedroom"] = master_bedroom
            self.rooms["master_bedroom"] = master_bedroom

            self.rooms["LowerHallway"] = lower_hallway
            self.rooms["lower_hallway"] = lower_hallway

            self.rooms["Kitchen"] = kitchen
            self.rooms["kitchen"] = kitchen

            self.rooms["DiningRoom"] = dining_room
            self.rooms["dining_room"] = dining_room

            self.rooms["LivingRoom"] = living_room
            self.rooms["living_room"] = living_room

            self.rooms["StorageRoom"] = storage_room
            self.rooms["storage_room"] = storage_room

            # Starting room
            self.current_room = first_room
            return True

        except Exception as e:
            print(f"Error loading Tiled cabin: {e}. Falling back to default cabin layout.")
            return False

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
