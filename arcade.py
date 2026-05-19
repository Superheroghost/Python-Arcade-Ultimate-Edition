import turtle
import time
import random
import math

# --- GLOBAL SCREEN SETUP ---
wn = turtle.Screen()
wn.setup(width=800, height=600)
wn.bgcolor("black")
wn.title("Python Arcade - Ultimate Edition")

# --- HIGH SCORES ---
high_scores = {
    "Pong (A/B)": "N/A",  # Pong doesn't really have a high score in this format
    "Snake": 0,
    "Tetris": 0,
    "Space Invaders": 0,
    "Breakout": 0
}

def clear_bindings():
    """Removes all keyboard bindings to prevent input overlap between games."""
    keys_to_unbind = [
        "w", "s", "Up", "Down", "Left", "Right", "a", "d",
        "space", "Escape", "1", "2", "3", "4", "5", "r", "Return"
    ]
    for key in keys_to_unbind:
        wn.onkeypress(None, key)
        wn.onkeyrelease(None, key)


# =====================================================================
# 1. PONG
# =====================================================================
def play_pong():
    clear_bindings()
    wn.clearscreen()
    wn.bgcolor("black")
    wn.title("Pong - Press ESC to Menu")
    
    speed_input = wn.numinput("Pong", "Enter ball speed (1-10):", default=5, minval=1, maxval=20)
    if speed_input is None:
        speed_input = 5

    wn.tracer(0)

    score_a = 0
    score_b = 0
    
    # Net (Center line)
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

    # Paddles
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

    # Ball & Trail
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

    paddle_speed = 7

    pen = turtle.Turtle()
    pen.speed(0)
    pen.color("white")
    pen.penup()
    pen.hideturtle()
    pen.goto(0, 230)
    score_flash = 0
    
    def update_score():
        pen.clear()
        pen.write(f"{score_a}    {score_b}", align="center", font=("Courier", 36, "bold"))

    update_score()

    keys = {"w": False, "s": False, "Up": False, "Down": False, "Escape": False}
    
    def k_press(k): keys[k] = True
    def k_release(k): keys[k] = False

    wn.listen()
    for k in ["w", "s", "Up", "Down", "Escape"]:
        wn.onkeypress(lambda k=k: k_press(k), k)
        wn.onkeyrelease(lambda k=k: k_release(k), k)

    last_speed_up = time.time()
    game_running = True
    
    while game_running:
        wn.update()
        time.sleep(0.01)

        if keys["Escape"]: break

        # Progressive Speed
        if time.time() - last_speed_up > 2.0:
            if abs(ball.dx) < 15:
                ball.dx *= 1.02
                ball.dy *= 1.02
            last_speed_up = time.time()

        # Animations
        if paddle_a_flash > 0:
            paddle_a_flash -= 1
            if paddle_a_flash == 0: paddle_a.color("white")
        if paddle_b_flash > 0:
            paddle_b_flash -= 1
            if paddle_b_flash == 0: paddle_b.color("white")
        if score_flash > 0:
            score_flash -= 1
            if score_flash == 0:
                pen.color("white")
                update_score()

        # Paddle Movement
        if keys["w"] and paddle_a.ycor() < 240: paddle_a.sety(paddle_a.ycor() + paddle_speed)
        if keys["s"] and paddle_a.ycor() > -230: paddle_a.sety(paddle_a.ycor() - paddle_speed)
        if keys["Up"] and paddle_b.ycor() < 240: paddle_b.sety(paddle_b.ycor() + paddle_speed)
        if keys["Down"] and paddle_b.ycor() > -230: paddle_b.sety(paddle_b.ycor() - paddle_speed)

        # Trail
        trail_drawer.goto(ball.xcor(), ball.ycor())
        trail_stamps.append(trail_drawer.stamp())
        if len(trail_stamps) > 6:
            trail_drawer.clearstamp(trail_stamps.pop(0))

        # Ball Movement
        ball.setx(ball.xcor() + ball.dx)
        ball.sety(ball.ycor() + ball.dy)

        # Border Collision
        if ball.ycor() > 280:
            ball.sety(280)
            ball.dy *= -1
        elif ball.ycor() < -280:
            ball.sety(-280)
            ball.dy *= -1

        # Scoring
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
            trail_drawer.clearstamps()
            trail_stamps.clear()
            
            wn.update()
            time.sleep(2)
            last_speed_up = time.time()
            keys = {k: False for k in keys}

        # Paddle Collision
        if ball.dx > 0 and (340 < ball.xcor() < 350) and (paddle_b.ycor() - 50 < ball.ycor() < paddle_b.ycor() + 50):
            ball.setx(340)
            ball.dx *= -1
            paddle_b.color("red")
            paddle_b_flash = 10
            
        if ball.dx < 0 and (-350 < ball.xcor() < -340) and (paddle_a.ycor() - 50 < ball.ycor() < paddle_a.ycor() + 50):
            ball.setx(-340)
            ball.dx *= -1
            paddle_a.color("cyan")
            paddle_a_flash = 10

    main_menu()


