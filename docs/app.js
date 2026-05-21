const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

const menuView = document.getElementById('menuView');
const gameView = document.getElementById('gameView');
const difficultySelect = document.getElementById('difficultySelect');
const dailyChallengeCheckbox = document.getElementById('dailyChallenge');
const profileEl = document.getElementById('profile');
const scoreBoard = document.getElementById('scoreBoard');
const achievementBoard = document.getElementById('achievementBoard');
const gameTitle = document.getElementById('gameTitle');
const hudScore = document.getElementById('hudScore');
const hudStatus = document.getElementById('hudStatus');
const touchControls = document.getElementById('touchControls');

const modal = document.getElementById('modal');
const modalTitle = document.getElementById('modalTitle');
const modalBody = document.getElementById('modalBody');

const STORAGE_KEYS = {
  settings: 'ultimateArcadeSettings',
  highscores: 'ultimateArcadeHighscores',
  profile: 'ultimateArcadeProfile',
  achievements: 'ultimateArcadeAchievements'
};

const DEFAULT_SETTINGS = {
  sound: true,
  music: true,
  reducedMotion: false,
  screenShake: true,
  keyMap: {
    left: 'ArrowLeft', right: 'ArrowRight', up: 'ArrowUp', down: 'ArrowDown',
    action: 'Space', pause: 'KeyP', restart: 'KeyR', menu: 'Escape'
  }
};

const state = {
  currentGameName: null,
  game: null,
  running: false,
  paused: false,
  difficulty: 'Normal',
  dailyChallenge: false,
  settings: load(STORAGE_KEYS.settings, DEFAULT_SETTINGS),
  highscores: load(STORAGE_KEYS.highscores, { pong: 0, breakout: 0, snake: 0 }),
  profile: load(STORAGE_KEYS.profile, { gamesPlayed: 0, totalScore: 0, sessionsWon: 0 }),
  achievements: load(STORAGE_KEYS.achievements, {
    firstGame: false, score100: false, perfectPong: false, dailyWin: false
  }),
  inputs: { left: false, right: false, up: false, down: false, action: false },
  particles: [],
  shake: 0,
  keyCaptureAction: null,
  audioCtx: null,
  lastTime: 0
};

const instructions = {
  pong: 'Move with Up/Down or W/S. Score by passing the AI paddle. P pause, R restart, ESC quit.',
  breakout: 'Move paddle left/right and launch with Space. Clear all bricks before losing lives.',
  snake: 'Move with arrows/WASD. Eat food to grow. Avoid walls and your own body.'
};

const achievementsMeta = {
  firstGame: 'First Credit: Start any game.',
  score100: 'Century: Reach 100+ score in any game.',
  perfectPong: 'Perfect Return: Win Pong 7-0.',
  dailyWin: 'Daily Challenger: Win a game in daily challenge mode.'
};

const remapable = ['left', 'right', 'up', 'down', 'action', 'pause', 'restart', 'menu'];

function load(key, fallback) {
  try {
    const value = localStorage.getItem(key);
    return value ? { ...fallback, ...JSON.parse(value) } : fallback;
  } catch {
    return fallback;
  }
}

function saveAll() {
  localStorage.setItem(STORAGE_KEYS.settings, JSON.stringify(state.settings));
  localStorage.setItem(STORAGE_KEYS.highscores, JSON.stringify(state.highscores));
  localStorage.setItem(STORAGE_KEYS.profile, JSON.stringify(state.profile));
  localStorage.setItem(STORAGE_KEYS.achievements, JSON.stringify(state.achievements));
}

function nowSeed() {
  const d = new Date();
  const key = `${d.getUTCFullYear()}-${d.getUTCMonth() + 1}-${d.getUTCDate()}`;
  let h = 2166136261;
  for (let i = 0; i < key.length; i++) h = (h ^ key.charCodeAt(i)) * 16777619;
  return Math.abs(h | 0);
}

function rng(seed) {
  let s = seed || 1;
  return () => {
    s ^= s << 13; s ^= s >> 17; s ^= s << 5;
    return ((s >>> 0) % 10000) / 10000;
  };
}

function beep(freq = 440, duration = 0.05, type = 'square', gain = 0.025) {
  if (!state.settings.sound) return;
  state.audioCtx ??= new (window.AudioContext || window.webkitAudioContext)();
  const o = state.audioCtx.createOscillator();
  const g = state.audioCtx.createGain();
  o.type = type;
  o.frequency.value = freq;
  g.gain.value = gain;
  o.connect(g).connect(state.audioCtx.destination);
  o.start();
  o.stop(state.audioCtx.currentTime + duration);
}

