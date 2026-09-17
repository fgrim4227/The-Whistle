"""
Interactions module: strategy/dispatcher dictionaries mapping interactable types
to their respective interaction action handlers and HUD prompt getters.
Decouples PlayState from item-specific and door-specific interaction branching.
"""

import math
from typing import Any, Callable, Dict, Optional, Set

import settings
from src.i18n import t
from src.states.game.NoteState import NoteState
from src.states.game.VictoryState import VictoryState
from src.minigames.MinigameFactory import MinigameFactory
from src.world.GameObject import GameObject


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
            play_state.objectives_progress["dining_cabinet"] = True
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
        play_state.objectives_progress["master_safe"] = True
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
    play_state.objectives_progress["explore"] = True

    def on_note_closed():
        if attached_item and not item.is_picked:
            item.is_picked = True
            play_state.player.add_item(attached_item)
            if attached_item == "lockpick":
                play_state.objectives_progress["kitchen_lockpick"] = True
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
        play_state.objectives_progress["fuse_power"] = True

    play_state.active_minigame = MinigameFactory.create(
        "fuse_box",
        play_state,
        target_object=item,
        on_success=on_fuse_box_powered,
    )


def _collect_with_granny_swap(play_state: Any, item: Any, new_item_type: str) -> None:
    player = play_state.player
    room = play_state.house.current_room

    # Si ya tiene un objeto en mano distinto, lo suelta en el suelo de la habitación actual
    if player.equipped_item and player.equipped_item != new_item_type:
        old_item = player.equipped_item
        player.remove_item(old_item)
        dropped_obj = GameObject(
            obj_type=old_item,
            x=player.x,
            y=player.y,
            width=16,
            height=16,
            is_collectible=True,
            render_graphic=True,
        )
        room.items.append(dropped_obj)

    item.is_picked = True
    player.add_item(new_item_type)


def interact_fuse_key(play_state: Any, item: Any) -> None:
    """Collects the fuse box key with Granny swap."""
    _collect_with_granny_swap(play_state, item, "fuse_key")
    play_state.player.set_thought("thought_got_fuse_key", 4.5)


def interact_default_collectible(play_state: Any, item: Any) -> None:
    """Default pickup handler for items and tools with Granny swap."""
    _collect_with_granny_swap(play_state, item, item.obj_type)
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

def get_reciprocal_door(house: Any, current_room: Any, door: Any) -> Optional[Any]:
    """Finds the corresponding door in target_room leading back to current_room."""
    if not house or not current_room or not door:
        return None
    target_rm = house.rooms.get(door.target_room_name)
    if not target_rm:
        return None

    names = {current_room.name}
    if hasattr(current_room, "display_name") and current_room.display_name:
        names.add(current_room.display_name)
    for k, v in getattr(house, "rooms", {}).items():
        if v is current_room:
            names.add(k)

    for d in getattr(target_rm, "doors", []):
        if d.target_room_name in names:
            return d
    return None


def is_reciprocal_door_barred(house: Any, current_room: Any, door: Any) -> bool:
    """Returns True if the matching door on the opposite side has barricaded planks."""
    reciprocal = get_reciprocal_door(house, current_room, door)
    if reciprocal and (reciprocal.is_barred or getattr(reciprocal, "planks_remaining", 0) > 0):
        return True
    return False


def is_passage_door(door: Any, room: Any) -> bool:
    """Checks if a door belongs to the secret passage shortcut network."""
    if getattr(door, "lock_type", None) == "keypad" or getattr(door, "is_passcode_locked", False):
        return True
    rname = getattr(room, "name", "").lower()
    tname = getattr(door, "target_room_name", "").lower()
    passage_rooms = {"storage_room", "master_bedroom", "secret_passage", "secretpassage"}
    if rname in passage_rooms and tname in passage_rooms:
        if "secret" in rname or "secret" in tname or "passage" in rname or "passage" in tname:
            return True
    return False


def unlock_secret_passage_network(house: Any, start_door: Any, visited_doors: Optional[Set[Any]] = None) -> None:
    """
    Recursively unlocks all doors belonging to the secret passage shortcut network
    across connected rooms (Master Bedroom, Secret Passage, Storage Room).
    """
    if visited_doors is None:
        visited_doors = set()

    if start_door in visited_doors:
        return
    visited_doors.add(start_door)

    # Unlock this door
    start_door.is_bolted = False
    start_door.is_locked = False
    start_door.is_barred = False
    setattr(start_door, "unlocked", True)
    setattr(start_door, "is_passcode_locked", False)

    # Find the target room
    target_rm = house.rooms.get(start_door.target_room_name)
    if not target_rm:
        return

    passage_room_names = {"master_bedroom", "storage_room", "secret_passage", "secretpassage"}

    # Recurse through all doors in target room connecting to passage rooms
    for d in getattr(target_rm, "doors", []):
        tname = getattr(d, "target_room_name", "").lower()
        if tname in passage_room_names or getattr(d, "lock_type", None) == "keypad":
            unlock_secret_passage_network(house, d, visited_doors)


