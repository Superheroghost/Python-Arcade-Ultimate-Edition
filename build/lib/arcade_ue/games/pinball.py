from __future__ import annotations

import random

from arcade_ue.framework import Scene
from arcade_ue.physics import Body2D, CollisionLayer, MovingPlatform, create_physics_world


class PinballScene(Scene):
    def __init__(self, app):
        self.app = app
        self.world, self.backend = create_physics_world(prefer_pymunk=True)
        self.ball = self.world.add_body(Body2D(0, 150, vx=140, vy=0, radius=10, layer=CollisionLayer.PLAYER))
        self.bumpers = [(-160, 80), (0, 180), (160, 70)]
        self.platform = MovingPlatform(-220, -170, 220, -170, speed=120)
        self.platform_x = 0.0
        self.score = 0

    def fixed_update(self, dt: float) -> None:
        if self.app.input.down("space"):
            self.ball.vy += 420 * dt
        self.world.step(dt)

        if self.ball.x < -390 or self.ball.x > 390:
            self.ball.vx *= -1
        if self.ball.y > 290:
            self.ball.vy *= -0.95
        if self.ball.y < -295:
            self.ball.x, self.ball.y = (0, 170)
            self.ball.vx, self.ball.vy = (random.choice([-160, 160]), 80)
            self.app.effects["shake"].trigger(8)

        self.platform_x, _ = self.platform.update(dt)
        if abs(self.ball.y + 170) < 14 and abs(self.ball.x - self.platform_x) < 70:
            self.ball.vy = abs(self.ball.vy) + 80
            self.ball.vx += (self.ball.x - self.platform_x) * 0.5

        for bx, by in self.bumpers:
            if abs(self.ball.x - bx) < 22 and abs(self.ball.y - by) < 22:
                self.ball.vx *= -1
                self.ball.vy = abs(self.ball.vy) + 40
                self.score += 20
                self.app.effects["hitstop"].trigger(0.02)
                self.app.profile.record_score("pinball", self.score)

    def render(self, _alpha: float) -> None:
        ui = self.app.ui
        ui.clear()
        ui.text(0, 280, "PHYSICS MINI PINBALL", font=("Courier", 22, "bold"), color="#7cf6ff")
        ui.text(
            -380,
            250,
            f"Backend: {self.backend}  Score: {self.score}",
            align="left",
            font=("Courier", 14, "normal"),
        )
        ui.text(200, 250, "SPACE = impulse", align="left", font=("Courier", 12, "normal"), color="gray")

        self.app.draw_box(0, -180, 760, 8, "#5f5f5f")
        self.app.draw_box(self.platform_x, -170, 140, 12, "#40f9ff")
        for bx, by in self.bumpers:
            self.app.draw_box(bx, by, 38, 38, "magenta")
        self.app.draw_box(self.ball.x, self.ball.y, 20, 20, "white")


class PinballPlugin:
    game_id = "pinball"
    name = "Physics Mini Pinball"
    description = "Physics scene with optional pymunk backend and moving-platform flipper helper."

    def create_scene(self, app):
        return PinballScene(app)