# =====================================================================
# 2. SNAKE
# =====================================================================
def play_snake():
    clear_bindings()
    wn.clearscreen()
    wn.bgcolor("black")
    wn.title("Snake - Press ESC to Menu")
    wn.tracer(0)

    # Play Area Border
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
    move_delay = 0.1
    last_move = time.time()

    def get_random_food_pos():
        return [random.randint(-18, 18) * 20, random.randint(-13, 13) * 20]

    food = get_random_food_pos()
    golden_apple = None
    golden_timer = 0

    pen = turtle.Turtle()
    pen.shape("square")
    pen.penup()
    pen.speed(0)

    ui_pen = turtle.Turtle()
    ui_pen.color("white")
    ui_pen.penup()
    ui_pen.hideturtle()
    ui_pen.goto(0, 250)
    
    def update_ui():
        ui_pen.clear()
        ui_pen.write(f"Score: {score}  High Score: {high_scores['Snake']}", align="center", font=("Courier", 20, "bold"))

    update_ui()

    def set_dir(new_dir):
        nonlocal direction
        opposites = {"up": "down", "down": "up", "left": "right", "right": "left", "stop": ""}
        if direction != opposites.get(new_dir):
            direction = new_dir

    keys = {"Escape": False}
    wn.listen()
    wn.onkeypress(lambda: set_dir("up"), "Up")
    wn.onkeypress(lambda: set_dir("up"), "w")
    wn.onkeypress(lambda: set_dir("down"), "Down")
    wn.onkeypress(lambda: set_dir("down"), "s")
    wn.onkeypress(lambda: set_dir("left"), "Left")
    wn.onkeypress(lambda: set_dir("left"), "a")
    wn.onkeypress(lambda: set_dir("right"), "Right")
    wn.onkeypress(lambda: set_dir("right"), "d")
    wn.onkeypress(lambda: keys.update({"Escape": True}), "Escape")

    game_running = True
    while game_running:
        wn.update()
        time.sleep(0.01)

        if keys["Escape"]: break

        if time.time() - last_move > move_delay:
            last_move = time.time()
            
            if direction != "stop":
                if len(body) > 0:
                    body.insert(0, list(head))
                    body.pop()

                if direction == "up": head[1] += 20
                elif direction == "down": head[1] -= 20
                elif direction == "left": head[0] -= 20
                elif direction == "right": head[0] += 20

            # Wall Collision
            if head[0] > 370 or head[0] < -370 or head[1] > 270 or head[1] < -270:
                direction = "stop"
                head = [0, 0]
                body.clear()
                score = 0
                move_delay = 0.1
                golden_apple = None
                update_ui()

            # Self Collision
            if head in body:
                direction = "stop"
                head = [0, 0]
                body.clear()
                score = 0
                move_delay = 0.1
                golden_apple = None
                update_ui()

            # Normal Food
            if head == food:
                food = get_random_food_pos()
                while food in body or food == head:
                    food = get_random_food_pos()
                body.append(list(head))
                score += 10
                if score > high_scores["Snake"]: high_scores["Snake"] = score
                move_delay = max(0.04, move_delay - 0.002) # Speed up
                update_ui()
                
                # Spawn Golden Apple randomly (10% chance)
                if golden_apple is None and random.random() < 0.1:
                    golden_apple = get_random_food_pos()
                    golden_timer = time.time()

            # Golden Apple
            if golden_apple:
                if head == golden_apple:
                    score += 50
                    if score > high_scores["Snake"]: high_scores["Snake"] = score
                    update_ui()
                    golden_apple = None
                elif time.time() - golden_timer > 5.0: # Despawn after 5s
                    golden_apple = None

            # Render
            pen.clearstamps()
            
            pen.color("red"); pen.goto(food[0], food[1]); pen.stamp()
            if golden_apple:
                pen.color("gold"); pen.goto(golden_apple[0], golden_apple[1]); pen.stamp()
            
            pen.color("lime"); pen.goto(head[0], head[1]); pen.stamp()
            
            # Draw Body (Gradient green)
            for i, segment in enumerate(body):
                shade = max(50, 255 - (i * 5))
                pen.color((0, shade/255.0, 0))
                pen.goto(segment[0], segment[1]); pen.stamp()

    main_menu()


