# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Data-driven definitions package (`src/definitions/`)**:
  - `entity.py`: `PLAYER_ANIMATIONS`/`MONSTER_ANIMATIONS` specs (per-animation texture + frame indices + interval/loop count) and a shared `build_animations()` loader, replacing the near-identical `_create_animations()` each class hand-rolled.
  - `items.py`: `ITEM_ARCHETYPES` (`GameObject.obj_type` -> draw function) and `HIDING_SPOT_ARCHETYPES` (`HidingSpot.spot_type` -> draw function), replacing the `if/elif` render chains in `GameObject.render()`/`HidingSpot.render()`.
  - `rooms.py`: `TILED_ROOMS` and `DEFAULT_CABIN_ROOMS`, the door/hiding-spot/waypoint/item layout data for all 8 cabin rooms plus the procedural fallback house, previously hardcoded inline across ~250 lines of `House.py`.
- **`settings.FRAMES` + `settings.frame()`**: centralizes animation frame slicing (via `gale.frames.generate_frames`) alongside the existing `TEXTURES` dict. `src/definitions/entity.py`'s animation specs now just list which 1-based frame indices to play (e.g. `{"texture": "silbon_walk", "frames": list(range(1, 11)), "interval": 0.10}`) instead of doing their own pixel-rect math.
- **`Player`/`Monster` finite state machines**:
  - `Monster`'s 7 behavior states moved out of `Monster.py` into their own files under `src/states/entity/` (`MonsterBaseState`, `MonsterPatrolState`, `MonsterMovingToDoorState`, `MonsterKnockingState`, `MonsterChaseState`, `MonsterInvestigateState`, `MonsterBerserkState`, `MonsterStunnedState`; renamed from the previous `Silbon*State` names).
  - `Player` gained a real state machine (`idle`/`walk`/`hiding`, in `src/states/entity/Player*State.py`) instead of calling `change_animation(...)` directly at each call site. `Player.change_state()` guards against re-entering the same state every frame, since movement is polled continuously rather than tile-stepped.
