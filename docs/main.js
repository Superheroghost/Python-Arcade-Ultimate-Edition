const WIDTH = 960;
const HEIGHT = 540;
const BRICK_COLS = 11;
const STORAGE_KEY = 'neonOverdriveHighScore';

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const scoreValue = document.getElementById('scoreValue');
const livesValue = document.getElementById('livesValue');
const levelValue = document.getElementById('levelValue');
const highValue = document.getElementById('highValue');
const powerValue = document.getElementById('powerValue');
const modeSelect = document.getElementById('modeSelect');
const difficultySelect = document.getElementById('difficultySelect');
const overlay = document.getElementById('overlay');
const overlayTitle = document.getElementById('overlayTitle');
const overlayText = document.getElementById('overlayText');
const startBtn = document.getElementById('startBtn');
const pauseBtn = document.getElementById('pauseBtn');
const restartBtn = document.getElementById('restartBtn');
const muteBtn = document.getElementById('muteBtn');
const touchLeft = document.getElementById('touchLeft');
const touchRight = document.getElementById('touchRight');
const touchLaunch = document.getElementById('touchLaunch');

canvas.width = WIDTH;
canvas.height = HEIGHT;

const input = {
  left: false,
  right: false,
  launch: false,
};

const state = {
  mode: 'breakout',
  difficulty: 'normal',
  running: false,
  paused: false,
  highScore: Number(localStorage.getItem(STORAGE_KEY) || 0),
  audioEnabled: true,
  scene: null,
  particles: [],
  flashTimer: 0,
  shake: 0,
  lastTime: performance.now(),
};

highValue.textContent = String(state.highScore);

let audioContext;

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function rand(min, max) {
  return Math.random() * (max - min) + min;
}

function ensureAudio() {
  if (!state.audioEnabled) return null;
  if (!audioContext) {
    audioContext = new AudioContext();
  }
  if (audioContext.state === 'suspended') {
    audioContext.resume();
  }
  return audioContext;
}

function beep({ frequency, duration = 0.08, type = 'square', volume = 0.05, slide = 0 }) {
  const ac = ensureAudio();
  if (!ac) return;
  const now = ac.currentTime;
  const oscillator = ac.createOscillator();
  const gain = ac.createGain();
  oscillator.type = type;
  oscillator.frequency.setValueAtTime(frequency, now);
  oscillator.frequency.linearRampToValueAtTime(frequency + slide, now + duration);
  gain.gain.setValueAtTime(0, now);
  gain.gain.linearRampToValueAtTime(volume, now + 0.01);
  gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);
  oscillator.connect(gain);
  gain.connect(ac.destination);
  oscillator.start(now);
  oscillator.stop(now + duration + 0.02);
}

function addParticles(x, y, amount, hue) {
  for (let i = 0; i < amount; i += 1) {
    const angle = Math.random() * Math.PI * 2;
    const speed = rand(0.7, 3.2);
    state.particles.push({
      x,
      y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      life: rand(18, 42),
      maxLife: rand(18, 42),
      hue: hue + rand(-16, 16),
      size: rand(1.5, 3.5),
    });
  }
}

function updateParticles() {
  state.particles = state.particles.filter((particle) => {
    particle.x += particle.vx;
    particle.y += particle.vy;
    particle.vy += 0.03;
    particle.life -= 1;
    return particle.life > 0;
  });
}

function drawParticles() {
  for (const particle of state.particles) {
    const alpha = clamp(particle.life / particle.maxLife, 0, 1);
    ctx.fillStyle = `hsla(${particle.hue}, 100%, 62%, ${alpha})`;
    ctx.fillRect(particle.x, particle.y, particle.size, particle.size);
  }
}

