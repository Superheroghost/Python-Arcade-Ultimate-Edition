from __future__ import annotations

import random

from arcade_ue.framework import Scene


class BreakoutScene(Scene):
    def __init__(self, app):
        self.app = app
        self.reset()

    def reset(self) -> None:
        self.score = 0
        self.win = False
        self.lose = False
        self.paddle_x = 0.0
        self.paddle_w = 130.0
        self.ball_x = 0.0
        self.ball_y = -130.0
        self.ball_vx = 240.0
        self.ball_vy = 220.0
        self.bricks = [
            {"x": -280 + col * 80, "y": 180 - row * 40, "alive": True}
            for row in range(5)
            for col in range(8)
        ]
        self.powerups: list[dict] = []

    def fixed_update(self, dt: float) -> None:
        if self.win or self.lose:
            if self.app.consume_key("space"):
                self.reset()
            return

        if self.app.input.down("Left") or self.app.input.down("a"):
            self.paddle_x -= 400 * dt
        if self.app.input.down("Right") or self.app.input.down("d"):
            self.paddle_x += 400 * dt
        self.paddle_x = max(-320, min(320, self.paddle_x))

        self.ball_x += self.ball_vx * dt
        self.ball_y += self.ball_vy * dt
        if self.ball_x < -390 or self.ball_x > 390:
            self.ball_vx *= -1
        if self.ball_y > 285:
            self.ball_vy *= -1
        if self.ball_y < -295:
            self.lose = True
            self.app.effects["shake"].trigger(6)
            return

        if abs(self.ball_y + 250) < 14 and abs(self.ball_x - self.paddle_x) < self.paddle_w / 2:
            self.ball_vy = abs(self.ball_vy)
            self.ball_vx += (self.ball_x - self.paddle_x) * 0.8

        for brick in self.bricks:
            if brick["alive"] and abs(self.ball_x - brick["x"]) < 34 and abs(self.ball_y - brick["y"]) < 16:
                brick["alive"] = False
                self.ball_vy *= -1
                self.score += 10
                self.app.audio.play("hit")
                self.app.effects["hitstop"].trigger(0.03)
                if random.random() < 0.1:
                    self.powerups.append({"x": brick["x"], "y": brick["y"], "vy": -120})
                break

        for p in self.powerups:
            p["y"] += p["vy"] * dt
            if abs(p["y"] + 250) < 20 and abs(p["x"] - self.paddle_x) < self.paddle_w / 2:
                self.paddle_w = min(190, self.paddle_w + 30)
                p["y"] = -999
        self.powerups = [p for p in self.powerups if p["y"] > -300]
        if all(not b["alive"] for b in self.bricks):
            self.win = True
            self.app.profile.record_score("breakout", self.score)

    def render(self, _alpha: float) -> None:
        ui = self.app.ui
        ui.clear()
        ui.text(0, 280, "BREAKOUT NOVA", font=("Courier", 22, "bold"), color="cyan")
        ui.text(-380, 250, f"Score: {self.score}", align="left", font=("Courier", 14, "normal"))
        ui.text(230, 250, "ESC Menu", align="left", font=("Courier", 12, "normal"), color="gray")

        self.app.draw_box(self.paddle_x, -250, self.paddle_w, 14, "#40f9ff")
        self.app.draw_box(self.ball_x, self.ball_y, 12, 12, "white")
        for brick in self.bricks:
            if brick["alive"]:
                self.app.draw_box(brick["x"], brick["y"], 68, 26, "#d974ff")
        for p in self.powerups:
            self.app.draw_box(p["x"], p["y"], 16, 16, "gold")

        if self.win:
            ui.text(0, 0, "YOU WIN! Press SPACE", font=("Courier", 22, "bold"), color="lime")
        if self.lose:
            ui.text(0, 0, "GAME OVER! Press SPACE", font=("Courier", 22, "bold"), color="red")


class BreakoutPlugin:
    game_id = "breakout"
    name = "Breakout Nova"
    description = "Breakout clone with paddle-size power-ups and hit-stop feedback."

    def create_scene(self, app):
        return BreakoutScene(app)