# =====================================================================
# 3. TETRIS
# =====================================================================
def play_tetris():
    clear_bindings()
    wn.clearscreen()
    wn.bgcolor("black")
    wn.title("Tetris - Press ESC to Menu")
    wn.tracer(0)

    cols, rows = 10, 20
    block_size = 25
    board = [[0] * cols for _ in range(rows)]
    
    SHAPES = [
        [[1, 1, 1, 1]], # I
        [[1, 1], [1, 1]], # O
        [[0, 1, 0], [1, 1, 1]], # T
        [[1, 0, 0], [1, 1, 1]], # L
        [[0, 0, 1], [1, 1, 1]], # J
        [[0, 1, 1], [1, 1, 0]], # S
        [[1, 1, 0], [0, 1, 1]]  # Z
    ]
    COLORS = ["cyan", "yellow", "purple", "orange", "blue", "green", "red"]

    pen = turtle.Turtle()
    pen.shape("square")
    pen.shapesize(block_size / 20)
    pen.penup()
    pen.speed(0)

    score, level, lines_cleared = 0, 1, 0
    drop_speed = 0.5

    ui_pen = turtle.Turtle()
    ui_pen.color("white"); ui_pen.penup(); ui_pen.hideturtle()
    
    def update_ui():
        ui_pen.clear()
        ui_pen.goto(150, 180); ui_pen.write("TETRIS", font=("Courier", 28, "bold"))
        ui_pen.goto(150, 120); ui_pen.write(f"Score: {score}", font=("Courier", 16, "normal"))
        ui_pen.goto(150, 90); ui_pen.write(f"Level: {level}", font=("Courier", 16, "normal"))
        ui_pen.goto(150, 60); ui_pen.write(f"Lines: {lines_cleared}", font=("Courier", 16, "normal"))
        ui_pen.goto(150, 30); ui_pen.write(f"High : {high_scores['Tetris']}", font=("Courier", 16, "normal"))
        ui_pen.goto(150, -30); ui_pen.write("Next Piece:", font=("Courier", 16, "normal"))

    update_ui()

    class Piece:
        def __init__(self):
            idx = random.randint(0, len(SHAPES) - 1)
            self.shape = SHAPES[idx]
            self.color = COLORS[idx]
            self.x = cols // 2 - len(self.shape[0]) // 2
            self.y = 0

    current_piece = Piece()
    next_piece = Piece()
    keys = {"Escape": False, "game_over": False}

    def check_collision(piece, offset_x=0, offset_y=0):
        for y, row in enumerate(piece.shape):
            for x, val in enumerate(row):
                if val:
                    nx, ny = piece.x + x + offset_x, piece.y + y + offset_y
                    if nx < 0 or nx >= cols or ny >= rows: return True
                    if ny >= 0 and board[ny][nx]: return True
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
            drop_speed = max(0.1, 0.5 - (level * 0.05))
            if score > high_scores["Tetris"]: high_scores["Tetris"] = score
            update_ui()

    def rotate():
        if keys["game_over"]: return
        new_shape = [list(row) for row in zip(*current_piece.shape[::-1])]
        old_shape = current_piece.shape
        current_piece.shape = new_shape
        if check_collision(current_piece):
            current_piece.x -= 1
            if check_collision(current_piece):
                current_piece.x += 2
                if check_collision(current_piece):
                    current_piece.x -= 1
                    current_piece.shape = old_shape # Undo

    def move_left():
        if not keys["game_over"] and not check_collision(current_piece, offset_x=-1): current_piece.x -= 1
    def move_right():
        if not keys["game_over"] and not check_collision(current_piece, offset_x=1): current_piece.x += 1
    def drop():
        if not keys["game_over"]:
            while not check_collision(current_piece, offset_y=1): current_piece.y += 1
            freeze(current_piece)
            next_turn()
            
    def next_turn():
        nonlocal current_piece, next_piece
        current_piece = next_piece
        next_piece = Piece()
        if check_collision(current_piece): keys["game_over"] = True

    wn.listen()
    wn.onkeypress(rotate, "Up"); wn.onkeypress(rotate, "w")
    wn.onkeypress(move_left, "Left"); wn.onkeypress(move_left, "a")
    wn.onkeypress(move_right, "Right"); wn.onkeypress(move_right, "d")
    wn.onkeypress(drop, "space")
    wn.onkeypress(lambda: keys.update({"Escape": True}), "Escape")

    last_drop = time.time()
    off_x, off_y = -150, (rows * block_size) / 2

    # Draw Border
    border = turtle.Turtle()
    border.hideturtle(); border.speed(0); border.color("gray"); border.penup()
    border.goto(off_x - 5, off_y + 5); border.pendown()
    for _ in range(2): 
        border.forward(cols * block_size + 10); border.right(90)
        border.forward(rows * block_size + 10); border.right(90)

    game_running = True
    while game_running:
        if keys["Escape"]: break

        if not keys["game_over"]:
            if time.time() - last_drop > drop_speed:
                if not check_collision(current_piece, offset_y=1): current_piece.y += 1
                else: freeze(current_piece); next_turn()
                last_drop = time.time()

        pen.clearstamps()
        
        # Draw Board
        for y, row in enumerate(board):
            for x, val in enumerate(row):
                if val:
                    pen.color(val)
                    pen.goto(off_x + x * block_size + block_size / 2, off_y - y * block_size - block_size / 2)
                    pen.stamp()

        if not keys["game_over"]:
            # Ghost Piece
            ghost_y = current_piece.y
            while not check_collision(current_piece, offset_y=(ghost_y - current_piece.y + 1)): ghost_y += 1
            pen.color("#333333")
            for y, row in enumerate(current_piece.shape):
                for x, val in enumerate(row):
                    if val:
                        pen.goto(off_x + (current_piece.x + x) * block_size + block_size / 2, off_y - (ghost_y + y) * block_size - block_size / 2)
                        pen.stamp()
                        
            # Current Piece
            pen.color(current_piece.color)
            for y, row in enumerate(current_piece.shape):
                for x, val in enumerate(row):
                    if val:
                        pen.goto(off_x + (current_piece.x + x) * block_size + block_size / 2, off_y - (current_piece.y + y) * block_size - block_size / 2)
                        pen.stamp()
                        
            # Next Piece
            pen.color(next_piece.color)
            for y, row in enumerate(next_piece.shape):
                for x, val in enumerate(row):
                    if val:
                        pen.goto(180 + x * block_size, -80 - y * block_size); pen.stamp()
        else:
            ui_pen.goto(off_x + (cols*block_size)/2, 0)
            ui_pen.color("red"); ui_pen.write("GAME OVER", align="center", font=("Courier", 30, "bold"))

        wn.update()
        time.sleep(0.02)

    main_menu()


