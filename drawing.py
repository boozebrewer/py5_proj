"""
Drawing functions for the Maxwell's Demon simulation.
"""

import math
from collections import deque
from typing import Any, Deque, List, Optional, Tuple

import py5

from particle import Particle
from utils import ensure_assets_dir
import config

def speed_color(s: float):
    t = min(max((s - 0.2) / (3.0 - 0.2), 0.0), 1.0)
    r = int(60 + 195 * t)
    g = int(160 * (1 - t))
    b = int(200 - 100 * t)
    return py5.color(r, g, b, 255)

def create_demon_graphic(size: int):
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
            ensure_assets_dir(config.ASSETS_DIR)
            img.save(config.DEMON_PNG)
        except Exception:
            pass
        return img
    except Exception:
        return g

def draw_background():
    for i in range(config.HEIGHT):
        t = i / config.HEIGHT
        r = int(20 + 80 * (1 - t))
        g = int(28 + 90 * (1 - t))
        b = int(40 + 160 * t)
        py5.stroke(r, g, b)
        py5.line(0, i, config.WIDTH, i)
    py5.no_stroke()
    py5.fill(255, 255, 255, 180)
    py5.rect(12, 12, config.WIDTH - 24, config.HEIGHT - 24, 20)

def draw_demon(x: float, y: float, demon_img: Optional[Any]):
    if demon_img:
        py5.image_mode(py5.CENTER)
        try:
            py5.image(demon_img, x, y, 140, 140)
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

def draw_gate_aura():
    py5.no_fill()
    for i in range(6):
        a = int(30 * (1 - i / 6))
        py5.stroke(200, 120, 240, a)
        py5.stroke_weight(6 - i)
        py5.line(config.GATE_X, config.GATE_Y1 + 6 + i * 4, config.GATE_X, config.GATE_Y2 - 6 - i * 4)
    py5.no_stroke()

def draw_particle(p: Particle):
    col = speed_color(p.speed())
    life_t = p.age / p.lifespan
    # parabolic fade in/out
    alpha_mul = min(1.0, 4.0 * life_t * (1.0 - life_t))

    # glow
    glow_alpha = int(80 * alpha_mul)
    py5.no_stroke()
    py5.fill(py5.red(col), py5.green(col), py5.blue(col), glow_alpha)
    glow_r = p.base_r * (3.0 + 2.5 * math.sin(life_t * math.pi))
    py5.ellipse(p.x, p.y, glow_r * 2, glow_r * 2)

    # trail
    if len(p.trail) > 1:
        for i, (tx, ty) in enumerate(p.trail):
            trail_t = i / len(p.trail)
            a = int(alpha_mul * (30 + 200 * trail_t))
            py5.no_stroke()
            py5.fill(py5.red(col), py5.green(col), py5.blue(col), a)
            size = p.base_r * (0.2 + 0.5 * trail_t)
            py5.ellipse(tx, ty, size * 2, size * 2)

    # core molecule
    py5.push_matrix()
    py5.translate(p.x, p.y)
    py5.rotate(p.rot_angle)
    
    alpha = int(255 * alpha_mul)
    
    O_color = (240, 50, 50, alpha)
    H_color = (245, 245, 245, alpha)
    C_color = (80, 80, 80, alpha)
    
    O_rad, H_rad, C_rad = 4, 2.5, 4.5
    
    py5.stroke(20, 20, 30, int(180 * alpha_mul))
    py5.stroke_weight(1.5)

    if p.molecule_type == "h2o":
        # H2O - bent molecule
        angle = math.radians(104.5 / 2)
        dist = 6
        # Oxygen
        py5.fill(*O_color)
        py5.ellipse(0, 0, O_rad * 2, O_rad * 2)
        # Hydrogens
        py5.fill(*H_color)
        hx1, hy1 = dist * math.cos(angle), dist * math.sin(angle)
        hx2, hy2 = dist * math.cos(-angle), dist * math.sin(-angle)
        py5.ellipse(hx1, hy1, H_rad * 2, H_rad * 2)
        py5.ellipse(hx2, hy2, H_rad * 2, H_rad * 2)
    elif p.molecule_type == "co2":
        # CO2 - linear molecule
        dist = 8
        # Carbon
        py5.fill(*C_color)
        py5.ellipse(0, 0, C_rad * 2, C_rad * 2)
        # Oxygens
        py5.fill(*O_color)
        py5.ellipse(-dist, 0, O_rad * 2, O_rad * 2)
        py5.ellipse(dist, 0, O_rad * 2, O_rad * 2)
    else:  # o2
        # O2 - diatomic
        dist = 4
        py5.fill(*O_color)
        py5.ellipse(-dist, 0, O_rad * 2, O_rad * 2)
        py5.ellipse(dist, 0, O_rad * 2, O_rad * 2)

    py5.pop_matrix()
    py5.no_stroke()

