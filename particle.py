"""
Particle model for the simulation.
"""

import math
import random
from collections import deque
from typing import Deque, Tuple

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
