from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ParallaxLayer:
    speed: float
    height: float
    color: str


class ParallaxRenderer:
    def __init__(self, pen):
        self.pen = pen

    def draw_layers(self, camera_x: float, layers: list[ParallaxLayer], width: int = 800) -> None:
        for layer in layers:
            offset = (camera_x * layer.speed) % width
            self.pen.color(layer.color)
            self.pen.penup()
            for x in range(-2 * width, 2 * width, 160):
                draw_x = x - offset
                self.pen.goto(draw_x, layer.height)
                self.pen.dot(70)


def mode7_project(screen_y: float, horizon: float = 40.0, depth_scale: float = 130.0) -> float:
    screen_y = max(horizon + 1.0, screen_y)
    return depth_scale / (screen_y - horizon)
