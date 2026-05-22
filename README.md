# Python Arcade: Ultimate Edition

Ultimate Edition now includes a modular `arcade_ue` framework with a plugin game selector, fixed-timestep updates, shared services, optional `pymunk` physics, and a 2.5D demo — while preserving the original `arcade.py` cabinet.

## What's New in this Upgrade

- App framework with scene manager + plugin interface
- Main menu/game selector (`arcade_ue.app.MenuScene`)
- Shared services for input/audio/settings/profile/UI drawing
- Fixed timestep loop with interpolation parameter and hit-stop support
- Physics abstraction with optional `pymunk` backend fallback
- Helpers: collision layers/masks, moving platforms, screen shake/hit-stop
- 2.5D module: parallax + Mode-7 style projection helper
- New plugin mini-games:
  1. Breakout Nova (power-ups)
  2. Twin-Stick Arena
  3. Physics Mini Pinball
  4. 2.5D Highway Demo
  5. Legacy Turtle Cabinet launcher

## Run

### Ultimate Edition framework (new)

```bash
python main.py
# or
python -m arcade_ue
```

### Legacy single-file cabinet (original)

```bash
python arcade.py
```

## Optional physics dependency

```bash
pip install .[physics]
```

If `pymunk` is unavailable, the game safely falls back to the built-in lightweight physics layer.

## Dev checks

```bash
python -m unittest discover -s tests -v
ruff check .
```

## Web Arcade (GitHub Pages)

The GitHub Pages arcade is served from `docs/` with `index.html`, `style.css`, and `main.js`.

## Docs

- `CONTRIBUTING.md` – how to add new game plugins
- `ROADMAP.md` – ~50 planned features grouped by category
