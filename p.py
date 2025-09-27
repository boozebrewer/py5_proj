"""
Refactored Maxwell's Demon sketch using py5.
- Demon allows fast left->right and slow right->left.
- Draws realtime temperature plot, counts sparkline, and speed histogram.
- Saves a generated high-res demon PNG to assets/demon.png for future runs.
Controls:
- Space: pause
- R: reset
- Left/Right: adjust speed threshold
"""

import os
import math
import random
from collections import deque
from typing import Any, Deque, List, Optional, Tuple

import py5

# --- Configuration
NUM_PARTICLES = 120
WIDTH, HEIGHT = 900, 560
GATE_X = WIDTH // 2
GATE_Y1, GATE_Y2 = HEIGHT // 2 - 80, HEIGHT // 2 + 80

ASSETS_DIR = 'assets'
DEMON_PNG = os.path.join(ASSETS_DIR, 'demon.png')
DEMON_IMG_SIZE = 512

TEMP_HISTORY_LEN = 600
HIST_BINS = 24

# defaults
SPEED_THRESHOLD = 2.0


# --- Utility helpers

def ensure_assets_dir():
    if not os.path.exists(ASSETS_DIR):
        os.makedirs(ASSETS_DIR, exist_ok=True)


# --- Particle model
class Particle:
    def __init__(self, w: int, h: int):
        pad = 80
        self.x = random.uniform(pad, w - pad)
        self.y = random.uniform(pad, h - pad)
        angle = random.uniform(0, math.tau)
        speed = random.uniform(0.2, 3.0)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.base_r = random.uniform(3.5, 7.5)
        self.trail: Deque[Tuple[float, float]] = deque(maxlen=18)

    def move(self, w: int, h: int, paused: bool):
        if paused:
            return
        self.x += self.vx
        self.y += self.vy
        self.trail.append((self.x, self.y))
        # walls
        if self.x < self.base_r or self.x > w - self.base_r:
            self.vx *= -1
            self.x = min(max(self.x, self.base_r), w - self.base_r)
        if self.y < self.base_r or self.y > h - self.base_r:
            self.vy *= -1
            self.y = min(max(self.y, self.base_r), h - self.base_r)

    def speed(self) -> float:
        return math.hypot(self.vx, self.vy)