# =====================================================================
# 4. SPACE INVADERS
# =====================================================================
def play_space_invaders():
    clear_bindings()
    wn.clearscreen()
    wn.bgcolor("black")
    wn.title("Space Invaders - Press ESC to Menu")
    wn.tracer(0)

    stars = []
    star_pen = turtle.Turtle()
    star_pen.hideturtle(); star_pen.penup()
    for _ in range(50): stars.append([random.randint(-400, 400), random.randint(-300, 300), random.uniform(0.5, 2)])

    player = turtle.Turtle()
    player.color("green"); player.shape("triangle"); player.shapesize(1.5)
    player.penup(); player.speed(0); player.setheading(90); player.goto(0, -250)
    
    bullet = turtle.Turtle()
    bullet.color("yellow"); bullet.shape("square"); bullet.shapesize(0.5, 0.2)
    bullet.penup(); bullet.hideturtle()
    bullet_state = "ready"

    enemies = []
    colors = ["cyan", "magenta", "orange"]
    for i, y in enumerate(range(100, 250, 45)):
        for x in range(-250, 250, 60):
            e = turtle.Turtle(); e.color(colors[i % len(colors)]); e.shape("circle")
            e.penup(); e.goto(x, y); enemies.append(e)

    enemy_bullets = []
    explosions = []
    ufo = turtle.Turtle()
    ufo.color("red"); ufo.shape("square"); ufo.shapesize(0.5, 2); ufo.penup()
    ufo.hideturtle(); ufo.goto(-500, 260)
    ufo_active = False

    enemy_speed = 1.5
    score, lives = 0, 3

    ui_pen = turtle.Turtle()
    ui_pen.color("white"); ui_pen.penup(); ui_pen.hideturtle()
    
    def update_ui():
        ui_pen.clear()
        ui_pen.goto(-380, 260); ui_pen.write(f"Score: {score}  High: {high_scores['Space Invaders']}", align="left", font=("Courier", 18, "bold"))
        ui_pen.goto(380, 260); ui_pen.write(f"Lives: {'♥' * lives}", align="right", font=("Courier", 18, "bold"))

    update_ui()

    keys = {"Left": False, "Right": False, "Escape": False, "game_over": False}
    
    def fire():
        nonlocal bullet_state
        if bullet_state == "ready" and not keys["game_over"]:
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
    wn.onkeypress(lambda: keys.update({"Escape": True}), "Escape")

    game_running = True
    while game_running:
        if keys["Escape"]: break
        
        star_pen.clear()
        for s in stars:
            s[1] -= s[2]
            if s[1] < -300: s[1] = 300; s[0] = random.randint(-400, 400)
            star_pen.goto(s[0], s[1]); star_pen.dot(s[2] * 2, "white")

        if keys["game_over"]:
            wn.update(); time.sleep(0.05)
            continue

        if keys["Left"] and player.xcor() > -380: player.setx(player.xcor() - 6)
        if keys["Right"] and player.xcor() < 380: player.setx(player.xcor() + 6)

        if bullet_state == "fire":
            bullet.sety(bullet.ycor() + 15)
            if bullet.ycor() > 280: bullet.hideturtle(); bullet_state = "ready"

        if not ufo_active and random.random() < 0.002:
            ufo_active = True; ufo.goto(-450, 260); ufo.showturtle()
            
        if ufo_active:
            ufo.setx(ufo.xcor() + 3)
            if ufo.xcor() > 450: ufo_active = False; ufo.hideturtle()
            if bullet_state == "fire" and ufo.distance(bullet) < 30:
                score += 100
                if score > high_scores["Space Invaders"]: high_scores["Space Invaders"] = score
                update_ui(); ufo_active = False; ufo.hideturtle(); bullet.hideturtle(); bullet_state = "ready"; bullet.goto(1000,1000)

        move_down = False
        for e in enemies:
            e.setx(e.xcor() + enemy_speed)
            if e.xcor() > 370 or e.xcor() < -370: move_down = True
            if random.random() < 0.001:
                eb = turtle.Turtle()
                eb.color("red"); eb.shape("square"); eb.shapesize(0.4, 0.2); eb.penup()
                eb.goto(e.xcor(), e.ycor() - 10); enemy_bullets.append(eb)

        if move_down:
            enemy_speed *= -1.05 
            for e in enemies:
                e.sety(e.ycor() - 30)
                if e.ycor() < -230: lives = 0; update_ui()

        for eb in enemy_bullets[:]:
            eb.sety(eb.ycor() - 5)
            if eb.ycor() < -300:
                eb.hideturtle(); enemy_bullets.remove(eb)
            elif eb.distance(player) < 20:
                lives -= 1; update_ui(); eb.hideturtle(); enemy_bullets.remove(eb)
                player.color("red"); wn.update(); time.sleep(0.1); player.color("green")
                if lives <= 0: keys["game_over"] = True

        for e in enemies[:]:
            if bullet_state == "fire" and e.distance(bullet) < 20:
                explosions.append({"x": e.xcor(), "y": e.ycor(), "timer": 10})
                bullet.hideturtle(); bullet_state = "ready"; bullet.goto(1000, 1000) 
                e.hideturtle(); enemies.remove(e); score += 10
                if score > high_scores["Space Invaders"]: high_scores["Space Invaders"] = score
                update_ui()

        for exp in explosions[:]:
            star_pen.goto(exp["x"], exp["y"])
            star_pen.dot(exp["timer"] * 2, "orange")
            exp["timer"] -= 1
            if exp["timer"] <= 0: explosions.remove(exp)

        if len(enemies) == 0:
            ui_pen.goto(0, 0); ui_pen.write("YOU WIN!", align="center", font=("Courier", 40, "bold"))
            keys["game_over"] = True

        if keys["game_over"] and len(enemies) > 0:
            ui_pen.goto(0, 0); ui_pen.write("GAME OVER", align="center", font=("Courier", 40, "bold"))

        wn.update()
        time.sleep(0.02)

    main_menu()


