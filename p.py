import py5
import random
import math

# --- Config
NUM_PARTICLES = 80
WIDTH, HEIGHT = 720, 480
GATE_X = WIDTH // 2
GATE_Y1, GATE_Y2 = HEIGHT // 2 - 60, HEIGHT // 2 + 60

# Slider config
slider_x = 80
slider_y = HEIGHT - 50
slider_w = WIDTH - 160
import py5
import random
import math

# --- Config
NUM_PARTICLES = 80
WIDTH, HEIGHT = 720, 480
GATE_X = WIDTH // 2
GATE_Y1, GATE_Y2 = HEIGHT // 2 - 60, HEIGHT // 2 + 60

# Slider config
slider_x = 80
slider_y = HEIGHT - 50
slider_w = WIDTH - 160
slider_h = 14
slider_knob_r = 12
slider_min = 0.5
slider_max = 6.0

# State
particles = []
speed_threshold = 2.0
slider_dragging = False
paused = False


# --- Particle class
class Particle:
    def __init__(self):
        pad = 80
        self.x = random.uniform(pad, WIDTH - pad)
        self.y = random.uniform(pad, HEIGHT - pad)
        angle = random.uniform(0, math.tau)
        speed = random.uniform(0.2, 2.8)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.base_r = random.uniform(4, 9)
        self.trail = []

    def move(self):
        if paused:
            return
        self.x += self.vx
        self.y += self.vy
        # Keep trail of last positions
        self.trail.append((self.x, self.y))
        if len(self.trail) > 20:
            self.trail.pop(0)
        # Bounce walls
        if self.x < self.base_r or self.x > WIDTH - self.base_r:
            self.vx *= -1
            self.x = min(max(self.x, self.base_r), WIDTH - self.base_r)
        if self.y < self.base_r or self.y > HEIGHT - self.base_r:
            self.vy *= -1
            self.y = min(max(self.y, self.base_r), HEIGHT - self.base_r)

    def speed(self):
        return math.hypot(self.vx, self.vy)

    def color(self):
        s = self.speed()
        # Smooth color between blue (slow) and red (fast)
        t = min(max((s - slider_min) / (slider_max - slider_min), 0), 1)
        r = int(60 + 195 * t)
        g = int(160 * (1 - t))
        b = int(200 - 100 * t)
        return py5.color(r, g, b)

    def show(self):
        # Glow trail
        col = self.color()
        recent = self.trail[-10:]
        for i, (tx, ty) in enumerate(recent):
            a = int(30 + 220 * (i / max(1, len(recent))))
            py5.no_stroke()
            py5.fill(py5.red(col), py5.green(col), py5.blue(col), a)
            size = self.base_r * (0.6 + 0.6 * i / 10)
            py5.ellipse(tx, ty, size * 2, size * 2)
        # Main particle with rim
        py5.stroke(255, 255, 255, 120)
        py5.stroke_weight(1)
        py5.fill(col)
        r = self.base_r * (1 + 0.6 * (self.speed() / slider_max))
        py5.ellipse(self.x, self.y, r * 2, r * 2)
        py5.no_stroke()


# --- Setup & Draw

def setup():
    py5.size(WIDTH, HEIGHT)
    py5.frame_rate(60)
    global particles
    particles = [Particle() for _ in range(NUM_PARTICLES)]


