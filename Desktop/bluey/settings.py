"""Preferences are non-secret JSON; credentials belong in the OS keyring."""
from __future__ import annotations

import json
import os
import math
import tempfile
import threading
from pathlib import Path
from dataclasses import dataclass, asdict

from platformdirs import user_config_path, user_log_path


# Windows does not permit overlapping replacements of an open destination.
# Serialize in-process saves while unique temporary files protect each writer.
_SAVE_LOCK = threading.Lock()


@dataclass
class Preferences:
    cursor_size: int = 72
    phone_position: float = 0.5
    follow_mouse: bool = True
    show_cursor: bool = True
    glow: bool = False
    reduced_motion: bool = False
    mood: str = "listening"
    personality: str = ""
    # Consent to computer actions is session-scoped and deliberately not persisted.

    @classmethod
    def load(cls, path: Path | None = None) -> "Preferences":
        path = path or config_file()
        result = cls()
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                return result
            for key, default in asdict(result).items():
                value = raw.get(key, default)
                if key=="phone_position" and type(value) in (int,float) and math.isfinite(value):
                    result.phone_position=float(value)
                elif type(value) is type(default) and (not isinstance(value,float) or math.isfinite(value)):
                    setattr(result, key, value)
            result.cursor_size = max(48, min(120, result.cursor_size))
            result.phone_position = max(0.0, min(1.0, result.phone_position))
            if result.mood not in MOODS:
                result.mood = "listening"
            result.personality = result.personality[:8000]
        except (OSError, ValueError, TypeError):
            pass
        return result

    def save(self, path: Path | None = None) -> None:
        with _SAVE_LOCK:
            path = path or config_file()
            path.parent.mkdir(parents=True, exist_ok=True)
            # A unique sibling keeps concurrent saves from sharing a temporary file.
            # Flush before replace; on failure the previous settings remain intact.
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                                 prefix=path.name + ".", suffix=".tmp", delete=False) as stream:
                    temporary = Path(stream.name)
                    json.dump(asdict(self), stream, indent=2, allow_nan=False)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.replace(temporary, path)
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)


MOODS = ("listening", "resting", "thinking", "talking", "pointing", "happy", "sleepy")


def clamp_cursor_size(value: int) -> int:
    """Cursor size is always kept between 48 and 120 pixels."""
    return max(48, min(120, int(value)))


def clamp_phone_position(value: float) -> float:
    """Phone position is a fraction of the screen width, 0.0 to 1.0."""
    return max(0.0, min(1.0, float(value)))


def provider_for_key(key: str) -> str:
    """Which service a saved key belongs to. Groq keys start with `gsk_`."""
    return "groq" if key.strip().startswith("gsk_") else "openai"


def config_file() -> Path:
    """Where the desktop settings live on this platform."""
    return user_config_path("BlueyDesktop", appauthor=False) / "settings.json"


def log_file() -> Path:
    """Where the desktop writes its log, so problems can be looked at afterwards."""
    return user_log_path("BlueyDesktop", appauthor=False) / "bluey-desktop.log"


class Credentials:
    """No plaintext fallback: when keyring is unavailable, keep a key in memory."""
    service = "BlueyDesktop"
    account = "openai-api-key"

    def __init__(self, use_keyring: bool = True):
        self._key = ""
        self.persisted = False
        self.use_keyring = use_keyring
        if use_keyring:
            try:
                import keyring
                self._key = keyring.get_password(self.service, self.account) or ""
                self.persisted = bool(self._key)
            except Exception:
                pass

    def get(self) -> str:
        return self._key

    def set(self, key: str) -> bool:
        key = key.strip()
        if not key or len(key) > 1024 or any(c.isspace() or ord(c)<33 or ord(c)>126 for c in key):
            raise ValueError("Paste a complete API key without spaces.")
        self._key = key
        self.persisted = False
        if self.use_keyring:
            try:
                import keyring
                keyring.set_password(self.service, self.account, key)
                self.persisted = True
            except Exception:
                pass
        return self.persisted

    def clear(self) -> None:
        if self.use_keyring:
            try:
                import keyring
                if keyring.get_password(self.service, self.account):
                    keyring.delete_password(self.service, self.account)
            except Exception as exc:
                raise RuntimeError("The credential vault is unavailable. Unlock it before removing the saved key.") from exc
        self._key = ""
        self.persisted = False
