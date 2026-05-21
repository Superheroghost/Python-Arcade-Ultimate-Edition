# Python Arcade: Ultimate Edition

A polished, single-file arcade cabinet packed with seven classic-style games built with Python’s built-in `turtle` module. It’s designed for instant play, smooth controls, and arcade-style polish.

## Games Included

1. **Pong** – Power-up orbs, curved paddle bounces, speed ramp, and score flashes.
2. **Snake** – Wrap mode toggle, obstacles, golden apples, and progressive speed.
3. **Tetris** – Hold piece, ghost piece, soft drop, and dynamic speed scaling.
4. **Space Invaders** – Shields, waves, UFO bonus, and enemy bullet patterns.
5. **Breakout** – Combo scoring, paddle/slow power-ups, and multi-level pacing.
6. **Asteroid Dodger** – Dodge falling asteroids, grab shields, and survive for score.
7. **Flappy Turtle** – Tap to flap through pipes with a smooth arcade feel.

## Global Controls

- **P**: Pause/Resume
- **R**: Restart current game
- **ESC**: Return to menu

Each game also shows its specific controls on-screen.

## Requirements

- Python 3.x
- `turtle` (ships with the standard library)

## Run

```bash
python arcade.py
```

### Python Arcade Settings

- In the main menu:
  - **D** cycles difficulty (**Easy / Normal / Hard**)
  - **T** cycles turtle speed (**Slow / Normal / Fast**)
- Settings are persisted in `arcade_settings.json`.

## Web Arcade (GitHub Pages)

A static web arcade is included in `docs/` and works with GitHub Pages.

### Local Preview

Open `docs/index.html` directly in a browser, or use a static server:

```bash
python -m http.server 8000
```

Then visit `http://localhost:8000/docs/`.

### GitHub Pages

1. In GitHub repository settings, open **Pages**.
2. Set source to **Deploy from a branch**.
3. Select your branch and `/docs` folder.
4. Save. GitHub will publish the web arcade site automatically.

## Notes

- All game logic lives in **`arcade.py`** as requested.
- This project is designed for quick play, polished arcade feedback, and easy extension.