function drawBackdrop() {
  const gradient = ctx.createLinearGradient(0, 0, 0, HEIGHT);
  gradient.addColorStop(0, '#090f22');
  gradient.addColorStop(1, '#03060e');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, WIDTH, HEIGHT);

  for (let i = 0; i < 40; i += 1) {
    const x = (i * 97 + performance.now() * 0.015) % WIDTH;
    const y = (i * 61) % HEIGHT;
    ctx.fillStyle = 'rgba(80, 190, 255, 0.05)';
    ctx.fillRect(x, y, 2, 2);
  }
}

class BreakoutScene {
  constructor(difficulty) {
    this.modeName = 'BREAKOUT';
    this.difficulty = difficulty;
    this.level = 1;
    this.score = 0;
    this.combo = 0;
    this.comboTimer = 0;
    this.lives = 3;
    this.powerText = 'Ready';
    this.expandTimer = 0;
    this.slowTimer = 0;
    this.shield = 0;
    this.finished = false;
    this.finishText = '';
    this.paddle = {
      x: WIDTH * 0.5 - 66,
      y: HEIGHT - 38,
      width: 132,
      height: 14,
      speed: difficulty === 'hard' ? 8.4 : difficulty === 'easy' ? 7.1 : 7.7,
    };
    this.balls = [];
    this.powerups = [];
    this.spawnBall(true);
    this.makeBricks();
  }

  makeBricks() {
    this.bricks = [];
    const rows = this.level + (this.difficulty === 'hard' ? 5 : this.difficulty === 'easy' ? 3 : 4);
    const brickWidth = 74;
    const brickHeight = 24;
    const gap = 6;
    const total = BRICK_COLS * (brickWidth + gap) - gap;
    const startX = (WIDTH - total) * 0.5;

    for (let row = 0; row < rows; row += 1) {
      for (let col = 0; col < BRICK_COLS; col += 1) {
        const hp = row > 4 ? 2 : 1;
        this.bricks.push({
          x: startX + col * (brickWidth + gap),
          y: 70 + row * (brickHeight + gap),
          width: brickWidth,
          height: brickHeight,
          hp,
          maxHp: hp,
          hue: 182 + row * 18,
          alive: true,
        });
      }
    }
  }

  spawnBall(stuck) {
    const speedBase = this.difficulty === 'hard' ? 5.7 : this.difficulty === 'easy' ? 4.7 : 5.2;
    this.balls.push({
      x: this.paddle.x + this.paddle.width * 0.5,
      y: this.paddle.y - 10,
      vx: rand(-2.6, 2.6),
      vy: -speedBase,
      radius: 8,
      stuck,
    });
  }

  updatePaddle() {
    if (input.left) this.paddle.x -= this.paddle.speed;
    if (input.right) this.paddle.x += this.paddle.speed;
    this.paddle.x = clamp(this.paddle.x, 0, WIDTH - this.paddle.width);
  }

