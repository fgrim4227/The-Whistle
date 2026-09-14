"""
Layout data for every room in the cabin: which Tiled map backs it, its
canonical name and any aliases House.rooms should also answer to, and
the doors/hiding spots/patrol waypoints/items to fall back to for
whatever a room's Tiled map doesn't already define itself (see
House._apply_room_fallbacks). Also DEFAULT_CABIN_ROOMS, the fully
procedural 4-room layout House falls back to if the Tiled maps aren't
present at all.

Door/hiding-spot/item entries are plain kwargs dicts for
src.world.Door.Door / HidingSpot.HidingSpot / GameObject.GameObject --
House builds the actual objects from them, this module only holds data.
"""

from typing import Any, Dict, List

import settings

# Anchored to settings.BASE_DIR (not a bare relative path) so these
# resolve correctly regardless of the process's working directory when
# the game is launched -- main.py only fixes up sys.path, it never
# chdir()s to the project root, so a relative "assets/tilemaps/..."
# path only works by accident, when the game happens to be started
# from inside this folder.
TILEMAPS_DIR = settings.BASE_DIR / "assets" / "tilemaps"

# Canonical room name TiledLevelLoader.load_room and House.rooms use as
# the primary key for each room; every other key in "aliases" below
# points at the same Room instance.
TILED_START_ROOM = "FirstRoom"

