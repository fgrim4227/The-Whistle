# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-09-11

### Added
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