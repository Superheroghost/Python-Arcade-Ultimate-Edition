from __future__ import annotations

import math
import random

from arcade_ue.framework import Scene


class TwinStickScene(Scene):
    def __init__(self, app):
        self.app = app
        self.reset()

    def reset(self) -> None:
        self.player_x = 0.0
        self.player_y = -40.0
        self.hp = 5
        self.score = 0
        self.cooldown = 0.0
        self.enemies: list[dict] = []
        self.bullets: list[dict] = []
        self.time = 0.0

    def fixed_update(self, dt: float) -> None:
        if self.hp <= 0:
            if self.app.consume_key("space"):
                self.reset()
            return

        speed = 250
        dx = (1 if self.app.input.down("d") else 0) - (1 if self.app.input.down("a") else 0)
        dy = (1 if self.app.input.down("w") else 0) - (1 if self.app.input.down("s") else 0)
        length = math.hypot(dx, dy) or 1.0
        self.player_x += (dx / length) * speed * dt
        self.player_y += (dy / length) * speed * dt
        self.player_x = max(-380, min(380, self.player_x))
        self.player_y = max(-280, min(280, self.player_y))

        aim_x = (1 if self.app.input.down("Right") else 0) - (1 if self.app.input.down("Left") else 0)
        aim_y = (1 if self.app.input.down("Up") else 0) - (1 if self.app.input.down("Down") else 0)

        self.cooldown = max(0.0, self.cooldown - dt)
        if (aim_x or aim_y or self.app.input.down("space")) and self.cooldown <= 0:
            if not (aim_x or aim_y):
                aim_y = 1
            mag = math.hypot(aim_x, aim_y) or 1.0
            self.bullets.append(
                {"x": self.player_x, "y": self.player_y, "vx": aim_x / mag * 420, "vy": aim_y / mag * 420}
            )
            self.cooldown = 0.18

        self.time += dt
        if self.time > 0.7:
            self.time = 0.0
            edge = random.choice([0, 1, 2, 3])
            if edge == 0:
                x, y = random.uniform(-380, 380), 300
            elif edge == 1:
                x, y = random.uniform(-380, 380), -300
            elif edge == 2:
                x, y = -400, random.uniform(-280, 280)
            else:
                x, y = 400, random.uniform(-280, 280)
            self.enemies.append({"x": x, "y": y, "hp": 2})

        for bullet in self.bullets:
            bullet["x"] += bullet["vx"] * dt
            bullet["y"] += bullet["vy"] * dt
        self.bullets = [b for b in self.bullets if -420 < b["x"] < 420 and -320 < b["y"] < 320]

        for enemy in self.enemies:
            vx = self.player_x - enemy["x"]
            vy = self.player_y - enemy["y"]
            mag = math.hypot(vx, vy) or 1.0
            enemy["x"] += (vx / mag) * 90 * dt
            enemy["y"] += (vy / mag) * 90 * dt

            for bullet in self.bullets:
                if abs(enemy["x"] - bullet["x"]) < 14 and abs(enemy["y"] - bullet["y"]) < 14:
                    enemy["hp"] -= 1
                    bullet["x"] = 9999
                    self.app.effects["hitstop"].trigger(0.015)
            if abs(enemy["x"] - self.player_x) < 20 and abs(enemy["y"] - self.player_y) < 20:
                self.hp -= 1
                enemy["hp"] = 0
                self.app.effects["shake"].trigger(9)

        before = len(self.enemies)
        self.enemies = [e for e in self.enemies if e["hp"] > 0]
        defeated = before - len(self.enemies)
        if defeated:
            self.score += defeated * 15
            self.app.profile.record_score("twinstick", self.score)

    def render(self, _alpha: float) -> None:
        ui = self.app.ui
        ui.clear()
        ui.text(0, 280, "TWIN-STICK ARENA", font=("Courier", 22, "bold"), color="#40f9ff")
        ui.text(-380, 250, f"HP: {self.hp}  Score: {self.score}", align="left", font=("Courier", 14, "normal"))
        ui.text(210, 250, "Move WASD / Aim Arrows", align="left", font=("Courier", 12, "normal"), color="gray")
        self.app.draw_box(self.player_x, self.player_y, 20, 20, "cyan")
        for bullet in self.bullets:
            self.app.draw_box(bullet["x"], bullet["y"], 6, 6, "yellow")
        for enemy in self.enemies:
            self.app.draw_box(enemy["x"], enemy["y"], 20, 20, "#ff5f5f")
        if self.hp <= 0:
            ui.text(0, 0, "DEFEATED - Press SPACE", font=("Courier", 22, "bold"), color="red")


class TwinStickPlugin:
    game_id = "twinstick"
    name = "Twin-Stick Arena"
    description = "Arena shooter with WASD movement, twin-stick aiming, and score waves."

    def create_scene(self, app):
        return TwinStickScene(app)