function addParticles(x, y, color = '#40f9ff', count = 8) {
  if (state.settings.reducedMotion) return;
  for (let i = 0; i < count; i++) {
    state.particles.push({ x, y, dx: (Math.random() - 0.5) * 4, dy: (Math.random() - 0.5) * 4, life: 18, color });
  }
}

function triggerShake(power = 8) {
  if (state.settings.reducedMotion || !state.settings.screenShake) return;
  state.shake = Math.max(state.shake, power);
}

function updateParticles() {
  for (const p of state.particles) {
    p.x += p.dx; p.y += p.dy; p.dy += 0.04; p.life -= 1;
  }
  state.particles = state.particles.filter(p => p.life > 0);
}

function drawParticles() {
  for (const p of state.particles) {
    ctx.globalAlpha = Math.max(0, p.life / 18);
    ctx.fillStyle = p.color;
    ctx.fillRect(p.x, p.y, 3, 3);
  }
  ctx.globalAlpha = 1;
}

class PongGame {
  constructor(diff, seed) {
    this.w = canvas.width; this.h = canvas.height;
    this.diff = diff;
    this.rand = rng(seed);
    this.reset();
  }
  reset() {
    const d = this.diff === 'Easy' ? 0.85 : this.diff === 'Hard' ? 1.2 : 1;
    this.p1 = { y: this.h / 2 - 50, h: 100, score: 0 };
    this.p2 = { y: this.h / 2 - 50, h: 100, score: 0 };
    this.ball = { x: this.w / 2, y: this.h / 2, vx: (this.rand() > .5 ? 5 : -5) * d, vy: (this.rand() * 4 - 2) * d };
    this.playerSpeed = 7 * (this.diff === 'Hard' ? 1.08 : 1);
    this.aiSpeed = 4.4 * d;
    this.over = false;
  }
  update(input) {
    if (this.over) return;
    if (input.up) this.p1.y -= this.playerSpeed;
    if (input.down) this.p1.y += this.playerSpeed;
    this.p1.y = Math.max(0, Math.min(this.h - this.p1.h, this.p1.y));

    const target = this.ball.y - this.p2.h / 2;
    this.p2.y += Math.sign(target - this.p2.y) * this.aiSpeed;
    this.p2.y = Math.max(0, Math.min(this.h - this.p2.h, this.p2.y));

    this.ball.x += this.ball.vx;
    this.ball.y += this.ball.vy;

    if (this.ball.y < 8 || this.ball.y > this.h - 8) {
      this.ball.vy *= -1; beep(300, 0.03);
    }

    const leftHit = this.ball.x < 30 && this.ball.y > this.p1.y && this.ball.y < this.p1.y + this.p1.h;
    const rightHit = this.ball.x > this.w - 30 && this.ball.y > this.p2.y && this.ball.y < this.p2.y + this.p2.h;
    if (leftHit || rightHit) {
      this.ball.vx *= -1.05;
      this.ball.vy += (this.ball.y - (leftHit ? this.p1.y + this.p1.h / 2 : this.p2.y + this.p2.h / 2)) * 0.03;
      beep(520, 0.04);
      addParticles(this.ball.x, this.ball.y, leftHit ? '#40f9ff' : '#ff4fd8');
    }

    if (this.ball.x < -20 || this.ball.x > this.w + 20) {
      if (this.ball.x < 0) this.p2.score += 1; else this.p1.score += 1;
      triggerShake(7); beep(160, 0.08, 'sawtooth');
      this.ball = { x: this.w / 2, y: this.h / 2, vx: (this.rand() > .5 ? 5 : -5), vy: this.rand() * 4 - 2 };
      if (this.p1.score >= 7 || this.p2.score >= 7) this.over = true;
    }
  }
  render() {
    ctx.fillStyle = '#05070f';
    ctx.fillRect(0, 0, this.w, this.h);
    ctx.strokeStyle = '#30496d';
    ctx.setLineDash([8, 14]);
    ctx.beginPath(); ctx.moveTo(this.w / 2, 0); ctx.lineTo(this.w / 2, this.h); ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = '#40f9ff'; ctx.fillRect(12, this.p1.y, 12, this.p1.h);
    ctx.fillStyle = '#ff4fd8'; ctx.fillRect(this.w - 24, this.p2.y, 12, this.p2.h);
    ctx.fillStyle = '#fff'; ctx.fillRect(this.ball.x - 6, this.ball.y - 6, 12, 12);
    ctx.fillStyle = '#9ab4d8'; ctx.font = 'bold 42px monospace';
    ctx.fillText(`${this.p1.score}`, this.w / 2 - 90, 60);
    ctx.fillText(`${this.p2.score}`, this.w / 2 + 60, 60);
    if (this.over) {
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 38px monospace';
      ctx.fillText(this.p1.score > this.p2.score ? 'YOU WIN' : 'AI WINS', this.w / 2 - 110, this.h / 2);
    }
  }
  score() { return this.p1.score; }
  isOver() { return this.over; }
  isWin() { return this.over && this.p1.score > this.p2.score; }
}

