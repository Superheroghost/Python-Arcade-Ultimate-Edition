from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class HitStop:
    remaining: float = 0.0

    def trigger(self, seconds: float) -> None:
        self.remaining = max(self.remaining, max(0.0, seconds))

    def tick(self, dt: float) -> bool:
        if self.remaining <= 0:
            return False
        self.remaining = max(0.0, self.remaining - dt)
        return True


@dataclass
class ScreenShake:
    power: float = 0.0
    damping: float = 11.0

    def trigger(self, power: float) -> None:
        self.power = max(self.power, power)

    def tick(self, dt: float) -> tuple[float, float]:
        self.power = max(0.0, self.power - self.damping * dt)
        if self.power <= 0:
            return (0.0, 0.0)
        return (random.uniform(-self.power, self.power), random.uniform(-self.power, self.power))
