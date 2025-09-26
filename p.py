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
        self.r = 8
        self.trail = []

    def move(self):
        self.x += self.vx
        self.y += self.vy

        # Store trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 15:
            self.trail.pop(0)

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
        color = py5.color(0, 120, 255) if speed < 2 else py5.color(255, 60, 60)
        # Draw trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(80 + 120 * i / len(self.trail)) if self.trail else 200
            py5.fill(py5.color(py5.red(color), py5.green(color), py5.blue(color), alpha))
            py5.no_stroke()
            py5.circle(tx, ty, self.r * 1.2)
        # Draw particle with shadow
        py5.fill(py5.color(40, 40, 40, 80))
        py5.no_stroke()
        py5.circle(self.x + 3, self.y + 3, self.r * 2.2)
        py5.fill(color)
        py5.stroke(255)
        py5.stroke_weight(1)
        py5.circle(self.x, self.y, self.r * 2)

particles = []

def setup():
    py5.size(WIDTH, HEIGHT)
    py5.background(200)
    global particles
    particles = [Particle() for _ in range(NUM_PARTICLES)]

def draw():
    # Gradient background
    for i in range(HEIGHT):
        py5.stroke(py5.color(220 - i//4, 240 - i//8, 255 - i//6))
        py5.line(0, i, WIDTH, i)
    # Draw box with rounded corners and shadow
    py5.fill(255, 255, 255, 180)
    py5.stroke(80, 80, 120, 120)
    py5.stroke_weight(3)
    py5.rect(5, 5, WIDTH-10, HEIGHT-10, 30)
    # Animated gate
    gate_anim = py5.frame_count % 60
    gate_color = py5.color(120 + gate_anim*2, 120, 220 - gate_anim*3)
    py5.stroke(gate_color)
    py5.stroke_weight(7)
    py5.line(GATE_X, 10, GATE_X, GATE_Y1)
    py5.line(GATE_X, GATE_Y2, GATE_X, HEIGHT-10)
    py5.stroke_weight(1)
    py5.no_stroke()
    py5.fill(40, 40, 60, 180)
    py5.text_size(22)
    py5.text("Maxwell's Demon", GATE_X - 90, HEIGHT // 2 - 10)

    # Split particles into red and blue containers
    red_particles = []
    blue_particles = []
    for p in particles:
        speed = (p.vx ** 2 + p.vy ** 2) ** 0.5
        if speed < 2:
            blue_particles.append(p)
        else:
            red_particles.append(p)

    # Draw containers with rounded corners and gradient
    py5.no_stroke()
    for i in range(60):
        py5.fill(0, 120, 255, 40 + i)
        py5.rect(10, 10 + i, 60, HEIGHT - 20 - 2*i, 18)
    for i in range(60):
        py5.fill(255, 60, 60, 40 + i)
        py5.rect(WIDTH - 70, 10 + i, 60, HEIGHT - 20 - 2*i, 18)
    # Container shadows
    py5.fill(40, 40, 60, 60)
    py5.rect(13, HEIGHT-25, 54, 10, 8)
    py5.rect(WIDTH-67, HEIGHT-25, 54, 10, 8)
    # Container labels
    py5.fill(0, 120, 255)
    py5.text_size(18)
    py5.text(f"Blue: {len(blue_particles)}", 15, 35)
    py5.fill(255, 60, 60)
    py5.text(f"Red: {len(red_particles)}", WIDTH - 65, 35)

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