class BreakoutGame {
  constructor(diff, seed) {
    this.w = canvas.width; this.h = canvas.height;
    this.diff = diff; this.rand = rng(seed + 1);
    this.reset();
  }
  reset() {
    const d = this.diff === 'Easy' ? 0.85 : this.diff === 'Hard' ? 1.18 : 1;
    this.paddle = { x: this.w / 2 - 56, y: this.h - 36, w: 112, h: 12, speed: 8 };
    this.ball = { x: this.w / 2, y: this.h - 54, vx: 4 * d, vy: -5 * d, r: 6, active: false };
    this.lives = 3; this.points = 0; this.over = false;
    this.bricks = [];
    for (let r = 0; r < 6; r++) {
      for (let c = 0; c < 12; c++) {
        this.bricks.push({ x: 36 + c * 74, y: 60 + r * 24, w: 64, h: 16, alive: true, hp: r > 3 ? 2 : 1 });
      }
    }
  }
  update(input) {
    if (this.over) return;
    if (input.left) this.paddle.x -= this.paddle.speed;
    if (input.right) this.paddle.x += this.paddle.speed;
    this.paddle.x = Math.max(0, Math.min(this.w - this.paddle.w, this.paddle.x));

    if (input.action && !this.ball.active) this.ball.active = true;
    if (!this.ball.active) {
      this.ball.x = this.paddle.x + this.paddle.w / 2;
      this.ball.y = this.paddle.y - 10;
      return;
    }

    this.ball.x += this.ball.vx; this.ball.y += this.ball.vy;
    if (this.ball.x < this.ball.r || this.ball.x > this.w - this.ball.r) this.ball.vx *= -1;
    if (this.ball.y < this.ball.r) this.ball.vy *= -1;

    if (this.ball.y > this.h + this.ball.r) {
      this.lives -= 1; this.ball.active = false; beep(140, 0.08, 'triangle');
      if (this.lives <= 0) this.over = true;
    }

    if (
      this.ball.y + this.ball.r > this.paddle.y && this.ball.y < this.paddle.y + this.paddle.h &&
      this.ball.x > this.paddle.x && this.ball.x < this.paddle.x + this.paddle.w && this.ball.vy > 0
    ) {
      const offset = (this.ball.x - (this.paddle.x + this.paddle.w / 2)) / (this.paddle.w / 2);
      this.ball.vx = offset * 7;
      this.ball.vy = -Math.abs(this.ball.vy) * 1.02;
      beep(480, 0.04);
    }

    for (const b of this.bricks) {
      if (!b.alive) continue;
      const hit = this.ball.x > b.x && this.ball.x < b.x + b.w && this.ball.y > b.y && this.ball.y < b.y + b.h;
      if (!hit) continue;
      this.ball.vy *= -1;
      b.hp -= 1;
      if (b.hp <= 0) {
        b.alive = false;
        this.points += 10;
        addParticles(this.ball.x, this.ball.y, '#ffd65f', 10);
      }
      beep(620, 0.03);
      break;
    }

    if (this.bricks.every(b => !b.alive)) {
      this.over = true;
      this.points += 50;
      triggerShake(10);
    }
  }
  render() {
    ctx.fillStyle = '#05070f';
    ctx.fillRect(0, 0, this.w, this.h);
    for (const b of this.bricks) {
      if (!b.alive) continue;
      ctx.fillStyle = b.hp === 2 ? '#ff8a3d' : '#40f9ff';
      ctx.fillRect(b.x, b.y, b.w, b.h);
    }
    ctx.fillStyle = '#fff';
    ctx.fillRect(this.paddle.x, this.paddle.y, this.paddle.w, this.paddle.h);
    ctx.fillStyle = '#ff4fd8';
    ctx.beginPath(); ctx.arc(this.ball.x, this.ball.y, this.ball.r, 0, Math.PI * 2); ctx.fill();
    ctx.fillStyle = '#9ab4d8'; ctx.font = 'bold 20px monospace';
    ctx.fillText(`Lives: ${this.lives}`, 18, 24);
    if (this.over) {
      ctx.fillStyle = '#fff'; ctx.font = 'bold 34px monospace';
      ctx.fillText(this.lives > 0 ? 'CLEARED!' : 'GAME OVER', this.w / 2 - 120, this.h / 2);
    }
  }
  score() { return this.points; }
  isOver() { return this.over; }
  isWin() { return this.over && this.lives > 0; }
}

