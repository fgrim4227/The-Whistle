# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


[Unreleased]
### Added
### Removed
### Changed
### [1.1.1]
### Added
-***Visual cue and ambientation for StartState and GameOverState***
-***Confirmation State to avoid closing the game on accident***
-***Credits***: Credit.txt and a display in the title screen of the credits for all the free assets used throughout the game
### Changed
-***Constants, collisions***
## [1.1.0] - 2026-09-18

### Added
- **Alien: Isolation Acoustic Door Stalking & Knocking (`src/states/entity/monster/MonsterInvestigateState.py`, `MonsterKnockingState.py`, `Monster.py`, `src/minigames/BaseMinigame.py`)**:
  - When a player triggers an acoustic disturbance in another room (e.g. failing the Lockpick minigame, buzzer alert on Keypad, or circuit short in Fuse Box), El Silbón does not drop the alert. Instead, he stalks to the exterior entrance door of the player's room and bangs loudly on the door (`MonsterKnockingState`).
  - Extended door knocking duration to 3.0–4.0 seconds, creating a heart-pounding window of pure panic for Andreas to scramble into a wardrobe or under a table before the door swings open and El Silbón enters to search.
  - Global acoustic alert threshold (`radius >= 1000.0` in `Monster.hear_noise`) allowing minigame penalties to reach the monster across cabin rooms regardless of local coordinate spaces.
- **Data-Oriented Item Drop Sound Effects (`settings.py`, `src/definitions/items.py`, `src/definitions/interactions.py`, `src/states/game/PlayState.py`)**:
  - Replaced the placeholder door-knocking sound effect previously reused during item drops with authentic, dedicated audio assets for each item archetype:
    - Forest Exit Key (`key`): `forest_key_drop.mp3` (`drop_forest_key`).
    - Master Bedroom Key (`old_key`) and Fuse Box Key (`fuse_key`): `master_bedroom_key_drop.mp3` (`drop_key`).
    - Lockpick (`lockpick`): `lock_pick_drop.mp3` (`drop_lockpick`).
    - Heavy Crowbar (`crowbar`): `heavy_bar_drop.mp3` (`drop_heavy`).
    - Throwable stones (`throwable`): `object_hit.mp3` (`object_hit`).
  - Implemented via data-oriented mapping `ITEM_DROP_SOUNDS` and accessor `get_item_drop_sound()`. Triggered consistently when dropping items intentionally via the `G` key as well as automatically during single-slot Granny item swaps.
  - Confirmed and preserved inventory stealth: dropping items does not emit acoustic alerts to El Silbón.

### Fixed
- **Title Menu & Ambient Audio Resumption After Death (`src/states/game/GameOverState.py`, `VictoryState.py`, `StartState.py`, `src/systems/AudioManager.py`)**:
  - Fixed an issue where dying to El Silbón and returning to the title screen left the game in silence due to Gale's `StateStack.pop()` not invoking `enter()` on the root `StartState`. Explicitly invoked `StartState.enter()` upon popping back to the menu, ensured `VictoryState` does the same, and added a fallback in `StartState.update` to guarantee menu music loops continuously.
  - Enhanced `AudioManager.update()` to automatically restart ambient cabin background tracks (`ambience1`) whenever the dedicated ambience channel goes silent during active exploration in `PlayState`.
- **Prologue Blackout Cinematic Auto-Transition (`src/states/game/IntroForestState.py`)**:
  - Fixed an issue where the cinematic intro forest sequence would hang indefinitely on the black transition screen after Andreas was attacked unless an input was pressed. Added an automatic 4-second timed transition into the cabin gameplay, giving players ample time to read the narrative text before waking up in the living room.
- **Cross-Room In-Flight Projectile Culling (`src/definitions/interactions.py`, `src/states/game/PlayState.py`)**:
  - Resolved a bug where stones or tools thrown in long corridors (like `LowerHallway`) retained their world coordinates and flew through doors into adjoining rooms upon room transitions (`play_state.projectiles.clear()` in `handle_door_interaction` and room transition detection in `PlayState.update`).
- **Seamless ESC Exit Handling (`src/states/game/PlayState.py`)**:
  - When a real-time puzzle minigame is active, pressing `ESC` cancels and closes the minigame (`BaseMinigame.close()`), returning movement control to Andreas.
  - When exploring the cabin outside minigames, pressing `ESC` cleanly posts a `pygame.QUIT` event, allowing the player to exit the game at any moment.

### Documentation
- **Comprehensive Bilingual Documentation (`README.md`)**:
  - Rebuilt `README.md` into a complete bilingual guide (English and Spanish) featuring top quick-jump navigation badges, full story synopsis, updated mechanics (whistle paradox, volumetric light, single-slot Granny inventory, 5 minigames, Director AI), controls reference, and software architecture.