  updateBalls() {
    const timeScale = this.slowTimer > 0 ? 0.78 : 1;

    for (const ball of this.balls) {
      if (ball.stuck) {
        ball.x = this.paddle.x + this.paddle.width * 0.5;
        ball.y = this.paddle.y - ball.radius - 2;
        if (input.launch) {
          ball.stuck = false;
          ball.vx = rand(-3.2, 3.2);
          beep({ frequency: 540, duration: 0.06, volume: 0.06 });
        }
        continue;
      }

      ball.x += ball.vx * timeScale;
      ball.y += ball.vy * timeScale;

      if (ball.x <= ball.radius || ball.x >= WIDTH - ball.radius) {
        ball.vx *= -1;
        state.shake = 3;
        beep({ frequency: 300, duration: 0.04, type: 'triangle', volume: 0.04 });
      }
      if (ball.y <= ball.radius) {
        ball.vy *= -1;
      }

      const overlapPaddle =
        ball.x + ball.radius > this.paddle.x &&
        ball.x - ball.radius < this.paddle.x + this.paddle.width &&
        ball.y + ball.radius > this.paddle.y &&
        ball.y - ball.radius < this.paddle.y + this.paddle.height;

      if (overlapPaddle && ball.vy > 0) {
        const rel = (ball.x - (this.paddle.x + this.paddle.width * 0.5)) / (this.paddle.width * 0.5);
        ball.vx = rel * 6.5;
        ball.vy = -Math.abs(ball.vy) - 0.08;
        addParticles(ball.x, ball.y, 8, 194);
        beep({ frequency: 470, duration: 0.05, type: 'sawtooth', volume: 0.05, slide: -120 });
      }

      for (const brick of this.bricks) {
        if (!brick.alive) continue;
        const hit =
          ball.x + ball.radius > brick.x &&
          ball.x - ball.radius < brick.x + brick.width &&
          ball.y + ball.radius > brick.y &&
          ball.y - ball.radius < brick.y + brick.height;

        if (!hit) continue;

        brick.hp -= 1;
        const wasDestroyed = brick.hp <= 0;
        if (wasDestroyed) {
          brick.alive = false;
          this.score += 120 + this.combo * 25;
          this.combo += 1;
          this.comboTimer = 110;
          addParticles(ball.x, ball.y, 20, brick.hue);
          if (Math.random() < 0.18) {
            this.spawnPowerup(brick.x + brick.width * 0.5, brick.y + brick.height * 0.5);
          }
          beep({ frequency: 680 + this.combo * 4, duration: 0.07, volume: 0.07, slide: -200 });
        } else {
          this.score += 40;
          beep({ frequency: 420, duration: 0.05, volume: 0.05, slide: -60 });
        }

        const prevX = ball.x - ball.vx;
        const prevY = ball.y - ball.vy;
        const fromLeft = prevX + ball.radius <= brick.x;
        const fromRight = prevX - ball.radius >= brick.x + brick.width;
        const fromTop = prevY + ball.radius <= brick.y;
        const fromBottom = prevY - ball.radius >= brick.y + brick.height;

        if (fromLeft || fromRight) {
          ball.vx *= -1;
        } else if (fromTop || fromBottom) {
          ball.vy *= -1;
        } else {
          ball.vy *= -1;
        }

        state.shake = 6;
        break;
      }
    }

    this.balls = this.balls.filter((ball) => ball.y < HEIGHT + 40);

    if (this.balls.length === 0) {
      if (this.shield > 0) {
        this.shield -= 1;
        this.powerText = 'Shield used';
        this.spawnBall(true);
        beep({ frequency: 260, duration: 0.16, volume: 0.06, type: 'triangle', slide: 260 });
      } else {
        this.lives -= 1;
        this.combo = 0;
        this.powerText = 'Lost ball';
        this.spawnBall(true);
        beep({ frequency: 190, duration: 0.2, volume: 0.07, type: 'sawtooth' });
      }
    }
  }

  spawnPowerup(x, y) {
    const roll = Math.random();
    const type = roll < 0.35 ? 'expand' : roll < 0.65 ? 'multiball' : roll < 0.85 ? 'slow' : 'shield';
    this.powerups.push({ x, y, vy: 2.1, type, width: 28, height: 14 });
  }

  applyPowerup(type) {
    if (type === 'expand') {
      this.expandTimer = 700;
      this.paddle.width = clamp(this.paddle.width + 34, 132, 230);
      this.powerText = 'Mega paddle';
    } else if (type === 'multiball') {
      const source = this.balls[0];
      if (source) {
        this.balls.push({ ...source, vx: Math.abs(source.vx) + 1.2, vy: source.vy * -1, stuck: false });
        this.balls.push({ ...source, vx: -Math.abs(source.vx) - 1.2, vy: source.vy, stuck: false });
      }
      this.powerText = 'Multiball x3';
    } else if (type === 'slow') {
      this.slowTimer = 520;
      this.powerText = 'Bullet-time';
    } else {
      this.shield = Math.min(2, this.shield + 1);
      this.powerText = `Shield x${this.shield}`;
    }
    state.flashTimer = 7;
    beep({ frequency: 840, duration: 0.09, volume: 0.07, type: 'triangle', slide: 240 });
  }

