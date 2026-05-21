import turtle
import time
import random
import math
import json
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# --- GLOBAL SCREEN SETUP ---
wn = turtle.Screen()
wn.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
wn.bgcolor("black")
wn.title("Python Arcade - Ultimate Edition")
turtle.colormode(1.0)

# --- HIGH SCORES ---
high_scores = {
    "Pong (A/B)": "N/A",
    "Snake": 0,
    "Tetris": 0,
    "Space Invaders": 0,
    "Breakout": 0,
    "Asteroid Dodger": 0,
    "Flappy Turtle": 0
}

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "arcade_settings.json")
DEFAULT_SETTINGS = {"difficulty": "Normal", "turtle_speed": "Normal"}
DIFFICULTY_LEVELS = ["Easy", "Normal", "Hard"]
TURTLE_SPEED_LEVELS = ["Slow", "Normal", "Fast"]


def load_settings():
    settings = dict(DEFAULT_SETTINGS)
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as fh:
            loaded = json.load(fh)
        if isinstance(loaded, dict):
            for key, allowed in (("difficulty", DIFFICULTY_LEVELS), ("turtle_speed", TURTLE_SPEED_LEVELS)):
                value = loaded.get(key)
                if value in allowed:
                    settings[key] = value
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return settings


def save_settings():
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as fh:
            json.dump(settings, fh, indent=2)
    except OSError:
        pass


def get_difficulty_scalar(easy=0.85, normal=1.0, hard=1.2):
    return {"Easy": easy, "Normal": normal, "Hard": hard}.get(settings["difficulty"], normal)


def get_turtle_speed_scalar():
    return {"Slow": 0.8, "Normal": 1.0, "Fast": 1.25}.get(settings["turtle_speed"], 1.0)


settings = load_settings()


def clear_bindings():
    """Removes all keyboard bindings to prevent input overlap between games."""
    keys_to_unbind = [
        "w", "s", "Up", "Down", "Left", "Right", "a", "d",
        "space", "Escape", "1", "2", "3", "4", "5", "6", "7",
        "r", "p", "c", "m", "t", "Return"
    ]
    for key in keys_to_unbind:
        wn.onkeypress(None, key)
        wn.onkeyrelease(None, key)


def reset_screen(title):
    wn.clearscreen()
    wn.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    wn.bgcolor("black")
    wn.title(title)
    wn.tracer(0)


def build_text_pen(color="white", size=18, bold=True):
    pen = turtle.Turtle()
    pen.hideturtle()
    pen.penup()
    pen.color(color)
    pen.speed(0)
    pen._font = ("Courier", size, "bold" if bold else "normal")
    return pen


def write_text(pen, text, x=0, y=0, align="center", font=None):
    pen.goto(x, y)
    pen.write(text, align=align, font=font or pen._font)


def write_controls(pen, lines, y=-260):
    pen.clear()
    for i, line in enumerate(lines):
        write_text(pen, line, 0, y - (i * 18), font=("Courier", 14, "normal"))


def clamp(value, low, high):
    return max(low, min(high, value))


def bind_common(keys):
    wn.onkeypress(lambda: keys.update({"Escape": True}), "Escape")
    wn.onkeypress(lambda: keys.update({"Restart": True}), "r")
    wn.onkeypress(lambda: keys.update({"Pause": not keys.get("Pause", False)}), "p")


def handle_pause(keys, pause_pen, message="PAUSED"):
    if keys.get("Pause"):
        pause_pen.clear()
        write_text(pause_pen, f"{message}\nPress P to Resume", 0, 0, font=("Courier", 28, "bold"))
        wn.update()
        time.sleep(0.05)
        return True
    pause_pen.clear()
    return False


def make_starfield(count, min_speed=0.3, max_speed=2.0):
    stars = []
    for _ in range(count):
        stars.append([random.randint(-400, 400), random.randint(-300, 300), random.uniform(min_speed, max_speed)])
    pen = turtle.Turtle()
    pen.hideturtle()
    pen.penup()
    return stars, pen


def update_starfield(stars, pen, multiplier=1.0):
    pen.clear()
    for s in stars:
        s[1] -= s[2] * multiplier
        if s[1] < -300:
            s[1] = 300
            s[0] = random.randint(-400, 400)
        pen.goto(s[0], s[1])
        pen.dot(s[2] * 3, "white")


# =====================================================================
# 1. PONG
# =====================================================================