# --- DemonSketch: encapsulates state and drawing
class DemonSketch:
    def __init__(self):
        self.particles: List[Particle] = []
        self.speed_threshold = SPEED_THRESHOLD
        self.paused = False
        self.door_open = 0.0
        self.door_timer = 0
        self.door_frames = 18
        self.left_temp_history: Deque[float] = deque(maxlen=TEMP_HISTORY_LEN)
        self.right_temp_history: Deque[float] = deque(maxlen=TEMP_HISTORY_LEN)
        self.left_count_history: Deque[int] = deque(maxlen=TEMP_HISTORY_LEN)
        self.right_count_history: Deque[int] = deque(maxlen=TEMP_HISTORY_LEN)
        self.hist_bins = HIST_BINS
        self.cumulative_energy_transfer = 0.0
        self.demon_img: Optional[Any] = None

    def settings(self):
        py5.size(WIDTH, HEIGHT)
    
    def setup(self):
        py5.frame_rate(60)
        self.reset_particles()
        ensure_assets_dir()
        self.demon_img = self._load_or_make_demon()

    def reset_particles(self):
        self.particles = [Particle(WIDTH, HEIGHT) for _ in range(NUM_PARTICLES)]
        self.cumulative_energy_transfer = 0.0

    # --- Demon image handling
    def _create_demon_graphic(self, size: int):
        """Create and return a PImage-like object. Also save PNG to disk."""
        try:
            g = py5.create_graphics(size, size)
        except Exception:
            return None
        g.begin_draw()
        g.clear()
        cx = cy = size // 2
        s = size / 128.0
        # shadow
        g.no_stroke()
        g.fill(20, 18, 30, 220)
        g.ellipse(cx + int(8 * s), cy + int(24 * s), int(96 * s), int(120 * s))
        # body
        g.fill(98, 20, 140)
        g.ellipse(cx, cy + int(18 * s), int(92 * s), int(112 * s))
        # head
        g.fill(140, 40, 200)
        g.ellipse(cx, cy - int(30 * s), int(56 * s), int(56 * s))
        # eyes
        g.fill(255)
        g.ellipse(cx - int(14 * s), cy - int(32 * s), int(14 * s), int(12 * s))
        g.ellipse(cx + int(14 * s), cy - int(32 * s), int(14 * s), int(12 * s))
        g.fill(20)
        g.ellipse(cx - int(14 * s), cy - int(32 * s), int(6 * s), int(6 * s))
        g.ellipse(cx + int(14 * s), cy - int(32 * s), int(6 * s), int(6 * s))
        # smile
        g.no_fill()
        g.stroke(20)
        g.stroke_weight(int(3 * s))
        g.arc(cx, cy - int(22 * s), int(28 * s), int(16 * s), math.pi * 0.18, math.pi * 0.82)
        g.no_stroke()
        # horns
        g.stroke(220, 160, 240)
        g.stroke_weight(int(4 * s))
        g.line(cx - int(20 * s), cy - int(56 * s), cx - int(38 * s), cy - int(86 * s))
        g.line(cx + int(20 * s), cy - int(56 * s), cx + int(38 * s), cy - int(86 * s))
        g.no_stroke()
        # hand
        g.fill(140, 40, 200)
        g.ellipse(cx + int(44 * s), cy + int(8 * s), int(22 * s), int(16 * s))
        g.end_draw()
        try:
            img = g.get()
            # Save to PNG for future runs
            try:
                ensure_assets_dir()
                img.save(DEMON_PNG)
            except Exception:
                pass
            return img
        except Exception:
            return g

    def _load_or_make_demon(self):
        # prefer user-provided asset
        try:
            if os.path.exists(DEMON_PNG):
                return py5.load_image(DEMON_PNG)
        except Exception:
            pass
        return self._create_demon_graphic(DEMON_IMG_SIZE)

    # --- Main draw loop
    def draw(self):
        # background
        self._draw_background()
        gate_phase = (py5.frame_count % 120) / 120.0
        # demon image
        self._draw_demon(GATE_X - 72, HEIGHT // 2 + 4, gate_phase)
        # draw containers and stats
        self._update_and_draw_particles()
        # door and aura
        self._draw_gate_aura(gate_phase)
        self._draw_gate_door()
        # plots
        self._draw_plots()
        # HUD
        self._draw_hud()

    # --- Drawing helpers
    def _draw_background(self):
        for i in range(HEIGHT):
            t = i / HEIGHT
            r = int(20 + 80 * (1 - t))
            g = int(28 + 90 * (1 - t))
            b = int(40 + 160 * t)
            py5.stroke(r, g, b)
            py5.line(0, i, WIDTH, i)
        py5.no_stroke()
        py5.fill(255, 255, 255, 180)
        py5.rect(12, 12, WIDTH - 24, HEIGHT - 24, 20)

    def _draw_demon(self, x: float, y: float, phase: float):
        img = self.demon_img
        if img:
            py5.image_mode(py5.CENTER)
            try:
                py5.image(img, x, y, 140, 140)
            except Exception:
                # fallback vector
                py5.no_stroke()
                py5.fill(98, 20, 140)
                py5.ellipse(x, y + 16, 64, 80)
            py5.image_mode(py5.CORNER)
        else:
            py5.no_stroke()
            py5.fill(98, 20, 140)
            py5.ellipse(x, y + 16, 64, 80)

    def _draw_gate_aura(self, phase: float):
        py5.no_fill()
        for i in range(6):
            a = int(30 * (1 - i / 6))
            py5.stroke(200, 120, 240, a)
            py5.stroke_weight(6 - i)
            py5.line(GATE_X, GATE_Y1 + 6 + i * 4, GATE_X, GATE_Y2 - 6 - i * 4)
        py5.no_stroke()

    def _update_and_draw_particles(self):
        left_particles = []
        right_particles = []
        # demon directional logic
        any_open = False
        for p in self.particles:
            near_gate = abs(p.x - GATE_X) < (p.base_r + 2) and (GATE_Y1 < p.y < GATE_Y2)
            if near_gate:
                s = p.speed()
                if p.x < GATE_X and p.vx > 0:
                    # coming from left
                    if s >= self.speed_threshold:
                        p.x = GATE_X + p.base_r + 2
                        any_open = True
                        self.cumulative_energy_transfer += 0.5 * (s ** 2)
                    else:
                        p.vx *= -1.0
                        p.x += p.vx * 1.2
                elif p.x > GATE_X and p.vx < 0:
                    # coming from right
                    if s <= self.speed_threshold:
                        p.x = GATE_X - p.base_r - 2
                        any_open = True
                        self.cumulative_energy_transfer -= 0.5 * (s ** 2)
                    else:
                        p.vx *= -1.0
                        p.x += p.vx * 1.2
            p.move(WIDTH, HEIGHT, self.paused)
            # draw particle
            self._draw_particle(p)
            if p.x < GATE_X:
                left_particles.append(p)
            else:
                right_particles.append(p)

        # animate door
        if any_open:
            self.door_open = 1.0
            self.door_timer = self.door_frames
        else:
            if self.door_timer > 0:
                self.door_timer -= 1
                self.door_open = self.door_timer / self.door_frames
            else:
                self.door_open = 0.0

        # update stats
        left_temp = self._mean_sq_speed(left_particles)
        right_temp = self._mean_sq_speed(right_particles)
        self.left_temp_history.append(left_temp)
        self.right_temp_history.append(right_temp)
        self.left_count_history.append(len(left_particles))
        self.right_count_history.append(len(right_particles))

        # draw containers
        self._draw_container(28, 64, 110, HEIGHT - 128, 'Left (cold)', py5.color(80, 160, 240), len(left_particles))
        self._draw_container(WIDTH - 138, 64, 110, HEIGHT - 128, 'Right (hot)', py5.color(240, 110, 90), len(right_particles))

    def _draw_particle(self, p: Particle):
        col = self._speed_color(p.speed())
        recent = list(p.trail)[-10:]
        for i, (tx, ty) in enumerate(recent):
            a = int(30 + 220 * (i / max(1, len(recent))))
            py5.no_stroke()
            py5.fill(py5.red(col), py5.green(col), py5.blue(col), a)
            size = p.base_r * (0.6 + 0.6 * i / 10)
            py5.ellipse(tx, ty, size * 2, size * 2)
        py5.stroke(255, 255, 255, 120)
        py5.stroke_weight(1)
        py5.fill(col)
        r = p.base_r * (1 + 0.6 * (p.speed() / (SPEED_THRESHOLD + 0.1)))
        py5.ellipse(p.x, p.y, r * 2, r * 2)
        py5.no_stroke()

    def _draw_container(self, x, y, w, h, label, col, count):
        py5.fill(py5.red(col), py5.green(col), py5.blue(col), 28)
        py5.no_stroke()
        py5.rect(x, y, w, h, 14)
        py5.fill(py5.red(col), py5.green(col), py5.blue(col))
        py5.text_size(14)
        py5.text_align(py5.CENTER, py5.TOP)
        py5.text(label, x + w // 2, y + 8)
        py5.fill(py5.red(col), py5.green(col), py5.blue(col))
        py5.ellipse(x + w // 2, y + h - 28, 48, 28)
        py5.fill(255)
        py5.text_size(14)
        py5.text_align(py5.CENTER, py5.CENTER)
        py5.text(str(count), x + w // 2, y + h - 28)
        py5.no_stroke()

    def _mean_sq_speed(self, particles: List[Particle]) -> float:
        if not particles:
            return 0.0
        return sum((p.speed() ** 2) for p in particles) / len(particles)

    def _speed_color(self, s: float):
        t = min(max((s - 0.2) / (3.0 - 0.2), 0.0), 1.0)
        r = int(60 + 195 * t)
        g = int(160 * (1 - t))
        b = int(200 - 100 * t)
        return py5.color(r, g, b)

    def _draw_plots(self):
        # temperature plot (top-right)
        plot_w, plot_h = 340, 150
        plot_x = WIDTH - plot_w - 24
        plot_y = 44
        py5.fill(250, 250, 250, 230)
        py5.stroke(200)
        py5.rect(plot_x, plot_y, plot_w, plot_h, 8)
        py5.no_stroke()
        # determine scale
        all_vals = list(self.left_temp_history) + list(self.right_temp_history)
        max_val = max(all_vals) if all_vals else 1.0
        max_val = max(0.1, max_val)
        # draw filled series
        def draw_fill(series: Deque[float], col: Tuple[int, int, int]):
            n = len(series)
            if n < 2:
                return
            step_x = plot_w / max(1, TEMP_HISTORY_LEN - 1)
            pts: List[Tuple[int, int]] = []
            for i, v in enumerate(series):
                sx = int(plot_x + i * step_x)
                sy = int(plot_y + plot_h - 8 - (v / max_val) * (plot_h - 24))
                pts.append((sx, sy))
            py5.no_stroke()
            py5.fill(col[0], col[1], col[2], 60)
            for i in range(len(pts) - 1):
                x1, y1 = pts[i]
                x2, y2 = pts[i + 1]
                py5.rect(x1, y1, max(1, x2 - x1), plot_y + plot_h - 8 - y1)
            py5.no_fill()
            py5.stroke(col[0], col[1], col[2])
            py5.stroke_weight(2)
            px, py_ = pts[0]
            for nx, ny in pts[1:]:
                py5.line(px, py_, nx, ny)
                px, py_ = nx, ny

        draw_fill(self.left_temp_history, (80, 160, 240))
        draw_fill(self.right_temp_history, (240, 110, 90))
        # legend
        py5.no_stroke()
        py5.fill(80, 160, 240)
        py5.ellipse(plot_x + 14, plot_y + 14, 10, 10)
        py5.fill(240, 110, 90)
        py5.ellipse(plot_x + 14 + 80, plot_y + 14, 10, 10)
        py5.fill(40)
        py5.text_align(py5.LEFT, py5.CENTER)
        left_val = self.left_temp_history[-1] if self.left_temp_history else 0.0
        right_val = self.right_temp_history[-1] if self.right_temp_history else 0.0
        py5.text(f"Left: {left_val:.2f}", plot_x + 32, plot_y + 14)
        py5.text(f"Right: {right_val:.2f}", plot_x + 32 + 80, plot_y + 14)
        py5.text_align(py5.RIGHT, py5.CENTER)
        py5.text(f"threshold: {self.speed_threshold:.2f}", plot_x + plot_w - 10, plot_y + 14)

        # counts sparkline (below temp)
        cs_w, cs_h = plot_w, 48
        cs_x, cs_y = plot_x, plot_y + plot_h + 12
        py5.fill(250, 250, 250, 230)
        py5.stroke(200)
        py5.rect(cs_x, cs_y, cs_w, cs_h, 8)
        py5.no_stroke()
        def draw_counts(series: Deque[int], col: Tuple[int,int,int], y_offset: int):
            n = len(series)
            if n < 2:
                return
            step_x = cs_w / max(1, TEMP_HISTORY_LEN - 1)
            pts = []
            maxc = max(series) if series else 1
            for i, v in enumerate(series):
                sx = int(cs_x + i * step_x)
                sy = int(cs_y + cs_h - 6 - (v / maxc) * (cs_h - 12))
                pts.append((sx, sy))
            py5.stroke(col[0], col[1], col[2])
            py5.stroke_weight(1)
            px, py_ = pts[0]
            for nx, ny in pts[1:]:
                py5.line(px, py_, nx, ny)
                px, py_ = nx, ny
        draw_counts(self.left_count_history, (80,160,240), 0)
        draw_counts(self.right_count_history, (240,110,90), 0)

        # histogram of speeds (bottom-left)
        hist_w, hist_h = 260, 140
        hist_x, hist_y = 28, HEIGHT - hist_h - 28
        py5.fill(250,250,250,230)
        py5.stroke(200)
        py5.rect(hist_x, hist_y, hist_w, hist_h, 8)
        py5.no_stroke()
        speeds = [p.speed() for p in self.particles]
        if speeds:
            maxs = max(speeds)
            bins = [0] * self.hist_bins
            for s in speeds:
                idx = min(self.hist_bins - 1, int((s / maxs) * self.hist_bins))
                bins[idx] += 1
            # draw bars
            bw = hist_w / self.hist_bins
            py5.fill(80,160,240)
            for i, b in enumerate(bins):
                h = int((b / max(bins)) * (hist_h - 28)) if max(bins) else 0
                py5.rect(int(hist_x + i * bw), hist_y + hist_h - h - 12, int(bw - 2), h)

    def _draw_gate_door(self):
        door_h = GATE_Y2 - GATE_Y1
        door_w = 12
        open_offset = int(self.door_open * 22)
        py5.fill(40, 40, 60, 220)
        py5.no_stroke()
        py5.rect(GATE_X - door_w - open_offset, GATE_Y1, door_w, door_h)
        py5.rect(GATE_X + open_offset, GATE_Y1, door_w, door_h)

    def _draw_hud(self):
        py5.fill(40, 40, 60)
        py5.text_size(14)
        py5.text_align(py5.LEFT, py5.TOP)
        left_c = self.left_count_history[-1] if self.left_count_history else 0
        right_c = self.right_count_history[-1] if self.right_count_history else 0
        py5.text(f"Left: {left_c}", 36, 48)
        py5.text(f"Right: {right_c}", WIDTH - 140, 48)
        py5.text_align(py5.LEFT, py5.BOTTOM)
        py5.text("Space: pause  R: reset  ←/→: threshold", 20, HEIGHT - 18)
        py5.fill(70)
        py5.text_align(py5.RIGHT, py5.TOP)
        py5.text(f"Cumulative ΔE: {self.cumulative_energy_transfer:.2f}", WIDTH - 24, 48)

    # --- Input handlers
    def key_pressed(self):
        k = py5.key
        if k == ' ':
            self.paused = not self.paused
        elif k == 'r' or k == 'R':
            self.reset_particles()
        elif k == py5.CODED:
            if py5.key_code == py5.LEFT:
                self.speed_threshold = max(0.1, self.speed_threshold - 0.1)
            elif py5.key_code == py5.RIGHT:
                self.speed_threshold = min(6.0, self.speed_threshold + 0.1)


# --- Global sketch instance
sketch = DemonSketch()


def settings():
    sketch.settings()


def setup():
    sketch.setup()


def draw():
    sketch.draw()


def key_pressed():
    sketch.key_pressed()


# Run the sketch
py5.run_sketch()