def draw_container(x, y, w, h, label, col, count):
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

def draw_plots(sketch):
    # temperature plot (top-right)
    plot_w, plot_h = 340, 150
    plot_x = config.WIDTH - plot_w - 24
    plot_y = 44
    py5.fill(250, 250, 250, 230)
    py5.stroke(200)
    py5.rect(plot_x, plot_y, plot_w, plot_h, 8)
    py5.no_stroke()
    # determine scale
    all_vals = list(sketch.left_temp_history) + list(sketch.right_temp_history)
    max_val = max(all_vals) if all_vals else 1.0
    max_val = max(0.1, max_val)
    # draw filled series
    def draw_fill(series: Deque[float], col: Tuple[int, int, int]):
        n = len(series)
        if n < 2:
            return
        step_x = plot_w / max(1, config.TEMP_HISTORY_LEN - 1)
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

    draw_fill(sketch.left_temp_history, (80, 160, 240))
    draw_fill(sketch.right_temp_history, (240, 110, 90))
    # legend
    py5.no_stroke()
    py5.fill(80, 160, 240)
    py5.ellipse(plot_x + 14, plot_y + 14, 10, 10)
    py5.fill(240, 110, 90)
    py5.ellipse(plot_x + 14 + 80, plot_y + 14, 10, 10)
    py5.fill(40)
    py5.text_align(py5.LEFT, py5.CENTER)
    left_val = sketch.left_temp_history[-1] if sketch.left_temp_history else 0.0
    right_val = sketch.right_temp_history[-1] if sketch.right_temp_history else 0.0
    py5.text(f"Left: {left_val:.2f}", plot_x + 32, plot_y + 14)
    py5.text(f"Right: {right_val:.2f}", plot_x + 32 + 80, plot_y + 14)
    py5.text_align(py5.RIGHT, py5.CENTER)
    py5.text(f"threshold: {sketch.speed_threshold:.2f}", plot_x + plot_w - 10, plot_y + 14)

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
        step_x = cs_w / max(1, config.TEMP_HISTORY_LEN - 1)
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
    draw_counts(sketch.left_count_history, (80,160,240), 0)
    draw_counts(sketch.right_count_history, (240,110,90), 0)

    # histogram of speeds (bottom-left)
    hist_w, hist_h = 260, 140
    hist_x, hist_y = 28, config.HEIGHT - hist_h - 28
    py5.fill(250,250,250,230)
    py5.stroke(200)
    py5.rect(hist_x, hist_y, hist_w, hist_h, 8)
    py5.no_stroke()
    speeds = [p.speed() for p in sketch.particles]
    if speeds:
        maxs = max(speeds)
        bins = [0] * sketch.hist_bins
        for s in speeds:
            idx = min(sketch.hist_bins - 1, int((s / maxs) * sketch.hist_bins))
            bins[idx] += 1
        # draw bars
        bw = hist_w / sketch.hist_bins
        py5.fill(80,160,240)
        for i, b in enumerate(bins):
            h = int((b / max(bins)) * (hist_h - 28)) if max(bins) else 0
            py5.rect(int(hist_x + i * bw), hist_y + hist_h - h - 12, int(bw - 2), h)

def draw_gate_door(door_open):
    door_h = config.GATE_Y2 - config.GATE_Y1
    door_w = 12
    open_offset = int(door_open * 22)
    py5.fill(40, 40, 60, 220)
    py5.no_stroke()
    py5.rect(config.GATE_X - door_w - open_offset, config.GATE_Y1, door_w, door_h)
    py5.rect(config.GATE_X + open_offset, config.GATE_Y1, door_w, door_h)

def draw_hud(sketch):
    py5.fill(40, 40, 60)
    py5.text_size(14)
    py5.text_align(py5.LEFT, py5.TOP)
    left_c = sketch.left_count_history[-1] if sketch.left_count_history else 0
    right_c = sketch.right_count_history[-1] if sketch.right_count_history else 0
    py5.text(f"Left: {left_c}", 36, 48)
    py5.text(f"Right: {right_c}", config.WIDTH - 140, 48)
    py5.text_align(py5.LEFT, py5.BOTTOM)
    py5.text("Space: pause  R: reset  ←/→: threshold", 20, config.HEIGHT - 18)
    py5.fill(70)
    py5.text_align(py5.RIGHT, py5.TOP)
    py5.text(f"Cumulative ΔE: {sketch.cumulative_energy_transfer:.2f}", config.WIDTH - 24, 48)