def play_pong():
    while True:
        clear_bindings()
        reset_screen("Pong - Press ESC to Menu")

        speed_input = {"Easy": 4.0, "Normal": 5.0, "Hard": 6.2}[settings["difficulty"]] * get_turtle_speed_scalar()

        score_a = 0
        score_b = 0

        net = turtle.Turtle()
        net.color("gray")
        net.penup()
        net.hideturtle()
        net.goto(0, 280)
        net.setheading(270)
        for _ in range(28):
            net.pendown()
            net.forward(10)
            net.penup()
            net.forward(10)

        paddle_a = turtle.Turtle()
        paddle_a.speed(0)
        paddle_a.shape("square")
        paddle_a.color("white")
        paddle_a.shapesize(stretch_wid=5, stretch_len=1)
        paddle_a.penup()
        paddle_a.goto(-350, 0)
        paddle_a_flash = 0

        paddle_b = turtle.Turtle()
        paddle_b.speed(0)
        paddle_b.shape("square")
        paddle_b.color("white")
        paddle_b.shapesize(stretch_wid=5, stretch_len=1)
        paddle_b.penup()
        paddle_b.goto(350, 0)
        paddle_b_flash = 0

        ball = turtle.Turtle()
        ball.speed(0)
        ball.shape("square")
        ball.color("white")
        ball.penup()
        ball.goto(0, 0)
        ball.dx = speed_input
        ball.dy = speed_input

        trail_drawer = turtle.Turtle()
        trail_drawer.shape("square")
        trail_drawer.color("gray")
        trail_drawer.penup()
        trail_drawer.hideturtle()
        trail_stamps = []

        powerup = turtle.Turtle()
        powerup.shape("circle")
        powerup.shapesize(0.7)
        powerup.penup()
        powerup.hideturtle()
        powerup_active = False
        powerup_type = None
        powerup_timer = 0
        last_powerup = time.time()
        paddle_boost_end = 0

        paddle_speed = 7 * get_turtle_speed_scalar()

        pen = turtle.Turtle()
        pen.speed(0)
        pen.color("white")
        pen.penup()
        pen.hideturtle()
        pen.goto(0, 230)
        score_flash = 0

        info_pen = build_text_pen("gray", 14, False)
        write_controls(info_pen, ["W/S & Up/Down: Move", "P: Pause  R: Restart  ESC: Menu"])
        pause_pen = build_text_pen("white", 28, True)
        status_pen = build_text_pen("yellow", 16, True)

        def update_score():
            pen.clear()
            pen.write(f"{score_a}    {score_b}", align="center", font=("Courier", 36, "bold"))

        def set_powerup_status(text, color):
            status_pen.clear()
            status_pen.color(color)
            write_text(status_pen, text, 0, -210, font=("Courier", 16, "bold"))

        update_score()

        keys = {"w": False, "s": False, "Up": False, "Down": False, "Escape": False, "Pause": False, "Restart": False}

        def k_press(k):
            keys[k] = True

        def k_release(k):
            keys[k] = False

        wn.listen()
        for k in ["w", "s", "Up", "Down"]:
            wn.onkeypress(lambda k=k: k_press(k), k)
            wn.onkeyrelease(lambda k=k: k_release(k), k)
        bind_common(keys)

        last_speed_up = time.time()
        game_running = True
        restart = False

        def bounce_from_paddle(paddle, flash_color):
            nonlocal score_flash
            offset = (ball.ycor() - paddle.ycor()) / 50.0
            ball.dx *= -1
            ball.dy += offset * 2.5
            ball.dy = clamp(ball.dy, -12, 12)
            paddle.color(flash_color)
            score_flash = 10

        def scoring_delay(duration):
            delay_end = time.time() + duration
            while time.time() < delay_end:
                wn.update()
                time.sleep(0.01)
                if keys["Escape"]:
                    return "escape"
                if keys["Restart"]:
                    return "restart"
            return None

        while game_running:
            wn.update()
            time.sleep(0.01)

            if keys["Escape"]:
                break
            if keys["Restart"]:
                restart = True
                break
            if handle_pause(keys, pause_pen):
                continue

            if paddle_boost_end and time.time() > paddle_boost_end:
                paddle_a.shapesize(stretch_wid=5, stretch_len=1)
                paddle_b.shapesize(stretch_wid=5, stretch_len=1)
                paddle_boost_end = 0
                set_powerup_status("", "yellow")

            if time.time() - last_powerup > 7 and not powerup_active:
                powerup_active = True
                powerup_timer = time.time()
                powerup_type = random.choice(["paddle", "speed", "slow"])
                color_map = {"paddle": "cyan", "speed": "orange", "slow": "purple"}
                powerup.color(color_map[powerup_type])
                powerup.goto(random.randint(-200, 200), random.randint(-200, 200))
                powerup.showturtle()

            if powerup_active and time.time() - powerup_timer > 6:
                powerup_active = False
                powerup.hideturtle()

            if powerup_active and ball.distance(powerup) < 20:
                powerup_active = False
                powerup.hideturtle()
                if powerup_type == "paddle":
                    paddle_a.shapesize(stretch_wid=7, stretch_len=1)
                    paddle_b.shapesize(stretch_wid=7, stretch_len=1)
                    paddle_boost_end = time.time() + 6
                    set_powerup_status("PADDLE BOOST!", "cyan")
                elif powerup_type == "speed":
                    ball.dx *= 1.2
                    ball.dy *= 1.2
                    set_powerup_status("SPEED UP!", "orange")
                else:
                    ball.dx *= 0.8
                    ball.dy *= 0.8
                    set_powerup_status("SLOW DOWN!", "purple")

            if time.time() - last_speed_up > 2.0:
                if abs(ball.dx) < 15:
                    ball.dx *= 1.02
                    ball.dy *= 1.02
                last_speed_up = time.time()

            if paddle_a_flash > 0:
                paddle_a_flash -= 1
                if paddle_a_flash == 0:
                    paddle_a.color("white")
            if paddle_b_flash > 0:
                paddle_b_flash -= 1
                if paddle_b_flash == 0:
                    paddle_b.color("white")
            if score_flash > 0:
                score_flash -= 1
                if score_flash == 0:
                    pen.color("white")
                    update_score()

            if keys["w"] and paddle_a.ycor() < 240:
                paddle_a.sety(paddle_a.ycor() + paddle_speed)
            if keys["s"] and paddle_a.ycor() > -230:
                paddle_a.sety(paddle_a.ycor() - paddle_speed)
            if keys["Up"] and paddle_b.ycor() < 240:
                paddle_b.sety(paddle_b.ycor() + paddle_speed)
            if keys["Down"] and paddle_b.ycor() > -230:
                paddle_b.sety(paddle_b.ycor() - paddle_speed)

            trail_drawer.goto(ball.xcor(), ball.ycor())
            trail_stamps.append(trail_drawer.stamp())
            if len(trail_stamps) > 6:
                trail_drawer.clearstamp(trail_stamps.pop(0))

            ball.setx(ball.xcor() + ball.dx)
            ball.sety(ball.ycor() + ball.dy)

            if ball.ycor() > 280:
                ball.sety(280)
                ball.dy *= -1
            elif ball.ycor() < -280:
                ball.sety(-280)
                ball.dy *= -1

            if ball.xcor() > 390 or ball.xcor() < -390:
                if ball.xcor() > 390:
                    score_a += 1
                    pen.color("cyan")
                    ball.dx = -speed_input
                else:
                    score_b += 1
                    pen.color("red")
                    ball.dx = speed_input

                score_flash = 30
                update_score()
                ball.goto(0, 0)
                ball.dy = speed_input
                trail_drawer.clearstamps()
                trail_stamps.clear()

                post_score_action = scoring_delay(1.5)
                if post_score_action == "escape":
                    break
                if post_score_action == "restart":
                    restart = True
                    break
                last_speed_up = time.time()
                for key_name in keys:
                    keys[key_name] = False

            if ball.dx > 0 and (340 < ball.xcor() < 350) and (paddle_b.ycor() - 55 < ball.ycor() < paddle_b.ycor() + 55):
                ball.setx(340)
                bounce_from_paddle(paddle_b, "red")
                paddle_b_flash = 10

            if ball.dx < 0 and (-350 < ball.xcor() < -340) and (paddle_a.ycor() - 55 < ball.ycor() < paddle_a.ycor() + 55):
                ball.setx(-340)
                bounce_from_paddle(paddle_a, "cyan")
                paddle_a_flash = 10

        if restart:
            continue
        break

    main_menu()


# =====================================================================
# 2. SNAKE
# =====================================================================