## [1.0.0] - 2026-09-18

### Added
- **Content Warning Boot Sequence (`src/states/game/WarningIntro.py`, `src/TheWhistle.py`, `settings.py`, `assets/graphics/warning/*`)**:
  - The game now boots into a new `WarningIntro` state instead of straight into `StartState`, handing off to the title screen once it finishes.
  - Plays three beats in sequence -- a "use headphones" notice, a flashing-lights/loud-noises/jumpscare content notice, and a "WhiteCircle presents..." studio card -- each icon and its caption fading in, holding, and fading out together (`Timer.tween`).
  - Pressing Enter/Space/E at any point cancels the current fade and jumps straight to the next beat (or into `StartState`).
- **Capture Sequence Walks to the Player (`src/states/entity/monster/MonsterCatchingState.py`)**:
  - El Silbón now routes with A* straight to the player's actual position instead of to a fixed point near the hiding spot's furniture.
  - The reveal triggers by real proximity (`CATCH_DISTANCE`, center to center), and the monster turns to face the player (`_face`) right before it plays, ensuring directional `catching-*` animations point the right way.
  - Added `APPROACH_TIMEOUT` so the reveal plays regardless if the walk over to the hiding spot cannot be completed, preventing softlocks.
- **New `breathing` State (`src/states/entity/monster/MonsterBreathing.py`, `src/entities/Monster.py`, `src/states/entity/monster/MonsterPatrolState.py`)**:
  - Added `MonsterBreathingState`: stops completely, plays its directional breathing animation, and repeats the breathing sound every `BREATH_SOUND_INTERVAL` -- escalating to `chase` if the player becomes detectable, otherwise returning to `patrol` once its 2-3s timer runs out.
  - `MonsterPatrolState` rolls a `BREATHING_CHANCE` (20%) each time it reaches a patrol waypoint to pause and breathe instead of immediately continuing to the next one.
- **Cabin Room Expansions & Architectural Topology (`assets/tilemaps/*.json`, `src/definitions/rooms.py`)**:
  - **Secret Passage (`SecretPassage.json`)**: Inverted L-shaped vertical corridor connecting Master Bedroom to Storage Room, furnished with cobwebs and survivor lore note (`note_secret_passage`).
  - **Abandoned Bathroom (`Bathroom.json`)**: 32x18 centered sanitary chamber connected to Lower Hallway with black void padding, calibrated collision barriers, battery pickup, and survivor note (`note_bathroom`).
  - **Private Study Room (`StudyRoom.json`)**: Private study with dark wood tiling, survivor note (`note_study`), battery, and connections to Lower Hallway and service corridor.
  - **Service Hallway (`BathroomHallway.json`)**: Connecting corridor bridging south exit of Bathroom to south exit of Study Room.
  - **Director AI Patrol Waypoints (`src/definitions/rooms.py`)**: Registered `bathroom`, `study_room`, `secret_passage`, and `bathroom_hallway` into `TILED_ROOMS` with dedicated waypoints.
- **Security Keypad Minigame & Recursive Shortcut Network (`src/minigames/KeypadMinigame.py`, `src/minigames/MinigameFactory.py`, `src/definitions/interactions.py`, `src/world/Door.py`, `src/world/TiledLevelLoader.py`, `src/i18n.py`)**:
  - **4-Digit Combination Lock Puzzle (`KeypadMinigame.py`)**: Electronic keypad puzzle with LCD screen displaying real-time digit inputs, illuminated buttons (0-9, CLEAR, ENTER), tactile input beeps, buzzer alert alerting monster on error, and success chimes.
  - **Recursive Room Network Unlock (`unlock_secret_passage_network`)**: Completing combination on either door (`Master Bedroom` or `Storage Room`) recursively unlocks all interconnecting doors across `master_bedroom`, `secret_passage`, and `storage_room`.
  - **Decoupled Door Metadata (`Door.py`, `TiledLevelLoader.py`)**: Added support for Tiled custom properties `lock_type`, `passcode`, and `unlocked` onto `Door` objects.
- **Hardware-Accelerated Fullscreen & Aspect-Ratio Scaling (`src/TheWhistle.py`, `settings.py`, `src/states/game/StartState.py`, `src/i18n.py`)**:
  - **SDL2 Hardware Scaling & Native Maximize (`pygame.SCALED | pygame.RESIZABLE`)**: Initialized display with combined hardware scaling and resizable window flags, enabling OS maximize while maintaining letterboxing across any monitor aspect ratio.
  - **Fullscreen Toggle Shortcuts (`F11` and `Alt+Enter`)**: Bound universal toggle keys to `toggle_fullscreen` in `settings.py` and handled globally in `TheWhistle.on_input`.
