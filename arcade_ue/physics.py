from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntFlag


class CollisionLayer(IntFlag):
    WORLD = 1
    PLAYER = 2
    ENEMY = 4
    PROJECTILE = 8
    PICKUP = 16


def can_collide(layer: CollisionLayer, mask: CollisionLayer, other: CollisionLayer) -> bool:
    return bool((layer & other) or (mask & other))


@dataclass
class Body2D:
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    radius: float = 8.0
    layer: CollisionLayer = CollisionLayer.WORLD
    mask: CollisionLayer = (
        CollisionLayer.WORLD
        | CollisionLayer.PLAYER
        | CollisionLayer.ENEMY
        | CollisionLayer.PROJECTILE
    )


class PhysicsWorld:
    def add_body(self, body: Body2D) -> Body2D:
        raise NotImplementedError

    def step(self, dt: float) -> None:
        raise NotImplementedError


@dataclass
class ArcadePhysicsWorld(PhysicsWorld):
    gravity: float = -220.0
    bodies: list[Body2D] = field(default_factory=list)

    def add_body(self, body: Body2D) -> Body2D:
        self.bodies.append(body)
        return body

    def step(self, dt: float) -> None:
        for body in self.bodies:
            body.vy += self.gravity * dt
            body.x += body.vx * dt
            body.y += body.vy * dt


class PymunkPhysicsWorld(PhysicsWorld):
    def __init__(self, gravity: float = -220.0):
        import pymunk  # type: ignore

        self._pymunk = pymunk
        self.space = pymunk.Space()
        self.space.gravity = (0.0, gravity)
        self._mapping: list[tuple[Body2D, object, object]] = []

    def add_body(self, body: Body2D) -> Body2D:
        pbody = self._pymunk.Body(1, self._pymunk.moment_for_circle(1, 0, body.radius))
        pbody.position = (body.x, body.y)
        pbody.velocity = (body.vx, body.vy)
        shape = self._pymunk.Circle(pbody, body.radius)
        self.space.add(pbody, shape)
        self._mapping.append((body, pbody, shape))
        return body

    def step(self, dt: float) -> None:
        self.space.step(dt)
        for body, pbody, _shape in self._mapping:
            body.x, body.y = pbody.position
            body.vx, body.vy = pbody.velocity


def create_physics_world(prefer_pymunk: bool) -> tuple[PhysicsWorld, str]:
    if prefer_pymunk:
        try:
            return PymunkPhysicsWorld(), "pymunk"
        except Exception:
            pass
    return ArcadePhysicsWorld(), "arcade"


@dataclass
class MovingPlatform:
    x1: float
    y1: float
    x2: float
    y2: float
    speed: float
    t: float = 0.0
    direction: int = 1

    def update(self, dt: float) -> tuple[float, float]:
        distance = ((self.x2 - self.x1) ** 2 + (self.y2 - self.y1) ** 2) ** 0.5
        if distance == 0:
            return (self.x1, self.y1)
        self.t += self.direction * (self.speed * dt / distance)
        if self.t >= 1.0:
            self.t = 1.0
            self.direction = -1
        elif self.t <= 0.0:
            self.t = 0.0
            self.direction = 1
        return (self.x1 + (self.x2 - self.x1) * self.t, self.y1 + (self.y2 - self.y1) * self.t)