def play_snake():
    while True:
        clear_bindings()
        reset_screen("Snake - Press ESC to Menu")

        border = turtle.Turtle()
        border.color("gray")
        border.penup()
        border.goto(-390, 280)
        border.pendown()
        border.pensize(3)
        for _ in range(2):
            border.forward(780)
            border.right(90)
            border.forward(560)
            border.right(90)
        border.hideturtle()

        head = [0, 0]
        body = []
        direction = "stop"
        score = 0
        speed_scale = get_turtle_speed_scalar()
        base_move_delay = {"Easy": 0.13, "Normal": 0.1, "Hard": 0.08}[settings["difficulty"]] / speed_scale
        min_move_delay = max(0.025, base_move_delay * 0.35)
        move_delay = base_move_delay
        last_move = time.time()
        wrap_mode = False
        rocks = []
        next_rock_score = 50

        def get_random_food_pos():
            return [random.randint(-18, 18) * 20, random.randint(-13, 13) * 20]

        def spawn_rock():
            for _ in range(50):
                pos = get_random_food_pos()
                if pos not in body and pos != head and pos != food and pos != golden_apple and pos not in rocks:
                    rocks.append(pos)
                    return

        food = get_random_food_pos()
        golden_apple = None
        golden_timer = 0

        pen = turtle.Turtle()
        pen.shape("square")
        pen.penup()
        pen.speed(0)

        ui_pen = build_text_pen("white", 20, True)
        pause_pen = build_text_pen("white", 28, True)
        controls_pen = build_text_pen("gray", 14, False)
        write_controls(controls_pen, ["Arrows/WASD: Move", "M: Wrap Toggle  P: Pause  R: Restart  ESC: Menu"])

        def update_ui():
            ui_pen.clear()
            write_text(ui_pen, f"Score: {score}  High Score: {high_scores['Snake']}  Wrap: {'ON' if wrap_mode else 'OFF'}", 0, 250,
                       font=("Courier", 18, "bold"))

        update_ui()

        def set_dir(new_dir):
            nonlocal direction
            opposites = {"up": "down", "down": "up", "left": "right", "right": "left", "stop": ""}
            if direction != opposites.get(new_dir):
                direction = new_dir

        keys = {"Escape": False, "Pause": False, "Restart": False}
        wn.listen()
        wn.onkeypress(lambda: set_dir("up"), "Up")
        wn.onkeypress(lambda: set_dir("up"), "w")
        wn.onkeypress(lambda: set_dir("down"), "Down")
        wn.onkeypress(lambda: set_dir("down"), "s")
        wn.onkeypress(lambda: set_dir("left"), "Left")
        wn.onkeypress(lambda: set_dir("left"), "a")
        wn.onkeypress(lambda: set_dir("right"), "Right")
        wn.onkeypress(lambda: set_dir("right"), "d")
        bind_common(keys)

        def toggle_wrap():
            nonlocal wrap_mode
            wrap_mode = not wrap_mode
            update_ui()

        wn.onkeypress(lambda: toggle_wrap(), "m")

        game_running = True
        restart = False
        while game_running:
            wn.update()
            time.sleep(0.01)

            if keys["Escape"]:
                break
            if keys["Restart"]:
                restart = True
                break
            if handle_pause(keys, pause_pen):
                continue

            if time.time() - last_move > move_delay:
                last_move = time.time()

                if direction != "stop":
                    if len(body) > 0:
                        body.insert(0, list(head))
                        body.pop()

                    if direction == "up":
                        head[1] += 20
                    elif direction == "down":
                        head[1] -= 20
                    elif direction == "left":
                        head[0] -= 20
                    elif direction == "right":
                        head[0] += 20

                if wrap_mode:
                    if head[0] > 370:
                        head[0] = -370
                    elif head[0] < -370:
                        head[0] = 370
                    if head[1] > 270:
                        head[1] = -270
                    elif head[1] < -270:
                        head[1] = 270
                else:
                    if head[0] > 370 or head[0] < -370 or head[1] > 270 or head[1] < -270:
                        direction = "stop"
                        head = [0, 0]
                        body.clear()
                        rocks.clear()
                        score = 0
                        next_rock_score = 50
                        move_delay = base_move_delay
                        golden_apple = None
                        update_ui()

                if head in body or head in rocks:
                    direction = "stop"
                    head = [0, 0]
                    body.clear()
                    rocks.clear()
                    score = 0
                    next_rock_score = 50
                    move_delay = base_move_delay
                    golden_apple = None
                    update_ui()

                if head == food:
                    food = get_random_food_pos()
                    while food in body or food == head or food in rocks:
                        food = get_random_food_pos()
                    body.append(list(head))
                    score += 10
                    if score > high_scores["Snake"]:
                        high_scores["Snake"] = score
                    move_delay = max(min_move_delay, move_delay - (0.002 * speed_scale))
                    update_ui()

                    if score >= next_rock_score:
                        spawn_rock()
                        next_rock_score += 50

                    if golden_apple is None and random.random() < 0.1:
                        golden_apple = get_random_food_pos()
                        golden_timer = time.time()

                if golden_apple:
                    if head == golden_apple:
                        score += 50
                        if score > high_scores["Snake"]:
                            high_scores["Snake"] = score
                        update_ui()
                        golden_apple = None
                    elif time.time() - golden_timer > 5.0:
                        golden_apple = None

                pen.clearstamps()

                pen.color("gray")
                for rock in rocks:
                    pen.goto(rock[0], rock[1])
                    pen.stamp()

                pen.color("red")
                pen.goto(food[0], food[1])
                pen.stamp()
                if golden_apple:
                    pen.color("gold")
                    pen.goto(golden_apple[0], golden_apple[1])
                    pen.stamp()

                pen.color("lime")
                pen.goto(head[0], head[1])
                pen.stamp()

                for i, segment in enumerate(body):
                    shade = max(50, 255 - (i * 5))
                    pen.color((0, shade / 255.0, 0))
                    pen.goto(segment[0], segment[1])
                    pen.stamp()

        if restart:
            continue
        break

    main_menu()


# =====================================================================
# 3. TETRIS
# =====================================================================

