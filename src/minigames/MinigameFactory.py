"""
MinigameFactory: Factory pattern implementation for creating minigames.
Decouples interaction definitions and gameplay states from concrete minigame classes.
"""

from typing import Any, Callable, Dict, Optional, Type
from src.minigames.BaseMinigame import BaseMinigame
from src.minigames.LockpickMinigame import LockpickMinigame
from src.minigames.SafeMinigame import SafeMinigame
from src.minigames.CrowbarMinigame import CrowbarMinigame
from src.minigames.FuseBoxMinigame import FuseBoxMinigame
from src.minigames.KeypadMinigame import KeypadMinigame


class MinigameFactory:
    """
    Factory for creating real-time overlay minigames by identifier.
    Decouples callers from specific class constructors and imports.
    """

    _registry: Dict[str, Type[BaseMinigame]] = {
        "lockpick": LockpickMinigame,
        "safe": SafeMinigame,
        "crowbar": CrowbarMinigame,
        "fuse_box": FuseBoxMinigame,
        "keypad": KeypadMinigame,
    }

    @classmethod
    def create(
        cls,
        minigame_type: str,
        play_state: Any,
        target_object: Any = None,
        on_success: Optional[Callable[[], None]] = None,
        on_fail: Optional[Callable[[], None]] = None,
        **kwargs: Any,
    ) -> BaseMinigame:
        """
        Creates and returns a newly instantiated minigame.
        
        Args:
            minigame_type: Type identifier (e.g. 'lockpick', 'safe', 'crowbar', 'fuse_box').
            play_state: Reference to the active PlayState.
            target_object: The interactive GameObject or Door associated with this minigame.
            on_success: Callback triggered when the minigame is won.
            on_fail: Callback triggered if the minigame fails.
            **kwargs: Extra parameters passed directly to the specific minigame constructor
                      (e.g., target_angle, combination_numbers).
        """
        key = minigame_type.lower()
        minigame_cls = cls._registry.get(key)
        if not minigame_cls:
            raise ValueError(
                f"Unknown minigame type: '{minigame_type}'. Registered types: {list(cls._registry.keys())}"
            )

        # CrowbarMinigame accepts target_door (or target_object)
        if issubclass(minigame_cls, CrowbarMinigame):
            return minigame_cls(
                play_state,
                target_door=target_object,
                on_success=on_success,
                on_fail=on_fail,
                **kwargs,
            )

        return minigame_cls(
            play_state,
            target_object=target_object,
            on_success=on_success,
            on_fail=on_fail,
            **kwargs,
        )
