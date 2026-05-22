from __future__ import annotations

import time

from .effects import HitStop, ScreenShake
from .framework import GameRegistration, Scene
from .games import default_plugins
from .services import AudioService, InputService, ProfileService, SettingsService, UiToolkit, running_in_ci


class MenuScene(Scene):
    def __init__(self, app: "ArcadeApp"):
        self.app = app
        self.selected = int(app.profile.values.get("selected_game", 0))

    def fixed_update(self, _dt: float) -> None:
        if self.app.consume_key("Up"):
            self.selected = (self.selected - 1) % len(self.app.games)
        if self.app.consume_key("Down"):
            self.selected = (self.selected + 1) % len(self.app.games)
        if self.app.consume_key("Return") or self.app.consume_key("space"):
            self.app.profile.values["selected_game"] = self.selected
            self.app.start_game(self.selected)

    def render(self, _alpha: float) -> None:
        self.app.ui.clear()
        self.app.ui.text(0, 265, "PYTHON ARCADE ULTIMATE EDITION", font=("Courier", 24, "bold"), color="#40f9ff")
        self.app.ui.text(0, 230, "Plugin Game Selector", font=("Courier", 14, "normal"), color="#d974ff")
        y = 160
        for idx, game in enumerate(self.app.games):
            color = "yellow" if idx == self.selected else "white"
            prefix = ">" if idx == self.selected else " "
            self.app.ui.text(0, y, f"{prefix} {idx + 1}. {game.name}", font=("Courier", 16, "bold"), color=color)
            self.app.ui.text(0, y - 22, game.description, font=("Courier", 11, "normal"), color="#8f96b3")
            y -= 60

        hs = self.app.profile.values.get("high_scores", {})
        self.app.ui.text(-390, -250, f"Highscores: {hs}", align="left", font=("Courier", 11, "normal"), color="#9fa9c9")
        self.app.ui.text(
            -390,
            -275,
            "UP/DOWN select • ENTER start • ESC back during game",
            align="left",
            font=("Courier", 11, "normal"),
            color="#7a829c",
        )


class ArcadeApp:
    def __init__(self):
        import turtle

        self.settings = SettingsService()
        self.profile = ProfileService()
        self.settings.load()
        self.profile.load()

        self.input = InputService()
        self.audio = AudioService(enabled=bool(self.settings.values.get("sfx", True)))

        self.screen = turtle.Screen()
        self.screen.setup(width=860, height=680)
        self.screen.bgcolor("black")
        self.screen.title("Python Arcade Ultimate Edition")
        self.screen.tracer(0, 0)

        self.pen = turtle.Turtle(visible=False)
        self.pen.speed(0)
        self.pen.penup()

        self.ui = UiToolkit(self.pen)
        self.effects = {"hitstop": HitStop(), "shake": ScreenShake()}

        self.fixed_dt = float(self.settings.values.get("fixed_timestep", 1 / 60))
        self.max_steps = 5
        self.accumulator = 0.0
        self.last_time = time.perf_counter()
        self.scene: Scene = MenuScene(self)
        self.games = [
            GameRegistration(game_id=p.game_id, name=p.name, description=p.description, plugin=p)
            for p in default_plugins()
        ]
        self._just_pressed: set[str] = set()

        self._bind_inputs()

    def _bind_inputs(self) -> None:
        keys = {
            "Left",
            "Right",
            "Up",
            "Down",
            "Return",
            "Escape",
            "space",
            "a",
            "d",
            "w",
            "s",
            "p",
        }
        for key in keys:
            self.screen.onkeypress(lambda k=key: self._set_key(k, True), key)
            self.screen.onkeyrelease(lambda k=key: self._set_key(k, False), key)
        self.screen.listen()

    def _set_key(self, key: str, is_down: bool) -> None:
        self.input.set_state(key, is_down)
        if is_down:
            self._just_pressed.add(key)

    def consume_key(self, key: str) -> bool:
        if key in self._just_pressed:
            self._just_pressed.remove(key)
            return True
        return False

    def draw_box(self, x: float, y: float, width: float, height: float, color: str) -> None:
        sx, sy = self.effects["shake"].tick(0)  # render-time offset only
        self.pen.goto(x - width / 2 + sx, y - height / 2 + sy)
        self.pen.color(color)
        self.pen.begin_fill()
        self.pen.pendown()
        for _ in range(2):
            self.pen.forward(width)
            self.pen.left(90)
            self.pen.forward(height)
            self.pen.left(90)
        self.pen.end_fill()
        self.pen.penup()
        self.pen.setheading(0)

    def start_game(self, index: int) -> None:
        self.scene.exit()
        self.scene = self.games[index].plugin.create_scene(self)
        self.profile.values["games_played"] = int(self.profile.values.get("games_played", 0)) + 1

    def switch_to_menu(self) -> None:
        self.scene.exit()
        self.scene = MenuScene(self)

    def frame(self) -> None:
        now = time.perf_counter()
        dt = min(0.25, now - self.last_time)
        self.last_time = now
        self.accumulator += dt

        steps = 0
        while self.accumulator >= self.fixed_dt and steps < self.max_steps:
            if self.consume_key("Escape") and not isinstance(self.scene, MenuScene):
                self.switch_to_menu()
            if self.consume_key("p"):
                pass
            if self.effects["hitstop"].tick(self.fixed_dt):
                self.accumulator -= self.fixed_dt
                steps += 1
                continue
            self.scene.fixed_update(self.fixed_dt)
            self.effects["shake"].tick(self.fixed_dt)
            self.accumulator -= self.fixed_dt
            steps += 1

        alpha = self.accumulator / self.fixed_dt
        self.scene.render(alpha)
        self.screen.update()
        self.screen.ontimer(self.frame, 0)

    def run(self) -> None:
        self.frame()
        self.screen.mainloop()



def run_app() -> None:
    if running_in_ci():
        print("CI environment detected; skip launching Turtle window.")
        return
    ArcadeApp().run()