# =====================================================================
# 5. ATARI BREAKOUT
# =====================================================================
def play_breakout():
    clear_bindings()
    wn.clearscreen()
    wn.bgcolor("black")
    wn.title("Breakout - Press ESC to Menu")
    wn.tracer(0)

    score = 0
    lives = 3
    level = 1
    
    ui_pen = turtle.Turtle()
    ui_pen.color("white")
    ui_pen.penup()
    ui_pen.hideturtle()
    
    def update_ui():
        ui_pen.clear()
        ui_pen.goto(-380, 260)
        ui_pen.write(f"Score: {score}  Level: {level}  High: {high_scores['Breakout']}", align="left", font=("Courier", 18, "bold"))
        ui_pen.goto(380, 260)
        ui_pen.write(f"Lives: {'♥' * lives}", align="right", font=("Courier", 18, "bold"))

    update_ui()

    paddle = turtle.Turtle()
    paddle.shape("square")
    paddle.color("cyan")
    paddle.shapesize(stretch_wid=0.5, stretch_len=5) # 100px wide
    paddle.penup()
    paddle.goto(0, -250)

    ball = turtle.Turtle()
    ball.shape("square")
    ball.color("white")
    ball.shapesize(stretch_wid=0.5, stretch_len=0.5) # 10x10
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

    ball_speed = 6.0
    ball.dx = 0
    ball.dy = 0
    ball_active = False

    bricks = []
    colors = ["red", "orange", "yellow", "green", "blue"]

    def build_level():
        for b in bricks:
            b.hideturtle()
        bricks.clear()
        
        start_y = 200
        # 10 columns, 5 rows. Gap of 5px. Brick width = 70px.
        for row in range(5):
            for col in range(10):
                b = turtle.Turtle()
                b.shape("square")
                b.shapesize(stretch_wid=1, stretch_len=3.5) # 70x20
                b.color(colors[row % len(colors)])
                b.penup()
                b.goto(-337.5 + (col * 75), start_y - (row * 30))
                bricks.append(b)

    build_level()

    keys = {"Left": False, "Right": False, "Escape": False}
    
    def launch_ball():
        nonlocal ball_active
        if not ball_active and lives > 0:
            ball_active = True
            # Launch straight up
            ball.dx = ball_speed * math.cos(math.pi / 2)
            ball.dy = ball_speed * math.sin(math.pi / 2)

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
    wn.onkeypress(lambda: keys.update({"Escape": True}), "Escape")

    game_running = True
    while game_running:
        if keys["Escape"]: break

        # Render particles
        particle_pen.clear()
        for exp in explosions[:]:
            particle_pen.goto(exp["x"], exp["y"])
            particle_pen.dot(exp["timer"] * 2.5, exp["color"])
            exp["timer"] -= 1
            if exp["timer"] <= 0:
                explosions.remove(exp)

        # Paddle Move
        if keys["Left"] and paddle.xcor() > -340: paddle.setx(paddle.xcor() - 8)
        if keys["Right"] and paddle.xcor() < 340: paddle.setx(paddle.xcor() + 8)

        if not ball_active:
            ball.setx(paddle.xcor())
            ball.sety(paddle.ycor() + 15)
            if lives <= 0:
                ui_pen.goto(0, 0)
                ui_pen.write("GAME OVER", align="center", font=("Courier", 40, "bold"))
            else:
                ui_pen.goto(0, -50)
                ui_pen.write("PRESS SPACE TO LAUNCH", align="center", font=("Courier", 16, "normal"))
        else:
            ui_pen.clear()
            update_ui()
            
            # Trail
            trail_pen.goto(ball.xcor(), ball.ycor())
            trail_stamps.append(trail_pen.stamp())
            if len(trail_stamps) > 5:
                trail_pen.clearstamp(trail_stamps.pop(0))
            
            # Ball Move
            ball.setx(ball.xcor() + ball.dx)
            ball.sety(ball.ycor() + ball.dy)

            # Walls
            if ball.xcor() > 390:
                ball.setx(390)
                ball.dx *= -1
            elif ball.xcor() < -390:
                ball.setx(-390)
                ball.dx *= -1
                
            if ball.ycor() > 290:
                ball.sety(290)
                ball.dy *= -1
                
            # Bottom (Lose Life)
            if ball.ycor() < -290:
                lives -= 1
                ball_active = False
                trail_pen.clearstamps()
                trail_stamps.clear()
                update_ui()

            # Paddle Collision (Physics-based bounce angle)
            if (ball.ycor() > -245 and ball.ycor() < -235) and \
               (paddle.xcor() - 55 < ball.xcor() < paddle.xcor() + 55) and ball.dy < 0:
                
                ball.sety(-235)
                # Calculate hit position (-1 to 1)
                offset = (ball.xcor() - paddle.xcor()) / 50.0 
                
                # Convert to angle (pi/2 is straight up. offset 1 = mostly right, offset -1 = mostly left)
                angle = (math.pi / 2) - (offset * 1.2)
                
                ball.dx = ball_speed * math.cos(angle)
                ball.dy = ball_speed * math.sin(angle)

            # Brick Collision
            active_bricks = 0
            for b in bricks:
                if b.isvisible():
                    active_bricks += 1
                    # AABB collision check
                    if abs(ball.xcor() - b.xcor()) < 40 and abs(ball.ycor() - b.ycor()) < 15:
                        b.hideturtle()
                        
                        # Calculate side hit vs top/bottom hit
                        ovX = 40 - abs(ball.xcor() - b.xcor())
                        ovY = 15 - abs(ball.ycor() - b.ycor())
                        
                        if ovX < ovY: ball.dx *= -1
                        else: ball.dy *= -1
                        
                        score += 10
                        if score > high_scores["Breakout"]: high_scores["Breakout"] = score
                        update_ui()
                        
                        explosions.append({"x": b.xcor(), "y": b.ycor(), "timer": 10, "color": b.color()[0]})
                        break # Only hit one brick per frame

            # Win Level
            if active_bricks == 0:
                level += 1
                ball_speed += 0.5 # Increase difficulty
                ball_active = False
                trail_pen.clearstamps()
                trail_stamps.clear()
                build_level()
                update_ui()

        wn.update()
        time.sleep(0.01)

    main_menu()


