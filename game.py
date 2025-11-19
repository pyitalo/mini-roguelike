import random
import math
from pygame import Rect

WIDTH = 800
HEIGHT = 600
CELL = 50

STATE_MENU = "Menu"
STATE_PLAY = "Playing"
STATE_OVER = "Game Over"
state = STATE_MENU

music_on = True
sound_on = True


class Animator:
    def __init__(self):
        self.t = 0

    def update(self, dt):
        self.t += dt * 5

    def pulse(self):
        return 1 + 0.05 * math.sin(self.t)


class Entity:
    def __init__(self, gx, gy, color):
        self.gx = gx
        self.gy = gy
        self.x = gx * CELL + CELL // 2
        self.y = gy * CELL + CELL // 2
        self.tx = self.x
        self.ty = self.y
        self.color = color
        self.size = CELL * 0.6
        self.speed = 200
        self.animator = Animator()

    def move_to(self, gx, gy):
        self.gx = gx
        self.gy = gy
        self.tx = gx * CELL + CELL // 2
        self.ty = gy * CELL + CELL // 2

    def rect(self):
        s = self.size
        return Rect(self.x - s/2, self.y - s/2, s, s)

    def update(self, dt):
        self.animator.update(dt)
        dx = self.tx - self.x
        dy = self.ty - self.y
        dist = math.hypot(dx, dy)
        if dist > 1:
            step = min(self.speed * dt, dist)
            self.x += dx / dist * step
            self.y += dy / dist * step

    def draw(self):
        s = self.size * self.animator.pulse()
        screen.draw.filled_rect(Rect(self.x - s/2, self.y - s/2, s, s), self.color)


class Hero(Entity):
    def __init__(self):
        super().__init__(4, 4, (80, 200, 150))
        self.lives = 3
        self.inv_timer = 0.0

        # Carregar spritesheets
        self.run_frames = [images.load("rabbit_run").subsurface(i*32, 0, 32, 32) for i in range(8)]
        self.idle_frames = [images.load("stopped").subsurface(i*32, 0, 32, 32) for i in range(12)]

        self.t = 0  # tempo interno para animação
        self.current_frames = self.idle_frames
        self.frame_index = 0

    def is_invulnerable(self):
        return self.inv_timer > 0

    def update(self, dt):
        super().update(dt)
        self.t += dt

        # Verifica se o herói está se movendo
        moving = (self.tx != self.x or self.ty != self.y)

        # Alterna animação dependendo se está se movendo
        if moving:
            self.current_frames = self.run_frames
        else:
            self.current_frames = self.idle_frames

        # Atualiza frame da animação
        speed = 10  # frames por segundo
        self.frame_index = int(self.t * speed) % len(self.current_frames)

        if self.inv_timer > 0:
            self.inv_timer = max(0, self.inv_timer - dt)

    def draw(self):
        frame = self.current_frames[self.frame_index]
        screen.blit(frame, (self.x - 16, self.y - 16))  # centraliza 32x32