class SnakeGame {
  constructor(diff, seed) {
    this.w = canvas.width; this.h = canvas.height;
    this.diff = diff;
    this.rand = rng(seed + 2);
    this.reset();
  }
  reset() {
    this.cell = 20;
    this.cols = Math.floor(this.w / this.cell);
    this.rows = Math.floor(this.h / this.cell);
    this.snake = [{ x: 10, y: 10 }];
    this.dir = { x: 1, y: 0 };
    this.nextDir = { x: 1, y: 0 };
    this.food = this.spawnFood();
    this.scoreVal = 0;
    this.over = false;
    const d = this.diff === 'Easy' ? 7 : this.diff === 'Hard' ? 11 : 9;
    this.tickRate = 1000 / d;
    this.acc = 0;
  }
  spawnFood() {
    return { x: Math.floor(this.rand() * (this.cols - 2)) + 1, y: Math.floor(this.rand() * (this.rows - 2)) + 1 };
  }
  update(input, dt) {
    if (this.over) return;
    if (input.left && this.dir.x !== 1) this.nextDir = { x: -1, y: 0 };
    if (input.right && this.dir.x !== -1) this.nextDir = { x: 1, y: 0 };
    if (input.up && this.dir.y !== 1) this.nextDir = { x: 0, y: -1 };
    if (input.down && this.dir.y !== -1) this.nextDir = { x: 0, y: 1 };

    this.acc += dt;
    if (this.acc < this.tickRate) return;
    this.acc = 0;

    this.dir = this.nextDir;
    const head = { x: this.snake[0].x + this.dir.x, y: this.snake[0].y + this.dir.y };

    if (head.x <= 0 || head.y <= 0 || head.x >= this.cols - 1 || head.y >= this.rows - 1 || this.snake.some(s => s.x === head.x && s.y === head.y)) {
      this.over = true;
      triggerShake(8);
      beep(150, 0.09, 'triangle');
      return;
    }

    this.snake.unshift(head);
    if (head.x === this.food.x && head.y === this.food.y) {
      this.scoreVal += 10;
      this.food = this.spawnFood();
      beep(760, 0.05, 'square');
      addParticles(head.x * this.cell, head.y * this.cell, '#62ff7a', 12);
    } else {
      this.snake.pop();
    }

    if (this.scoreVal >= 200) this.over = true;
  }
  render() {
    ctx.fillStyle = '#05070f';
    ctx.fillRect(0, 0, this.w, this.h);
    ctx.strokeStyle = '#263a58';
    ctx.strokeRect(this.cell, this.cell, this.w - this.cell * 2, this.h - this.cell * 2);
    for (let i = 0; i < this.snake.length; i++) {
      ctx.fillStyle = i === 0 ? '#62ff7a' : '#33c66f';
      ctx.fillRect(this.snake[i].x * this.cell, this.snake[i].y * this.cell, this.cell - 1, this.cell - 1);
    }
    ctx.fillStyle = '#ff6c6c';
    ctx.fillRect(this.food.x * this.cell, this.food.y * this.cell, this.cell - 1, this.cell - 1);
    if (this.over) {
      ctx.fillStyle = '#fff';
      ctx.font = 'bold 34px monospace';
      ctx.fillText('GAME OVER', this.w / 2 - 115, this.h / 2);
    }
  }
  score() { return this.scoreVal; }
  isOver() { return this.over; }
  isWin() { return this.over && this.scoreVal >= 100; }
}

const gameConstructors = { pong: PongGame, breakout: BreakoutGame, snake: SnakeGame };

function setView(view) {
  menuView.classList.toggle('active', view === 'menu');
  gameView.classList.toggle('active', view === 'game');
}