def draw():
    global speed_threshold
    # Background gradient
    for i in range(HEIGHT):
        t = i / HEIGHT
        r = int(18 + 60 * (1 - t))
        g = int(28 + 80 * (1 - t))
        b = int(40 + 160 * t)
        py5.stroke(r, g, b)
        py5.line(0, i, WIDTH, i)

    # Soft panel
    py5.fill(255, 255, 255, 180)
    py5.stroke(30, 30, 40, 90)
    py5.stroke_weight(3)
    py5.rect(12, 12, WIDTH - 24, HEIGHT - 24, 24)
    py5.no_stroke()

    # Title
    py5.fill(30, 30, 60)
    py5.text_size(26)
    py5.text_align(py5.CENTER, py5.CENTER)
    py5.text("Maxwell's Demon — Particle Separator", WIDTH // 2, 36)

    # Animated gate
    gate_phase = (py5.frame_count % 120) / 120
    glow = int(80 + 120 * abs(math.sin(py5.frame_count * 0.08)))
    py5.stroke(160 + int(80 * gate_phase), 130, 210 - int(80 * gate_phase), glow)
    py5.stroke_weight(8)
    py5.line(GATE_X, 24, GATE_X, GATE_Y1)
    py5.line(GATE_X, GATE_Y2, GATE_X, HEIGHT - 24)
    py5.stroke_weight(1)

    # Demon figure (polished)
    draw_demon(GATE_X - 60, HEIGHT // 2 + 8, gate_phase)

    # Slider UI (drawn before counts so knob overlays)
    draw_slider()

    # Split particles into containers
    red_particles = []
    blue_particles = []
    for p in particles:
        if p.speed() < speed_threshold:
            blue_particles.append(p)
        else:
            red_particles.append(p)

    # Draw containers
    draw_container(32, 64, 92, HEIGHT - 128, "Blue Chamber", py5.color(30, 140, 240), len(blue_particles))
    draw_container(WIDTH - 124, 64, 92, HEIGHT - 128, "Red Chamber", py5.color(240, 90, 90), len(red_particles))

    # Demon gate aura
    py5.no_fill()
    for i in range(6):
        a = int(30 * (1 - i / 6))
        py5.stroke(200, 120, 240, a)
        py5.stroke_weight(6 - i)
        py5.line(GATE_X, GATE_Y1 + 6 + i * 4, GATE_X, GATE_Y2 - 6 - i * 4)
    py5.no_stroke()

    # Move & show particles
    for p in particles:
        # Demon logic: only allow fast (red) particles through
        if abs(p.x - GATE_X) < p.base_r and (GATE_Y1 < p.y < GATE_Y2):
            if p.speed() >= speed_threshold:
                # nudge across
                if p.x < GATE_X and p.vx > 0.6:
                    p.x = GATE_X + p.base_r + 2
                elif p.x > GATE_X and p.vx < -0.6:
                    p.x = GATE_X - p.base_r - 2
            else:
                # bounce slow particles
                p.vx *= -1.0
                p.x += p.vx * 1.5
        p.move()
        p.show()

    # HUD: counts & instructions
    py5.fill(40, 40, 60)
    py5.text_size(14)
    py5.text_align(py5.LEFT, py5.TOP)
    py5.text(f"Blue: {len(blue_particles)}", 36, 48)
    py5.text(f"Red: {len(red_particles)}", WIDTH - 120, 48)
    py5.text_align(py5.LEFT, py5.BOTTOM)
    py5.text("Space: pause  R: reset  ←/→: threshold", 20, HEIGHT - 18)


# --- UI & helpers

def draw_container(x, y, w, h, label, col, count):
    # soft rounded box
    py5.fill(py5.red(col), py5.green(col), py5.blue(col), 28)
    py5.no_stroke()
    py5.rect(x, y, w, h, 14)
    # label
    py5.fill(py5.red(col), py5.green(col), py5.blue(col))
    py5.text_size(16)
    py5.text_align(py5.CENTER, py5.TOP)
    py5.text(label, x + w // 2, y + 8)
    # count badge
    py5.fill(py5.red(col), py5.green(col), py5.blue(col))
    py5.ellipse(x + w // 2, y + h - 28, 48, 28)
    py5.fill(255)
    py5.text_size(14)
    py5.text_align(py5.CENTER, py5.CENTER)
    py5.text(str(count), x + w // 2, y + h - 28)
    py5.no_stroke()


def draw_slider():
    # track
    py5.fill(240)
    py5.no_stroke()
    py5.rect(slider_x, slider_y, slider_w, slider_h, 8)
    # knob
    kn_x = int(slider_x + (speed_threshold - slider_min) / (slider_max - slider_min) * slider_w)
    py5.fill(60, 20, 100)
    py5.stroke(255, 255, 255, 140)
    py5.stroke_weight(2)
    py5.ellipse(kn_x, slider_y + slider_h // 2, slider_knob_r * 2, slider_knob_r * 2)
    py5.no_stroke()
    # label
    py5.fill(30, 30, 60)
    py5.text_size(14)
    py5.text_align(py5.CENTER, py5.CENTER)
    py5.text(f"Speed threshold: {speed_threshold:.2f}", WIDTH // 2, slider_y - 16)


def draw_demon(x, y, phase):
    # body shadow
    py5.no_stroke()
    py5.fill(20, 18, 30, 160)
    py5.ellipse(x + 8, y + 24, 72, 88)
    # body
    py5.fill(98, 20, 140)
    py5.ellipse(x, y + 16, 64, 80)
    # head
    py5.fill(140, 40, 200)
    py5.ellipse(x, y - 26, 44, 44)
    # eyes
    eye_wobble = math.sin(py5.frame_count * 0.12) * 2
    py5.fill(255)
    py5.ellipse(x - 10, y - 28 + eye_wobble, 10, 8)
    py5.ellipse(x + 10, y - 28 - eye_wobble, 10, 8)
    py5.fill(20)
    py5.ellipse(x - 10, y - 28 + eye_wobble, 4, 4)
    py5.ellipse(x + 10, y - 28 - eye_wobble, 4, 4)
    # smile
    py5.no_fill()
    py5.stroke(20)
    py5.stroke_weight(2)
    py5.arc(x, y - 18, 22, 12, math.pi * 0.15, math.pi * 0.85)
    py5.no_stroke()
    # horns
    py5.stroke(200, 140, 220)
    py5.stroke_weight(3)
    py5.line(x - 16, y - 48, x - 28, y - 66)
    py5.line(x + 16, y - 48, x + 28, y - 66)
    py5.no_stroke()
    # small animated hand pointing at gate
    hand_x = x + 34 + math.sin(py5.frame_count * 0.18) * 6 * phase
    hand_y = y + 4
    py5.fill(140, 40, 200)
    py5.ellipse(hand_x, hand_y, 16, 12)


# --- Input

def mouse_pressed():
    global slider_dragging
    # check knob hit
    kn_x = int(slider_x + (speed_threshold - slider_min) / (slider_max - slider_min) * slider_w)
    if py5.dist(py5.mouse_x, py5.mouse_y, kn_x, slider_y + slider_h // 2) < slider_knob_r * 1.2:
        slider_dragging = True


def mouse_released():
    global slider_dragging
    slider_dragging = False


def mouse_dragged():
    global speed_threshold, slider_dragging
    if slider_dragging:
        mx = min(max(py5.mouse_x, slider_x), slider_x + slider_w)
        speed_threshold = slider_min + (mx - slider_x) / slider_w * (slider_max - slider_min)


def key_pressed():
    global paused, particles, speed_threshold
    k = py5.key
    if k == ' ':
        paused = not paused
    elif k == 'r' or k == 'R':
        particles = [Particle() for _ in range(NUM_PARTICLES)]
    elif k == py5.CODED:
        # arrow keys handled via key_code
        if py5.key_code == py5.LEFT:
            speed_threshold = max(slider_min, speed_threshold - 0.1)
        elif py5.key_code == py5.RIGHT:
            speed_threshold = min(slider_max, speed_threshold + 0.1)


# --- Run
py5.run_sketch()