  updatePowerups() {
    this.powerups = this.powerups.filter((power) => {
      power.y += power.vy;
      const caught =
        power.x + power.width * 0.5 > this.paddle.x &&
        power.x - power.width * 0.5 < this.paddle.x + this.paddle.width &&
        power.y + power.height * 0.5 > this.paddle.y &&
        power.y - power.height * 0.5 < this.paddle.y + this.paddle.height;

      if (caught) {
        this.applyPowerup(power.type);
        addParticles(power.x, power.y, 18, 60);
        return false;
      }

      return power.y < HEIGHT + 40;
    });
  }

  update() {
    if (this.finished) return;
    this.updatePaddle();
    this.updateBalls();
    this.updatePowerups();

    if (this.comboTimer > 0) this.comboTimer -= 1;
    else this.combo = 0;

    if (this.expandTimer > 0) this.expandTimer -= 1;
    if (this.expandTimer === 0) this.paddle.width = clamp(this.paddle.width - 0.7, 132, 230);

    if (this.slowTimer > 0) this.slowTimer -= 1;

    if (this.lives <= 0) {
      this.finished = true;
      this.finishText = 'Game Over';
    }

    if (this.bricks.every((brick) => !brick.alive)) {
      this.level += 1;
      this.score += 800;
      this.combo = 0;
      this.powerups = [];
      this.makeBricks();
      this.balls = [];
      this.spawnBall(true);
      this.finishText = `Level ${this.level}`;
      this.powerText = 'New wave';
      addParticles(WIDTH * 0.5, HEIGHT * 0.45, 90, 210);
      beep({ frequency: 940, duration: 0.2, volume: 0.09, type: 'triangle', slide: -200 });
    }
  }

  draw() {
    drawBackdrop();

    ctx.fillStyle = '#0f2045';
    for (const brick of this.bricks) {
      if (!brick.alive) continue;
      const glow = brick.hp === 2 ? 56 : 62;
      ctx.fillStyle = `hsl(${brick.hue}, 96%, ${glow}%)`;
      ctx.fillRect(brick.x, brick.y, brick.width, brick.height);
      ctx.fillStyle = 'rgba(255,255,255,0.2)';
      ctx.fillRect(brick.x + 4, brick.y + 4, brick.width - 8, 3);
      if (brick.maxHp > 1 && brick.hp === 1) {
        ctx.fillStyle = 'rgba(12, 22, 38, 0.45)';
        ctx.fillRect(brick.x + 2, brick.y + 2, brick.width - 4, brick.height - 4);
      }
    }

    for (const power of this.powerups) {
      const color = power.type === 'expand' ? '#42f6ff' : power.type === 'multiball' ? '#ff62e3' : power.type === 'slow' ? '#ffb83d' : '#9aff5d';
      ctx.fillStyle = color;
      ctx.fillRect(power.x - power.width * 0.5, power.y - power.height * 0.5, power.width, power.height);
      ctx.fillStyle = 'rgba(255,255,255,0.35)';
      ctx.fillRect(power.x - power.width * 0.35, power.y - power.height * 0.35, power.width * 0.7, 3);
    }

    ctx.fillStyle = '#ecf5ff';
    ctx.fillRect(this.paddle.x, this.paddle.y, this.paddle.width, this.paddle.height);

    for (const ball of this.balls) {
      ctx.beginPath();
      ctx.fillStyle = '#ffd86f';
      ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
      ctx.fill();
    }

    drawParticles();

    if (this.combo > 1) {
      ctx.fillStyle = '#9fd8ff';
      ctx.font = '700 24px monospace';
      ctx.fillText(`COMBO x${this.combo}`, WIDTH - 220, 35);
    }

    if (state.flashTimer > 0) {
      ctx.fillStyle = 'rgba(255,255,255,0.08)';
      ctx.fillRect(0, 0, WIDTH, HEIGHT);
    }
  }
}

