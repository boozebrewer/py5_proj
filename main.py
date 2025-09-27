"""
Main entry point for the Maxwell's Demon simulation.
"""

import py5

from demon_sketch import DemonSketch

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