def handle_door_interaction(play_state: Any, door: Any) -> None:
    """Handles unlocking, unbolting, prying planks, and room navigation."""
    room = play_state.house.current_room
    if not room:
        return

    # Check if door is barred with planks on the opposite side
    if is_reciprocal_door_barred(play_state.house, room, door):
        play_state.player.set_thought("thought_door_barred_other_side", 4.0)
        return

    # 0. Secret Passage keypad / combination security door
    if is_passage_door(door, room) and not getattr(door, "unlocked", False) and (door.is_bolted or getattr(door, "is_passcode_locked", False)):
        def on_passcode_success():
            unlock_secret_passage_network(play_state.house, door)
            play_state.player.set_thought("thought_passage_unlocked", 4.5)
            settings.play_sound("minigame_unlock_click", loops=0, volume=1.0, channel_name="sfx")

        play_state.active_minigame = MinigameFactory.create(
            "keypad",
            play_state,
            target_object=door,
            passcode=getattr(door, "passcode", "1973"),
            on_success=on_passcode_success,
        )
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
                    reciprocal = get_reciprocal_door(play_state.house, room, door)
                    if reciprocal:
                        reciprocal.unbar()
                        if getattr(reciprocal, "is_bolted", False):
                            reciprocal.unbolt()
                    target_rm = play_state.house.rooms.get(door.target_room_name)
                    if target_rm:
                        for d in target_rm.doors:
                            if d.target_room_name in (room.name, room.display_name):
                                d.unbar()
                                if getattr(d, "is_bolted", False):
                                    d.unbolt()

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
    reciprocal = get_reciprocal_door(play_state.house, room, door)
    is_door_locked = door.is_locked or (reciprocal is not None and reciprocal.is_locked)
    if is_door_locked:
        req_key = door.required_key if door.is_locked else (reciprocal.required_key if reciprocal else "key")
        can_open = False
        if hasattr(play_state.player, "has_item"):
            can_open = play_state.player.has_item(req_key)
        else:
            can_open = (play_state.player.equipped_item == req_key)

        if can_open:
            door.unlock()
            if reciprocal:
                reciprocal.unlock()
            try:
                settings.play_sound("minigame_unlock_click", loops=0, volume=0.8)
            except Exception:
                pass
        else:
            play_state.player.set_thought("prompt_door_locked", 3.0)
        return

    # 5. Walk through door into target room
    play_state.house.change_room(door.target_room_name, door.target_spawn_x, door.target_spawn_y, play_state.player)
    play_state.objectives_progress["explore"] = True


def get_door_prompt(play_state: Any, door: Any) -> str:
    """Returns the contextual prompt string for a door."""
    room = play_state.house.current_room

    if door.is_barred:
        return t("prompt_door_barred")
    elif is_reciprocal_door_barred(play_state.house, room, door):
        return t("prompt_door_barred_other_side")
    elif is_passage_door(door, room) and not getattr(door, "unlocked", False) and (door.is_bolted or getattr(door, "is_passcode_locked", False)):
        return t("prompt_keypad")
    elif door.is_bolted:
        if room and room.name in ("living_room", "LivingRoom"):
            return t("prompt_unbolt_door")
        return t("prompt_door_bolted")
    elif door.is_exit_door and not getattr(play_state.house, "power_restored", False):
        return t("prompt_exit_sensor_active")
    else:
        reciprocal = get_reciprocal_door(play_state.house, room, door)
        if door.is_locked or (reciprocal is not None and reciprocal.is_locked):
            req_key = door.required_key if door.is_locked else (reciprocal.required_key if reciprocal else "key")
            can_open = False
            if hasattr(play_state.player, "has_item"):
                can_open = play_state.player.has_item(req_key)
            else:
                can_open = (play_state.player.equipped_item == req_key)
            if can_open:
                return t("prompt_open_door")
            return t("prompt_door_locked")
    if getattr(door, "is_stairs", False):
        return t("prompt_use_stairs")
    return t("prompt_open_door")