class PongScene {
  constructor(difficulty) {
    this.modeName = 'PONG';
    this.difficulty = difficulty;
    this.score = 0;
    this.lives = 7;
    this.level = 1;
    this.powerText = 'First to 7';
    this.finished = false;
    this.finishText = '';
    this.player = { x: 28, y: HEIGHT * 0.5 - 52, width: 12, height: 104, speed: 7.2 };
    this.ai = { x: WIDTH - 40, y: HEIGHT * 0.5 - 52, width: 12, height: 104, speed: 5.3 };
    this.ball = { x: WIDTH * 0.5, y: HEIGHT * 0.5, vx: 5.2, vy: 2.2, radius: 9 };
    this.playerPoints = 0;
    this.aiPoints = 0;
    this.errorBias = 0;
    this.errorFrames = 0;
  }

  hardBeatableAI() {
    const settings = {
      easy: { speed: 4.3, track: 0.12, noise: 32 },
      normal: { speed: 5.4, track: 0.17, noise: 20 },
      hard: { speed: 6.2, track: 0.22, noise: 13 },
    }[this.difficulty];

    this.ai.speed = settings.speed;

    if (this.errorFrames <= 0) {
      const chance = this.difficulty === 'hard' ? 0.014 : 0.02;
      if (Math.random() < chance) {
        this.errorBias = rand(-95, 95);
        this.errorFrames = this.difficulty === 'hard' ? 24 : 34;
      }
    } else {
      this.errorFrames -= 1;
    }

    const target = this.ball.y - this.ai.height * 0.5 + this.errorBias + rand(-settings.noise, settings.noise);
    this.ai.y += (target - this.ai.y) * settings.track;
    this.ai.y = clamp(this.ai.y, 0, HEIGHT - this.ai.height);
  }

  bounceFromPaddle(paddle, side) {
    const relative = (this.ball.y - (paddle.y + paddle.height * 0.5)) / (paddle.height * 0.5);
    this.ball.vx = Math.abs(this.ball.vx) * side;
    this.ball.vy = relative * 6.5;
    this.ball.vx += side * 0.16;
    this.ball.vx = clamp(this.ball.vx, -8, 8);
    addParticles(this.ball.x, this.ball.y, 12, side > 0 ? 190 : 328);
    beep({ frequency: side > 0 ? 520 : 440, duration: 0.06, volume: 0.05, type: 'square', slide: -80 });
  }

  resetBall(direction) {
    this.ball.x = WIDTH * 0.5;
    this.ball.y = HEIGHT * 0.5;
    const speed = this.difficulty === 'hard' ? 5.8 : this.difficulty === 'easy' ? 4.8 : 5.3;
    this.ball.vx = speed * direction;
    this.ball.vy = rand(-2.8, 2.8);
  }

  update() {
    if (this.finished) return;

    if (input.left) this.player.y -= this.player.speed;
    if (input.right) this.player.y += this.player.speed;
    this.player.y = clamp(this.player.y, 0, HEIGHT - this.player.height);

    this.hardBeatableAI();

    this.ball.x += this.ball.vx;
    this.ball.y += this.ball.vy;

    if (this.ball.y <= this.ball.radius || this.ball.y >= HEIGHT - this.ball.radius) {
      this.ball.vy *= -1;
      beep({ frequency: 310, duration: 0.05, volume: 0.04, type: 'triangle' });
    }

    const hitPlayer =
      this.ball.x - this.ball.radius < this.player.x + this.player.width &&
      this.ball.y > this.player.y &&
      this.ball.y < this.player.y + this.player.height &&
      this.ball.vx < 0;

    const hitAI =
      this.ball.x + this.ball.radius > this.ai.x &&
      this.ball.y > this.ai.y &&
      this.ball.y < this.ai.y + this.ai.height &&
      this.ball.vx > 0;

    if (hitPlayer) this.bounceFromPaddle(this.player, 1);
    if (hitAI) this.bounceFromPaddle(this.ai, -1);

    if (this.ball.x < -20) {
      this.aiPoints += 1;
      this.lives = Math.max(0, 7 - this.aiPoints);
      this.powerText = 'AI scored';
      beep({ frequency: 190, duration: 0.15, volume: 0.06, type: 'sawtooth' });
      this.resetBall(1);
    }

    if (this.ball.x > WIDTH + 20) {
      this.playerPoints += 1;
      this.score = this.playerPoints * 1000;
      this.powerText = 'You scored';
      beep({ frequency: 840, duration: 0.12, volume: 0.08, type: 'triangle', slide: -140 });
      this.resetBall(-1);
    }

    if (this.playerPoints >= 7 || this.aiPoints >= 7) {
      this.finished = true;
      this.finishText = this.playerPoints > this.aiPoints ? 'Victory! You Beat Hard AI' : 'Defeat - Try Again';
    }
  }