- **Authentic Pixel Art Sprites for Dropped & Floor Items (`src/definitions/items.py`, `assets/graphics/environment/spritesheet.png`)**:
  - Pixel art sprites mapped from environment spritesheet for Master Bedroom Key (`old_key`), Forest Exit Key (`key`), and Lockpick (`lockpick`).
- **Standalone Windows Executable Packaging**:
  - Embedded multi-resolution icon (`assets/graphics/icon.ico`) and `settings.py` frozen path detection (`sys.frozen`, `sys._MEIPASS`) for pre-compiled Windows executable releases in `dist/The-Whistle/`.

### Fixed
- **Monster Animation Naming & State Desync (`src/entities/Monster.py`, `src/definitions/entity.py`, `settings.py`, FSM states)**:
  - Fixed directional idle animations (`idle-up`/`idle-down`/`idle-left`/`idle-right`); fixed directional `catching-*` animations missing `loops: 1`; fixed `PlayState` capture name check with `.startswith("catching")`; fixed duplicate `breathing-*` texture typo.
- **A\* Navigation Reliability Audit (`src/systems/Pathfinding.py`, `src/entities/Monster.py`, `MonsterMovingToDoorState.py`, `MonsterKnockingState.py`, `DirectorAI.py`)**:
  - Unreachable-goal waypoints snap to nearest standable cell; stuck-in-obstacle recovery ignores collision until cleared; unified room-entry landing snaps arrival points to standable cells; noise-thrash guard ignores footsteps while holding a real lead; Director AI stands down while player is hidden.
- **Reciprocal Door Lock Synchronization (`MasterBedroom.json`, `House.py`, `interactions.py`)**:
  - Fixed locked door bypass exploit where entering Master Bedroom via secret passage allowed exiting into hallway without `old_key`.
- **Hiding Spot Layer Migration**:
  - Migrated tables and wardrobes incorrectly authored in `Collisions` over to `Interactables` across `UpperHallway.json`, `LowerHallway.json`, `Bathroom.json`, and `StudyRoom.json`.

## [0.5.0] - 2026-09-16

### Added
- **Director AI System (`src/systems/DirectorAI.py`, `src/entities/Monster.py`, `src/states/entity/monster/MonsterPatrolState.py`, `src/states/game/PlayState.py`)**:
  - Added a `DirectorAI` layer, ticked once per frame in `PlayState.update()`, inspired by *Alien: Isolation*. Evaluates pacing, player safety, and tension, feeding organic perceptual cues to El Silbón without giving away exact coordinates.
  - Biases monster room changes via `Monster.director_room_hint` when tension builds up while player is exploring quiet rooms.
- **Integrated A\* Pathfinding for El Silbón (`src/systems/Pathfinding.py`, `MonsterChaseState`, `MonsterStalkingState`, `MonsterInvestigateState`)**:
  - Monster navigates cabin rooms using grid-based A* routing around solid furniture, locked doors, and collision barriers.
  - Route safety margins derived dynamically from monster collision box (`Monster.get_route_widths()`).
  - Line-of-sight vision cone: 120-degree cone with 64px omnidirectional close-proximity awareness.
- **Granny-Style Single-Slot Inventory & In-World Dropping (`src/entities/Player.py`, `src/commands.py`, `src/definitions/interactions.py`, `src/ui/HUD.py`)**:
  - Restricted player hand capacity to 1 active physical item at a time.
  - Spatial dropping (`G` key / `DROP` command): drops held item as an interactive `GameObject` at `(player.x, player.y)` into the active room.
  - Automatic item swap (`_collect_with_granny_swap`): picking up an item while holding another immediately drops previous item.
  - Persistent in-world items: dropped items remain in their room across transitions.
- **Intro Road & Forest Arrival Cinematic Cutscenes (`src/states/game/IntroRoadState.py`, `IntroForestState.py`, `settings.py`, assets)**:
  - Multi-layer parallax highway backdrop, authored road/grass textures, timer-driven roadside underbrush, vehicle breakdown, and dialogue subtitles.
  - Seamless transition to forest arrival cutscene where El Silbón ambushes Andreas, knocking him unconscious and transitioning into the cabin.
- **Smooth Volumetric Flashlight Diffusion (`src/systems/LightingSystem.py`)**:
  - Upgraded directional flashlight cone from 5 stepped layers to 10 tightly-spaced layers with smooth alpha progression (35 -> 255), eliminating radial banding.
  - Per-direction origin offsets and inner exclusion radius preventing head-clipping when facing up.
  - Single faint circular personal glow (`player_ambient_radius = 18`, `player_ambient_alpha = 70`).
