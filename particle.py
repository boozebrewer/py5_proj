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
        
        self.molecule_type = random.choice(["h2o", "co2", "o2"])
        if self.molecule_type == "h2o":
            self.base_r = 5.0
        elif self.molecule_type == "co2":
            self.base_r = 7.0
        else:  # o2
            self.base_r = 6.0
        
        self.rot_angle = random.uniform(0, math.tau)
        self.rot_speed = random.uniform(-0.05, 0.05)

        max_trail_len = random.randint(10, 25)
        self.trail: Deque[Tuple[float, float]] = deque(maxlen=max_trail_len)
        self.age = 0
        self.lifespan = random.uniform(120, 300)  # in frames

    def is_dead(self) -> bool:
        return self.age > self.lifespan

    def update(self, w: int, h: int, paused: bool):
        if paused:
            return
        self.age += 1
        self.rot_angle += self.rot_speed
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
