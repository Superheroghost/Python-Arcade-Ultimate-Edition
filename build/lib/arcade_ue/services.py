from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SETTINGS_PATH = ROOT / "ultimate_settings.json"
PROFILE_PATH = ROOT / "ultimate_profile.json"


DEFAULT_SETTINGS = {
    "volume": 0.4,
    "music": True,
    "sfx": True,
    "fixed_timestep": 1 / 60,
    "controls": {
        "left": "Left",
        "right": "Right",
        "up": "Up",
        "down": "Down",
        "action": "space",
        "pause": "p",
        "menu": "Escape",
    },
}

DEFAULT_PROFILE = {"games_played": 0, "high_scores": {}, "selected_game": 0}


@dataclass
class SettingsService:
    settings_path: Path = SETTINGS_PATH
    values: dict = field(default_factory=lambda: json.loads(json.dumps(DEFAULT_SETTINGS)))

    def load(self) -> None:
        self.values = json.loads(json.dumps(DEFAULT_SETTINGS))
        try:
            with self.settings_path.open("r", encoding="utf-8") as fh:
                loaded = json.load(fh)
            if isinstance(loaded, dict):
                self._merge(self.values, loaded)
        except (OSError, json.JSONDecodeError):
            pass

    def save(self) -> None:
        self.settings_path.write_text(json.dumps(self.values, indent=2), encoding="utf-8")

    def _merge(self, target: dict, source: dict) -> None:
        for key, value in source.items():
            if isinstance(value, dict) and isinstance(target.get(key), dict):
                self._merge(target[key], value)
            else:
                target[key] = value


@dataclass
class ProfileService:
    profile_path: Path = PROFILE_PATH
    values: dict = field(default_factory=lambda: json.loads(json.dumps(DEFAULT_PROFILE)))

    def load(self) -> None:
        self.values = json.loads(json.dumps(DEFAULT_PROFILE))
        try:
            with self.profile_path.open("r", encoding="utf-8") as fh:
                loaded = json.load(fh)
            if isinstance(loaded, dict):
                self.values.update(loaded)
        except (OSError, json.JSONDecodeError):
            pass

    def save(self) -> None:
        self.profile_path.write_text(json.dumps(self.values, indent=2), encoding="utf-8")

    def record_score(self, game_id: str, score: int) -> None:
        high_scores = self.values.setdefault("high_scores", {})
        high_scores[game_id] = max(score, int(high_scores.get(game_id, 0)))


@dataclass
class InputService:
    pressed: dict[str, bool] = field(default_factory=dict)

    def set_state(self, key: str, is_down: bool) -> None:
        self.pressed[key] = is_down

    def down(self, key: str) -> bool:
        return bool(self.pressed.get(key, False))


@dataclass
class AudioService:
    enabled: bool = True

    def play(self, _name: str = "beep") -> None:
        if self.enabled:
            print("\a", end="")


class UiToolkit:
    def __init__(self, pen):
        self.pen = pen

    def text(
        self,
        x: float,
        y: float,
        message: str,
        align: str = "center",
        font=("Courier", 16, "normal"),
        color: str = "white",
    ) -> None:
        self.pen.color(color)
        self.pen.goto(x, y)
        self.pen.write(message, align=align, font=font)

    def clear(self) -> None:
        self.pen.clear()


def running_in_ci() -> bool:
    return os.getenv("CI", "").lower() in {"1", "true", "yes"}
