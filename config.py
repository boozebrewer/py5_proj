"""
Configuration constants for the Maxwell's Demon simulation.
"""

import os

# --- Simulation
NUM_PARTICLES = 120
WIDTH, HEIGHT = 900, 560
GATE_X = WIDTH // 2
GATE_Y1, GATE_Y2 = HEIGHT // 2 - 80, HEIGHT // 2 + 80

# --- Assets
ASSETS_DIR = 'assets'
DEMON_PNG = os.path.join(ASSETS_DIR, 'demon.png')
DEMON_IMG_SIZE = 512

# --- UI & Plots
TEMP_HISTORY_LEN = 600
HIST_BINS = 24

# --- Defaults
SPEED_THRESHOLD = 2.0