# =====================================================================
# MAIN MENU
# =====================================================================
def main_menu():
    clear_bindings()
    wn.clearscreen()
    wn.title("Python Arcade - Ultimate Edition")
    wn.bgcolor("black")
    wn.tracer(0)

    # Animated Starfield for Menu
    stars = []
    star_pen = turtle.Turtle()
    star_pen.hideturtle()
    star_pen.penup()
    for _ in range(100):
        stars.append([random.randint(-400, 400), random.randint(-300, 300), random.uniform(0.2, 1.5)])

    title_pen = turtle.Turtle()
    title_pen.speed(0)
    title_pen.color("cyan")
    title_pen.penup()
    title_pen.hideturtle()
    title_pen.goto(0, 190)
    title_pen.write("PYTHON ARCADE", align="center", font=("Courier", 48, "bold"))
    
    title_pen.goto(0, 150)
    title_pen.color("magenta")
    title_pen.write("ULTIMATE EDITION", align="center", font=("Courier", 20, "bold"))

    menu_pen = turtle.Turtle()
    menu_pen.speed(0)
    menu_pen.color("white")
    menu_pen.penup()
    menu_pen.hideturtle()
    
    options = [
        ("1. PONG", 60), 
        ("2. SNAKE", 20), 
        ("3. TETRIS", -20), 
        ("4. SPACE INVADERS", -60),
        ("5. BREAKOUT", -100)
    ]
    
    for text, y in options:
        menu_pen.goto(0, y)
        menu_pen.write(text, align="center", font=("Courier", 26, "bold"))

    menu_pen.goto(0, -220)
    menu_pen.color("gray")
    menu_pen.write("Press 1, 2, 3, 4, or 5 to Play", align="center", font=("Courier", 16, "normal"))

    in_menu = {"state": True}
    
    def start_game(func):
        in_menu["state"] = False
        func()

    wn.listen()
    wn.onkeypress(lambda: start_game(play_pong), "1")
    wn.onkeypress(lambda: start_game(play_snake), "2")
    wn.onkeypress(lambda: start_game(play_tetris), "3")
    wn.onkeypress(lambda: start_game(play_space_invaders), "4")
    wn.onkeypress(lambda: start_game(play_breakout), "5")

    # Menu Animation Loop
    color_hue = 0
    while in_menu["state"]:
        star_pen.clear()
        for s in stars:
            s[1] -= s[2] # Move down
            if s[1] < -300:
                s[1] = 300
                s[0] = random.randint(-400, 400)
            star_pen.goto(s[0], s[1])
            star_pen.dot(s[2] * 3, "white")
            
        # Color shifting title
        color_hue = (color_hue + 5) % 360
        r, g, b = colorsys_hsv_to_rgb(color_hue/360, 1.0, 1.0)
        title_pen.clear()
        title_pen.color((r, g, b))
        title_pen.goto(0, 190)
        title_pen.write("PYTHON ARCADE", align="center", font=("Courier", 48, "bold"))
        title_pen.goto(0, 150)
        title_pen.color("magenta")
        title_pen.write("ULTIMATE EDITION", align="center", font=("Courier", 20, "bold"))

        wn.update()
        time.sleep(0.03)

# Helper function for title colors
def colorsys_hsv_to_rgb(h, s, v):
    if s == 0.0: return v, v, v
    i = int(h*6.)
    f = (h*6.)-i
    p,q,t = v*(1.-s), v*(1.-s*f), v*(1.-s*(1.-f))
    i%=6
    if i == 0: return v, t, p
    if i == 1: return q, v, p
    if i == 2: return p, v, t
    if i == 3: return p, q, v
    if i == 4: return t, p, v
    if i == 5: return v, p, q

if __name__ == "__main__":
    main_menu()