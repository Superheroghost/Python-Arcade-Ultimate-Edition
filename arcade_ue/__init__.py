"""Python Arcade Ultimate Edition package."""

__all__ = ["run"]


def run() -> None:
    from .app import run_app

    run_app()