TILED_ROOMS: Dict[str, Dict[str, Any]] = {
    "FirstRoom": {
        "path": str(TILEMAPS_DIR / "FirstRoom.json"),
        "display_name": "Habitación Sombría",
        "aliases": ["first_room", "bedroom"],
        "player_spawn": (94.0, 129.0),
        "hiding_spots": [
            {"spot_type": "wardrobe", "x": 32, "y": 16, "width": 48, "height": 48, "render_graphic": False, "is_solid": False},
        ],
        "doors": [
            {"x": 464, "y": 104, "target_room_name": "UpperHallway", "target_spawn_x": 48, "target_spawn_y": 116, "width": 32, "height": 48, "render_graphic": False},
        ],
        "patrol_waypoints": [],
        "items": [],
    },
    "UpperHallway": {
        "path": str(TILEMAPS_DIR / "UpperHallway.json"),
        "display_name": "Pasillo Superior",
        "aliases": ["upper_hallway", "hallway"],
        "hiding_spots": [
            {"spot_type": "table", "x": 64, "y": 48, "width": 48, "height": 28, "render_graphic": False, "is_solid": False},
            {"spot_type": "table", "x": 464, "y": 144, "width": 48, "height": 28, "render_graphic": False, "is_solid": False},
        ],
        "doors": [
            {"x": 0, "y": 96, "target_room_name": "FirstRoom", "target_spawn_x": 440, "target_spawn_y": 120, "width": 32, "height": 54, "render_graphic": False},
            {"x": 224, "y": 16, "target_room_name": "lower_hallway", "target_spawn_x": 190, "target_spawn_y": 60, "width": 80, "height": 40, "render_graphic": False, "is_stairs": True},
            {"x": 488, "y": 96, "target_room_name": "master_bedroom", "target_spawn_x": 48, "target_spawn_y": 116, "width": 24, "height": 48, "is_locked": True, "required_key": "old_key", "render_graphic": False},
        ],
        "patrol_waypoints": [(80, 116), (200, 116), (340, 116), (460, 116)],
        "items": [
            {"obj_type": "throwable", "x": 440, "y": 150},
        ],
    },
    "lower_hallway": {
        "path": str(TILEMAPS_DIR / "LowerHallway.json"),
        "display_name": "Pasillo Inferior",
        "aliases": ["LowerHallway"],
        "hiding_spots": [
            {"spot_type": "table", "x": 80, "y": 64, "width": 48, "height": 32, "render_graphic": False, "is_solid": False},
            {"spot_type": "table", "x": 448, "y": 192, "width": 48, "height": 32, "render_graphic": False, "is_solid": False},
            {"spot_type": "table", "x": 768, "y": 80, "width": 48, "height": 32, "render_graphic": False, "is_solid": False},
            {"spot_type": "wardrobe", "x": 928, "y": 48, "width": 48, "height": 48, "render_graphic": False, "is_solid": False},
        ],
        "doors": [
            {"x": 160, "y": 16, "target_room_name": "UpperHallway", "target_spawn_x": 260, "target_spawn_y": 60, "width": 80, "height": 32, "is_stairs": True, "render_graphic": False},
        ],
        "patrol_waypoints": [(80, 112), (190, 80), (330, 112), (480, 140), (620, 112), (780, 80), (940, 112)],
        "items": [],
    },
    "kitchen": {
        "path": str(TILEMAPS_DIR / "Kitchen.json"),
        "display_name": "Cocina Abandonada",
        "aliases": ["Kitchen"],
        "hiding_spots": [
            {"spot_type": "table", "x": 224, "y": 112, "width": 64, "height": 32, "render_graphic": False, "is_solid": False},
        ],
        "doors": [
            {"x": 488, "y": 96, "target_room_name": "dining_room", "target_spawn_x": 48, "target_spawn_y": 116, "width": 24, "height": 48, "render_graphic": False},
        ],
        "patrol_waypoints": [(100, 120), (380, 140)],
        "items": [],
    },
    "dining_room": {
        "path": str(TILEMAPS_DIR / "DiningRoom.json"),
        "display_name": "Comedor Principal",
        "aliases": ["DiningRoom"],
        "hiding_spots": [
            {"spot_type": "table", "x": 12 * 16, "y": 7 * 16, "width": 8 * 16, "height": 2 * 16, "render_graphic": False, "is_solid": False},
        ],
        "doors": [
            {"x": 0, "y": 96, "target_room_name": "kitchen", "target_spawn_x": 440, "target_spawn_y": 116, "width": 24, "height": 48, "render_graphic": False},
            {"x": 488, "y": 96, "target_room_name": "living_room", "target_spawn_x": 48, "target_spawn_y": 192, "width": 24, "height": 48, "is_bolted": True, "render_graphic": False},
        ],
        "patrol_waypoints": [(100, 120), (256, 160), (420, 120)],
        "items": [
            {"obj_type": "cabinet", "x": 22 * 16, "y": 2 * 16},
            {"obj_type": "fuse_key", "x": 120, "y": 180},
        ],
    },
    "living_room": {
        "path": str(TILEMAPS_DIR / "LivingRoom.json"),
        "display_name": "Sala Principal",
        "aliases": ["LivingRoom"],
        "hiding_spots": [
            {"spot_type": "wardrobe", "x": 432, "y": 48, "width": 48, "height": 48, "render_graphic": False, "is_solid": False},
        ],
        "doors": [
            {"x": 0, "y": 180, "target_room_name": "dining_room", "target_spawn_x": 450, "target_spawn_y": 116, "width": 24, "height": 48, "is_bolted": True, "render_graphic": False},
        ],
        "patrol_waypoints": [(120, 120), (360, 120)],
        "items": [],
    },
    "storage_room": {
        "path": str(TILEMAPS_DIR / "StorageRoom.json"),
        "display_name": "Almacén Oscuro",
        "aliases": ["StorageRoom"],
        "hiding_spots": [
            {"spot_type": "wardrobe", "x": 400, "y": 48, "width": 48, "height": 48, "render_graphic": False, "is_solid": False},
        ],
        "doors": [],
        "patrol_waypoints": [(120, 130), (360, 130)],
        "items": [
            {"obj_type": "crowbar", "x": 380, "y": 80},
            {"obj_type": "battery", "x": 180, "y": 90},
        ],
    },
    "master_bedroom": {
        "path": str(TILEMAPS_DIR / "MasterBedroom.json"),
        "display_name": "Dormitorio Principal",
        "aliases": ["MasterBedroom"],
        "hiding_spots": [
            {"spot_type": "wardrobe", "x": 26 * 16, "y": 2 * 16, "width": 32, "height": 48, "render_graphic": False, "is_solid": False},
        ],
        "doors": [
            {"x": 0, "y": 96, "target_room_name": "UpperHallway", "target_spawn_x": 440, "target_spawn_y": 116, "width": 24, "height": 48, "render_graphic": False},
        ],
        "patrol_waypoints": [(120, 130), (256, 140), (380, 130)],
        "items": [
            {"obj_type": "safe", "x": 9 * 16, "y": 3 * 16},
        ],
    },
}