class Enemy(Entity):
    def __init__(self, gx, gy):
        super().__init__(gx, gy, (200, 80, 80))
        self.timer = random.uniform(0.5, 1.5)

        # Carregar spritesheets
        self.run_frames = [images.load("enemyrun").subsurface(i*32, 0, 32, 32) for i in range(8)]
        self.idle_frames = [images.load("enemystopped").subsurface(i*32, 0, 32, 32) for i in range(12)]

        self.t = 0
        self.current_frames = self.idle_frames
        self.frame_index = 0

    def update(self, dt):
        super().update(dt)
        self.t += dt

        # Movimento aleatório
        self.timer -= dt
        if self.timer <= 0:
            self.timer = random.uniform(0.5, 1.5)
            nx = self.gx + random.choice([-1, 0, 1])
            ny = self.gy + random.choice([-1, 0, 1])
            nx = max(0, min(nx, WIDTH // CELL - 1))
            ny = max(0, min(ny, HEIGHT // CELL - 1))
            self.move_to(nx, ny)

        # Alterna animação dependendo se está se movendo
        moving = (self.tx != self.x or self.ty != self.y)
        self.current_frames = self.run_frames if moving else self.idle_frames

        # Atualiza frame da animação
        speed = 10  # frames por segundo
        self.frame_index = int(self.t * speed) % len(self.current_frames)

    def draw(self):
        frame = self.current_frames[self.frame_index]
        screen.blit(frame, (self.x - 16, self.y - 16))  # centraliza 32x32


class Button:
    def __init__(self, rect, text, callback):
        self.rect = Rect(rect)
        self.text = text
        self.callback = callback

    def draw(self):
        screen.draw.filled_rect(self.rect, (50, 50, 90))
        screen.draw.textbox(self.text, self.rect, color="white")

    def click(self, pos):
        if self.rect.collidepoint(pos):
            self.callback()


hero = Hero()
enemies = []
buttons = []


def start_game():
    global state, hero, enemies
    hero = Hero()
    enemies = [Enemy(random.randint(0, WIDTH//CELL-1), random.randint(0, HEIGHT//CELL-1)) for _ in range(5)]
    state = STATE_PLAY

    if music_on:
        try:
            # Use o caminho relativo e o nome sem extensão
            music.play("time_for_adventure")  # sem loop=True
        except Exception as e:
            print("Erro ao tocar música:", e)


def toggle_music():
    global music_on
    music_on = not music_on
    if not music_on:
        music.stop()

def toggle_sound():
    global sound_on
    sound_on = not sound_on

def quit_game():
    exit()

def setup_menu():
    buttons.clear()
    buttons.append(Button((WIDTH//2-120, 250, 240, 50), "Start Game", start_game))
    buttons.append(Button((WIDTH//2-120, 320, 240, 50), "Music On/Off", toggle_music))
    buttons.append(Button((WIDTH//2-120, 390, 240, 50), "Sound On/Off", toggle_sound))
    buttons.append(Button((WIDTH//2-120, 460, 240, 50), "Exit", quit_game))

setup_menu()


def draw():
    screen.clear()

    screen.blit(images.load("background"), (0, 0))

    if state == STATE_MENU:
        screen.draw.text("Mini Roguelike", center=(WIDTH/2, 140), fontsize=60)
        for b in buttons:
            b.draw()
    elif state == STATE_PLAY:
        for e in enemies: e.draw()
        hero.draw()
        screen.draw.text(f"Lives: {hero.lives}", (10,10), color="white")
    else:
        screen.draw.text("GAME OVER", center=(WIDTH/2, HEIGHT/2), fontsize=70)


def update(dt):
    global state
    if state != STATE_PLAY:
        return

    # Atualiza herói e inimigos
    hero.update(dt)
    for e in enemies:
        e.update(dt)

    # Verifica colisão do herói com inimigos
    for e in enemies:
        if hero.rect().colliderect(e.rect()):
            if not hero.is_invulnerable():
                hero.lives -= 1
                hero.inv_timer = 1.2
                if sound_on:
                    try:
                        sounds.kick.play()  # <-- Aqui toca o som de hit
                    except:
                        pass
                if hero.lives <= 0:
                    state = STATE_OVER


def on_key_down(key):
    if state != STATE_PLAY:
        return
    max_x = WIDTH // CELL - 1
    max_y = HEIGHT // CELL - 1
    if key == keys.RIGHT and hero.gx < max_x:
        hero.move_to(hero.gx + 1, hero.gy)
    if key == keys.LEFT and hero.gx > 0:
        hero.move_to(hero.gx - 1, hero.gy)
    if key == keys.UP and hero.gy > 0:
        hero.move_to(hero.gx, hero.gy - 1)
    if key == keys.DOWN and hero.gy < max_y:
        hero.move_to(hero.gx, hero.gy + 1)

def on_mouse_down(pos):
    if state == STATE_MENU:
        for b in buttons:
            b.click(pos)