- **Dynamic Multi-Stage Objectives Notebook (`src/states/game/ObjectiveState.py`, `src/i18n.py`)**:
  - Replaced static checklist with immersive stage-based narrative progression (`obj_explore` -> `obj_kitchen_lockpick` -> `obj_dining_cabinet` -> `obj_crowbar` -> `obj_fuse_power` -> `obj_master_safe` -> `obj_escape_forest`).
- **Survivor Parchment Notes Environmental Storytelling (`assets/tilemaps/*.json`, `src/i18n.py`)**:
  - Authored interactive parchment survivor notes from José Gregorio across cabin rooms, replacing human NPC dialogues.
- **Dynamic Door Rendering & Sequential Escape Security Sequence (`src/world/Door.py`, `interactions.py`)**:
  - Dynamic door overlays (padlocks, security chains, open doors) based on puzzle state.
  - Two-phase escape sequence: electronic sensor must be deactivated via fuse box before Forest Key can unlock the physical chains.
- **Door Barricades Progression & Planks (`DiningRoom.json`, `LowerHallway.json`, `TiledLevelLoader.py`)**:
  - Barricaded doors with configurable wooden planks (2 on Dining Room, 3 on Lower Hallway) pryable using crowbar.

### Changed
- **Horror Atmosphere & Pacing Balancing (`LightingSystem.py`, `AudioManager.py`, `DirectorAI.py`, `settings.py`)**:
  - Removed glowing eye points (`MONSTER_EYE_LIGHT_RADIUS = 0`) to cloak El Silbón in pure silhouette.
  - Deepened ambient darkness alpha to 252.0 for intense reliance on the flashlight.
  - Shortened repeat whistle cooldown to 2.0-6.0s with higher baseline audibility.
  - Tuned footsteps audibility radius through cabin floors to 500px.

## [0.4.0] - 2026-09-14

### Added
- **Command Pattern Architecture (`src/commands.py`)**:
  - Decoupled keyboard input handling from entity action execution for player and monster movements, interactions, throwing, and inventory.
- **Entity Finite State Machines (`src/states/entity/`)**:
  - Player FSM: `PlayerIdleState`, `PlayerWalkState`, `PlayerHidingState`.
  - Monster FSM: `MonsterPatrolState`, `MonsterMovingToDoorState`, `MonsterKnockingState`, `MonsterChaseState`, `MonsterInvestigateState`, `MonsterBerserkState`, `MonsterStunnedState`.
- **Real-Time Active Minigames System (`src/minigames/`)**:
  - `BaseMinigame`: Abstract overlay architecture running in real time over `PlayState` while preserving monster stalking, footsteps, and lighting.
  - `LockpickMinigame`: Tension and sweet-spot angle lockpicking for dining room vintage cabinet (yields `old_key`).
  - `SafeMinigame`: Rotary acoustic combination safe dial in master bedroom (yields `key`).
  - `CrowbarMinigame`: Button-mashing tug-of-war to pry wooden planks off barred doors.
  - `FuseBoxMinigame`: Electrical wire patching in First Room restoring cabin electricity.
  - `MinigameFactory`: Centralized polymorphic factory for puzzle instantiation.
- **Interactions Strategy & Dispatcher Pattern (`src/definitions/interactions.py`)**:
  - Centralized item interaction handlers in `ITEM_INTERACTIONS` and prompt formatters in `ITEM_PROMPTS`, eliminating monolithic conditionals in `PlayState`.
- **Standalone A\* Grid Pathfinding Module (`src/systems/Pathfinding.py`)**:
  - 16px grid walkability generator and turn simplifier routing around obstacles and entity safety margins.
- **Data-Driven Cabin Layouts & Entity Definitions (`src/definitions/`)**:
  - Centralized room layouts (`rooms.py`), item archetypes (`items.py`), and animation specifications (`entity.py`).
- **Player Sprint & Footstep Cadence (`Player.py`, `commands.py`)**:
  - Sprinting with `Shift` (135 px/s sprint vs 80 px/s walk) with physical step cadence tracking alerting El Silbón dynamically.
- **Tactical Throwables Physics & Distraction (`GameObject.py`, `PlayState.py`)**:
  - Projectiles collide against room obstacles, trigger impact audio, and lure El Silbón (75% stun / 25% berserk).

### Fixed
- **Minigame Completion `AttributeError` in `PlayState.update()`**:
  - Cached active minigame locally during update loop to safely evaluate completion and execute cleanup.
- **Modal Movement Resumption Glitch**:
  - Implemented `Player.clear_movement()` and `Player.sync_movement_keys()` on modal close (`NoteState`, `PauseState`, `ObjectiveState`).
- **Player Diagonal Walk Direction Desync**:
  - Updated movement direction animation continuously during active locomotion.

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