import py5
import random

NUM_PARTICLES = 50
WIDTH, HEIGHT = 400, 400
GATE_X = WIDTH // 2
GATE_Y1, GATE_Y2 = HEIGHT // 2 - 40, HEIGHT // 2 + 40

class Particle:
    def __init__(self):
        self.x = random.uniform(50, WIDTH - 50)
        self.y = random.uniform(50, HEIGHT - 50)
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.r = 6

    def move(self):
        self.x += self.vx
        self.y += self.vy

        # Bounce off walls
        if self.x < self.r or self.x > WIDTH - self.r:
            self.vx *= -1
        if self.y < self.r or self.y > HEIGHT - self.r:
            self.vy *= -1

        # Bounce off gate except at opening
        if abs(self.x - GATE_X) < self.r:
            if not (GATE_Y1 < self.y < GATE_Y2):
                self.vx *= -1
                self.x += self.vx

    def show(self):
        speed = (self.vx ** 2 + self.vy ** 2) ** 0.5
        color = py5.color(0, 0, 255) if speed < 2 else py5.color(255, 0, 0)
        py5.fill(color)
        py5.circle(self.x, self.y, self.r * 2)

particles = []

def setup():
    py5.size(WIDTH, HEIGHT)
    py5.background(200)
    global particles
    particles = [Particle() for _ in range(NUM_PARTICLES)]

def draw():
    py5.background(200)
    # Draw box
    py5.stroke(0)
    py5.no_fill()
    py5.rect(0, 0, WIDTH, HEIGHT)
    # Draw gate
    py5.stroke(0)
    py5.stroke_weight(4)
    py5.line(GATE_X, 0, GATE_X, GATE_Y1)
    py5.line(GATE_X, GATE_Y2, GATE_X, HEIGHT)
    py5.stroke_weight(1)
    py5.no_stroke()
    py5.fill(0)
    py5.text("Demon", GATE_X - 20, HEIGHT // 2)

    # Split particles into red and blue containers
    red_particles = []
    blue_particles = []
    for p in particles:
        speed = (p.vx ** 2 + p.vy ** 2) ** 0.5
        if speed < 2:
            blue_particles.append(p)
        else:
            red_particles.append(p)

    # Draw containers and counts
    py5.fill(0, 0, 255, 80)
    py5.rect(10, 10, 60, HEIGHT - 20)
    py5.fill(255, 0, 0, 80)
    py5.rect(WIDTH - 70, 10, 60, HEIGHT - 20)
    py5.fill(0)
    py5.text(f"Blue: {len(blue_particles)}", 15, 30)
    py5.text(f"Red: {len(red_particles)}", WIDTH - 65, 30)

    # Move and show particles
    for p in particles:
        # Maxwell Demon logic
        if abs(p.x - GATE_X) < p.r and (GATE_Y1 < p.y < GATE_Y2):
            # If moving right and fast, let through
            if p.x < GATE_X and p.vx > 1.5:
                p.x = GATE_X + p.r
            # If moving left and slow, let through
            elif p.x > GATE_X and p.vx < -1.5:
                p.x = GATE_X - p.r
        p.move()
        p.show()

py5.run_sketch()
