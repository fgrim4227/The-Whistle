# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

- **Content Warning Boot Sequence (`src/states/game/WarningIntro.py`, `src/TheWhistle.py`, `settings.py`, `assets/graphics/warning/*`)**:
  - The game now boots into a new `WarningIntro` state instead of straight into `StartState`, handing off to the title screen once it finishes.
  - Plays three beats in sequence -- a "use headphones" notice, a flashing-lights/loud-noises/jumpscare content notice, and a "WhiteCircle presents..." studio card -- each icon and its caption fading in, holding, and fading out together (`Timer.tween`) before the next one begins.
  - Pressing Enter/Space/E at any point cancels the current fade and jumps straight to the next beat (or into `StartState`, if already on the last one), instead of waiting out the full timing.

- **A\* Navigation Reliability Audit (`src/systems/Pathfinding.py`, `src/entities/Monster.py`, `src/states/entity/monster/MonsterMovingToDoorState.py`, `src/states/entity/monster/MonsterKnockingState.py`, `src/states/entity/monster/MonsterCatchingState.py`, `src/systems/DirectorAI.py`)**:
  - **Unreachable-Goal Waypoints (`Pathfinding.find_path`)**: The final waypoint no longer gets overwritten with the raw, unreachable goal when that goal sits inside furniture's safety margin -- it stays at the nearest cell a body can actually stand on, so the caller's arrival check can succeed instead of the monster shoving against the obstacle forever. This was the root cause of El Silbón appearing to walk endlessly at a player's hiding spot without ever settling.
  - **Stuck-In-Obstacle Recovery (`Monster.move_towards`)**: A body that already overlaps something solid (e.g. an authored door spawn point landing inside a wall) now ignores collision blocking until it clears the overlap, instead of every direction -- including the way back out -- reading as blocked forever.
  - **Unified Room-Entry Landing (`Monster.enter_room`, `Pathfinding.nearest_standable`)**: New shared method replacing duplicated teleport code in `MonsterMovingToDoorState` and `MonsterKnockingState`; snaps the arrival point to the nearest standable cell when a door's authored spawn coordinate lands inside solid geometry.
  - **Noise-Thrash Guard (`Monster.hear_noise`)**: Ignores noise entirely while already holding a real lead (`chase`, `stalking`, `catching`), and ignores a noise within `SAME_NOISE_RADIUS` of the spot it's already walking to -- footsteps firing several times a second could otherwise restart `investigate`'s route, timer, and animation every few frames, or even cancel an active chase.
  - **Capture Timeout (`MonsterCatchingState`)**: Added `APPROACH_TIMEOUT` so the reveal plays regardless if the walk over to the hiding spot can't be completed -- the player can't leave a hiding spot mid-capture, so an unreachable approach point was a permanent softlock.
  - **Director Silence While Hidden (`DirectorAI.update`)**: Stands down entirely while `player.is_hidden` instead of continuing to seed fake noise at the hider's position -- previously it kept calling the monster back to `investigate` every few seconds, which also kept restarting `MonsterPatrolState`'s room-leave countdown, so the monster could never actually give up and leave.