  draw() {
    drawBackdrop();

    ctx.strokeStyle = '#2d4f89';
    ctx.setLineDash([9, 13]);
    ctx.beginPath();
    ctx.moveTo(WIDTH * 0.5, 0);
    ctx.lineTo(WIDTH * 0.5, HEIGHT);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.fillStyle = '#4ff7ff';
    ctx.fillRect(this.player.x, this.player.y, this.player.width, this.player.height);
    ctx.fillStyle = '#ff62e3';
    ctx.fillRect(this.ai.x, this.ai.y, this.ai.width, this.ai.height);

    ctx.fillStyle = '#f2f7ff';
    ctx.beginPath();
    ctx.arc(this.ball.x, this.ball.y, this.ball.radius, 0, Math.PI * 2);
    ctx.fill();

    drawParticles();

    ctx.fillStyle = '#a5bee5';
    ctx.font = '700 58px monospace';
    ctx.fillText(String(this.playerPoints), WIDTH * 0.5 - 92, 66);
    ctx.fillText(String(this.aiPoints), WIDTH * 0.5 + 48, 66);
  }
}

function createScene() {
  state.mode = modeSelect.value;
  state.difficulty = difficultySelect.value;
  state.scene = state.mode === 'pong' ? new PongScene(state.difficulty) : new BreakoutScene(state.difficulty);
  state.particles = [];
  state.running = true;
  state.paused = false;
  pauseBtn.textContent = 'Pause';
  hideOverlay();
  updateHud();
}

function updateHud() {
  if (!state.scene) return;
  scoreValue.textContent = String(Math.floor(state.scene.score || 0));
  livesValue.textContent = String(state.scene.lives ?? 0);
  levelValue.textContent = String(state.scene.level ?? 1);
  powerValue.textContent = state.scene.powerText || 'Ready';
}

function updateHighScore(score) {
  if (score > state.highScore) {
    state.highScore = score;
    localStorage.setItem(STORAGE_KEY, String(score));
    highValue.textContent = String(score);
  }
}

function showOverlay(title, text, buttonText = 'Play Again') {
  overlayTitle.textContent = title;
  overlayText.textContent = text;
  startBtn.textContent = buttonText;
  overlay.classList.add('visible');
}

function hideOverlay() {
  overlay.classList.remove('visible');
}

function drawPauseLayer() {
  ctx.fillStyle = 'rgba(0, 0, 0, 0.52)';
  ctx.fillRect(0, 0, WIDTH, HEIGHT);
  ctx.fillStyle = '#ffffff';
  ctx.font = '700 46px monospace';
  ctx.fillText('PAUSED', WIDTH * 0.5 - 108, HEIGHT * 0.5 + 14);
}

