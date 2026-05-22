from __future__ import annotations

from arcade_ue.framework import Scene
from arcade_ue.render25d import ParallaxLayer, ParallaxRenderer, mode7_project


class Mode7DemoScene(Scene):
    def __init__(self, app):
        self.app = app
        self.camera_x = 0.0
        self.speed = 0.0
        self.parallax = ParallaxRenderer(app.pen)
        self.layers = [
            ParallaxLayer(speed=0.15, height=220, color="#1c2f66"),
            ParallaxLayer(speed=0.3, height=180, color="#324a90"),
            ParallaxLayer(speed=0.55, height=140, color="#4f63a9"),
        ]

    def fixed_update(self, dt: float) -> None:
        turn = (1 if self.app.input.down("Right") else 0) - (1 if self.app.input.down("Left") else 0)
        accel = (1 if self.app.input.down("Up") else 0) - (1 if self.app.input.down("Down") else 0)
        self.speed = max(40.0, min(350.0, self.speed + accel * 280 * dt))
        self.camera_x += (turn * 180 + self.speed * 0.3) * dt

    def render(self, _alpha: float) -> None:
        ui = self.app.ui
        ui.clear()
        self.parallax.draw_layers(self.camera_x, self.layers)

        for y in range(-200, 260, 14):
            depth = mode7_project(y + 240, horizon=40.0, depth_scale=120.0)
            road_half = 20 + depth * 180
            center = ((self.camera_x * depth) % 220) - 110
            stripe = "#5d5d5d" if int((y + 260) / 28) % 2 == 0 else "#7a7a7a"
            self.app.draw_box(center, y, road_half * 2, 12, stripe)

        ui.text(0, 280, "2.5D HIGHWAY DEMO", font=("Courier", 22, "bold"), color="#7cf6ff")
        ui.text(-380, 250, "Arrows steer pseudo-3D camera", align="left", font=("Courier", 13, "normal"))


class Mode7DemoPlugin:
    game_id = "mode7"
    name = "2.5D Highway Demo"
    description = "Pseudo-3D/Mode-7 style lane rendering with parallax depth layers."

    def create_scene(self, app):
        return Mode7DemoScene(app)
