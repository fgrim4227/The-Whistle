"""
Interactions module: strategy/dispatcher dictionaries mapping interactable types
to their respective interaction action handlers and HUD prompt getters.
Decouples PlayState from item-specific and door-specific interaction branching.
"""

import math
from typing import Any, Callable, Dict

from src.i18n import t
from src.states.game.NoteState import NoteState
from src.states.game.VictoryState import VictoryState
from src.minigames.MinigameFactory import MinigameFactory


# =========================================================================
# Item Action Handlers
# =========================================================================

def interact_battery(play_state: Any, item: Any) -> None:
    """Recharges Andreas's flashlight battery."""
    item.is_picked = True
    play_state.player.recharge_battery()
    play_state.player.set_thought("thought_dark", 3.0)


def interact_cabinet(play_state: Any, item: Any) -> None:
    """Vintage cabinet in DiningRoom requiring lockpick minigame."""
    if play_state.player.has_item("lockpick"):
        def on_cabinet_unlocked():
            item.is_picked = True
            play_state.player.add_item("old_key")
            play_state.player.set_thought("thought_got_old_key", 4.5)

        play_state.active_minigame = MinigameFactory.create(
            "lockpick",
            play_state,
            target_object=item,
            on_success=on_cabinet_unlocked,
        )
    else:
        play_state.player.set_thought("prompt_cabinet_locked", 3.5)


def interact_safe(play_state: Any, item: Any) -> None:
    """Master Bedroom safe requiring rotary dial acoustic minigame."""
    def on_safe_unlocked():
        item.is_picked = True
        play_state.player.add_item("key")
        play_state.objectives_progress["key"] = True
        play_state.player.set_thought("thought_got_exit_key", 4.5)

    play_state.active_minigame = MinigameFactory.create(
        "safe",
        play_state,
        target_object=item,
        on_success=on_safe_unlocked,
    )


def interact_note(play_state: Any, item: Any) -> None:
    """Survivor parchment note modal."""
    note_id = getattr(item, "note_id", "note_kitchen")
    title_key = f"{note_id}_title"
    body_key = f"{note_id}_body"
    attached_item = getattr(item, "yields", None)

    play_state.player.clear_movement()

    def on_note_closed():
        if attached_item and not item.is_picked:
            item.is_picked = True
            play_state.player.add_item(attached_item)
            if attached_item == "lockpick":
                play_state.player.set_thought("thought_note_got_lockpick", 4.5)
        play_state.player.sync_movement_keys()

    play_state.state_machine.push(
        NoteState(
            play_state.state_machine,
            title_key,
            body_key,
            attached_item=attached_item if not item.is_picked else None,
            on_close=on_note_closed,
        )
    )


def interact_fuse_box(play_state: Any, item: Any) -> None:
    """FirstRoom electrical fuse box requiring wiring minigame and fuse_key."""
    if getattr(play_state.house, "power_restored", False):
        play_state.player.set_thought("thought_fuse_box", 3.5)
        return

    if not play_state.player.has_item("fuse_key"):
        play_state.player.set_thought("thought_fuse_box_locked", 4.0)
        return

    def on_fuse_box_powered():
        setattr(play_state.house, "power_restored", True)

    play_state.active_minigame = MinigameFactory.create(
        "fuse_box",
        play_state,
        target_object=item,
        on_success=on_fuse_box_powered,
    )


def interact_fuse_key(play_state: Any, item: Any) -> None:
    """Collects the fuse box key."""
    item.is_picked = True
    play_state.player.add_item("fuse_key")
    play_state.player.set_thought("thought_got_fuse_key", 4.5)


def interact_default_collectible(play_state: Any, item: Any) -> None:
    """Default pickup handler for items and tools."""
    item.is_picked = True
    play_state.player.add_item(item.obj_type)
    if item.obj_type == "crowbar":
        play_state.objectives_progress["crowbar"] = True
    elif item.obj_type == "key":
        play_state.objectives_progress["key"] = True


# Dispatch Table for Item Interactions
ITEM_INTERACTIONS: Dict[str, Callable[[Any, Any], None]] = {
    "battery": interact_battery,
    "cabinet": interact_cabinet,
    "safe": interact_safe,
    "note": interact_note,
    "fuse_box": interact_fuse_box,
    "fuse_key": interact_fuse_key,
}


# =========================================================================
# Item Prompt Formatters
# =========================================================================

def prompt_cabinet(play_state: Any, item: Any) -> str:
    if play_state.player.has_item("lockpick"):
        return t("prompt_pick_cabinet")
    return t("prompt_cabinet_locked")


def prompt_safe(play_state: Any, item: Any) -> str:
    return t("prompt_open_safe")


def prompt_note(play_state: Any, item: Any) -> str:
    return t("prompt_read_note")


def prompt_fuse_box(play_state: Any, item: Any) -> str:
    if getattr(play_state.house, "power_restored", False):
        return t("prompt_fuse_box")
    elif not play_state.player.has_item("fuse_key"):
        return t("prompt_fuse_box_locked")
    return t("prompt_open_fuse_box")