# The fully procedural fallback used only if the Tiled maps above aren't
# present at all (see House.__init__). A separate, smaller 4-room house
# by design -- it predates the Tiled levels and is kept as a safety net,
# not meant to stay in sync room-for-room with TILED_ROOMS.
DEFAULT_START_ROOM = "bedroom"

DEFAULT_CABIN_ROOMS: Dict[str, Dict[str, Any]] = {
    "bedroom": {
        "display_name": "Dormitorio Sombrío",
        "hiding_spots": [{"spot_type": "wardrobe", "x": 64, "y": 40}],
        "items": [{"obj_type": "battery", "x": 140, "y": 100}],
        "doors": [
            {"x": settings.VIRTUAL_WIDTH - settings.TILE_SIZE, "y": settings.VIRTUAL_HEIGHT // 2 - 16,
             "target_room_name": "hallway", "target_spawn_x": 48, "target_spawn_y": settings.VIRTUAL_HEIGHT // 2 - 12},
        ],
        "patrol_waypoints": [(100, 100), (250, 150)],
    },
    "hallway": {
        "display_name": "Pasillo Principal",
        "hiding_spots": [],
        "items": [{"obj_type": "throwable", "x": 200, "y": 120}],
        "doors": [
            {"x": 0, "y": settings.VIRTUAL_HEIGHT // 2 - 16, "target_room_name": "bedroom",
             "target_spawn_x": settings.VIRTUAL_WIDTH - 64, "target_spawn_y": settings.VIRTUAL_HEIGHT // 2 - 12},
            {"x": settings.VIRTUAL_WIDTH // 2 - 16, "y": 0, "target_room_name": "kitchen",
             "target_spawn_x": settings.VIRTUAL_WIDTH // 2 - 10, "target_spawn_y": settings.VIRTUAL_HEIGHT - 64},
            {"x": settings.VIRTUAL_WIDTH - settings.TILE_SIZE, "y": settings.VIRTUAL_HEIGHT // 2 - 16,
             "target_room_name": "living_room", "target_spawn_x": 48, "target_spawn_y": settings.VIRTUAL_HEIGHT // 2 - 12,
             "is_barred": True},
        ],
        "patrol_waypoints": [(80, 140), (240, 140), (400, 140)],
    },
    "kitchen": {
        "display_name": "Cocina Abandonada",
        "hiding_spots": [{"spot_type": "table", "x": 200, "y": 80, "width": 48, "height": 32}],
        "items": [
            {"obj_type": "crowbar", "x": 380, "y": 70},
            {"obj_type": "throwable", "x": 120, "y": 180},
        ],
        "doors": [
            {"x": settings.VIRTUAL_WIDTH // 2 - 16, "y": settings.VIRTUAL_HEIGHT - settings.TILE_SIZE,
             "target_room_name": "hallway", "target_spawn_x": settings.VIRTUAL_WIDTH // 2 - 10, "target_spawn_y": 48},
        ],
        "patrol_waypoints": [(150, 100), (320, 160)],
    },
    "living_room": {
        "display_name": "Sala Principal",
        "hiding_spots": [{"spot_type": "wardrobe", "x": 380, "y": 40}],
        "items": [{"obj_type": "key", "x": 100, "y": 80}],
        "doors": [
            {"x": 0, "y": settings.VIRTUAL_HEIGHT // 2 - 16, "target_room_name": "hallway",
             "target_spawn_x": settings.VIRTUAL_WIDTH - 64, "target_spawn_y": settings.VIRTUAL_HEIGHT // 2 - 12},
            {"x": settings.VIRTUAL_WIDTH // 2 - 16, "y": 0, "target_room_name": "exit",
             "target_spawn_x": 0, "target_spawn_y": 0, "is_locked": True, "required_key": "key", "is_exit_door": True},
        ],
        "patrol_waypoints": [(120, 120), (360, 120)],
    },
}