function startGame(name) {
  state.currentGameName = name;
  state.difficulty = difficultySelect.value;
  state.dailyChallenge = dailyChallengeCheckbox.checked;
  const seed = state.dailyChallenge ? nowSeed() : (Date.now() & 0xffff);
  const Ctor = gameConstructors[name];
  state.game = new Ctor(state.difficulty, seed);
  state.running = true;
  state.paused = false;
  state.profile.gamesPlayed += 1;
  state.achievements.firstGame = true;
  saveAll();
  gameTitle.textContent = `${name.toUpperCase()} • ${state.difficulty}${state.dailyChallenge ? ' • Daily' : ''}`;
  hudStatus.textContent = 'Running';
  setView('game');
}

function endToMenu() {
  state.running = false;
  state.game = null;
  setView('menu');
  renderMeta();
}

function pauseToggle() {
  state.paused = !state.paused;
  hudStatus.textContent = state.paused ? 'Paused' : 'Running';
}

function restartGame() {
  if (!state.game) return;
  state.game.reset();
  state.paused = false;
  hudStatus.textContent = 'Running';
}

function maybeFinishGame() {
  if (!state.game || !state.game.isOver()) return;
  const gameKey = state.currentGameName;
  const score = state.game.score();
  state.highscores[gameKey] = Math.max(state.highscores[gameKey] || 0, score);
  state.profile.totalScore += score;
  if (state.game.isWin()) state.profile.sessionsWon += 1;
  if (score >= 100) state.achievements.score100 = true;
  if (gameKey === 'pong' && state.game.p1?.score === 7 && state.game.p2?.score === 0) state.achievements.perfectPong = true;
  if (state.dailyChallenge && state.game.isWin()) state.achievements.dailyWin = true;
  saveAll();
  hudStatus.textContent = state.game.isWin() ? 'Victory' : 'Defeat';
}

function renderMeta() {
  profileEl.textContent = `Games: ${state.profile.gamesPlayed} • Wins: ${state.profile.sessionsWon} • Total Score: ${state.profile.totalScore}`;
  scoreBoard.innerHTML = `<strong>High Scores</strong><br>
    Pong: ${state.highscores.pong || 0} • Breakout: ${state.highscores.breakout || 0} • Snake: ${state.highscores.snake || 0}`;
  achievementBoard.innerHTML = `<strong>Achievements</strong><br>${Object.entries(achievementsMeta)
    .map(([k, label]) => `${state.achievements[k] ? '✅' : '⬜'} ${label}`).join('<br>')}`;
}

function openInstructions(name) {
  modalTitle.textContent = `${name.toUpperCase()} Instructions`;
  modalBody.textContent = instructions[name];
  modal.showModal();
}

function openSettingsModal() {
  modalTitle.textContent = 'Arcade Settings';
  const keyRows = remapable.map(key => `<button data-remap="${key}">${key}: ${state.settings.keyMap[key]}</button>`).join(' ');
  modalBody.innerHTML = `
    <label><input type="checkbox" id="sSound" ${state.settings.sound ? 'checked' : ''}/> Sound Effects</label><br>
    <label><input type="checkbox" id="sMusic" ${state.settings.music ? 'checked' : ''}/> Music (toggle reserved)</label><br>
    <label><input type="checkbox" id="sReduced" ${state.settings.reducedMotion ? 'checked' : ''}/> Reduced Motion</label><br>
    <label><input type="checkbox" id="sShake" ${state.settings.screenShake ? 'checked' : ''}/> Screen Shake</label><hr>
    <strong>Key Remapping</strong><br>${keyRows}`;
  modal.showModal();

  const read = id => modalBody.querySelector(`#${id}`);
  read('sSound').onchange = e => { state.settings.sound = e.target.checked; saveAll(); };
  read('sMusic').onchange = e => { state.settings.music = e.target.checked; saveAll(); };
  read('sReduced').onchange = e => { state.settings.reducedMotion = e.target.checked; saveAll(); };
  read('sShake').onchange = e => { state.settings.screenShake = e.target.checked; saveAll(); };

  modalBody.querySelectorAll('[data-remap]').forEach(btn => {
    btn.onclick = () => {
      state.keyCaptureAction = btn.dataset.remap;
      btn.textContent = `${btn.dataset.remap}: press key...`;
    };
  });
}

