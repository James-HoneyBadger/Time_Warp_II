"""Settings persistence for Time Warp II."""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

SETTINGS_FILE = Path(
    os.environ.get("TEMPLECODE_SETTINGS_DIR", str(Path.home()))
) / ".templecode_settings.json"

MAX_RECENT = 10

DEFAULTS: dict[str, Any] = {
    "theme": "dark",
    "font_size": "medium",
    "font_family": "Courier",
    "recent_files": [],
    "auto_dark": True,
    "exec_speed": 0,
    "turtle_speed": 0,
    "geometry": "",
}

# Lazy-imported at validation time to avoid circular imports
_VALID_THEMES: set[str] | None = None
_VALID_FONT_SIZES: set[str] | None = None


def _valid_themes() -> set[str]:
    global _VALID_THEMES
    if _VALID_THEMES is None:
        try:
            from core.config import THEMES
            _VALID_THEMES = set(THEMES.keys())
        except Exception:
            _VALID_THEMES = {"dark", "light"}
    return _VALID_THEMES


def _valid_font_sizes() -> set[str]:
    global _VALID_FONT_SIZES
    if _VALID_FONT_SIZES is None:
        try:
            from core.config import FONT_SIZES
            _VALID_FONT_SIZES = set(FONT_SIZES.keys())
        except Exception:
            _VALID_FONT_SIZES = {"medium"}
    return _VALID_FONT_SIZES


def _validate(data: dict[str, Any]) -> dict[str, Any]:
    """Return a sanitised copy of *data*, falling back to defaults."""
    out = dict(DEFAULTS)
    out.update(data)

    # Theme must be known
    if out["theme"] not in _valid_themes():
        log.warning("Unknown theme %r, falling back to 'dark'", out["theme"])
        out["theme"] = DEFAULTS["theme"]

    # Font size must be known
    if out["font_size"] not in _valid_font_sizes():
        log.warning("Unknown font_size %r, falling back to 'medium'", out["font_size"])
        out["font_size"] = DEFAULTS["font_size"]

    # Speed ranges
    out["exec_speed"] = max(0, min(int(out.get("exec_speed", 0)), 500))
    out["turtle_speed"] = max(0, min(int(out.get("turtle_speed", 0)), 200))

    # Boolean
    out["auto_dark"] = bool(out.get("auto_dark", True))

    # Recent files — must be list of strings, prune missing
    rf = out.get("recent_files", [])
    if not isinstance(rf, list):
        rf = []
    out["recent_files"] = [f for f in rf if isinstance(f, str)][:MAX_RECENT]

    # Geometry — must be a string (e.g. "1200x800+100+50")
    if not isinstance(out.get("geometry", ""), str):
        out["geometry"] = ""

    return out


def load_settings() -> dict[str, Any]:
    """Load user settings from disk, validated against known constraints."""
    raw: dict[str, Any] = {}
    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                raw = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        log.warning("Failed to read settings from %s: %s", SETTINGS_FILE, exc)
    except Exception as exc:
        log.warning("Unexpected error loading settings: %s", exc)
    return _validate(raw)


def save_settings(data: dict[str, Any]) -> None:
    """Persist user settings to disk."""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except OSError as exc:
        log.warning("Failed to save settings to %s: %s", SETTINGS_FILE, exc)