- **Monster Navigation & Perception (`src/entities/Monster.py`, `src/states/entity/monster/*`, `src/systems/Pathfinding.py`)**:
  - **Movement Contract**: `Monster.move_towards()` only takes one step toward the given point and never decides arrival on its own -- every AI state measures arrival itself from the monster's collision box, since only the state knows whether the point was a route waypoint or the real destination.
  - **Route-Following States**: `MonsterChaseState` walks its route waypoint by waypoint, re-planning only when the remembered player position drifts past `REPATH_DIST` or the route runs out; `MonsterStalkingState` distinguishes "no route exists" from "route finished," pushing straight at its target in the former case instead of standing still; `MonsterInvestigateState` routes to a noise with A* instead of walking straight at it.
  - **Procedural Patrol Waypoints**: `MonsterPatrolState` generates its own waypoints via `Pathfinding.sample_walkable_points()` for rooms with none authored in Tiled.
  - **Route Width From the Collision Box**: `Monster.get_route_widths()` derives the safety margin a route is planned against from the monster's own collision box, replacing hand-tuned figures at each call site.
  - **Line-of-Sight Vision Cone**: `Monster.can_detect_player()` requires a clear line to the player (`has_line_of_sight()`, tested against the room's obstacles) inside a 120-degree cone in the direction it's moving or last moved, with a 64px radius where it notices the player regardless of facing; hearing still carries through walls.
  - **Hiding Is No Longer Always Safe**: `Monster.checks_hiding_spot()` gives a chance of being caught in the act if the monster already had a real lead close to the hiding spot; the `catching` state freezes the scene, plays a one-shot reveal animation while the room's ambient darkness lifts, and resolves into the jumpscare.

- **Player Sprite & Animation Corrections (`src/entities/Player.py`, `src/definitions/entity.py`)**:
  - **Real Spritesheet Wiring (`entity.py`)**: `PLAYER_ANIMATIONS` now points at the actual consolidated `"player"` texture atlas (11x4 grid of 48x48 cells) with the correct per-direction frame ranges, instead of texture ids that were never loaded -- the player was silently rendering as a flat placeholder rectangle in every animation.
  - **Collision Box vs. Sprite Size Split (`PLAYER_SIZE`, `PLAYER_SPRITE_SIZE`)**: Separated the hitbox from the rendered sprite size the same way `Monster` already does; `Player.render()` centers the sprite horizontally and anchors it by the feet over the collision box, so a taller/wider spritesheet no longer shifts hit-detection.
  - **Flashlight Animation Variants**: Added `walk-*-flashlight`/`idle-*-flashlight` entries sharing the flashlight spritesheet's frame layout; `Player.change_animation()` automatically resolves to the `-flashlight` suffixed variant whenever the flashlight is on, so every existing call site picks up the right pose with no changes needed there.
  - Removed a leftover 2px "flashlight origin" indicator dot from `Player.render()`, redundant now that `LightingSystem` draws the real cone.

- **Flashlight Cone Calibration (`src/systems/LightingSystem.py`)**:
  - **Per-Direction Origin Offset**: The cone's vertex can be nudged per facing direction (`flashlight_origin_offset`) independently of the ambient glow, which stays centered on the body.
  - **Head-Clipping Fix (Facing Up)**: Added an inner exclusion radius (`flashlight_inner_radius`) so the cone's near edge starts past the character's own head instead of sweeping through it -- the only direction where the head sits directly on the cone's own axis.

- **Intro Road Cutscene Rebuild (`src/states/game/IntroRoadState.py`, `settings.py`, `assets/graphics/intro/Road/Road.png`, `assets/graphics/intro/Road/Grass.png`, `assets/graphics/intro/Plants/*`, `assets/graphics/intro/Paralax/*`)**:
  - **Layered Forest Backdrop**: Replaced the hand-drawn triangle mountains with four real parallax layers (flat backdrop, far/mid/close treelines) scrolling at independent speeds, each anchored by its own bottom edge to the strip above the road so the dense treeline shows instead of just its sparse upper fringe.
  - **Authored Road & Grass Ground (`Road.png`, `Grass.png`)**: Swapped the procedural road tint and flat grass rectangle for two tileable ground textures, scrolling together at the same offset.
  - **Timer-Driven Roadside Underbrush**: Plants spawn on an independent clock (`PLANT_SPAWN_INTERVAL`) and get culled once off-screen -- the same split Flappy Bird's log spawner uses -- instead of respawning in place when one exits; seeded in two rows (tree-line and road-edge, kept tight by `PLANT_ROW_JITTER`) and sorted by `y` at render time so the back row always draws under the front row for depth.
  - **Physically-Reserved Forest Opening**: A plant is never created if, accounting for the deterministic remaining drive/brake distance at the moment it spawns, it would end up resting inside the gap reserved at `forest_entry_x` (`FOREST_GAP_HALF_WIDTH`) -- the clearing the player actually walks into stays genuinely empty instead of relying on a render-time skip that real plant drift could still fill in.
  - **Player Walks Into the Tree Line**: After the roadside dialogue, the player walks north and shrinks (`player_scale`, anchored by the feet) over the `entering_forest` phase, reading as receding into the distance instead of just walking off the top of the screen.
  - **Dual Headlight Beams, Rounded Cone (`_headlight_cone_points`)**: The car casts two vertically-offset headlight beams instead of one, each with an arced far edge (matching the flashlight's cone technique) instead of a flat triangle tip.
  - **Direct Handoff to the Forest**: Removed the unused red full-screen ambush flash and its separate phase; `entering_forest` now transitions straight into `"ending"` and, after a beat, into `IntroForestState`.

- **New Forest Arrival Cutscene (`src/states/game/IntroForestState.py`)**:
  - Continues directly from `IntroRoadState`: the player walks up from off-screen to the middle of the clearing, turns to face south, and two lines of dialogue play out in sequence.
  - El Silbón then appears behind the player and closes the distance until it's standing right over them, a punch sound plays, and the screen cuts to black with the closing narrative line ("Algo te ha intentado matar pero lograste sobrevivir... Despiertas en otro lugar...").

- **Cabin Room Expansions & Architectural Topology (`assets/tilemaps/*.json`, `src/definitions/rooms.py`)**:
  - **Secret Passage (`SecretPassage.json`)**: Added an inverted L-shaped vertical corridor connecting Master Bedroom to Storage Room, furnished with atmospheric cobwebs and an authentic survivor lore note (`note_secret_passage`).
  - **Abandoned Bathroom (`Bathroom.json`)**: Added a 32x18 centered sanitary chamber connected to Lower Hallway with black void padding, calibrated collision barriers, battery pickup, and survivor note (`note_bathroom`).
  - **Private Study Room (`StudyRoom.json`)**: Added a private study with dark wood tiling, survivor note (`note_study`), battery, and connections to Lower Hallway and the connecting service corridor.
  - **Service Hallway (`BathroomHallway.json`)**: Created a connecting corridor with dark wood flooring and wall sconces bridging the south exit of the Bathroom to the south exit of the Study Room, providing natural architectural topology and removing direct cross-room teleportation.
  - **Director AI Patrol Waypoints (`src/definitions/rooms.py`)**: Registered `bathroom`, `study_room`, `secret_passage`, and `bathroom_hallway` into `TILED_ROOMS` with dedicated waypoints, enabling El Silbón's Director AI to actively stalk Andreas through all newly expanded sectors.

- **Security Keypad Minigame & Recursive Shortcut Network (`src/minigames/KeypadMinigame.py`, `src/minigames/MinigameFactory.py`, `src/definitions/interactions.py`, `src/world/Door.py`, `src/world/TiledLevelLoader.py`, `src/i18n.py`)**:
  - **4-Digit Combination Lock Puzzle (`KeypadMinigame.py`)**: Developed an electronic keypad puzzle with LCD screen displaying real-time digit inputs, illuminated buttons (0-9, CLEAR, ENTER), tactile input beeps, buzzer alert with monster audio trigger on incorrect attempts (`hear_noise`), and success chimes.
  - **Recursive Room Network Unlock (`unlock_secret_passage_network`)**: Successfully completing the combination on either door (`Master Bedroom` or `Storage Room`) recursively unlocks all interconnecting doors across `master_bedroom`, `secret_passage`, and `storage_room`, permanently granting access to the cabin shortcut.
  - **Closure Scope & Sound Mapping Resolution (`interactions.py`)**: Resolved a Python closure scoping issue where an inner local import shadowed global `settings` upon passcode completion, and mapped keypad unlock feedback to the authentic `"minigame_unlock_click"` audio cue.
  - **Decoupled Door Metadata (`Door.py`, `TiledLevelLoader.py`)**: Added support for Tiled custom properties `lock_type`, `passcode`, and `unlocked` onto `Door` objects, allowing level maps to define specialized locking mechanisms declaratively.
  - **Bilingual Translations (`src/i18n.py`)**: Added `prompt_keypad`, `keypad_title`, `keypad_clear`, `keypad_enter`, and related UI keys in both English and Spanish.

- **Collision Boundaries & Aerial Door Spawns Calibration (`LowerHallway.json`, `StorageRoom.json`, `Bathroom.json`, `StudyRoom.json`, `UpperHallway.json`)**:
  - **Hiding Spot Layer Migration**: Migrated table and wardrobe hiding spots incorrectly authored in `Collisions` over to `Interactables` across `UpperHallway.json` (`id: 56`, `id: 57`), `LowerHallway.json` (`id: 16`), `Bathroom.json` (`id: 11`), and `StudyRoom.json` (`id: 14`), while moving wall collision barrier `id: 13` in `StudyRoom.json` back to `Collisions`. Resolves player hiding failures and phantom collision barriers.
  - **Storage Room Spawn Bug Fix**: Fixed player movement lock when entering Storage Room from Lower Hallway caused by the south wall's aerial-perspective collision barrier overlapping player feet rect (`target_spawn_y = 190`). Removed duplicate door entity and aligned interactable trigger `id: 20` at `(224, 236.5, 64, 32)`.
  - **Bathroom Centering & Void Barriers**: Resized Bathroom map from 16 to 32 tiles (512x288), centering the active room with 8 tiles of black void padding on each side and impenetrable collision boundaries (`id: 16`, `id: 17`) to keep camera rendering stable.
  - **Transit Clearance Verification**: Calibrated player feet collision bounds across all newly authored room transitions (`Bathroom`, `BathroomHallway`, `StudyRoom`), guaranteeing zero obstacle overlap on entry.

- **Reciprocal Door Lock Synchronization & Master Bedroom Validation (`MasterBedroom.json`, `src/definitions/rooms.py`, `src/definitions/interactions.py`, `src/world/House.py`, `src/world/Door.py`)**:
  - **Locked Door Bypass Resolution**: Fixed an exploit where entering Master Bedroom via the secret passage allowed the player to open and exit through the locked hallway door without possessing the Master Bedroom key (`old_key`).
  - **Reciprocal Lock Enforcement (`House.py` & `interactions.py`)**: Synchronized reciprocal door lock states during cabin loading and runtime interactions (`get_reciprocal_door`), strictly forbidding transit through any door whose counterpart is locked unless unlocked with the required key.
  - **Door Sprite Presentation Scope (`Door.py`)**: Scoped top-down padlock overlay rendering to Upper Hallway entrance, preserving authored clean interior door frames inside Master Bedroom.

- **Authentic Pixel Art Sprites for Dropped & Floor Items (`src/definitions/items.py`, `assets/graphics/environment/spritesheet.png`)**:
  - **Master Bedroom Key (`old_key`)**: Mapped floor and drop item rendering to the authored golden key sprite at `(592, 96, 16, 16)`.
  - **Forest Exit Key (`key`)**: Mapped floor and drop item rendering to the authored mossy green key sprite at `(608, 96, 16, 16)`.
  - **Lockpick Sprite (`lockpick`)**: Extracted custom pixel art lockpick sprite directly into the environment spritesheet at `(624, 96, 16, 16)`, completely replacing procedural geometry rendering when dropped with `G` or placed in-world.

- **Immersive Audio & Minimalist HUD Polish (`src/systems/AudioManager.py`, `src/definitions/interactions.py`, `src/ui/HUD.py`, `src/systems/LightingSystem.py`, `src/minigames/LockpickMinigame.py`, `src/states/game/PlayState.py`, `src/i18n.py`):**
  - **Audio Threshold Calibration (`AudioManager.py`)**: Calibrated baseline whistle volume to `0.10`, heightened closed-door breathing volume to `0.80 - 0.95` for distinct acoustic proximity cues, and refined same-room breathing detection to `100px`.
  - **Organic Acoustic Tension**: Removed textual door breathing spoiler prompt (`prompt_open_door_danger`), letting directional door breathing audio convey danger naturally without UI spoilers.
  - **Text Banner Removal (`hud_silbon_near`)**: Stripped the red text warning banner from the HUD, immersing the player in auditory awareness where El Silbón's proximity is tracked solely through the whistling folklore paradox.
  - **Door Banging Banner & Prompt Cleanup (`PlayState.py`, `i18n.py`)**: Removed obsolete door banging warning text (`prompt_door_banging`) and stripped dead monster banging prompt evaluation in `PlayState._update_contextual_prompt()`, relying entirely on authentic 3D banging sound effects.
  - **Unused & Legacy String Pruning (`src/i18n.py`)**: Pruned obsolete prototype localization keys (`elena_dialogue_*`, `prompt_talk_npc`, `prompt_keypad_locked`, `inst_inventory`, `minigame_crowbar_title`, `minigame_safe_title`, etc.), ensuring identical 117-key bilingual consistency across English and Spanish.
  - **AST Structural Audit (`src/`)**: Inspected all game modules via Python Abstract Syntax Tree analysis, verifying clean execution flow and zero duplicate method declarations.
  - **Ambient Darkness Calibration (`LightingSystem.py`)**: Fine-tuned base ambient darkness alpha to `251.0` for balanced nocturnal room contrast.
  - **Minigame UI Minimalism (`LockpickMinigame.py`)**: Simplified lockpicking interface by removing redundant header text, focusing attention on the brass tumbler mechanics.

- **Level Geometry & Tilemap Collisions Calibration (`assets/tilemaps/*.json`)**:
  - Refined wall collisions, door boundaries, stair trigger dimensions, and note placements across cabin tilemaps (`Kitchen.json`, `UpperHallway.json`, `LowerHallway.json`, `LivingRoom.json`, `MasterBedroom.json`, `StorageRoom.json`) for smooth entity navigation and accurate room transitions.

- **Hardware-Accelerated Fullscreen & Aspect-Ratio Scaling (`src/TheWhistle.py`, `settings.py`, `src/states/game/StartState.py`, `src/i18n.py`)**:
  - **SDL2 Hardware Scaling & Native Maximize (`pygame.SCALED | pygame.RESIZABLE`)**: Initialized display with combined hardware scaling and resizable window flags, enabling the OS window frame's native Maximize button while maintaining GPU-accelerated letterboxing across any monitor aspect ratio.
  - **Fullscreen Toggle Shortcuts (`F11` and `Alt+Enter`)**: Bound universal toggle keys to `toggle_fullscreen` in `settings.py` and handled globally in `TheWhistle.on_input` across all game states.
  - **Physics & Collision Integrity**: Kept internal virtual resolution strictly locked at 512x288, guaranteeing that character hitboxes, door interaction zones, lighting diffusion, and AI pathfinding operate without displacement or desynchronization.
  - **Controls Modal Expansion**: Updated instructions dialog in `StartState.py` and `i18n.py` to document the fullscreen shortcuts in both Spanish and English.

- **Intro Cinematic Polish & Asset Calibration (`src/states/game/IntroRoadState.py`, `assets/graphics/intro/car_084.png`, `assets/graphics/intro/car_083.png`)**:
  - **High-Fidelity Vehicle Sprite (`car_084.png`)**: Configured intro road cinematic to render the calibrated vehicle model (`car_084.png`, 95x45), improving visual fidelity and proportions during the breakdown sequence.
  - **Deduplication of `enter()`**: Removed redundant duplicate `enter()` method definition in `IntroRoadState.py`.
  - **Dialogue Subtitle Timing**: Synchronized roadside whistle cue with Andreas' dialogue prompt (`"¿Quién anda ahí...? ¿Hay alguien?"`), extending the stillness window to 4.5s so dialogue and atmospheric tension are clearly experienced before entering the forest.

- **Audio Lifecycle & Whistle Pacing Fixes (`src/states/game/IntroRoadState.py`, `src/systems/AudioManager.py`)**:
  - **Timer Isolation in Intro Scene (`IntroRoadState.py`)**: Cleared global engine timers on intro exit (`Timer.clear()`) and guarded roadside whistle callbacks so they cannot bleed post-transition or abruptly kill El Silbón's whistling channel inside `PlayState`.
  - **Recurrent Whistle Pacing Synchronization (`AudioManager.py`)**: Unified the repeat whistle cooldown to `2.0 - 6.0s` (fixing the legacy `4.0 - 15.0s` fallback), ensuring consistent, persistent folklore cues across the cabin.
- **Repository Cleanup (`scratch/`)**:
  - Purged obsolete temporary sprite inspection dumps from `scratch/inspect_sprites/`; all dynamic door overlays, padlocks, and interactive items continue rendering cleanly from `assets/graphics/environment/spritesheet.png`.

- **Intro Visual Atmosphere Calibration & Dependency Fix (`src/states/game/IntroRoadState.py`, `assets/graphics/intro/roads2W.png`, `requirements.txt`)**:
  - **Nocturnal Grass Palette (`IntroRoadState.py`)**: Updated roadside ground color to deep nocturnal pine green `(5, 55, 3)` (from bright olive `(160, 192, 112)`), seamlessly blending the highway verge into the midnight mountain aesthetic.
  - **Roadside Horizon Alignment (`IntroRoadState.py`)**: Re-anchored grass rectangle positioning to `road_y` (removing the `-30px` vertical overlap), creating clean visual layer separation between the highway asphalt and the distant mountain silhouettes.
  - **Highway Asphalt Palette Tuning (`roads2W.png`)**: Calibrated road surface colors for cohesive night-time contrast with vehicle headlights and particle smoke.
  - **Engine Dependency Specification (`requirements.txt`)**: Updated engine requirement to `gale-engine>=1.16.0` (official PyPI package by Prof. Alejandro Mujica), preventing build failures caused by the legacy abandoned `gale` package.

- **Horror Atmosphere & Pacing Balancing (`src/systems/LightingSystem.py`, `AudioManager.py`, `DirectorAI.py`, `settings.py`, `Kitchen.json`)**:
  - **Shadowy El Silbón Silhouette**: Removed glowing eye points (`MONSTER_EYE_LIGHT_RADIUS = 0`), fully cloaking the monster in darkness as an unseen, terrifying presence.
  - **Denser Ambient Darkness**: Deepened base ambient darkness alpha to `252.0` (from `240.0`) and capture sequence alpha to `245.0` (from `200.0`) for intense claustrophobia and reliance on the flashlight.
  - **Intensified Audio Landscape (`AudioManager.py`)**:
    - Reduced periodic whistle cooldown to `2.0 - 6.0s` (from `4.0 - 15.0s`) with higher minimum baseline audibility (`0.06`), making his whistling far more persistent and unnerving.
    - Extended monster footstep audibility radius through cabin floors to `500px` (from `260px`) with higher minimum volume (`0.3`).
    - Heightened breathing sensitivity and volume (up to `0.5` through closed doors and `0.3` within same-room proximity).
  - **Relentless Director AI Pacing (`DirectorAI.py`)**: Shortened tension threshold to `5.0s` (from `30.0s`) and chase recovery cooldown to `5.0s` (from `25.0s`), drastically reducing idle wandering downtime and keeping El Silbón actively stalking Andreas.
  - **Level Geometry Collision Tuning (`Kitchen.json`)**: Adjusted kitchen island counter collision box for smooth player and entity navigation.
- **Director AI (`src/systems/DirectorAI.py`, `src/entities/Monster.py`, `src/states/entity/monster/MonsterPatrolState.py`, `src/states/game/PlayState.py`)**:
  - Added a `DirectorAI` layer, ticked once per frame in `PlayState.update()` right before `Monster.update_ai()`, that knows the player's real room and position but never drives the monster directly -- it only ever feeds the same senses the monster's own FSM states already read, so a nudge is indistinguishable from a real noise or a patrol choice.
  - Tracks two timers: a tension timer that builds only while the monster is idly wandering (`patrol` or `moving_to_door`, reset whenever anything else is happening) and a cooldown that suppresses all nudging after a real `chase`.
  - Once tension crosses `TENSION_THRESHOLD` and the monster is back in plain `patrol`, nudges it: if the monster shares the player's room, seeds a fake sound via `Monster.hear_noise()` at a random point `NOISE_JITTER_MIN`-`NOISE_JITTER_MAX` (40-100px) from the player; otherwise it sets `Monster.director_room_hint` to the player's room name.
  - `Monster.director_room_hint` is a one-shot suggestion: `MonsterPatrolState._leave_room()` picks a matching door when one exists, and clears the hint the moment a door is chosen (matched or not) so it only ever biases a single room change.
- **Smooth Volumetric Flashlight Diffusion (`src/systems/LightingSystem.py`)**:
  - Upgraded directional flashlight cone from 5 stepped layers to 10 tightly-spaced layers (steps of ~8px length and 5° angular increments; alpha progression 35 -> 255), preserving the exact original 68° to 20° cone width oriented to player facing direction (`down`, `up`, `right`, `left`).
  - Fixed angular step interpolation in `_carve_flashlight_cone` (`2.0 * half / steps`), completely eliminating the radial fan bug and harsh contour banding for a smooth, cohesive light falloff.
  - Single faint circular personal glow (`player_ambient_radius = 18`, `player_ambient_alpha = 70`): unified personal player light without concentric diffusion rings, preserving smooth multi-layer diffusion exclusively for the directional cone.
  - Subtractive alpha blending (`pygame.BLEND_RGBA_SUB`) with smooth diffusion into the darkness; absolute darkness (0 light) when Andreas hides inside wardrobes/tables.
- **Granny-Style Single-Slot Inventory & Persistent In-World Item Dropping (`src/entities/Player.py`, `src/commands.py`, `src/definitions/interactions.py`, `src/ui/HUD.py`, `settings.py`)**:
  - Restricted player hand capacity to 1 active physical item at a time.
  - Spatial dropping (`G` key / `DROP` command): drops held item as an interactive `GameObject` at `(player.x, player.y)` into the active room's item list (`house.current_room.items`).
  - Automatic item swap (`_collect_with_granny_swap`): picking up an item while holding another immediately drops the previous item on the floor.
  - Guaranteed persistence: dropped items remain in their room across room transitions and can be picked back up anytime.
  - Batteries bypass hand slot and instantly recharge the flashlight.
  - HUD updated to display single hand item with clean status badge (`Mano: [Item] | G: Soltar` or `Mano: Vacía`).
- **Dynamic Multi-Stage Objectives Notebook (`src/states/game/ObjectiveState.py`, `src/definitions/interactions.py`, `src/i18n.py`)**:
  - Replaced static item checklist with an immersive stage-based narrative progression (`obj_explore` -> `obj_kitchen_lockpick` -> `obj_dining_cabinet` -> `obj_crowbar` -> `obj_fuse_power` -> `obj_master_safe` -> `obj_escape_forest`).
  - Notebook interface renders prominent `[▶] Misión Actual` pointer with strikethrough completed objectives and locked future milestones.
  - Dynamically triggers milestone advances upon reading notes, picking locks, prying door planks, solving the fuse box, and opening the master safe.
- **Guidance Survivor Notes Environmental Expansion (`assets/tilemaps/*.json`, `src/i18n.py`)**:
  - Authored interactive parchment survivor notes across cabin rooms: Lower Hallway (`note_lower_hallway`), Dining Room (`note_dining_room`), Master Bedroom (`note_master_safe`), and Living Room (`note_fuse_warning`).
  - Notes provide organic in-world hints and survivor lore from José Gregorio, guiding the player through the house layout and escape sequence.
- **Visual Environment Sprites for In-World Items (`src/definitions/items.py`)**:
  - Replaced procedural Pygame primitive placeholders with authored sprites from `assets/graphics/environment/spritesheet.png`.
  - Added cached subsurfaces for `battery` `(592, 48, 16, 16)`, `fuse_key` `(592, 64, 16, 16)`, and `cabinet` (lockpick box) `(592, 80, 16, 16)`.
- **Dynamic Door Rendering & State Transitions (`src/world/Door.py` & `UpperHallway.json`)**:
  - **Master Bedroom Door**: Implemented clean door base in Tiled (`GID 425, 521, 617, 713` in `UpperHallway.json`). In `Door.py`, renders the door with padlock `(704, 64, 16, 64)` while locked. When unlocked, removing the overlay cleanly reveals the unpadlocked door underneath without transparency bleed.
  - **Living Room Escape Door**: Corrected coordinates from red sofa to authentic 32x32 double door sprites:
    1. *Active Security Sensor*: Renders chained door with red sensor light `(688, 32, 32, 32)` when power is off.
    2. *Chained & Padlocked*: Renders chained door with padlock without red sensor `(656, 32, 32, 32)` once cabin power is restored.
    3. *Free Access*: Renders clear open double door `(624, 32, 32, 32)` upon unlocking with the exit key.
  - **Sequential Escape Validation (`src/definitions/interactions.py`)**: Enforced two-stage security sequence for escaping:
    1. *Phase 1 (Electronic Sensor)*: While `house.power_restored == False`, the red sensor beam physically prevents escape; interacting shows `prompt_exit_sensor_active` and triggers `thought_exit_no_power` even if player holds the forest key.
    2. *Phase 2 (Physical Chains & Padlock)*: Once electricity is restored in the fuse box, the sensor shuts off and chains require the Forest Key. Interacting without the key prompts `thought_exit_locked_chains`. Unlocking with the key triggers `VictoryState`.
  - **Bidirectional Door Sync (`src/definitions/interactions.py`)**: Unlocking Master Bedroom or unbarring doors automatically unlocks/unbars the reciprocal door in the adjoining room.
- **Dynamic Fuse Box Visual States (`src/world/GameObject.py` & `FirstRoom.json`)**:
  - Aligned interactable `fuse_box` object at `(448, 0, 16, 32)` to perfectly match the visual fuse box tile in Tiled.
  - Dynamically renders the closed fuse box sprite with hazard symbol `(720, 32, 16, 32)` by default, and seamlessly overlays the open fuse box sprite `(736, 32, 16, 32)` with exposed circuitry once `FuseBoxMinigame` is solved, completely covering the closed box underneath.
- **Fix Duplicate Fuse Key in Dining Room (`src/definitions/rooms.py`)**:
  - Removed lingering `fuse_key` fallback entry from `TILED_ROOMS["dining_room"]["items"]`, preventing duplicate key injection in the dining room and keeping it exclusively in `LivingRoom.json`.
- **Door Barricades Progression & Planks Configuration (`DiningRoom.json`, `LowerHallway.json`, `TiledLevelLoader.py`)**:
  - Configured Dining Room to Living Room door with **2 planks** (`is_barred=True`, `planks_remaining=2`), allowing the player to pry it open from the dining room side using the crowbar.
  - Configured Lower Hallway to Living Room door with **3 planks** (`planks_remaining=3`).
  - Added Tiled custom property parsing for `planks_remaining` in `TiledLevelLoader.py`.
- **FirstRoom Stealth Tutorial Note (`FirstRoom.json` & `src/i18n.py`)**:
  - Added interactive survivor note `note_first_room` in `FirstRoom` teaching the player how to survive by hiding inside wardrobes and under tables when El Silbón approaches.
  - Updated all survivor note and thought references from Elena to **Jose Gregorio** across Spanish and English localizations.
- **Data-Driven Survivor Notes via Tiled Custom Properties (`src/world/TiledLevelLoader.py`)**:
  - Replaced hardcoded room name conditionals (`if "kitchen" in room_name...`) with generic, data-driven extraction of custom properties (`note_id`, `yields`, `is_collectible`, `render_graphic`) from Tiled object layers (`Npcs`, `Notes`, `Interactables`).
  - Added multi-tier fallback for `note_id` (object name -> room name), enabling level designers to place interactive notes in any room without touching Python code.
  - Configured custom properties for `note_kitchen` (yielding `lockpick`) in `Kitchen.json` and `note_hallway` in `UpperHallway.json`.
- **Minigame Factory Pattern (`src/minigames/MinigameFactory.py`)**:
  - Implemented `MinigameFactory` to centralize instantiation and dynamic registration of minigames (`lockpick`, `safe`, `crowbar`, `fuse_box`).
  - Decoupled `src/definitions/interactions.py` and `PlayState` from concrete minigame classes, adhering to the Open/Closed Principle.
  - Normalized constructor arguments polymorphically (`target_object`/`target_door`, callbacks, and `**kwargs`).
- **Interactions Strategy / Dispatcher Pattern (`src/definitions/interactions.py`)**:
  - Centralized item interaction handlers in `ITEM_INTERACTIONS` and contextual prompt formatters in `ITEM_PROMPTS`.
  - Added dedicated door interaction handlers (`handle_door_interaction`) and prompt formatters (`get_door_prompt`) covering unbolting, crowbar minigame on barred doors, key unlocks, electronic sensor checks, and monster proximity detection.
  - Drastically reduced `PlayState._handle_interaction` and `PlayState._update_contextual_prompt` from monolithic conditional blocks to clean, extensible dictionary dispatches.
- **Atmospheric Dynamic Ambient Darkness Tweening (`gale.timer.Timer.tween`)**:
  - Added `Timer.update(dt)` in `TheWhistle.update()` to enable Gale engine tweening and scheduled callbacks.
  - Extended `LightingSystem` with `base_ambient_alpha = 215.0`, `monster_ambient_alpha = 255.0`, and smooth float `darkness_alpha`.
  - In `PlayState.update()`, dynamically tweens darkness alpha to 255.0 (pitch black) when El Silbón enters the player's room, and back to 215.0 when he exits, using `"in_out_quad"` easing.
- **Real-Time Active Overlay Minigames System (`src/minigames/`)**:
  - `BaseMinigame`: Abstract lifecycle base class for active overlays running directly over `PlayState`. Crucially preserves real-time world simulation (El Silbón continues stalking, moving, and generating footstep audio; darkness and lighting remain active; player can press `ESC` to cancel and flee anytime).
  - `SafeMinigame`: Rotary acoustic combination safe dial in `master_bedroom`. Features rotational audio cues (`normal_click.wav`), target discovery clicks (`unlock_click.mp3`), and metallic jam penalty (`lock_forced.mp3`) alerting El Silbón upon failure. Yields the Forest Exit Key (`key`).
  - `LockpickMinigame`: Tension and sweet-spot angle lockpicking for the dining room vintage cabinet. Simulates lock cylinder rotation, pick strain vibration, and metallic forced sound (`lock_forced.mp3`) that alerts El Silbón when overstressed. Yields the Old Key (`old_key`).
  - `CrowbarMinigame`: Button-mashing tug-of-war against resistance to pry wooden planks off barred doors. Each plank removal snaps with an authentic wood cracking sound (`wood_break.mp3`), decrements `planks_remaining`, and alerts El Silbón with heavy noise (`monster.hear_noise`).
  - `FuseBoxMinigame`: Electrical wire patching in `FirstRoom`. Connects 4 colored terminals across shuffled endpoints. Incorrect connections trigger an electrical short-circuit and alert the monster; completing the circuit restores cabin electricity (`house.power_restored = True`), unlocking the final exit door's electronic security sensor.
  - Dedicated `"minigame"` audio channel (Channel 8) in `settings.AUDIO_CHANNELS` with loaded sound effects.
- **Authored Tiled Doors & Transitions (`FirstRoom` <-> `UpperHallway`)**:
  - Authored standard interactable `door` object in `assets/tilemaps/FirstRoom.json` (`type="door"`, target `UpperHallway` with spawn `(48, 116)`).
  - Authored corresponding interactable `door` object in `assets/tilemaps/UpperHallway.json` (`type="door"`, target `FirstRoom` with spawn `(440, 120)`) and `stairs` object targeting `lower_hallway` with spawn `(190, 60)`).
  - Replaces hardcoded fallback room dicts with first-class authored Tiled objects across both maps, enabling seamless bidirectional room navigation.
- **Fuse Box Key (`fuse_key`) & Locked Electrical Cabinet**:
  - Authored `fuse_key` item in `assets/tilemaps/DiningRoom.json` and `src/definitions/rooms.py` (`x=120, y=180` in `dining_room`).
  - Added `_draw_fuse_key` archetype in `src/definitions/items.py` (`ITEM_ARCHETYPES`).
  - Added bilingual translations in `src/i18n.py` for item label, locked prompt, unlock prompt, and internal thoughts.
  - The upstairs fuse box (`FirstRoom`) is now locked tight by default, preventing premature access to the wiring minigame and requiring the player to explore downstairs to `dining_room` to retrieve the key.
- **Fuse Box (`fuse_box`) Interactable Object**:
  - Placed authored `fuse_box` interactable in `assets/tilemaps/FirstRoom.json` (`is_collectible=False`, `render_graphic=False`).
  - Added `_draw_fuse_box` archetype in `src/definitions/items.py` (`ITEM_ARCHETYPES`).
  - Extended `TiledLevelLoader.py` to support `props.get("id")`, honor custom `is_collectible` and `render_graphic` properties, and properly configure non-collectible stationary objects.
  - Added Spanish and English localization in `src/i18n.py` for item label, interaction prompt, and Andreas's inspection thought.
  - Handled contextual prompt and interaction in `src/states/game/PlayState.py`, leaving the fuse box interactive for the upcoming wiring minigame.
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
- **Survivor Parchment Notes & `NoteState` modal (Slender-style environmental storytelling)**:
  - Replaced human NPC Elena with collectible survivor notes left on the floor (`note_kitchen`, `note_hallway`).
  - Added `src/states/game/NoteState.py`: pauses the scene and renders an aged parchment sheet with word-wrapped narrative, attached item indicators, and close controls (`E`, `SPACE`, `ESC`).
  - Reading Elena's note in the kitchen yields the Lockpick (`lockpick`) required for the dining room cabinet.
  - Added `_draw_note` rendering archetype in `ITEM_ARCHETYPES`.
- **Tactical Throwable Obstacle Collisions & Noise Distraction**:
  - `ThrowableProjectile` now checks collision against solid room obstacles (`room.get_obstacles()`) instead of flying through walls.
  - Upon impacting a wall, furniture, or landing, the projectile triggers impact audio and calls `monster.hear_noise(p.x, p.y, radius=320.0)`, luring El Silbón to investigate the sound location.
- **El Silbón Stalking & Running Footstep Audio**:
  - Registered dedicated channel `silbon_footsteps` in `settings.AUDIO_CHANNELS`.
  - Dynamically loops `walk_sound.mp3` when El Silbón patrols/investigates and `run_sound.mp3` during chases/berserk, with proximity volume attenuation.
- **Compact HUD Multi-Slot Inventory (Option B)**:
  - Redesigned the inventory indicator into a clean, compact top-right badge (`[Slot/Total] > Item <`), preventing text overlap with `[ESCONDIDO]` and `[EL SILBÓN ESTÁ CERCA]`.
- **Enhanced Typography & Dialogue / Prompt Readability**:
  - Upgraded fonts (`dialogue`, `note_title`, `note_body`, `hud`) and added padded semi-transparent dark borders for prompts and internal thought banners.
- **Player Sprint & Footstep Cadence (`Shift`)**:
  - Bound `KEY_LSHIFT` and `KEY_RSHIFT` to `"run"` in `InputHandler` and registered `RUN` and `STOP_RUN` commands in `src/commands.py`.
  - Player moves at `PLAYER_RUN_SPEED` (135 px/s) while holding Shift, and normal `PLAYER_SPEED` (80 px/s) otherwise.
  - Implemented step cadence tracking in `Player.py` (`step_interval` of 0.25s during sprint vs 0.44s during walking), firing `footstep_taken = True` per physical footstep.
- **Dynamic Acoustic Hearing for El Silbón**:
  - `PlayState.py` evaluates footstep noise at step cadence intervals instead of per-frame random rolls.
  - Sprinting footsteps generate noise with a 75% probability across a 320 px radius, attracting El Silbón to investigate Andreas's position.
  - Walking footsteps generate subtle noise with a 20% probability within a tight 140 px radius.
- **Grid-based A\* pathfinding** (`src/systems/Pathfinding.py`): given a room and a start/goal point, routes around `room.get_obstacles()` (furniture, locked doors) instead of walking straight at the target. Builds a fresh 16px-cell walkability grid per call (rooms here are small enough that this costs well under a millisecond), pads every obstacle by half the entity's width so a path never threads a gap its body couldn't fit through, and collapses the raw cell-by-cell route down to just its turns before returning it. Not yet used by `Monster` -- currently a standalone module, verified independently against both a synthetic obstacle layout and real room data.
- **Generic light-source system** (`src/systems/LightingSystem.py`, built on `gale.stencil.Stencil`): darkness is now driven by a plain list of `Light(x, y, radius, color, intensity, reveal)` entries that `PlayState._collect_lights()` rebuilds every frame, each carved out of the ambient darkness as a flat, hard-edged circle -- `reveal` controls how much darkness that light removes and `intensity` controls how much of its own color gets cast over that same area, independently of each other. The player's flashlight (colorless) and El Silbón's eyes (a constant red glow, active whenever he shares the player's room) are the two lights in use today; any future light source is just another entry in that list, with no change needed to `LightingSystem` itself. New `settings.py` constants `FLASHLIGHT_LIGHT_RADIUS`, `MONSTER_EYE_LIGHT_RADIUS`, and `COLOR_MONSTER_EYES` tune the two without touching the rendering code.
- **New El Silbón Sprite Artwork**:
  - Added dedicated spritesheets for El Silbón (`assets/graphics/characters/monster/`): `monster_idle.png` (64x64 idle pose), `monster_walk.png` (92x92 4-directional walking cycles in down/left/up/right order), and `monster_running.png` (92x92 chase/running cycle).

### Removed
-**HUD for when the player hides**: Removed message for the hud
- **Legacy NPC Code & Cleanup**:
  - Completely deleted `src/entities/NPC.py` and purged all obsolete references and imports across `src/world/Room.py`, `src/world/House.py`, `src/world/TiledLevelLoader.py`, `src/definitions/rooms.py`, and `src/states/game/PlayState.py`.
  - Level layouts now rely exclusively on environmental parchment notes (`note_kitchen`, `note_hallway`) and Tiled object layers for storytelling and item yields.

### Changed
- Added sprites in the tileset
-`i18n.py`: Modified elena's name
-`settings.py`: Modified silbon's light radius (in the future it will be 0)
-`Crowbarminigame.py`: Modified notification radius
- `House.py` rewritten to be data-driven: `_build_tiled_cabin()`/`_build_default_cabin()` now loop over `src/definitions/rooms.py` instead of repeating a near-identical block of Python per room (422 lines -> ~130 lines). Room name aliases (`"FirstRoom"`/`"first_room"`/`"bedroom"`, etc.) are now declared once per room in that data.
- `GameObject`: dropped the `name` constructor parameter (confirmed unread anywhere in the codebase; display names come from `i18n`'s `item_<obj_type>` keys instead).
- `TiledLevelLoader`: the `Interactables` layer now checks `item_type in ITEM_ARCHETYPES` instead of a separate hardcoded tuple + `name_lookup` dict that had to be kept in sync by hand.
- `build_animations()` now returns `(animations, textures)` instead of just `animations`; `Player`/`Monster` track `self.current_texture` (updated inside `change_animation()`), and their `render()`/`render_sprite()` branch on `isinstance(frame, pygame.Rect)` (blit from `settings.TEXTURES[self.current_texture]`) vs. the pre-existing `pygame.Surface` fallback path used when a texture failed to load.
- Removed the redundant `src/states/game/BaseState.py`: it was a 1:1 duplicate of `gale.state.BaseState` (same empty `enter`/`exit`/`on_input`/`update`/`render`), differing only in naming its stored reference `self.state_stack` instead of gale's own `self.state_machine`. Every game state now extends `gale.state.BaseState` directly, and every `self.state_stack`/`state_stack` reference in the 6 game states was renamed to `self.state_machine`/`state_machine` to match.
- Player gained a `held` dict (`move_left/right/up/down`) set by the Move/StopMove commands and resolved into actual movement by the renamed `Player.update_movement(obstacles, dt)` (previously `update_movement_from_input(pressed_keys, obstacles, dt)`, which took a dict `PlayState` built by hand from raw input events).
- `Player.interact_requested`/`throw_requested` are edge-triggered intents set by the `INTERACT`/`THROW` commands and consumed once per frame by `PlayState.update()` (mirrors `sword_requested`/`interact_requested` in princess's `Player`), since resolving them needs `PlayState`'s `house`/`monster`/`projectiles`. Flashlight/cycle-item/slot-selection commands call the corresponding `Player` method directly, since there's no further resolution step needed for those.
- `PlayState.on_input` no longer hand-rolls a `pressed_inputs` dict or an `elif` chain per action id; it now only handles state-stack navigation (`pause`/`objectives`) itself and forwards everything else to `self.player.command_bindings.dispatch(...)`.
- `TEXTURES` and `SOUNDS` in `settings.py` rewritten from empty-dict-plus-helper-function (`_load_image()`/`_load_sound()`, each doing a `Path.exists()` check + try/except + returning `None` on failure) to plain dict literals with direct `pygame.image.load(...)`/`pygame.mixer.Sound(...)` calls, matching the structure both `06-princess` and `07-ultimate_fantasy` already use. `FRAMES` similarly dropped its `_generate_frames()` wrapper in favor of calling `frames.generate_frames(TEXTURES["..."], w, h)` directly, since a texture can no longer be `None` by the time `FRAMES` is built. `FONTS` was deliberately left on `pygame.font.SysFont(...)` (not switched to a bundled `.ttf` like the other two projects), since `assets/fonts/` has no real font file yet.
- `MONSTER_ANIMATIONS` retargeted from the old `silbon_walk`/`silbon_idle` textures to the definitive `monster_walk`/`monster_idle` art: `monster_walk` is one 8-col x 4-row sheet in **down, left, up, right** row order (different from the old sheet's up/left/right/down, confirmed by rendering each row separately), and `monster_idle` is a single 4-frame row with no per-direction variants, so the idle animation is now just `"idle"` instead of `idle-down/up/left/right`. `monster_running` is loaded but not yet wired into any state.
- `Monster.render_sprite()` no longer positions the sprite via a fixed offset constant: since `monster_idle` (64x64) and `monster_walk`/`monster_running` (92x92) are different sizes, a fixed offset made the monster visibly jump position when switching between idle and walking. It now centers horizontally and anchors the bottom a fixed `MONSTER_SPRITE_BOTTOM_MARGIN` (8px) below the collision box, computed from each frame's actual size. `MONSTER_SPRITE_SIZE` (the solid-color placeholder shown only if a texture fails to load) updated to `(92, 92)` to match.
- **Survival, Movement, and Acoustic Balance Adjustments**:
  - `PLAYER_SPEED` nerfed from `90.0` px/s to `69.0` px/s (-33%) and `PLAYER_RUN_SPEED` from `135.0` px/s to `75.0` px/s (-44%). Andreas is now strictly slower than El Silbón (Patrol: 70 px/s, Chase: 105 px/s, Berserk: 300 px/s), ensuring sprinting is used for tactical repositioning to hiding spots rather than outrunning the monster in straight corridors.
  - `MONSTER_BERSERK_SPEED` boosted from `160.0` px/s to `300.0` px/s (+87.5%), making an enraged El Silbón extraordinarily fast and lethal.
  - `THROW_STUN_CHANCE` increased from 75% to 80% and `THROW_BERSERK_CHANCE` lowered from 25% to 20% to balance the extreme danger of the new berserk speed.
  - `BATTERY_DRAIN_RATE` tripled from `0.3` %/s to `0.9` %/s, enforcing tighter flashlight resource management and darker exploration.
  - Player acoustic footprint in `PlayState.py` significantly amplified:
    - Running footsteps noise chance increased from 75% to 90%, with detection radius expanded from 320 px to 600 px (alerting El Silbón across multiple adjacent rooms).
    - Walking footsteps noise chance increased from 20% to 45%, with detection radius increased from 140 px to 200 px.
  - `AudioManager.py`: Whistle audio distance modulation `max_range` extended from 500 px to 700 px to cover the expanded cabin layout and provide smoother audio proximity cues.
- **Level Collision & Tilemap Polish**:
  - `MasterBedroom.json`: adjusted collision obstacle hitbox height (12 -> 9 px) and vertical alignment ($y = 63.3 \to 66.3$) near bedroom furniture to eliminate player collision snagging.
  - `UpperHallway.json`: corrected tile ID assignment on the upper hallway floor boundary.

### Fixed
- **Minigame Completion `AttributeError` in `PlayState.update()`**:
  - When completing or exiting a minigame (such as `LockpickMinigame`), `BaseMinigame.close()` set `play_state.active_minigame = None`. Line 279 then attempted `not self.active_minigame.is_active`, raising `AttributeError: 'NoneType' object has no attribute 'is_active'`.
  - Cached the active minigame in a local variable `current_minigame` during `update(dt)` to safely evaluate completion and execute cleanup without exceptions.
- **`Player.sync_movement_keys()` Robust Key Retrieval**:
  - Added a defensive key lookup helper `get_k` in `sync_movement_keys()` to support both standard Pygame `ScancodeWrapper` sequences and dictionary objects without triggering `KeyError`.
- **El Silbón Footstep Audio Persisting on Game Over**:
  - When Andreas was caught and killed by El Silbón, transitioning to `GameOverState` left the looping footstep audio (`silbon_footsteps`) and any active minigame sounds playing endlessly on the Game Over screen.
  - Added immediate channel silencing (`pygame.mixer.Channel(AUDIO_CHANNELS["silbon_footsteps"]).stop()` and `AUDIO_CHANNELS["minigame"]`) in `GameOverState.enter()` and `PlayState.update()`, ensuring complete audio cleanup upon death.
- **Player stuck moving or sprinting after closing modal states (`NoteState`, `PauseState`, `ObjectiveState`)**:
  - Because `gale.state.StateStack` routes `on_input()` exclusively to the top state on the stack, key releases performed while reading notes or pausing were swallowed by the modal and never delivered to `PlayState`. This left `Player.held` directional keys and `Player.is_running` permanently true upon resuming.
  - Added `Player.clear_movement()` to halt velocities and clear all movement intents immediately when any modal state is pushed.
  - Implemented `Player.sync_movement_keys()` querying physical keyboard states via `pygame.key.get_pressed()`, wired through an `exit()` lifecycle hook on all modal states (`NoteState`, `PauseState`, `ObjectiveState`) upon closing to guarantee clean resumption.
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
- **Monster rendering as a solid-color fallback rectangle**: `src/definitions/entity.py`'s `MONSTER_ANIMATIONS` still referenced the retired `silbon_walk`/`silbon_idle` texture ids after they were replaced with `monster_walk`/`monster_idle`/`monster_running` in `settings.TEXTURES`, so `build_animations()` fell through to `MONSTER_FALLBACK_COLOR` for every monster animation. Retargeted to the current textures (see Changed above).

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