function handleSpecialKey(code, isDown) {
  if (!isDown) return;
  const map = state.settings.keyMap;
  if (code === map.pause && state.running) pauseToggle();
  if (code === map.restart && state.running) restartGame();
  if (code === map.menu && state.running) endToMenu();
}

function bindInputs() {
  document.addEventListener('keydown', e => {
    if (state.keyCaptureAction) {
      state.settings.keyMap[state.keyCaptureAction] = e.code;
      state.keyCaptureAction = null;
      saveAll();
      openSettingsModal();
      return;
    }
    mapInput(e.code, true);
    handleSpecialKey(e.code, true);
    if (e.code === 'Space') e.preventDefault();
  });
  document.addEventListener('keyup', e => mapInput(e.code, false));

  touchControls.querySelectorAll('button').forEach(btn => {
    const key = btn.dataset.touch;
    const down = () => setTouchInput(key, true);
    const up = () => setTouchInput(key, false);
    btn.addEventListener('touchstart', down, { passive: true });
    btn.addEventListener('touchend', up, { passive: true });
    btn.addEventListener('mousedown', down);
    btn.addEventListener('mouseup', up);
    btn.addEventListener('mouseleave', up);
  });
}

function setTouchInput(k, val) {
  if (k === 'left') state.inputs.left = val;
  if (k === 'right') state.inputs.right = val;
  if (k === 'up') state.inputs.up = val;
  if (k === 'down') state.inputs.down = val;
  if (k === 'action') state.inputs.action = val;
}

function mapInput(code, pressed) {
  const m = state.settings.keyMap;
  if (code === m.left || code === 'KeyA') state.inputs.left = pressed;
  if (code === m.right || code === 'KeyD') state.inputs.right = pressed;
  if (code === m.up || code === 'KeyW') state.inputs.up = pressed;
  if (code === m.down || code === 'KeyS') state.inputs.down = pressed;
  if (code === m.action) state.inputs.action = pressed;
}

function readGamepad() {
  const pads = navigator.getGamepads?.() || [];
  const gp = pads.find(Boolean);
  if (!gp) return;
  state.inputs.left = gp.axes[0] < -0.4 || gp.buttons[14]?.pressed || state.inputs.left;
  state.inputs.right = gp.axes[0] > 0.4 || gp.buttons[15]?.pressed || state.inputs.right;
  state.inputs.up = gp.axes[1] < -0.4 || gp.buttons[12]?.pressed || state.inputs.up;
  state.inputs.down = gp.axes[1] > 0.4 || gp.buttons[13]?.pressed || state.inputs.down;
  state.inputs.action = gp.buttons[0]?.pressed || state.inputs.action;
  if (gp.buttons[9]?.pressed && state.running) pauseToggle();
}

function loop(ts) {
  const dt = Math.min(32, ts - (state.lastTime || ts));
  state.lastTime = ts;

  ctx.save();
  if (state.shake > 0) {
    const s = state.shake;
    ctx.translate((Math.random() - 0.5) * s, (Math.random() - 0.5) * s);
    state.shake *= 0.8;
    if (state.shake < 0.1) state.shake = 0;
  }

  if (state.running && state.game) {
    readGamepad();
    if (!state.paused) state.game.update(state.inputs, dt);
    state.game.render(ctx);
    updateParticles();
    drawParticles();
    maybeFinishGame();
    hudScore.textContent = `Score: ${state.game.score()}`;
    if (state.paused) {
      ctx.fillStyle = '#0009';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#fff';
      ctx.font = 'bold 42px monospace';
      ctx.fillText('PAUSED', canvas.width / 2 - 90, canvas.height / 2);
    }
  } else {
    ctx.fillStyle = '#05070f';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }

  ctx.restore();
  requestAnimationFrame(loop);
}

function wireUI() {
  document.querySelectorAll('.start-btn').forEach(btn => btn.onclick = () => startGame(btn.dataset.game));
  document.querySelectorAll('.info-btn').forEach(btn => btn.onclick = () => openInstructions(btn.dataset.game));
  document.getElementById('pauseBtn').onclick = pauseToggle;
  document.getElementById('restartBtn').onclick = restartGame;
  document.getElementById('quitBtn').onclick = endToMenu;
  document.getElementById('closeModal').onclick = () => modal.close();
  document.getElementById('openSettings').onclick = openSettingsModal;
  difficultySelect.value = state.difficulty;
}

bindInputs();
wireUI();
renderMeta();
setView('menu');
requestAnimationFrame(loop);