function tick(now) {
  state.lastTime = now;

  if (state.flashTimer > 0) state.flashTimer -= 1;
  if (state.shake > 0) state.shake = Math.max(0, state.shake - 0.4);

  ctx.save();
  if (state.shake > 0) {
    ctx.translate(rand(-state.shake, state.shake), rand(-state.shake, state.shake));
  }

  if (state.scene) {
    if (state.running && !state.paused) {
      state.scene.update();
      updateParticles();
      state.scene.draw();
      updateHud();
      updateHighScore(Math.floor(state.scene.score || 0));

      if (state.scene.finished) {
        state.running = false;
        const modeLabel = state.scene.modeName === 'PONG' ? 'Pong Duel' : 'Breakout';
        showOverlay(state.scene.finishText, `${modeLabel} score: ${Math.floor(state.scene.score || 0)} · Press Start to go again.`);
      }
    } else {
      state.scene.draw();
      if (state.paused) drawPauseLayer();
    }
  } else {
    drawBackdrop();
  }

  ctx.restore();
  requestAnimationFrame(tick);
}

function setKeyState(key, pressed) {
  if (key === 'ArrowLeft' || key.toLowerCase() === 'a') input.left = pressed;
  if (key === 'ArrowRight' || key.toLowerCase() === 'd') input.right = pressed;
  if (key === ' ' || key === 'Enter') input.launch = pressed;
}

function setupInput() {
  window.addEventListener('keydown', (event) => {
    if (['ArrowLeft', 'ArrowRight', 'a', 'A', 'd', 'D', ' ', 'Enter'].includes(event.key)) {
      event.preventDefault();
      setKeyState(event.key, true);
      if (!state.running && event.key === ' ') createScene();
    }
    if (event.key.toLowerCase() === 'r') createScene();
    if (event.key.toLowerCase() === 'p' && state.running) {
      state.paused = !state.paused;
      pauseBtn.textContent = state.paused ? 'Resume' : 'Pause';
      if (!state.paused) hideOverlay();
    }
  });

  window.addEventListener('keyup', (event) => {
    setKeyState(event.key, false);
  });

  const bindTouch = (element, onDown, onUp) => {
    element.addEventListener('touchstart', (event) => {
      event.preventDefault();
      onDown();
    }, { passive: false });
    element.addEventListener('touchend', (event) => {
      event.preventDefault();
      onUp();
    }, { passive: false });
    element.addEventListener('mousedown', onDown);
    element.addEventListener('mouseup', onUp);
    element.addEventListener('mouseleave', onUp);
  };

  bindTouch(touchLeft, () => { input.left = true; }, () => { input.left = false; });
  bindTouch(touchRight, () => { input.right = true; }, () => { input.right = false; });
  bindTouch(touchLaunch, () => { input.launch = true; if (!state.running) createScene(); }, () => { input.launch = false; });
}

startBtn.addEventListener('click', () => {
  createScene();
});

pauseBtn.addEventListener('click', () => {
  if (!state.scene || !state.running) return;
  state.paused = !state.paused;
  pauseBtn.textContent = state.paused ? 'Resume' : 'Pause';
});

restartBtn.addEventListener('click', () => {
  createScene();
});

muteBtn.addEventListener('click', () => {
  state.audioEnabled = !state.audioEnabled;
  muteBtn.setAttribute('aria-pressed', String(!state.audioEnabled));
  muteBtn.textContent = state.audioEnabled ? '🔊 Sound' : '🔇 Muted';
  if (!state.audioEnabled && audioContext) {
    audioContext.suspend();
  }
});

modeSelect.addEventListener('change', () => {
  const isPong = modeSelect.value === 'pong';
  livesValue.parentElement.querySelector('span').textContent = isPong ? 'To Lose' : 'Lives';
  levelValue.parentElement.querySelector('span').textContent = isPong ? 'Goal' : 'Level';
  powerValue.textContent = isPong ? 'First to 7' : 'Ready';
  overlayText.textContent = isPong
    ? 'Move up/down with A/D or ←/→. Press Space to serve and outplay the AI.'
    : 'Move with A/D or ←/→, then press Space to launch.';
});

showOverlay('Neon Overdrive', 'Move with A/D or ←/→, then press Space to launch.', 'Start Game');
setupInput();
requestAnimationFrame(tick);
