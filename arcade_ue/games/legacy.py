from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from arcade_ue.framework import Scene


class LegacyScene(Scene):
    def __init__(self, app):
        self.app = app
        self.launched = False

    def fixed_update(self, _dt: float) -> None:
        if not self.launched:
            self.launched = True
            legacy = Path(__file__).resolve().parents[2] / "arcade.py"
            subprocess.run([sys.executable, str(legacy)], check=False)
            self.app.switch_to_menu()

    def render(self, _alpha: float) -> None:
        self.app.ui.clear()
        self.app.ui.text(0, 0, "Launching legacy arcade...", font=("Courier", 20, "bold"), color="white")


class LegacyPlugin:
    game_id = "legacy"
    name = "Legacy Turtle Cabinet"
    description = "Launches the original single-file 7-game arcade for compatibility."

    def create_scene(self, app):
        return LegacyScene(app)