- **Command pattern for Andreas and El Silbón** (`src/commands.py`, mirroring `06-princess`'s `gale.command` usage):
  - Player commands (`MOVE_LEFT/RIGHT/UP/DOWN`, `STOP_MOVE_*`, `INTERACT`, `THROW`, `FLASHLIGHT`, `CYCLE_ITEM`, `SELECT_SLOT_1..5`) are bound to `InputHandler` action ids through a `CommandBindings` instance owned by `Player`.
  - El Silbón's three parameter-free transitions (`CHASE`, `PATROL`, `BERSERK`) are now called directly by his own states' `process_ai()`, the same way an AI-controlled entity fires the shared movement commands in princess's `EntityWalkState`. `moving_to_door`/`knocking`/`investigate`/`stunned` were deliberately left as direct `change_state(...)` calls: they need extra per-call data (`door`, `target_room`, `target_x/y`, `duration`) that `Command.execute(receiver, dt)`'s fixed signature has no room for.
  - Monster's *movement* deliberately was **not** folded into a `held`-flag model like Player's: princess's held-flag resolution is strictly 4-directional (tile-locked), while Monster's chase/investigate/patrol already move at any continuous angle toward an arbitrary point via `move_towards()` -- also exactly the primitive a future A* pathfinder would want to hand waypoints to. Snapping Monster's movement to held-flags would have made chases feel robotic for no pathfinding benefit.

### Changed
- `House.py` rewritten to be data-driven: `_build_tiled_cabin()`/`_build_default_cabin()` now loop over `src/definitions/rooms.py` instead of repeating a near-identical block of Python per room (422 lines -> ~130 lines). Room name aliases (`"FirstRoom"`/`"first_room"`/`"bedroom"`, etc.) are now declared once per room in that data.
- `GameObject`: dropped the `name` constructor parameter (confirmed unread anywhere in the codebase; display names come from `i18n`'s `item_<obj_type>` keys instead).
- `TiledLevelLoader`: the `Interactables` layer now checks `item_type in ITEM_ARCHETYPES` instead of a separate hardcoded tuple + `name_lookup` dict that had to be kept in sync by hand.
- `build_animations()` now returns `(animations, textures)` instead of just `animations`; `Player`/`Monster` track `self.current_texture` (updated inside `change_animation()`), and their `render()`/`render_sprite()` branch on `isinstance(frame, pygame.Rect)` (blit from `settings.TEXTURES[self.current_texture]`) vs. the pre-existing `pygame.Surface` fallback path used when a texture failed to load.
- Removed the redundant `src/states/game/BaseState.py`: it was a 1:1 duplicate of `gale.state.BaseState` (same empty `enter`/`exit`/`on_input`/`update`/`render`), differing only in naming its stored reference `self.state_stack` instead of gale's own `self.state_machine`. Every game state now extends `gale.state.BaseState` directly, and every `self.state_stack`/`state_stack` reference in the 6 game states was renamed to `self.state_machine`/`state_machine` to match.
- Player gained a `held` dict (`move_left/right/up/down`) set by the Move/StopMove commands and resolved into actual movement by the renamed `Player.update_movement(obstacles, dt)` (previously `update_movement_from_input(pressed_keys, obstacles, dt)`, which took a dict `PlayState` built by hand from raw input events).
- `Player.interact_requested`/`throw_requested` are edge-triggered intents set by the `INTERACT`/`THROW` commands and consumed once per frame by `PlayState.update()` (mirrors `sword_requested`/`interact_requested` in princess's `Player`), since resolving them needs `PlayState`'s `house`/`monster`/`projectiles`. Flashlight/cycle-item/slot-selection commands call the corresponding `Player` method directly, since there's no further resolution step needed for those.
- `PlayState.on_input` no longer hand-rolls a `pressed_inputs` dict or an `elif` chain per action id; it now only handles state-stack navigation (`pause`/`objectives`) itself and forwards everything else to `self.player.command_bindings.dispatch(...)`.

### Fixed
- **Game silently loading the old pre-Tiled prototype house instead of the real 8-room cabin**: `main.py` never `chdir()`s to the project root, so the bare relative paths in `_build_tiled_cabin()` (`"assets/tilemaps/FirstRoom.json"`, etc.) and `TilesetManager`'s default `spritesheet_path` only resolved correctly when the game happened to be launched with the working directory already set to `The-Whistle/`. Launched from anywhere else, `House` silently fell back to `_build_default_cabin()`, the old 4-room procedural prototype. Both paths are now anchored to `settings.BASE_DIR` (`src/definitions/rooms.py`'s new `TILEMAPS_DIR`, and `TilesetManager.__init__`'s default).
- **Broken imports after the `src/states/*.py` -> `src/states/game/*.py` move**: `from src.states.BaseState import ...`-style imports across `GameOverState`/`ObjectiveState`/`PauseState`/`PlayState`/`StartState`/`VictoryState`/`TheWhistle.py` still pointed at the old path, so the game failed to import at all. All updated to `src.states.game.*`.
- **`Monster.ai_state` never actually reflected the current state**: it compared `self.state_machine.current` against the *lambda factories* in `state_machine.states` (never real classes), which always fell through to `SilbonBaseState` and always returned the first key in the dict. `LightingSystem`'s berserk eye-glow color, driven by this property, never fired correctly. Replaced with a plain attribute (`self.ai_state`) set directly by `change_state()`.
- **Missing `cabinet`/`safe` sprite and label**: these two item types (added in 0.3.0 for the Dining Room cabinet and Master Bedroom safe) had no entry in `GameObject.render()`'s draw chain and no `item_cabinet`/`item_safe` key in `i18n.py`, so they rendered as nothing. Both are now in `ITEM_ARCHETYPES` and `i18n.py` (es/en).
- **Player facing the wrong direction while walking diagonally / switching movement keys mid-walk**: `PlayerWalkState.enter()` only set the `walk-{direction}` animation once, when the `walk` state was first entered; since `Player.change_state()` skips re-entering a state already active, the animation stayed frozen on whichever direction was held first even as `Player.direction` kept changing underneath it (e.g. holding Down, then also Right, then releasing Down: the character kept animating/facing "down" while actually moving right). Fixed by having `Player.update_movement()` call `change_animation(f"walk-{self.direction}")` itself every frame while moving, the same way `Monster.move_towards()` already does.
- **Unreachable / non-interactive `safe` and `cabinet` due to hardcoded item dimensions**:
  - `GameObject.__init__` hardcoded `width = 16` and `height = 16`, completely discarding custom dimensions authored in Tiled JSON maps (`Interactables` layer).
  - In `MasterBedroom.json`, the desk obstacle collision stopped Andreas at $y=64$, while the safe sat at $y=37.5$ with $h=16$ ($y$ ending at $53.5$). Andreas's interaction reach extended only to $y=54$, causing `interact_zone.colliderect` and HUD prompt checks to fail.
  - Updated `GameObject` to accept `width`, `height`, and `render_graphic`, and updated `TiledLevelLoader` to forward these parameters from Tiled objects.
  - Repositioned the safe in `MasterBedroom.json` to $x=124, y=44$ with dimensions $24 \times 34$, centering it on the desk and bringing its hitbox within reach from the front.
  - Expanded interaction and prompt zone padding from `inflate(20, 20)` to `inflate(24, 24)` in `PlayState.py` for smoother proximity detection, and removed temporary debug print statements.

## [0.3.0] - 2026-09-12

### Added
- **8-Room House Expansion & Continuous 360° Loop Layout**:
  - Added `DiningRoom.json` ($512 \times 288$ px) featuring a central dining table hiding spot, locked vintage china cabinet, and doorways connecting Kitchen and Living Room.
  - Added `MasterBedroom.json` ($512 \times 288$ px) on the upper floor with a master bed, double wardrobe hiding spot, desk, and the Master Safe.
  - Added unboltable door mechanic (`Door.is_bolted`, `Door.unbolt()`). The shortcut door between `DiningRoom` and `LivingRoom` starts bolted from the living room side; once reached and unbolted, it completes a continuous ground floor loop (`LowerHallway` <-> `Kitchen` <-> `DiningRoom` <-> `LivingRoom` <-> `LowerHallway`) so the player is never trapped in dead ends by El Silbón.
  - Integrated and registered all 8 cabin rooms in `House.py` with bidirectional door transitions.

- **Player Multi-Slot Inventory System & HUD Hotbar**:
  - Implemented multi-slot inventory (`player.inventory: List[str]`, capacity up to 5 items) in `Player.py` preventing acquired tools and keys from being discarded or overwritten on pickup.
  - Added hotkeys `1` to `5` for direct inventory slot selection and `C` to cycle active items sequentially in `settings.py`.
  - Upgraded HUD in `HUD.py` with top-right inventory badges displaying slot numbers and item names (`[1: Palanca] > 2: Ganzúa < [3: Llave Antigua]`), highlighting the active equipped item in bright gold.
  - Battery items recharge flashlight immediately upon pickup without occupying inventory space.

- **Interactive Story NPC Progression & Puzzle Dependency Flow**:
  - Enhanced `NPC.py` with story-driven item giving and dynamic contextual dialogues (`interact_with_player()`).
  - Elena delivers the Lockpick (`lockpick`) on first interaction, and provides narrative hints guiding the player through the house based on their current inventory.
  - Established complete non-linear puzzle chain:
    - Elena delivers Lockpick in Kitchen/Upper Hallway.
    - Lockpick unlocks vintage cabinet in Dining Room -> Yields Old Key.
    - Old Key unlocks Master Bedroom door upstairs.
    - Master Safe yields Forest Exit Key.
    - Crowbar in Storage Room unbars Living Room entrance.
    - Unbolting Living Room door opens shortcut to Dining Room.
    - Forest Exit Key unlocks final exit into the woods.
  - Decoupled NPC instantiation in `House.py` so the Tiled JSON `Npcs` layer serves as the single source of truth for survivor placement.

- **Audio Revision & Sound Assets**:
  - Added provisional assets for walking, running, heavy breathing, and jump scares (`breathing.wav`, `run_sound.mp3`, `walk_sound.mp3`, `sfx/screams.wav`).
  - Implemented folklore-accurate inverse volume modulation for El Silbón's whistling in `AudioManager.py` (distant sound = extremely near; clear loud sound = far away).
  - Adjusted whistle cooldown timer range to `(4.0, 15.0)` seconds for atmospheric pacing.

### Changed
- **Door Traversal AI for El Silbón**:
  - Updated valid door filtering in `Monster.py` so El Silbón respects bolted doors (`is_bolted`) until they are unlocked by Andreas.
- **Relocated Tools & Key Placement**:
  - Moved the crowbar to `StorageRoom.json` tool shelf.
  - Removed loose key from `LivingRoom.json` floor, relocating it inside the `MasterBedroom.json` safe.

### Fixed
- **Duplicate NPC Initialization**:
  - Removed hardcoded fallback for `kitchen.npc` in `House.py`, allowing level designers full control of NPC placement directly through Tiled JSON object layers without code duplication.

## [0.2.0] - 2026-09-12

### Added
- **Tiled JSON Map Integration & Level Loader (`TiledLevelLoader.py`)**:
  - Implemented dynamic Tiled JSON level loader parsing tile layers (`Floors`, `Walls`, `Decors`) and object groups (`Collisions`, `interest_points`, `Interactables`, `Npcs`).
  - Added `TilesetManager` singleton slicing and caching 16x16 tiles from `assets/graphics/environment/spritesheet.png`.
  - Added support for arbitrary map sizes (e.g. 1024x288 px) with dynamic background surface allocation.
  - Added extraction of custom Tiled object properties: `is_stairs`, `is_exit_door`, `required_key`, and hiding spot types (`wardrobe`, `table`).

- **Ground Floor Expansion & Tiled Level Maps**:
  - Generated and integrated 4 new Tiled JSON levels matching `spritesheet.tsx`:
    - `LowerHallway.json`: Long 1024px ground floor corridor (64x18 tiles) with 4 interconnected doorways, stairs up to the second floor, 4 hiding spots, throwable objects, and distributed Silbón patrol waypoints.
    - `Kitchen.json`: Abandoned kitchen with counters, dining table hiding spot, crowbar, throwable item, and Elena survivor NPC.
    - `LivingRoom.json`: Main living room with red carpet, sofa, wardrobe hiding spot, master escape key, and locked forest exit door.
    - `StorageRoom.json`: Dark storage room with crates/shelves, spare flashlight battery recharge, throwable brick, and wardrobe hiding spot.
  - Linked all levels with upper floor maps (`FirstRoom.json` and `UpperHallway.json`) to create a complete 6-room interconnected cabin.

- **Smooth Camera Tracking System**:
  - Implemented automatic camera tracking in `PlayState` that smoothly centers on Andreas and clamps to room boundaries.
  - Added seamless horizontal panning across rooms wider than 512px (panning $x=0 \rightarrow 512$ in `LowerHallway`).
  - Updated render pipelines in `Room`, `Player`, `Monster`, `Door`, `HidingSpot`, `GameObject`, `NPC`, and `ThrowableProjectile` to support `camera_offset`.
  - Adapted `LightingSystem` to render darkness masks, flashlight beam polygons, player halos, and El Silbón glowing eyes in screen space while tracking world positions.
  - Maintained screen-space positioning for HUD, prompts, and inner dialogue monologues.

- **Door Listening Mechanic & Ambient Ducking**:
  - Added proximity door listening: approaching a door (< 50 px) while El Silbón is near the other side (< 180 px) plays heavy breathing sound effects (`silbon_breath`).
  - Added dynamic ambient ducking: background audio ducks from 0.45 down to ~0.12–0.15 for acoustic clarity.
  - Added contextual danger warning prompt: *"Presiona E para abrir (¡Se escucha respiración pesada al otro lado!)"* / *"Press E to open (Heavy breathing heard on the other side!)"*.

- **Multi-Floor Stair Navigation**:
  - Added functional stairs connecting `UpperHallway` and `LowerHallway` with contextual prompt *"Presiona E para usar las escaleras"* / *"Press E to use the stairs"*.

### Changed
- **Silbón AI Aggressiveness & Reaction Rebalance**:
  - Tuned AI parameters in `src/entities/Monster.py`:
    - Reduced `room_change_cooldown` intervals to `(2.0, 4.0)`s and `(5.0, 8.0)`s for more frequent, urgent room transitions.
    - Sharpened flashlight suspicion reaction threshold from `0.9`s down to `0.3`s, triggering chases much faster when illuminated.
    - Shortened `SilbonKnockingState` banging duration to `(2.0, 3.0)`s to maintain pressure on the player.
    - Tightened door arrival detection threshold from `24`px to `16`px for crisper room transitions.
- **Flashlight Battery Rebalance**:
  - Reduced `BATTERY_DRAIN_RATE` from `2.5` to `0.3` %/s in `settings.py`, improving exploration flow across larger multi-room layouts.
- **Tiled Map Adjustments**:
  - Refined level layouts, object placement, and collision definitions across `Kitchen.json`, `LowerHallway.json`, `StorageRoom.json`, and `UpperHallway.json`.
- **Silbón AI Physical Door Transit (`SilbonMovingToDoorState`)**:
  - Replaced instant monster teleportation between rooms with physical pathfinding to the doorway before transitioning.
  - Added immediate chase interruption: El Silbón cancels door transit and charges into `SilbonChaseState` if Andreas is spotted unhidden while the monster approaches an exit.
  - Added safe door fallback (`random.choice(valid_doors)`) to prevent monster freezing when traversing disconnected rooms.

### Fixed
- **Thought & NPC Dialogue Darkness Occlusion**:
  - Fixed bug where character thoughts (`player.current_thought`) and NPC dialogues rendered underneath `LightingSystem`'s darkness mask, making them unreadable.
  - Moved thought and dialogue rendering to the screen-space HUD overlay (`HUD.render()`), rendering on top of ambient darkness.
  - Added automatic multi-line word wrapping with semi-transparent dark backdrops (`(0, 0, 0, 210)`) and dynamic vertical positioning avoiding interaction prompt overlap.
  - Ensured thoughts and monologue text remain readable while Andreas is hiding in wardrobes or under tables (`is_hidden = True`).
- **Silbón "Zombie State" & Knocking Vulnerability**:
  - Removed `SilbonKnockingState` from safe states in `PlayState`, ensuring El Silbón remains lethal if touched in the same room.
  - Shortened door knocking timer from 10.0s to 5.0s and added instant cancellation into `chase` if Andreas enters or approaches within 140 px.
- **Pygame Subsurface Locking Glitch**:
  - Resolved `Surface was not closed` error across tile rendering by appending `.copy()` to sliced tile surfaces and bottom wall strips.
- **Perimeter Wall Double Scaling**:
  - Fixed `Room` tile size assignment by adding `tile_size` parameter to `Room.__init__`, correctly differentiating 16px Tiled maps from 32px procedural maps.

## [0.1.0] - 2026-09-11

### Added
- **Artwork Jumpscare System**:
  - Replaced primitive geometric jumpscare in `GameOverState` with animated alternation between `silbon_attack`, `silbon_red` (pure `#b80200`), and subliminal flashes of `silbon_sad`.
  - Added generated pure red texture (`silbon_red.png`) cushioning transitions and making `silbon_sad` appear as a rare, eerie micro-glimpse.
  - Added `COLOR_SILBON_RED = (184, 2, 0)` to `settings.py` and implemented margin-padded screen shake to eliminate visual seams.

- **Core Architecture & State Stack**:
  - Implementation of Gale `Game` and `StateStack` managing layered game states: `StartState`, `PlayState`, `PauseState`, `ObjectiveState`, `GameOverState`, and `VictoryState`.
  - Resolution handling with virtual 16:9 canvas (512x288) scaled uniformly (1280x720).
  - Clean global configuration in `settings.py` with 16 mixer audio channels, input bindings, and color constants.

- **Entity & AI Systems**:
  - `Player` (Andreas): 8-directional movement with foot-based bounding collision, flashlight battery consumption/recharge, internal monologue system, and concealment mechanics.
  - `Monster` (El Silbón) FSM: Refactored to modular Finite State Machine (`SilbonBaseState`, `SilbonPatrolState`, `SilbonKnockingState`, `SilbonChaseState`, `SilbonInvestigateState`, `SilbonBerserkState`, `SilbonStunnedState`).
  - Inter-room monster navigation with autonomous door pathfinding and door knocking warnings before entering rooms.
  - Stealth hiding resolution: monster disengages chase when player hides, avoids patrolling near wardrobes/tables, and leaves the room after countdown.
  - `NPC` (Elena): Survivor ally in the kitchen with contextual dialogue and interaction prompts.

- **World & Cabin Environment**:
  - `House` manager coordinating 4 interconnected rooms: Bedroom (spawn), Central Hallway (danger hub), Kitchen (supplies), and Living Room (exit).
  - Interactive `Door` mechanics supporting open passages, key locks, and wooden barricades requiring prying tools.
  - `HidingSpot` system allowing hiding inside wardrobes and under tables.
  - `GameObject` and `ThrowableProjectile` physics: items can be picked up and thrown (75% stun chance, 25% berserk enrage chance).

- **Dynamic Lighting & Darkness**:
  - Real-time dark overlay mask using `pygame.BLEND_RGBA_SUB` for flashlight cone rendering.
  - Complete shadow occlusion when hiding inside wardrobes (no residual ambient light halo).
  - Piercing eye glows for El Silbón through the dark fog.

- **16-Channel Audio System**:
  - Dedicated channels for ambient cabin loops, periodic folklore whistling, heavy breathing, door knocks, and SFX.
  - Folklore whistling paradox: dynamic inverse volume attenuation (whispers when close, loud echoes when distant) with periodic bursts every 14–24 seconds.
  - Dual composite jumpscare audio (`jumpscare1` + `jumpscare2`) upon defeat.

- **Internationalization (i18n)**:
  - Unified bilingual support (`es` / `en`) backed by `settings.IS_ENGLISH` boolean flag.
  - In-game language toggle via `L` key with real-time UI/HUD and dialogue string resolution.

- **Sprites & Graphical Assets**:
  - Directional spritesheets for player (Andreas) and custom folk-decorated sprites for El Silbón (sombrero, bone sack, crimson eyes).
  - Walk and idle frame slicing mapped directly to sprite sheet row directions.