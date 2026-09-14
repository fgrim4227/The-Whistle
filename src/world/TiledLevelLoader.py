"""
Tiled Level Loader module.
Parses Tiled JSON maps, slices and caches spritesheet tiles, bakes static tile layers
onto Room background surfaces, and extracts collisions, doors, hiding spots, and waypoints.
"""

import json
import os
from typing import Dict, List, Optional, Tuple
import pygame

import settings
from src.definitions.items import ITEM_ARCHETYPES
from src.world.Room import Room
from src.world.Door import Door
from src.world.GameObject import GameObject
from src.world.HidingSpot import HidingSpot


class TilesetManager:
    """Singleton manager for loading, slicing, and caching tileset graphics."""
    _instance: Optional["TilesetManager"] = None

    def __init__(self, spritesheet_path: Optional[str] = None, tile_size: int = 16) -> None:
        if spritesheet_path is None:
            # Anchored to settings.BASE_DIR, not a bare relative path --
            # see the same note on TILEMAPS_DIR in src/definitions/rooms.py.
            spritesheet_path = str(settings.BASE_DIR / "assets" / "graphics" / "environment" / "spritesheet.png")
        self.tile_size = tile_size
        self.spritesheet_path = spritesheet_path
        self.sheet: Optional[pygame.Surface] = None
        self.columns = 0
        self.rows = 0
        self.tile_cache: Dict[Tuple[int, bool, bool], pygame.Surface] = {}
        self._load_sheet()

    @classmethod
    def get_instance(cls) -> "TilesetManager":
        if cls._instance is None:
            cls._instance = TilesetManager()
        return cls._instance

    def _load_sheet(self) -> None:
        if not os.path.exists(self.spritesheet_path):
            print(f"Notice: Spritesheet not found at '{self.spritesheet_path}'.")
            return

        try:
            self.sheet = pygame.image.load(self.spritesheet_path).convert_alpha()
            self.columns = self.sheet.get_width() // self.tile_size
            self.rows = self.sheet.get_height() // self.tile_size
        except Exception as e:
            print(f"Error loading spritesheet '{self.spritesheet_path}': {e}")
            self.sheet = None

    def get_tile(self, tile_id: int, flip_x: bool = False, flip_y: bool = False) -> Optional[pygame.Surface]:
        if self.sheet is None or tile_id < 0:
            return None

        cache_key = (tile_id, flip_x, flip_y)
        if cache_key in self.tile_cache:
            return self.tile_cache[cache_key]

        col = tile_id % self.columns
        row = tile_id // self.columns
        src_rect = pygame.Rect(col * self.tile_size, row * self.tile_size, self.tile_size, self.tile_size)

        try:
            tile_surf = self.sheet.subsurface(src_rect).copy()
            if flip_x or flip_y:
                tile_surf = pygame.transform.flip(tile_surf, flip_x, flip_y)
            self.tile_cache[cache_key] = tile_surf
            return tile_surf
        except Exception:
            return None


