"""
Main sketch class for the Maxwell's Demon simulation.
"""

import os
import math
from collections import deque
from typing import Any, Deque, List, Optional

import py5

import config
from particle import Particle
from utils import ensure_assets_dir
import drawing

class DemonSketch:
    def __init__(self):
        self.particles: List[Particle] = []
        self.speed_threshold = config.SPEED_THRESHOLD
        self.paused = False
        self.door_open = 0.0
        self.door_timer = 0
        self.door_frames = 18
        self.left_temp_history: Deque[float] = deque(maxlen=config.TEMP_HISTORY_LEN)
        self.right_temp_history: Deque[float] = deque(maxlen=config.TEMP_HISTORY_LEN)
        self.left_count_history: Deque[int] = deque(maxlen=config.TEMP_HISTORY_LEN)
        self.right_count_history: Deque[int] = deque(maxlen=config.TEMP_HISTORY_LEN)
        self.hist_bins = config.HIST_BINS
        self.cumulative_energy_transfer = 0.0
        self.demon_img: Optional[Any] = None

    def settings(self):
        py5.size(config.WIDTH, config.HEIGHT)
    
    def setup(self):
        py5.frame_rate(60)
        self.reset_particles()
        ensure_assets_dir(config.ASSETS_DIR)
        self.demon_img = self._load_or_make_demon()

    def reset_particles(self):
        self.particles = [Particle(config.WIDTH, config.HEIGHT) for _ in range(config.NUM_PARTICLES)]
        self.cumulative_energy_transfer = 0.0

    def _load_or_make_demon(self):
        # prefer user-provided asset
        try:
            if os.path.exists(config.DEMON_PNG):
                return py5.load_image(config.DEMON_PNG)
        except Exception:
            pass
        return drawing.create_demon_graphic(config.DEMON_IMG_SIZE)

    def draw(self):
        drawing.draw_background()
        gate_phase = (py5.frame_count % 120) / 120.0
        drawing.draw_demon(config.GATE_X - 72, config.HEIGHT // 2 + 4, self.demon_img)
        self._update_and_draw_particles()
        drawing.draw_gate_aura()
        drawing.draw_gate_door(self.door_open)
        drawing.draw_plots(self)
        drawing.draw_hud(self)

    def _update_and_draw_particles(self):
        left_particles = []
        right_particles = []
        any_open = False
        for p in self.particles:
            near_gate = abs(p.x - config.GATE_X) < (p.base_r + 2) and (config.GATE_Y1 < p.y < config.GATE_Y2)
            if near_gate:
                s = p.speed()
                if p.x < config.GATE_X and p.vx > 0:
                    if s >= self.speed_threshold:
                        p.x = config.GATE_X + p.base_r + 2
                        any_open = True
                        self.cumulative_energy_transfer += 0.5 * (s ** 2)
                    else:
                        p.vx *= -1.0
                        p.x += p.vx * 1.2
                elif p.x > config.GATE_X and p.vx < 0:
                    if s <= self.speed_threshold:
                        p.x = config.GATE_X - p.base_r - 2
                        any_open = True
                        self.cumulative_energy_transfer -= 0.5 * (s ** 2)
                    else:
                        p.vx *= -1.0
                        p.x += p.vx * 1.2
            p.move(config.WIDTH, config.HEIGHT, self.paused)
            drawing.draw_particle(p)
            if p.x < config.GATE_X:
                left_particles.append(p)
            else:
                right_particles.append(p)

        if any_open:
            self.door_open = 1.0
            self.door_timer = self.door_frames
        else:
            if self.door_timer > 0:
                self.door_timer -= 1
                self.door_open = self.door_timer / self.door_frames
            else:
                self.door_open = 0.0

        left_temp = self._mean_sq_speed(left_particles)
        right_temp = self._mean_sq_speed(right_particles)
        self.left_temp_history.append(left_temp)
        self.right_temp_history.append(right_temp)
        self.left_count_history.append(len(left_particles))
        self.right_count_history.append(len(right_particles))

        drawing.draw_container(28, 64, 110, config.HEIGHT - 128, 'Left (cold)', py5.color(80, 160, 240), len(left_particles))
        drawing.draw_container(config.WIDTH - 138, 64, 110, config.HEIGHT - 128, 'Right (hot)', py5.color(240, 110, 90), len(right_particles))

    def _mean_sq_speed(self, particles: List[Particle]) -> float:
        if not particles:
            return 0.0
        return sum((p.speed() ** 2) for p in particles) / len(particles)

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