def play_tetris():
    while True:
        clear_bindings()
        reset_screen("Tetris - Press ESC to Menu")

        cols, rows = 10, 20
        block_size = 25
        board = [[0] * cols for _ in range(rows)]

        SHAPES = [
            [[1, 1, 1, 1]],
            [[1, 1], [1, 1]],
            [[0, 1, 0], [1, 1, 1]],
            [[1, 0, 0], [1, 1, 1]],
            [[0, 0, 1], [1, 1, 1]],
            [[0, 1, 1], [1, 1, 0]],
            [[1, 1, 0], [0, 1, 1]]
        ]
        COLORS = ["cyan", "yellow", "purple", "orange", "blue", "green", "red"]

        pen = turtle.Turtle()
        pen.shape("square")
        pen.shapesize(block_size / 20)
        pen.penup()
        pen.speed(0)

        score, level, lines_cleared = 0, 1, 0
        speed_scale = get_turtle_speed_scalar()
        base_drop_speed = {"Easy": 0.62, "Normal": 0.5, "Hard": 0.4}[settings["difficulty"]] / speed_scale
        min_drop_speed = max(0.06, 0.1 / speed_scale)
        drop_speed = base_drop_speed

        ui_pen = build_text_pen("white", 16, False)
        pause_pen = build_text_pen("white", 28, True)
        status_pen = build_text_pen("white", 30, True)
        controls_pen = build_text_pen("gray", 14, False)
        write_controls(controls_pen, ["Arrows/WASD: Move", "Space: Hard Drop  C: Hold", "P: Pause  R: Restart  ESC: Menu"], y=-260)

        def update_ui():
            ui_pen.clear()
            write_text(ui_pen, "TETRIS", 150, 180, font=("Courier", 28, "bold"), align="left")
            write_text(ui_pen, f"Score: {score}", 150, 120, align="left")
            write_text(ui_pen, f"Level: {level}", 150, 90, align="left")
            write_text(ui_pen, f"Lines: {lines_cleared}", 150, 60, align="left")
            write_text(ui_pen, f"High : {high_scores['Tetris']}", 150, 30, align="left")
            write_text(ui_pen, "Next Piece:", 150, -20, align="left")
            write_text(ui_pen, "Hold:", 150, -140, align="left")

        update_ui()

        class Piece:
            def __init__(self, idx=None):
                if idx is None:
                    idx = random.randint(0, len(SHAPES) - 1)
                self.shape = SHAPES[idx]
                self.color = COLORS[idx]
                self.x = cols // 2 - len(self.shape[0]) // 2
                self.y = 0

        current_piece = Piece()
        next_piece = Piece()
        hold_piece = None
        hold_used = False
        keys = {"Escape": False, "Pause": False, "Restart": False, "game_over": False}

        def check_collision(piece, offset_x=0, offset_y=0):
            for y, row in enumerate(piece.shape):
                for x, val in enumerate(row):
                    if val:
                        nx, ny = piece.x + x + offset_x, piece.y + y + offset_y
                        if nx < 0 or nx >= cols or ny >= rows:
                            return True
                        if ny >= 0 and board[ny][nx]:
                            return True
            return False

        def freeze(piece):
            for y, row in enumerate(piece.shape):
                for x, val in enumerate(row):
                    if val and piece.y + y >= 0:
                        board[piece.y + y][piece.x + x] = piece.color
            clear_lines()

        def clear_lines():
            nonlocal score, lines_cleared, level, drop_speed
            cleared = [i for i, row in enumerate(board) if all(row)]
            if cleared:
                for i in cleared:
                    del board[i]
                    board.insert(0, [0] * cols)
                pts = {1: 100, 2: 300, 3: 500, 4: 800}
                score += pts.get(len(cleared), 0) * level
                lines_cleared += len(cleared)
                level = (lines_cleared // 10) + 1
                drop_speed = max(min_drop_speed, base_drop_speed - (level * (0.05 / speed_scale)))
                if score > high_scores["Tetris"]:
                    high_scores["Tetris"] = score
                update_ui()

        def rotate():
            if keys["game_over"] or keys.get("Pause"):
                return
            new_shape = [list(row) for row in zip(*current_piece.shape[::-1])]
            old_shape = current_piece.shape
            current_piece.shape = new_shape
            if check_collision(current_piece):
                current_piece.x -= 1
                if check_collision(current_piece):
                    current_piece.x += 2
                    if check_collision(current_piece):
                        current_piece.x -= 1
                        current_piece.shape = old_shape

        def move_left():
            if not keys["game_over"] and not keys.get("Pause") and not check_collision(current_piece, offset_x=-1):
                current_piece.x -= 1

        def move_right():
            if not keys["game_over"] and not keys.get("Pause") and not check_collision(current_piece, offset_x=1):
                current_piece.x += 1

        def soft_drop():
            if not keys["game_over"] and not keys.get("Pause"):
                if not check_collision(current_piece, offset_y=1):
                    current_piece.y += 1
                else:
                    freeze(current_piece)
                    next_turn()

        def hard_drop():
            if not keys["game_over"] and not keys.get("Pause"):
                while not check_collision(current_piece, offset_y=1):
                    current_piece.y += 1
                freeze(current_piece)
                next_turn()

        def next_turn():
            nonlocal current_piece, next_piece, hold_used
            current_piece = next_piece
            next_piece = Piece()
            hold_used = False
            if check_collision(current_piece):
                keys["game_over"] = True

        def swap_hold():
            nonlocal hold_piece, current_piece, next_piece, hold_used
            if hold_used or keys["game_over"] or keys.get("Pause"):
                return
            if hold_piece is None:
                hold_piece = current_piece
                current_piece = next_piece
                next_piece = Piece()
            else:
                hold_piece, current_piece = current_piece, hold_piece
            current_piece.x = cols // 2 - len(current_piece.shape[0]) // 2
            current_piece.y = 0
            hold_used = True

        wn.listen()
        wn.onkeypress(rotate, "Up")
        wn.onkeypress(rotate, "w")
        wn.onkeypress(move_left, "Left")
        wn.onkeypress(move_left, "a")
        wn.onkeypress(move_right, "Right")
        wn.onkeypress(move_right, "d")
        wn.onkeypress(soft_drop, "Down")
        wn.onkeypress(soft_drop, "s")
        wn.onkeypress(hard_drop, "space")
        wn.onkeypress(swap_hold, "c")
        bind_common(keys)

        last_drop = time.time()
        off_x, off_y = -150, (rows * block_size) / 2

        border = turtle.Turtle()
        border.hideturtle()
        border.speed(0)
        border.color("gray")
        border.penup()
        border.goto(off_x - 5, off_y + 5)
        border.pendown()
        for _ in range(2):
            border.forward(cols * block_size + 10)
            border.right(90)
            border.forward(rows * block_size + 10)
            border.right(90)

        game_running = True
        restart = False
        while game_running:
            if keys["Escape"]:
                break
            if keys["Restart"]:
                restart = True
                break
            if handle_pause(keys, pause_pen):
                continue

            if not keys["game_over"]:
                if time.time() - last_drop > drop_speed:
                    if not check_collision(current_piece, offset_y=1):
                        current_piece.y += 1
                    else:
                        freeze(current_piece)
                        next_turn()
                    last_drop = time.time()

            pen.clearstamps()

            for y, row in enumerate(board):
                for x, val in enumerate(row):
                    if val:
                        pen.color(val)
                        pen.goto(off_x + x * block_size + block_size / 2, off_y - y * block_size - block_size / 2)
                        pen.stamp()

            status_pen.clear()
            if not keys["game_over"]:
                ghost_y = current_piece.y
                while not check_collision(current_piece, offset_y=(ghost_y - current_piece.y + 1)):
                    ghost_y += 1
                pen.color("#333333")
                for y, row in enumerate(current_piece.shape):
                    for x, val in enumerate(row):
                        if val:
                            pen.goto(off_x + (current_piece.x + x) * block_size + block_size / 2,
                                    off_y - (ghost_y + y) * block_size - block_size / 2)
                            pen.stamp()

                pen.color(current_piece.color)
                for y, row in enumerate(current_piece.shape):
                    for x, val in enumerate(row):
                        if val:
                            pen.goto(off_x + (current_piece.x + x) * block_size + block_size / 2,
                                    off_y - (current_piece.y + y) * block_size - block_size / 2)
                            pen.stamp()

                pen.color(next_piece.color)
                for y, row in enumerate(next_piece.shape):
                    for x, val in enumerate(row):
                        if val:
                            pen.goto(180 + x * block_size, -70 - y * block_size)
                            pen.stamp()

                if hold_piece:
                    pen.color(hold_piece.color)
                    for y, row in enumerate(hold_piece.shape):
                        for x, val in enumerate(row):
                            if val:
                                pen.goto(180 + x * block_size, -190 - y * block_size)
                                pen.stamp()
            else:
                write_text(status_pen, "GAME OVER", off_x + (cols * block_size) / 2, 0,
                           font=("Courier", 30, "bold"))

            wn.update()
            time.sleep(0.02)

        if restart:
            continue
        break

    main_menu()


# =====================================================================
# 4. SPACE INVADERS
# =====================================================================

def play_space_invaders():
    while True:
        clear_bindings()
        reset_screen("Space Invaders - Press ESC to Menu")

        stars, star_pen = make_starfield(60)

        player = turtle.Turtle()
        player.color("green")
        player.shape("triangle")
        player.shapesize(1.5)
        player.penup()
        player.speed(0)
        player.setheading(90)
        player.goto(0, -250)

        bullet = turtle.Turtle()
        bullet.color("yellow")
        bullet.shape("square")
        bullet.shapesize(0.5, 0.2)
        bullet.penup()
        bullet.hideturtle()
        bullet_state = "ready"

        enemy_bullets = []
        explosions = []
        ufo = turtle.Turtle()
        ufo.color("red")
        ufo.shape("square")
        ufo.shapesize(0.5, 2)
        ufo.penup()
        ufo.hideturtle()
        ufo.goto(-500, 260)
        ufo_active = False

        shields = []
        shield_positions = [-200, 0, 200]
        for x in shield_positions:
            shield = turtle.Turtle()
            shield.shape("square")
            shield.shapesize(1, 3)
            shield.color("green")
            shield.penup()
            shield.goto(x, -170)
            shields.append({"t": shield, "hp": 3})

        def update_shield(shield):
            colors = {3: "green", 2: "yellow", 1: "orange"}
            if shield["hp"] <= 0:
                shield["t"].hideturtle()
            else:
                shield["t"].color(colors[shield["hp"]])

        enemies = []
        wave = 1
        speed_scale = get_turtle_speed_scalar()
        difficulty_scale = get_difficulty_scalar(easy=0.85, normal=1.0, hard=1.2)
        player_speed = 6 * speed_scale
        bullet_speed = 15 * speed_scale
        enemy_bullet_chance = 0.0015 * difficulty_scale
        ufo_spawn_chance = 0.002 * difficulty_scale

        def spawn_wave():
            enemies.clear()
            colors = ["cyan", "magenta", "orange", "yellow"]
            rows = 3 + min(2, wave // 2)
            for i, y in enumerate(range(110, 110 + rows * 40, 40)):
                for x in range(-250, 250, 60):
                    e = turtle.Turtle()
                    e.color(colors[i % len(colors)])
                    e.shape("circle")
                    e.penup()
                    e.goto(x, y)
                    enemies.append(e)

        spawn_wave()

        enemy_speed = (1.4 + (wave * 0.2)) * difficulty_scale * speed_scale
        score, lives = 0, 3

        ui_pen = build_text_pen("white", 18, True)
        pause_pen = build_text_pen("white", 28, True)
        status_pen = build_text_pen("white", 40, True)
        controls_pen = build_text_pen("gray", 14, False)
        write_controls(controls_pen, ["A/D or Left/Right: Move", "Space: Fire  P: Pause  R: Restart  ESC: Menu"])

        def update_ui():
            ui_pen.clear()
            write_text(ui_pen, f"Score: {score}  High: {high_scores['Space Invaders']}  Wave: {wave}", -380, 260, align="left",
                       font=("Courier", 16, "bold"))
            hearts = '\u2665' * lives  # <--- FIXED
            write_text(ui_pen, f"Lives: {hearts}", 380, 260, align="right",  # <--- FIXED
                       font=("Courier", 16, "bold"))

        update_ui()

        keys = {"Left": False, "Right": False, "Escape": False, "Pause": False, "Restart": False, "game_over": False}

        def fire():
            nonlocal bullet_state
            if bullet_state == "ready" and not keys["game_over"] and not keys.get("Pause"):
                bullet_state = "fire"
                bullet.goto(player.xcor(), player.ycor() + 15)
                bullet.showturtle()

        wn.listen()
        wn.onkeypress(lambda: keys.update({"Left": True}), "Left")
        wn.onkeypress(lambda: keys.update({"Right": True}), "Right")
        wn.onkeypress(lambda: keys.update({"Left": True}), "a")
        wn.onkeypress(lambda: keys.update({"Right": True}), "d")
        wn.onkeyrelease(lambda: keys.update({"Left": False}), "Left")
        wn.onkeyrelease(lambda: keys.update({"Right": False}), "Right")
        wn.onkeyrelease(lambda: keys.update({"Left": False}), "a")
        wn.onkeyrelease(lambda: keys.update({"Right": False}), "d")
        wn.onkeypress(fire, "space")
        bind_common(keys)

        game_running = True
        restart = False
        while game_running:
            if keys["Escape"]:
                break
            if keys["Restart"]:
                restart = True
                break
            if handle_pause(keys, pause_pen):
                continue

            update_starfield(stars, star_pen)

            if keys["game_over"]:
                wn.update()
                time.sleep(0.05)
                continue

            if keys["Left"] and player.xcor() > -380:
                player.setx(player.xcor() - player_speed)
            if keys["Right"] and player.xcor() < 380:
                player.setx(player.xcor() + player_speed)

            if bullet_state == "fire":
                bullet.sety(bullet.ycor() + bullet_speed)
                if bullet.ycor() > 280:
                    bullet.hideturtle()
                    bullet_state = "ready"

            if not ufo_active and random.random() < ufo_spawn_chance:
                ufo_active = True
                ufo.goto(-450, 260)
                ufo.showturtle()

            if ufo_active:
                ufo.setx(ufo.xcor() + 3)
                if ufo.xcor() > 450:
                    ufo_active = False
                    ufo.hideturtle()
                if bullet_state == "fire" and ufo.distance(bullet) < 30:
                    score += 100
                    if score > high_scores["Space Invaders"]:
                        high_scores["Space Invaders"] = score
                    update_ui()
                    ufo_active = False
                    ufo.hideturtle()
                    bullet.hideturtle()
                    bullet_state = "ready"
                    bullet.goto(1000, 1000)

            move_down = False
            for e in enemies:
                e.setx(e.xcor() + enemy_speed)
                if e.xcor() > 370 or e.xcor() < -370:
                    move_down = True
                if random.random() < enemy_bullet_chance:
                    eb = turtle.Turtle()
                    eb.color("red")
                    eb.shape("square")
                    eb.shapesize(0.4, 0.2)
                    eb.penup()
                    eb.goto(e.xcor(), e.ycor() - 10)
                    enemy_bullets.append(eb)

            if move_down:
                enemy_speed *= -1.05
                for e in enemies:
                    e.sety(e.ycor() - 30)
                    if e.ycor() < -230:
                        lives = 0
                        update_ui()

            for eb in enemy_bullets[:]:
                eb.sety(eb.ycor() - 5)
                if eb.ycor() < -300:
                    eb.hideturtle()
                    enemy_bullets.remove(eb)
                    continue
                hit_shield = False
                for shield in shields:
                    if shield["hp"] > 0 and eb.distance(shield["t"]) < 25:
                        shield["hp"] -= 1
                        update_shield(shield)
                        eb.hideturtle()
                        enemy_bullets.remove(eb)
                        hit_shield = True
                        break
                if hit_shield:
                    continue
                if eb.distance(player) < 20:
                    lives -= 1
                    update_ui()
                    eb.hideturtle()
                    enemy_bullets.remove(eb)
                    player.color("red")
                    wn.update()
                    time.sleep(0.1)
                    player.color("green")
                    if lives <= 0:
                        keys["game_over"] = True

            for e in enemies[:]:
                if bullet_state == "fire" and e.distance(bullet) < 20:
                    explosions.append({"x": e.xcor(), "y": e.ycor(), "timer": 10})
                    bullet.hideturtle()
                    bullet_state = "ready"
                    bullet.goto(1000, 1000)
                    e.hideturtle()
                    enemies.remove(e)
                    score += 10
                    if score > high_scores["Space Invaders"]:
                        high_scores["Space Invaders"] = score
                    update_ui()

            for shield in shields:
                if shield["hp"] > 0 and bullet_state == "fire" and bullet.distance(shield["t"]) < 25:
                    shield["hp"] -= 1
                    update_shield(shield)
                    bullet.hideturtle()
                    bullet_state = "ready"
                    bullet.goto(1000, 1000)

            for exp in explosions[:]:
                star_pen.goto(exp["x"], exp["y"])
                star_pen.dot(exp["timer"] * 2, "orange")
                exp["timer"] -= 1
                if exp["timer"] <= 0:
                    explosions.remove(exp)

            if len(enemies) == 0 and not keys["game_over"]:
                wave += 1
                enemy_speed = (1.4 + (wave * 0.2)) * difficulty_scale * speed_scale
                spawn_wave()
                lives = min(5, lives + 1)
                update_ui()

            status_pen.clear()
            if keys["game_over"] and len(enemies) > 0:
                write_text(status_pen, "GAME OVER", 0, 0, font=("Courier", 40, "bold"))

            wn.update()
            time.sleep(0.02)

        if restart:
            continue
        break

    main_menu()


# =====================================================================
# 5. ATARI BREAKOUT
# =====================================================================
def play_breakout():
    while True:
        clear_bindings()
        reset_screen("Breakout - Press ESC to Menu")

        score = 0
        lives = 3
        level = 1
        combo = 0

        ui_pen = build_text_pen("white", 18, True)
        pause_pen = build_text_pen("white", 28, True)
        status_pen = build_text_pen("white", 28, True)
        controls_pen = build_text_pen("gray", 14, False)
        write_controls(controls_pen, ["A/D or Left/Right: Move", "Space: Launch  P: Pause  R: Restart  ESC: Menu"])

        def update_ui():
            ui_pen.clear()
            write_text(ui_pen, f"Score: {score}  Level: {level}  Combo: {combo}  High: {high_scores['Breakout']}", -380, 260,
                       align="left", font=("Courier", 16, "bold"))
            hearts = '\u2665' * lives  # <--- FIXED
            write_text(ui_pen, f"Lives: {hearts}", 380, 260, align="right", font=("Courier", 16, "bold"))  # <--- FIXED

        update_ui()

        paddle = turtle.Turtle()
        paddle.shape("square")
        paddle.color("cyan")
        paddle.shapesize(stretch_wid=0.5, stretch_len=5)
        paddle.penup()
        paddle.goto(0, -250)

        ball = turtle.Turtle()
        ball.shape("square")
        ball.color("white")
        ball.shapesize(stretch_wid=0.5, stretch_len=0.5)
        ball.penup()
        ball.goto(0, -230)

        trail_pen = turtle.Turtle()
        trail_pen.shape("square")
        trail_pen.shapesize(0.5, 0.5)
        trail_pen.color("gray")
        trail_pen.penup()
        trail_pen.hideturtle()
        trail_stamps = []

        explosions = []
        particle_pen = turtle.Turtle()
        particle_pen.hideturtle()
        particle_pen.penup()

        speed_scale = get_turtle_speed_scalar()
        difficulty_scale = get_difficulty_scalar(easy=0.9, normal=1.0, hard=1.15)
        paddle_speed = 8 * speed_scale
        ball_speed = 6.0 * difficulty_scale * speed_scale
        speed_multiplier = 1.0
        ball.dx = 0
        ball.dy = 0
        ball_active = False

        powerups = []
        expand_until = 0
        slow_until = 0

        bricks = []
        colors = ["red", "orange", "yellow", "green", "blue"]

        def build_level():
            for b in bricks:
                b.hideturtle()
            bricks.clear()

            start_y = 200
            for row in range(5):
                for col in range(10):
                    b = turtle.Turtle()
                    b.shape("square")
                    b.shapesize(stretch_wid=1, stretch_len=3.5)
                    b.color(colors[row % len(colors)])
                    b.penup()
                    b.goto(-337.5 + (col * 75), start_y - (row * 30))
                    bricks.append(b)

        def apply_speed_multiplier():
            if ball_active:
                current = math.hypot(ball.dx, ball.dy)
                target = ball_speed * speed_multiplier
                if current > 0:
                    ball.dx = ball.dx / current * target
                    ball.dy = ball.dy / current * target

        build_level()

        keys = {"Left": False, "Right": False, "Escape": False, "Pause": False, "Restart": False}

        def launch_ball():
            nonlocal ball_active
            if not ball_active and lives > 0:
                ball_active = True
                ball.dx = ball_speed * speed_multiplier * math.cos(math.pi / 2)
                ball.dy = ball_speed * speed_multiplier * math.sin(math.pi / 2)

        wn.listen()
        wn.onkeypress(lambda: keys.update({"Left": True}), "Left")
        wn.onkeypress(lambda: keys.update({"Right": True}), "Right")
        wn.onkeypress(lambda: keys.update({"Left": True}), "a")
        wn.onkeypress(lambda: keys.update({"Right": True}), "d")
        wn.onkeyrelease(lambda: keys.update({"Left": False}), "Left")
        wn.onkeyrelease(lambda: keys.update({"Right": False}), "Right")
        wn.onkeyrelease(lambda: keys.update({"Left": False}), "a")
        wn.onkeyrelease(lambda: keys.update({"Right": False}), "d")
        wn.onkeypress(launch_ball, "space")
        bind_common(keys)

        game_running = True
        restart = False
        while game_running:
            if keys["Escape"]:
                break
            if keys["Restart"]:
                restart = True
                break
            if handle_pause(keys, pause_pen):
                continue

            particle_pen.clear()
            for exp in explosions[:]:
                particle_pen.goto(exp["x"], exp["y"])
                particle_pen.dot(exp["timer"] * 2.5, exp["color"])
                exp["timer"] -= 1
                if exp["timer"] <= 0:
                    explosions.remove(exp)

            if keys["Left"] and paddle.xcor() > -340:
                paddle.setx(paddle.xcor() - paddle_speed)
            if keys["Right"] and paddle.xcor() < 340:
                paddle.setx(paddle.xcor() + paddle_speed)

            if expand_until and time.time() > expand_until:
                paddle.shapesize(stretch_wid=0.5, stretch_len=5)
                expand_until = 0

            if slow_until and time.time() > slow_until:
                speed_multiplier = 1.0
                apply_speed_multiplier()
                slow_until = 0

            for p in powerups[:]:
                p["t"].sety(p["t"].ycor() - (4 * speed_scale))
                if p["t"].ycor() < -290:
                    p["t"].hideturtle()
                    powerups.remove(p)
                    continue
                if p["t"].distance(paddle) < 40:
                    if p["type"] == "expand":
                        paddle.shapesize(stretch_wid=0.5, stretch_len=7)
                        expand_until = time.time() + 8
                    else:
                        speed_multiplier = 0.7
                        apply_speed_multiplier()
                        slow_until = time.time() + 8
                    p["t"].hideturtle()
                    powerups.remove(p)

            status_pen.clear()
            if not ball_active:
                update_ui()
                ball.setx(paddle.xcor())
                ball.sety(paddle.ycor() + 15)
                if lives <= 0:
                    write_text(status_pen, "GAME OVER", 0, 0, font=("Courier", 40, "bold"))
                else:
                    write_text(status_pen, "PRESS SPACE TO LAUNCH", 0, -50, font=("Courier", 16, "normal"))
            else:
                update_ui()

                trail_pen.goto(ball.xcor(), ball.ycor())
                trail_stamps.append(trail_pen.stamp())
                if len(trail_stamps) > 5:
                    trail_pen.clearstamp(trail_stamps.pop(0))

                ball.setx(ball.xcor() + ball.dx)
                ball.sety(ball.ycor() + ball.dy)

                if ball.xcor() > 390:
                    ball.setx(390)
                    ball.dx *= -1
                elif ball.xcor() < -390:
                    ball.setx(-390)
                    ball.dx *= -1

                if ball.ycor() > 290:
                    ball.sety(290)
                    ball.dy *= -1

                if ball.ycor() < -290:
                    lives -= 1
                    combo = 0
                    ball_active = False
                    trail_pen.clearstamps()
                    trail_stamps.clear()
                    update_ui()

                if (ball.ycor() > -245 and ball.ycor() < -235) and \
                        (paddle.xcor() - 55 < ball.xcor() < paddle.xcor() + 55) and ball.dy < 0:
                    ball.sety(-235)
                    offset = (ball.xcor() - paddle.xcor()) / 50.0
                    angle = (math.pi / 2) - (offset * 1.2)
                    ball.dx = ball_speed * speed_multiplier * math.cos(angle)
                    ball.dy = ball_speed * speed_multiplier * math.sin(angle)

                active_bricks = 0
                for b in bricks:
                    if b.isvisible():
                        active_bricks += 1
                        if abs(ball.xcor() - b.xcor()) < 40 and abs(ball.ycor() - b.ycor()) < 15:
                            b.hideturtle()

                            ovX = 40 - abs(ball.xcor() - b.xcor())
                            ovY = 15 - abs(ball.ycor() - b.ycor())

                            if ovX < ovY:
                                ball.dx *= -1
                            else:
                                ball.dy *= -1

                            combo += 1
                            score += 10 + (combo * 2)
                            if score > high_scores["Breakout"]:
                                high_scores["Breakout"] = score
                            update_ui()

                            if random.random() < 0.2:
                                p = turtle.Turtle()
                                p.shape("circle")
                                p.shapesize(0.6)
                                p.penup()
                                p_type = random.choice(["expand", "slow"])
                                p.color("cyan" if p_type == "expand" else "purple")
                                p.goto(b.xcor(), b.ycor())
                                powerups.append({"t": p, "type": p_type})

                            explosions.append({"x": b.xcor(), "y": b.ycor(), "timer": 10, "color": b.color()[0]})
                            break

                if active_bricks == 0:
                    level += 1
                    ball_speed += 0.5 * difficulty_scale
                    ball_active = False
                    trail_pen.clearstamps()
                    trail_stamps.clear()
                    build_level()
                    update_ui()

            wn.update()
            time.sleep(0.01)

        if restart:
            continue
        break

    main_menu()


# =====================================================================
# 6. ASTEROID DODGER
# =====================================================================

def play_asteroid_dodger():
    while True:
        clear_bindings()
        reset_screen("Asteroid Dodger - Press ESC to Menu")

        stars, star_pen = make_starfield(70)

        player = turtle.Turtle()
        player.color("cyan")
        player.shape("triangle")
        player.shapesize(1.2)
        player.penup()
        player.setheading(90)
        player.goto(0, -220)

        asteroids = []
        powerups = []
        score = 0
        lives = 3
        shield_charges = 0
        last_spawn = time.time()
        last_power = time.time()
        speed_scale = get_turtle_speed_scalar()
        difficulty_scale = get_difficulty_scalar(easy=0.85, normal=1.0, hard=1.2)
        player_speed = 6 * speed_scale
        spawn_interval = max(0.35, 0.6 / difficulty_scale / speed_scale)
        power_spawn_interval = max(5.5, 8 / speed_scale)

        ui_pen = build_text_pen("white", 16, True)
        pause_pen = build_text_pen("white", 28, True)
        status_pen = build_text_pen("white", 40, True)
        controls_pen = build_text_pen("gray", 14, False)
        write_controls(controls_pen, ["Arrows/WASD: Move", "P: Pause  R: Restart  ESC: Menu"])

        def update_ui():
            ui_pen.clear()
            write_text(ui_pen, f"Score: {score}  High: {high_scores['Asteroid Dodger']}", -380, 260,
                       align="left", font=("Courier", 16, "bold"))
            hearts = '\u2665' * lives  # <--- FIXED
            write_text(ui_pen, f"Lives: {hearts}  Shield: {shield_charges}", 380, 260,
                       align="right", font=("Courier", 16, "bold"))  # <--- FIXED

        update_ui()
        keys = {"Left": False, "Right": False, "Up": False, "Down": False,
                "Escape": False, "Pause": False, "Restart": False}

        wn.listen()
        wn.onkeypress(lambda: keys.update({"Left": True}), "Left")
        wn.onkeypress(lambda: keys.update({"Right": True}), "Right")
        wn.onkeypress(lambda: keys.update({"Up": True}), "Up")
        wn.onkeypress(lambda: keys.update({"Down": True}), "Down")
        wn.onkeypress(lambda: keys.update({"Left": True}), "a")
        wn.onkeypress(lambda: keys.update({"Right": True}), "d")
        wn.onkeypress(lambda: keys.update({"Up": True}), "w")
        wn.onkeypress(lambda: keys.update({"Down": True}), "s")
        wn.onkeyrelease(lambda: keys.update({"Left": False}), "Left")
        wn.onkeyrelease(lambda: keys.update({"Right": False}), "Right")
        wn.onkeyrelease(lambda: keys.update({"Up": False}), "Up")
        wn.onkeyrelease(lambda: keys.update({"Down": False}), "Down")
        wn.onkeyrelease(lambda: keys.update({"Left": False}), "a")
        wn.onkeyrelease(lambda: keys.update({"Right": False}), "d")
        wn.onkeyrelease(lambda: keys.update({"Up": False}), "w")
        wn.onkeyrelease(lambda: keys.update({"Down": False}), "s")
        bind_common(keys)

        game_running = True
        restart = False
        game_over = False
        while game_running:
            if keys["Escape"]:
                break
            if keys["Restart"]:
                restart = True
                break
            if handle_pause(keys, pause_pen):
                continue

            update_starfield(stars, star_pen, multiplier=1.2)

            status_pen.clear()
            if not game_over:
                if keys["Left"] and player.xcor() > -370:
                    player.setx(player.xcor() - player_speed)
                if keys["Right"] and player.xcor() < 370:
                    player.setx(player.xcor() + player_speed)
                if keys["Up"] and player.ycor() < 250:
                    player.sety(player.ycor() + player_speed)
                if keys["Down"] and player.ycor() > -260:
                    player.sety(player.ycor() - player_speed)

                if time.time() - last_spawn > spawn_interval:
                    a = turtle.Turtle()
                    a.shape("circle")
                    a.shapesize(random.uniform(0.6, 1.4))
                    a.color(random.choice(["gray", "light gray", "white"]))
                    a.penup()
                    a.goto(random.randint(-380, 380), 320)
                    a.speed_val = random.uniform(3.5, 6.5) * difficulty_scale * speed_scale
                    asteroids.append(a)
                    last_spawn = time.time()

                if time.time() - last_power > power_spawn_interval and random.random() < 0.3:
                    p = turtle.Turtle()
                    p.shape("triangle")
                    p.shapesize(0.8)
                    p.color("gold")
                    p.penup()
                    p.goto(random.randint(-350, 350), 320)
                    powerups.append(p)
                    last_power = time.time()

                for a in asteroids[:]:
                    a.sety(a.ycor() - a.speed_val)
                    if a.ycor() < -320:
                        score += 2
                        a.hideturtle()
                        asteroids.remove(a)
                        if score > high_scores["Asteroid Dodger"]:
                            high_scores["Asteroid Dodger"] = score
                        update_ui()
                        continue
                    if a.distance(player) < 20:
                        if shield_charges > 0:
                            shield_charges -= 1
                        else:
                            lives -= 1
                        a.hideturtle()
                        asteroids.remove(a)
                        update_ui()
                        player.color("red")
                        wn.update()
                        time.sleep(0.1)
                        player.color("cyan")
                        if lives <= 0:
                            game_over = True

                for p in powerups[:]:
                    p.sety(p.ycor() - (4 * speed_scale))
                    if p.ycor() < -320:
                        p.hideturtle()
                        powerups.remove(p)
                        continue
                    if p.distance(player) < 20:
                        shield_charges += 1
                        p.hideturtle()
                        powerups.remove(p)
                        update_ui()

                if score > high_scores["Asteroid Dodger"]:
                    high_scores["Asteroid Dodger"] = score

            else:
                write_text(status_pen, "GAME OVER", 0, 0, font=("Courier", 40, "bold"))

            wn.update()
            time.sleep(0.02)

        if restart:
            continue
        break

    main_menu()


# =====================================================================
# 7. FLAPPY TURTLE
# =====================================================================

def play_flappy_turtle():
    while True:
        clear_bindings()
        reset_screen("Flappy Turtle - Press ESC to Menu")

        player = turtle.Turtle()
        player.shape("turtle")
        player.color("lime")
        player.penup()
        player.goto(-200, 0)

        pipes = []
        stars, star_pen = make_starfield(50, 0.2, 1.2)

        speed_scale = get_turtle_speed_scalar()
        difficulty_scale = get_difficulty_scalar(easy=0.85, normal=1.0, hard=1.2)
        velocity = 0
        gravity = -0.4 * difficulty_scale * speed_scale
        flap_strength = 8 * speed_scale
        last_pipe = time.time()
        pipe_gap = int(140 / difficulty_scale)
        pipe_speed = 3.5 * difficulty_scale * speed_scale
        pipe_interval = max(1.4, 2.2 / speed_scale)

        score = 0
        game_over = False

        ui_pen = build_text_pen("white", 18, True)
        pause_pen = build_text_pen("white", 28, True)
        status_pen = build_text_pen("white", 40, True)
        controls_pen = build_text_pen("gray", 14, False)
        write_controls(controls_pen, ["Space/Up/W: Flap", "P: Pause  R: Restart  ESC: Menu"])

        def update_ui():
            ui_pen.clear()
            write_text(ui_pen, f"Score: {score}  High: {high_scores['Flappy Turtle']}", 0, 260,
                       font=("Courier", 16, "bold"))

        def flap():
            nonlocal velocity
            status_pen.clear()
            if not game_over:
                velocity = flap_strength

        def spawn_pipe():
            gap_y = random.randint(-120, 120)
            top = turtle.Turtle()
            top.shape("square")
            top.shapesize(stretch_wid=12, stretch_len=2)
            top.color("green")
            top.penup()
            top.goto(420, gap_y + (pipe_gap / 2) + 120)
            bottom = turtle.Turtle()
            bottom.shape("square")
            bottom.shapesize(stretch_wid=12, stretch_len=2)
            bottom.color("green")
            bottom.penup()
            bottom.goto(420, gap_y - (pipe_gap / 2) - 120)
            pipes.append({"top": top, "bottom": bottom, "x": 420, "gap": gap_y, "scored": False})

        update_ui()

        keys = {"Escape": False, "Pause": False, "Restart": False}
        wn.listen()
        wn.onkeypress(flap, "space")
        wn.onkeypress(flap, "Up")
        wn.onkeypress(flap, "w")
        bind_common(keys)

        game_running = True
        restart = False
        while game_running:
            if keys["Escape"]:
                break
            if keys["Restart"]:
                restart = True
                break
            if handle_pause(keys, pause_pen):
                continue

            update_starfield(stars, star_pen, multiplier=0.7)

            if not game_over:
                velocity += gravity
                player.sety(player.ycor() + velocity)

                if player.ycor() > 260 or player.ycor() < -260:
                    game_over = True

                if time.time() - last_pipe > pipe_interval:
                    spawn_pipe()
                    last_pipe = time.time()

                for pipe in pipes[:]:
                    pipe["x"] -= pipe_speed
                    pipe["top"].setx(pipe["x"])
                    pipe["bottom"].setx(pipe["x"])

                    if pipe["x"] < -450:
                        pipe["top"].hideturtle()
                        pipe["bottom"].hideturtle()
                        pipes.remove(pipe)
                        continue

                    if not pipe["scored"] and pipe["x"] < player.xcor():
                        score += 1
                        pipe["scored"] = True
                        if score > high_scores["Flappy Turtle"]:
                            high_scores["Flappy Turtle"] = score
                        update_ui()

                    if abs(pipe["x"] - player.xcor()) < 25:
                        if player.ycor() > pipe["gap"] + (pipe_gap / 2) or player.ycor() < pipe["gap"] - (pipe_gap / 2):
                            game_over = True

            if game_over:
                write_text(status_pen, "GAME OVER", 0, 0, font=("Courier", 40, "bold"))

            wn.update()
            time.sleep(0.02)

        if restart:
            continue
        break

    main_menu()


# =====================================================================
# MAIN MENU
# =====================================================================

def main_menu():
    clear_bindings()
    reset_screen("Python Arcade - Ultimate Edition")

    stars, star_pen = make_starfield(100, 0.2, 1.5)

    title_pen = turtle.Turtle()
    title_pen.speed(0)
    title_pen.color("cyan")
    title_pen.penup()
    title_pen.hideturtle()
    title_pen.goto(0, 190)
    title_pen.write("PYTHON ARCADE", align="center", font=("Courier", 48, "bold"))

    subtitle_pen = turtle.Turtle()
    subtitle_pen.speed(0)
    subtitle_pen.color("magenta")
    subtitle_pen.penup()
    subtitle_pen.hideturtle()
    subtitle_pen.goto(0, 150)
    subtitle_pen.write("ULTIMATE EDITION", align="center", font=("Courier", 20, "bold"))

    menu_pen = turtle.Turtle()
    menu_pen.speed(0)
    menu_pen.color("white")
    menu_pen.penup()
    menu_pen.hideturtle()

    options = [
        ("1. PONG", 100),
        ("2. SNAKE", 65),
        ("3. TETRIS", 30),
        ("4. SPACE INVADERS", -5),
        ("5. BREAKOUT", -40),
        ("6. ASTEROID DODGER", -75),
        ("7. FLAPPY TURTLE", -110)
    ]

    def draw_menu_text():
        menu_pen.clear()
        menu_pen.color("white")
        for text, y in options:
            menu_pen.goto(0, y)
            menu_pen.write(text, align="center", font=("Courier", 22, "bold"))

        menu_pen.goto(0, -165)
        menu_pen.color("cyan")
        menu_pen.write(f"Difficulty [D]: {settings['difficulty']}", align="center", font=("Courier", 16, "bold"))
        menu_pen.goto(0, -192)
        menu_pen.color("cyan")
        menu_pen.write(f"Turtle Speed [T]: {settings['turtle_speed']}", align="center", font=("Courier", 16, "bold"))
        menu_pen.goto(0, -235)
        menu_pen.color("gray")
        menu_pen.write("Press 1-7 to Play | D: Difficulty | T: Turtle Speed", align="center",
                       font=("Courier", 14, "normal"))
        menu_pen.goto(0, -255)
        menu_pen.write("In-game: P Pause | R Restart | ESC Menu", align="center", font=("Courier", 14, "normal"))

    draw_menu_text()

    in_menu = {"state": True}

    def start_game(func):
        in_menu["state"] = False
        func()

    def cycle_setting(key, allowed):
        current = settings[key]
        idx = allowed.index(current)
        settings[key] = allowed[(idx + 1) % len(allowed)]
        save_settings()
        draw_menu_text()

    wn.listen()
    wn.onkeypress(lambda: start_game(play_pong), "1")
    wn.onkeypress(lambda: start_game(play_snake), "2")
    wn.onkeypress(lambda: start_game(play_tetris), "3")
    wn.onkeypress(lambda: start_game(play_space_invaders), "4")
    wn.onkeypress(lambda: start_game(play_breakout), "5")
    wn.onkeypress(lambda: start_game(play_asteroid_dodger), "6")
    wn.onkeypress(lambda: start_game(play_flappy_turtle), "7")
    wn.onkeypress(lambda: cycle_setting("difficulty", DIFFICULTY_LEVELS), "d")
    wn.onkeypress(lambda: cycle_setting("turtle_speed", TURTLE_SPEED_LEVELS), "t")

    color_hue = 0
    while in_menu["state"]:
        update_starfield(stars, star_pen)

        color_hue = (color_hue + 5) % 360
        r, g, b = colorsys_hsv_to_rgb(color_hue / 360, 1.0, 1.0)
        title_pen.clear()
        title_pen.color((r, g, b))
        title_pen.goto(0, 190)
        title_pen.write("PYTHON ARCADE", align="center", font=("Courier", 48, "bold"))

        wn.update()
        time.sleep(0.03)


# Helper function for title colors

def colorsys_hsv_to_rgb(h, s, v):
    if s == 0.0:
        return v, v, v
    i = int(h * 6.)
    f = (h * 6.) - i
    p, q, t = v * (1. - s), v * (1. - s * f), v * (1. - s * (1. - f))
    i %= 6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q


if __name__ == "__main__":
    main_menu()