def get_default_item_prompt(play_state: Any, item: Any) -> str:
    item_label = t(f"item_{item.obj_type}")
    return f"{t('prompt_pickup')} ({item_label})"


# Dispatch Table for Contextual Prompts
ITEM_PROMPTS: Dict[str, Callable[[Any, Any], str]] = {
    "cabinet": prompt_cabinet,
    "safe": prompt_safe,
    "note": prompt_note,
    "fuse_box": prompt_fuse_box,
}


# =========================================================================
# Door Interactions and Prompts
# =========================================================================

def handle_door_interaction(play_state: Any, door: Any) -> None:
    """Handles unlocking, unbolting, prying planks, and room navigation."""
    room = play_state.house.current_room
    if not room:
        return

    # 1. Unboltable passage between LivingRoom and DiningRoom
    if door.is_bolted:
        if room.name in ("living_room", "LivingRoom"):
            door.unbolt()
            # Also unbolt reverse door in dining_room to complete the continuous loop
            dining_room = play_state.house.rooms.get("dining_room")
            if dining_room:
                for d in dining_room.doors:
                    if d.target_room_name in ("living_room", "LivingRoom"):
                        d.unbolt()
            play_state.player.set_thought("thought_unbolted", 4.0)
        else:
            play_state.player.set_thought("prompt_door_bolted", 3.5)
        return

    # 2. Barred door requiring crowbar minigame
    if door.is_barred:
        if play_state.player.has_item("crowbar"):
            def on_plank_pried():
                if not door.is_barred:
                    play_state.objectives_progress["crowbar"] = True
                    play_state.player.set_thought("thought_door_unbarred", 3.5)
                    target_rm = play_state.house.rooms.get(door.target_room_name)
                    if target_rm:
                        for d in target_rm.doors:
                            if d.target_room_name in (room.name, room.display_name):
                                d.unbar()

            play_state.active_minigame = MinigameFactory.create(
                "crowbar",
                play_state,
                target_object=door,
                on_success=on_plank_pried,
            )
        else:
            play_state.player.set_thought("prompt_door_barred", 3.5)
        return

    # 3. Exit door: sequential security validation (Power/Sensor -> Key/Padlock -> Victory)
    if door.is_exit_door:
        # Step 1: Electronic security sensor MUST be deactivated by restoring power first
        if not getattr(play_state.house, "power_restored", False):
            play_state.player.set_thought("thought_exit_no_power", 4.0)
            return

        # Step 2: Once sensor is disabled, padlock and chains must be unlocked with the forest key
        if door.is_locked:
            if door.can_open(play_state.player):
                door.unlock()
                play_state.objectives_progress["escape"] = True
                play_state.state_machine.push(VictoryState(play_state.state_machine))
                return
            else:
                play_state.player.set_thought("thought_exit_locked_chains", 3.5)
                return

        # Step 3: If already unlocked and powered, escape directly
        play_state.objectives_progress["escape"] = True
        play_state.state_machine.push(VictoryState(play_state.state_machine))
        return

    # 4. Standard locked door requiring key (e.g. Master Bedroom)
    if door.is_locked:
        if door.can_open(play_state.player):
            door.unlock()
            target_rm = play_state.house.rooms.get(door.target_room_name)
            if target_rm:
                for d in target_rm.doors:
                    if d.target_room_name in (room.name, room.display_name):
                        d.unlock()
        else:
            play_state.player.set_thought("prompt_door_locked", 3.0)
        return

    # 5. Walk through door into target room
    play_state.house.change_room(door.target_room_name, door.target_spawn_x, door.target_spawn_y, play_state.player)
    play_state.objectives_progress["explore"] = True


def get_door_prompt(play_state: Any, door: Any) -> str:
    """Returns the contextual prompt string for a door."""
    room = play_state.house.current_room

    # Check if El Silbón is lurking on the other side of this door
    is_danger = False
    if play_state.monster.current_room_name == door.target_room_name:
        mx, my = play_state.monster.get_center()
        m_dist = math.hypot(mx - door.target_spawn_x, my - door.target_spawn_y)
        if m_dist < 180.0:
            is_danger = True

    if door.is_bolted:
        if room and room.name in ("living_room", "LivingRoom"):
            return t("prompt_unbolt_door")
        return t("prompt_door_bolted")
    elif door.is_barred:
        return t("prompt_door_barred")
    elif door.is_exit_door and not getattr(play_state.house, "power_restored", False):
        return t("prompt_exit_sensor_active")
    elif door.is_locked:
        if door.can_open(play_state.player):
            return t("prompt_open_door")
        return t("prompt_door_locked")
    elif is_danger:
        return t("prompt_open_door_danger")
    elif getattr(door, "is_stairs", False):
        return t("prompt_use_stairs")
    return t("prompt_open_door")
