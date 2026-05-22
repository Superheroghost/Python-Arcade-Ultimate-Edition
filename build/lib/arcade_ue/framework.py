from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from .app import ArcadeApp


class Scene:
    def enter(self) -> None:
        pass

    def exit(self) -> None:
        pass

    def fixed_update(self, dt: float) -> None:
        pass

    def render(self, alpha: float) -> None:
        pass


class GamePlugin(Protocol):
    game_id: str
    name: str
    description: str

    def create_scene(self, app: "ArcadeApp") -> Scene:
        ...


@dataclass
class GameRegistration:
    game_id: str
    name: str
    description: str
    plugin: GamePlugin
