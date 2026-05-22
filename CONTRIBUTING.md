# Contributing

## Add a new game plugin

1. Create a file in `arcade_ue/games/`.
2. Implement:
   - a `Scene` subclass (`fixed_update`, `render`)
   - a plugin class with `game_id`, `name`, `description`, and `create_scene(app)`.
3. Export the plugin in `arcade_ue/games/__init__.py` via `default_plugins()`.
4. Keep game code isolated from core services where possible.

## Shared systems available

- `app.input` for key states
- `app.audio` for simple SFX hooks
- `app.profile` and `app.settings` for persistence
- `app.effects['hitstop']`, `app.effects['shake']`
- `arcade_ue.physics` for backend-agnostic physics helpers
- `arcade_ue.render25d` for parallax + pseudo-3D helpers

## Local checks

```bash
python -m unittest discover -s tests -v
ruff check .
```

## Optional dependency

Install optional `pymunk` support:

```bash
pip install .[physics]
```
