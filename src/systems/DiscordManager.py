"""
Discord Rich Presence Integration for 'El Silbón: Nightmare at the Cabin'.
Uses pypresence running on a non-blocking background daemon thread.
Safely ignores connection errors if Discord is closed or offline.
"""

import threading
import time
from typing import Optional

try:
    from pypresence import Presence
    PYPRESENCE_AVAILABLE = True
except ImportError:
    PYPRESENCE_AVAILABLE = False

CLIENT_ID = "1561900878196252766"


class DiscordRPCManager:
    def __init__(self, client_id: str = CLIENT_ID) -> None:
        self.client_id = client_id
        self.rpc: Optional[Presence] = None
        self.is_connected = False
        self.running = True

        self.start_timestamp: Optional[int] = int(time.time())
        self.details = "En el menú principal"
        self.state = "Preparándose para entrar"
        self.large_image = "silbon_main"
        self.large_text = "El Silbón: Nightmare at the Cabin"
        self.small_image: Optional[str] = None
        self.small_text: Optional[str] = None

        self._dirty = True
        self._lock = threading.Lock()

        if PYPRESENCE_AVAILABLE:
            self.thread = threading.Thread(
                target=self._worker_loop, daemon=True, name="DiscordRPCThread"
            )
            self.thread.start()

    def _worker_loop(self) -> None:
        """Background thread handling Discord RPC connection and updates."""
        while self.running:
            if not self.is_connected:
                try:
                    self.rpc = Presence(self.client_id)
                    self.rpc.connect()
                    self.is_connected = True
                    self._dirty = True
                except Exception:
                    self.is_connected = False
                    self.rpc = None
                    time.sleep(15)
                    continue

            # Connected: check if update is needed
            with self._lock:
                should_update = self._dirty
                details = self.details
                state = self.state
                large_image = self.large_image
                large_text = self.large_text
                small_image = self.small_image
                small_text = self.small_text
                start_ts = self.start_timestamp
                self._dirty = False

            if should_update and self.rpc:
                try:
                    payload = {
                        "details": details[:128] if details else None,
                        "state": state[:128] if state else None,
                        "large_image": large_image,
                        "large_text": large_text[:128] if large_text else None,
                    }
                    if small_image:
                        payload["small_image"] = small_image
                        if small_text:
                            payload["small_text"] = small_text[:128]
                    if start_ts:
                        payload["start"] = start_ts

                    self.rpc.update(**payload)
                except Exception:
                    # Connection dropped or Discord closed
                    self.is_connected = False
                    self.rpc = None
                    time.sleep(5)
                    continue

            # Sleep between loop iterations to respect Discord rate limits
            time.sleep(4)

    def update(
        self,
        details: Optional[str] = None,
        state: Optional[str] = None,
        large_image: Optional[str] = "silbon_main",
        large_text: Optional[str] = "El Silbón: Nightmare at the Cabin",
        small_image: Optional[str] = None,
        small_text: Optional[str] = None,
        reset_timer: bool = False,
    ) -> None:
        """Thread-safe update of the presence payload."""
        with self._lock:
            changed = False
            if reset_timer:
                self.start_timestamp = int(time.time())
                changed = True
            if details is not None and details != self.details:
                self.details = details
                changed = True
            if state is not None and state != self.state:
                self.state = state
                changed = True
            if large_image is not None and large_image != self.large_image:
                self.large_image = large_image
                changed = True
            if large_text is not None and large_text != self.large_text:
                self.large_text = large_text
                changed = True
            if small_image != self.small_image:
                self.small_image = small_image
                changed = True
            if small_text != self.small_text:
                self.small_text = small_text
                changed = True

            if changed:
                self._dirty = True

    def close(self) -> None:
        self.running = False
        if self.rpc and self.is_connected:
            try:
                self.rpc.close()
            except Exception:
                pass


# Global singleton instance for easy import and access across game states
discord_rpc = DiscordRPCManager()