class TiledLevelLoader:
    """Loads and compiles Tiled JSON maps into game Room instances."""

    @staticmethod
    def load_room(
        json_path: str,
        room_name: str,
        display_name: str,
        target_width: int = settings.VIRTUAL_WIDTH,
        target_height: int = settings.VIRTUAL_HEIGHT,
    ) -> Room:
        """Loads a room from a Tiled JSON file and bakes its tile layers into a background surface."""
        ts_mgr = TilesetManager.get_instance()

        if not os.path.exists(json_path):
            print(f"Notice: Tiled JSON '{json_path}' not found. Falling back to default procedural room.")
            return Room(room_name, display_name)

        with open(json_path, "r", encoding="utf-8") as f:
            map_data = json.load(f)

        map_w = map_data.get("width", 32)
        map_h = map_data.get("height", 18)
        tile_size = map_data.get("tilewidth", 16)

        actual_w = max(target_width, map_w * tile_size)
        actual_h = max(target_height, map_h * tile_size)

        # Create room without automatic perimeter walls (Tiled Collisions layer handles boundaries)
        room = Room(name=room_name, display_name=display_name, cols=actual_w // tile_size, rows=actual_h // tile_size, tile_size=tile_size, build_walls=False)

        # Bake static tilelayers onto background surface
        bg_surface = pygame.Surface((actual_w, actual_h))
        bg_surface.fill((25, 20, 18))  # Dark ambient wooden wall color

        # Bitmasks for Tiled tile flipping
        FLIPPED_HORIZONTALLY_FLAG = 0x80000000
        FLIPPED_VERTICALLY_FLAG = 0x40000000
        FLIPPED_DIAGONALLY_FLAG = 0x20000000
        CLEAN_GID_MASK = ~(FLIPPED_HORIZONTALLY_FLAG | FLIPPED_VERTICALLY_FLAG | FLIPPED_DIAGONALLY_FLAG)

        for layer in map_data.get("layers", []):
            ltype = layer.get("type")
            if ltype == "tilelayer" and layer.get("visible", True):
                data = layer.get("data", [])
                for idx, raw_gid in enumerate(data):
                    if raw_gid == 0:
                        continue
                    clean_gid = raw_gid & CLEAN_GID_MASK
                    if clean_gid == 0:
                        continue

                    tile_id = clean_gid - 1
                    flip_x = bool(raw_gid & FLIPPED_HORIZONTALLY_FLAG)
                    flip_y = bool(raw_gid & FLIPPED_VERTICALLY_FLAG)

                    tile_surf = ts_mgr.get_tile(tile_id, flip_x=flip_x, flip_y=flip_y)
                    if tile_surf:
                        tx = (idx % map_w) * tile_size
                        ty = (idx // map_w) * tile_size
                        bg_surface.blit(tile_surf, (tx, ty))

            elif ltype == "objectgroup":
                gname = layer.get("name", "")
                objects = layer.get("objects", [])

                if gname == "Collisions":
                    for obj in objects:
                        ox = float(obj.get("x", 0))
                        oy = float(obj.get("y", 0))
                        ow = float(obj.get("width", 0))
                        oh = float(obj.get("height", 0))
                        if ow > 0 and oh > 0:
                            room.solid_tiles.append(pygame.Rect(int(ox), int(oy), int(ow), int(oh)))

                elif gname == "interest_points":
                    for obj in objects:
                        ox = float(obj.get("x", 0))
                        oy = float(obj.get("y", 0))
                        props = {p.get("name"): p.get("value") for p in obj.get("properties", [])}
                        ptype = props.get("type", "")
                        if ptype == "player_spawn":
                            room.player_spawn = (ox, oy)
                        elif ptype == "inv_point":
                            room.patrol_waypoints.append((ox, oy))

                elif gname == "Interactables":
                    for obj in objects:
                        ox = float(obj.get("x", 0))
                        oy = float(obj.get("y", 0))
                        props = {p.get("name"): p.get("value") for p in obj.get("properties", [])}
                        item_type = props.get("object") or props.get("id") or obj.get("type")
                        ow = int(float(obj.get("width", 16))) or 16
                        oh = int(float(obj.get("height", 16))) or 16

                        is_collectible = props.get("is_collectible")
                        if is_collectible is None:
                            is_collectible = item_type not in ("cabinet", "safe", "fuse_box")
                        else:
                            is_collectible = bool(is_collectible)

                        if item_type in ("safe", "fuse_box") and "render_graphic" not in props:
                            render_graphic = False
                        else:
                            render_graphic = bool(props.get("render_graphic", True))

                        note_id = props.get("note_id")
                        yields = props.get("yields")
                        if item_type in ITEM_ARCHETYPES:
                            room.items.append(
                                GameObject(
                                    item_type,
                                    ox,
                                    oy,
                                    width=ow,
                                    height=oh,
                                    is_collectible=is_collectible,
                                    render_graphic=render_graphic,
                                    note_id=note_id,
                                    yields=yields,
                                )
                            )

                        # Check if hiding spot object is authored in Tiled
                        spot_type = props.get("spot_type") or (item_type if item_type in ("wardrobe", "table") else None)
                        if spot_type:
                            dw = int(obj.get("width", 48))
                            dh = int(obj.get("height", 32))
                            room.hiding_spots.append(
                                HidingSpot(spot_type, ox, oy, width=dw, height=dh, render_graphic=False, is_solid=False)
                            )

                        # Check if door or stairs object is authored in Tiled
                        if props.get("id") in ("door", "stairs") or obj.get("type") in ("door", "stairs"):
                            target = props.get("target_room", "hallway")
                            tsx = float(props.get("target_spawn_x", 48))
                            tsy = float(props.get("target_spawn_y", 120))
                            dw = int(obj.get("width", 32))
                            dh = int(obj.get("height", 32))
                            is_locked = bool(props.get("is_locked", False))
                            is_barred = bool(props.get("is_barred", False))
                            is_bolted = bool(props.get("is_bolted", False))
                            is_stairs = bool(props.get("is_stairs", False)) or (props.get("id") == "stairs") or (obj.get("type") == "stairs")
                            is_exit = (props.get("is_exit_door") in ("Yes", "yes", True)) or bool(props.get("is_exit", False))
                            req_key = props.get("required_key", "key")
                            room.doors.append(
                                Door(
                                    x=ox,
                                    y=oy,
                                    target_room_name=target,
                                    target_spawn_x=tsx,
                                    target_spawn_y=tsy,
                                    width=dw,
                                    height=dh,
                                    is_locked=is_locked,
                                    is_barred=is_barred,
                                    is_bolted=is_bolted,
                                    required_key=req_key,
                                    is_exit_door=is_exit,
                                    is_stairs=is_stairs,
                                    render_graphic=False,
                                )
                            )

                elif gname == "Npcs":
                    for obj in objects:
                        ox = float(obj.get("x", 0))
                        oy = float(obj.get("y", 0))
                        # Replace survivor NPC with an environmental parchment note on the floor (Slender-style)
                        if "kitchen" in room_name.lower():
                            room.items.append(
                                GameObject(
                                    "note",
                                    ox,
                                    oy,
                                    width=16,
                                    height=16,
                                    note_id="note_kitchen",
                                    yields="lockpick",
                                )
                            )
                        else:
                            room.items.append(
                                GameObject(
                                    "note",
                                    ox,
                                    oy,
                                    width=16,
                                    height=16,
                                    note_id="note_hallway",
                                    yields=None,
                                )
                            )

        # Seamlessly extend bottom wall rows if map height is less than target canvas height (e.g. 16 vs 18 rows)
        map_pixel_h = map_h * tile_size
        if map_pixel_h < actual_h:
            # Repeat the bottom slice to fill remaining height smoothly
            slice_h = tile_size
            sample_y = map_pixel_h - slice_h
            bottom_strip = bg_surface.subsurface(pygame.Rect(0, sample_y, actual_w, slice_h)).copy()
            for fill_y in range(map_pixel_h, actual_h, slice_h):
                bg_surface.blit(bottom_strip, (0, fill_y))

        room.background_surface = bg_surface
        return room
