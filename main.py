#!/usr/bin/env python3
"""Draw a 1024x1024 newspaper front page summing up the world news of
Saturday 21 November 2026, using only the Python standard library.

The program renders every pixel itself (own bitmap font, own PNG encoder)
and writes entry.png to $MAKEFUN_OUTPUT_DIR (default: out/). Deterministic:
no clock, no randomness, no network -- two runs produce identical bytes.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---- palette ----
PAPER = (247, 242, 231)
PANEL = (255, 253, 246)
INK = (18, 18, 22)
RED = (176, 30, 30)
GREY = (110, 106, 98)
NIGHT = (14, 22, 46)
NIGHT2 = (24, 36, 68)
SEA = (36, 82, 122)
SEA2 = (52, 110, 158)
FIRE = (232, 116, 28)
FLAME = (244, 178, 44)
GOLD = (196, 152, 40)
WHITE = (245, 245, 240)
SMOKE = (150, 148, 142)
GREEN = (46, 120, 66)

# ---- 5x7 bitmap font (uppercase, digits, punctuation) ----
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("###..", "#..#.", "#...#", "#...#", "#...#", "#..#.", "###.."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "/": ("....#", "...#.", "...#.", "..#..", "..#..", ".#...", "#...."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "$": ("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "*": (".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "@": (".###.", "#...#", "#.###", "#.#.#", "#.##.", "#....", ".###."),
}


def new_canvas():
    return bytearray(bytes(PAPER) * (W * H))


def set_px(buf, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = color


def fill_rect(buf, x, y, w, h, color):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            buf[i], buf[i + 1], buf[i + 2] = color


def rect_outline(buf, x, y, w, h, color, t=2):
    fill_rect(buf, x, y, w, t, color)
    fill_rect(buf, x, y + h - t, w, t, color)
    fill_rect(buf, x, y, t, h, color)
    fill_rect(buf, x + w - t, y, t, h, color)


def line(buf, x0, y0, x1, y1, color):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        set_px(buf, x0, y0, color)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def circle(buf, cx, cy, r, color, filled=True):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d = (xx - cx) ** 2 + (yy - cy) ** 2
            if filled:
                if d <= r * r:
                    set_px(buf, xx, yy, color)
            else:
                if r * r - 2 * r <= d <= r * r:
                    set_px(buf, xx, yy, color)


def fill_poly(buf, pts, color):
    ys = [p[1] for p in pts]
    n = len(pts)
    for y in range(min(ys), max(ys) + 1):
        xs = []
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            if (y1 <= y < y2) or (y2 <= y < y1):
                xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            xa, xb = int(xs[i]), int(xs[i + 1])
            fill_rect(buf, xa, y, xb - xa + 1, 1, color)


def starburst(buf, cx, cy, r, color, rays=8):
    for i in range(rays):
        a = math.pi * 2 * i / rays
        line(buf, cx, cy, int(cx + r * math.cos(a)), int(cy + r * math.sin(a)), color)
    circle(buf, cx, cy, max(2, r // 4), color)


def arc(buf, x0, y0, x1, y1, peak, color):
    cx, cy = (x0 + x1) // 2, min(y0, y1) - peak
    prev = None
    for k in range(25):
        t = k / 24
        x = int((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1)
        y = int((1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1)
        if prev:
            line(buf, prev[0], prev[1], x, y, color)
        prev = (x, y)


# ---- text ----

def char_w(scale):
    return 6 * scale


def text_w(text, scale):
    return len(text) * char_w(scale) - scale if text else 0


def draw_char(buf, x, y, ch, scale, color):
    glyph = FONT.get(ch, FONT[" "])
    for r, row in enumerate(glyph):
        for c, bit in enumerate(row):
            if bit == "#":
                fill_rect(buf, x + c * scale, y + r * scale, scale, scale, color)


def draw_text(buf, x, y, text, scale, color):
    cx = x
    for ch in text:
        draw_char(buf, cx, y, ch, scale, color)
        cx += char_w(scale)


def draw_text_centered(buf, cx, y, text, scale, color):
    draw_text(buf, cx - text_w(text, scale) // 2, y, text, scale, color)


def wrap(text, max_chars):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        if not cur:
            cur = w
        elif len(cur) + 1 + len(w) <= max_chars:
            cur += " " + w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_block(buf, x, y, text, scale, color, max_chars, lh):
    for i, ln in enumerate(wrap(text, max_chars)):
        draw_text(buf, x, y + i * lh, ln, scale, color)
    return y + len(wrap(text, max_chars)) * lh


# ---- illustrations ----

def bahrain_scene(buf, x, y, w, h):
    """Night attack over Bahrain: skyline, missile arcs, factory fire."""
    fill_rect(buf, x, y, w, h, NIGHT)
    # stars (fixed positions)
    for sx, sy in [(30, 14), (90, 26), (150, 10), (230, 22), (310, 12),
                   (390, 28), (470, 16), (560, 24), (640, 10), (720, 26),
                   (800, 14), (880, 22), (940, 12), (60, 44), (520, 40)]:
        if sx < w:
            set_px(buf, x + sx, y + sy, WHITE)
            set_px(buf, x + sx + 1, y + sy, WHITE)
    # moon
    circle(buf, x + w - 70, y + 26, 14, (226, 224, 200))
    circle(buf, x + w - 74, y + 22, 11, NIGHT)
    # skyline
    base = y + h - 18
    buildings = [(0, 34), (52, 52), (104, 40), (150, 62), (210, 46), (268, 70),
                 (330, 44), (392, 58), (452, 38), (520, 66), (590, 48),
                 (650, 58), (712, 42), (772, 60), (832, 46), (890, 56)]
    for bx, bh in buildings:
        if bx < w - 20:
            fill_rect(buf, x + bx, base - bh, 48, bh + 18, NIGHT2)
            for wy in range(base - bh + 6, base - 4, 12):
                for wx in range(bx + 8, bx + 42, 14):
                    fill_rect(buf, x + wx, wy, 5, 6, FLAME)
    # industrial site with chimneys, left-center
    fx, fy = x + 330, base - 30
    fill_rect(buf, fx, fy, 120, 30, (30, 30, 36))
    fill_rect(buf, fx + 12, fy - 34, 10, 34, (30, 30, 36))
    fill_rect(buf, fx + 34, fy - 44, 10, 44, (30, 30, 36))
    fill_rect(buf, fx + 56, fy - 28, 10, 28, (30, 30, 36))
    # fire glow + flames on the factory
    circle(buf, fx + 60, fy - 6, 34, (232, 116, 28))
    circle(buf, fx + 60, fy - 6, 24, FLAME)
    fill_poly(buf, [(fx + 44, fy - 2), (fx + 60, fy - 44), (fx + 76, fy - 2)], FIRE)
    fill_poly(buf, [(fx + 52, fy - 2), (fx + 60, fy - 30), (fx + 68, fy - 2)], (255, 226, 120))
    # smoke
    for sx, sy, sr in [(fx + 30, fy - 48, 9), (fx + 46, fy - 56, 11),
                       (fx + 66, fy - 60, 13), (fx + 88, fy - 56, 10)]:
        circle(buf, sx, sy, sr, SMOKE)
    # missile arcs (red trails) + bright heads
    arc(buf, x + 40, y + 8, x + 330, y + h - 60, 26, (255, 90, 60))
    arc(buf, x + 120, y + 4, x + 430, y + h - 70, 34, (255, 90, 60))
    arc(buf, x + 700, y + 6, x + 560, y + h - 80, 30, (255, 90, 60))
    circle(buf, x + 330, y + h - 60, 4, (255, 240, 200))
    circle(buf, x + 430, y + h - 70, 4, (255, 240, 200))
    circle(buf, x + 560, y + h - 80, 4, (255, 240, 200))
    # air-defence intercepts: white starbursts high in the sky
    starburst(buf, x + 620, y + 34, 16, WHITE)
    starburst(buf, x + 180, y + 30, 13, WHITE)
    starburst(buf, x + 830, y + 46, 12, WHITE)
    # caption
    draw_text(buf, x + 10, y + h - 16, "BAHRAIN, SATURDAY NIGHT", 1, WHITE)


def tanker_scene(buf, x, y, w, h):
    """Two tankers struck off Khasab: sea, tanker, smoke, impact flash."""
    fill_rect(buf, x, y, w, h, SEA)
    for i in range(6):
        fill_rect(buf, x, y + h - 8 - i * 10, w, 3, SEA2)
    # tanker hull
    hx, hy = x + 30, y + h - 30
    fill_rect(buf, hx, hy, 220, 20, (22, 22, 26))
    fill_poly(buf, [(hx + 220, hy), (hx + 252, hy + 10), (hx + 220, hy + 20)], (22, 22, 26))
    fill_rect(buf, hx + 150, hy - 20, 34, 20, (200, 200, 196))
    fill_rect(buf, hx + 156, hy - 26, 8, 6, (200, 200, 196))
    # impact flash on the stern + smoke
    starburst(buf, hx + 12, hy + 6, 14, FLAME)
    circle(buf, hx + 12, hy + 6, 6, FIRE)
    for sx, sy, sr in [(hx - 6, hy - 12, 9), (hx - 16, hy - 20, 11), (hx - 10, hy - 26, 12)]:
        circle(buf, sx, sy, sr, SMOKE)
    # second tanker, far right, engine-room hit
    hx2 = x + w - 190
    fill_rect(buf, hx2, hy + 4, 150, 16, (30, 30, 36))
    fill_poly(buf, [(hx2 + 150, hy + 4), (hx2 + 172, hy + 12), (hx2 + 150, hy + 20)], (30, 30, 36))
    fill_rect(buf, hx2 + 96, hy - 16, 26, 20, (180, 180, 176))
    starburst(buf, hx2 + 110, hy - 2, 11, FLAME)
    # projectile streak
    line(buf, x + w - 30, y + 6, hx2 + 110, hy - 2, (255, 240, 200))
    draw_text(buf, x + 8, y + 6, "KHASAB, OMAN", 1, WHITE)


def riyadh_scene(buf, x, y, w, h):
    """Riyadh skyline at dawn: PIF tower, three intercepts."""
    fill_rect(buf, x, y, w, h, NIGHT)
    base = y + h - 10
    # PIF tower (tall, centre)
    tx = x + w // 2 - 16
    fill_rect(buf, tx, y + 12, 32, base - y - 12, (52, 70, 116))
    fill_poly(buf, [(tx, y + 12), (tx + 16, y + 2), (tx + 32, y + 12)], (52, 70, 116))
    for wy in range(y + 20, base - 6, 10):
        fill_rect(buf, tx + 6, wy, 20, 4, FLAME)
    # flanking buildings
    for bx, bh in [(10, 30), (52, 40), (96, 26), (w - 130, 34), (w - 84, 42), (w - 42, 28)]:
        fill_rect(buf, x + bx, base - bh, 38, bh, (44, 60, 100))
    # three intercept starbursts
    starburst(buf, x + 70, y + 22, 12, WHITE)
    starburst(buf, x + w // 2, y + 30, 14, WHITE)
    starburst(buf, x + w - 70, y + 20, 12, WHITE)
    # falling debris lines
    line(buf, x + 70, y + 36, x + 64, y + 52, FLAME)
    line(buf, x + w - 70, y + 34, x + w - 76, y + 50, FLAME)
    draw_text(buf, x + 8, y + h - 14, "RIYADH, DAWN", 1, WHITE)


def kryvyi_scene(buf, x, y, w, h):
    """Damaged apartment block: broken silhouette, fires, smoke."""
    fill_rect(buf, x, y, w, h, (58, 56, 62))
    base = y + h - 8
    # broken apartment block
    fill_rect(buf, x + 40, y + 18, 90, base - y - 18, (28, 28, 32))
    fill_poly(buf, [(x + 40, y + 18), (x + 62, y + 30), (x + 84, y + 14),
                    (x + 106, y + 28), (x + 130, y + 18), (x + 130, y + 34),
                    (x + 40, y + 34)], (28, 28, 32))
    for wy in range(y + 40, base - 6, 12):
        for wx in range(48, 122, 16):
            fill_rect(buf, x + wx, wy, 7, 7, FLAME)
    # second block
    fill_rect(buf, x + 160, y + 30, 70, base - y - 30, (34, 34, 40))
    # fires at the base
    fill_poly(buf, [(x + 56, base), (x + 66, base - 22), (x + 76, base)], FIRE)
    fill_poly(buf, [(x + 96, base), (x + 104, base - 16), (x + 112, base)], FIRE)
    # smoke
    for sx, sy, sr in [(x + 90, y + 14, 7), (x + 110, y + 10, 8)]:
        circle(buf, sx, sy, sr, SMOKE)
    # rescue light
    circle(buf, x + w - 40, base - 14, 6, (255, 240, 200))
    draw_text(buf, x + w - 68, y + 6, "KRYVYI RIH", 1, WHITE)


def mexico_scene(buf, x, y, w, h):
    """Desert road, badge star, roadblock fire."""
    fill_rect(buf, x, y, w, h, (214, 196, 160))
    # sun
    circle(buf, x + w - 42, y + 22, 14, FLAME)
    # mountains
    fill_poly(buf, [(x, y + h - 30), (x + 60, y + h - 48), (x + 120, y + h - 30)], (150, 118, 84))
    fill_poly(buf, [(x + 100, y + h - 30), (x + 170, y + h - 52), (x + 240, y + h - 30)], (138, 106, 74))
    # road
    fill_rect(buf, x, y + h - 22, w, 22, (70, 66, 60))
    for dx in range(8, w, 28):
        fill_rect(buf, x + dx, y + h - 12, 14, 3, (240, 234, 210))
    # badge star (gold)
    cx, cy = x + 52, y + 30
    circle(buf, cx, cy, 18, GOLD)
    circle(buf, cx, cy, 14, (232, 196, 90))
    starburst(buf, cx, cy, 12, (120, 84, 20), rays=5)
    # roadblock fire, right
    fill_rect(buf, x + w - 90, y + h - 44, 60, 22, (40, 38, 34))
    fill_poly(buf, [(x + w - 82, y + h - 44), (x + w - 60, y + h - 52), (x + w - 38, y + h - 44)], FIRE)
    draw_text(buf, x + 8, y + 6, "GUASAVE, SINALOA", 1, INK)


def gold_chart(buf, x, y, w, h):
    """Gold's week: closes Mon 3857, Tue 3849, Wed 3725, Thu 3625, Fri 3538."""
    fill_rect(buf, x, y, w, h, PANEL)
    draw_text(buf, x + w - 132, y + 6, "LOWEST SINCE SEPT 2025", 1, GREY)
    cx0, cy0 = x + 34, y + 16
    cw, ch = w - 48, h - 40
    rect_outline(buf, cx0, cy0, cw, ch, GREY, 1)
    vals = [3857, 3849, 3725, 3625, 3538]
    days = ["MON", "TUE", "WED", "THU", "FRI"]
    lo, hi = 3450, 3950
    pts = []
    for i, v in enumerate(vals):
        px = cx0 + 10 + i * (cw - 20) // 4
        py = cy0 + ch - 6 - int((v - lo) / (hi - lo) * (ch - 12))
        pts.append((px, py))
    for gv, gl in ((3500, "3.5K"), (3700, "3.7K"), (3900, "3.9K")):
        gy = cy0 + ch - 6 - int((gv - lo) / (hi - lo) * (ch - 12))
        for gx in range(cx0, cx0 + cw, 8):
            set_px(buf, gx, gy, (200, 196, 186))
        draw_text(buf, x + 4, gy - 4, gl, 1, GREY)
    for i in range(4):
        line(buf, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], RED)
        line(buf, pts[i][0], pts[i][1] + 1, pts[i + 1][0], pts[i + 1][1] + 1, RED)
    for (px, py), d in zip(pts, days):
        circle(buf, px, py, 4, RED)
        draw_text(buf, px - 9, cy0 + ch + 4, d, 1, INK)
    draw_text(buf, pts[-1][0] - 34, pts[-1][1] - 14, "$3,538", 1, RED)


def cop31_scene(buf, x, y, w, h):
    """Globe with a rising thermometer: COP31 in overtime."""
    fill_rect(buf, x, y, w, h, (226, 238, 244))
    # globe
    cx, cy = x + 56, y + h // 2 + 2
    circle(buf, cx, cy, 26, SEA)
    fill_poly(buf, [(cx - 20, cy - 8), (cx - 2, cy - 18), (cx + 12, cy - 6),
                    (cx - 4, cy + 4)], GREEN)
    fill_poly(buf, [(cx - 8, cy + 12), (cx + 10, cy + 8), (cx + 20, cy + 20),
                    (cx - 2, cy + 24)], GREEN)
    # thermometer
    tx = x + w - 52
    fill_rect(buf, tx, y + 12, 12, h - 34, WHITE)
    rect_outline(buf, tx, y + 12, 12, h - 34, INK, 1)
    fill_rect(buf, tx + 2, y + 26, 8, h - 48, RED)
    circle(buf, tx + 6, y + h - 16, 10, RED)
    draw_text(buf, tx - 30, y + 14, "1.5C", 2, RED)
    draw_text(buf, x + w - 98, y + 6, "ANTALYA, TURKEY", 1, INK)


# ---- page composition ----

def panel(buf, x, y, w, h, kicker, headline, body, scene=None, scene_h=0):
    fill_rect(buf, x, y, w, h, PANEL)
    rect_outline(buf, x, y, w, h, INK, 2)
    pad = 12
    cy = y + 10
    draw_text(buf, x + pad, cy, kicker, 1, RED)
    cy += 12
    head_lines = wrap(headline, (w - 2 * pad) // 18)
    for ln in head_lines:
        draw_text(buf, x + pad, cy, ln, 3, INK)
        cy += 24
    cy += 2
    body_max = (w - 2 * pad) // 12
    for ln in wrap(body, body_max):
        draw_text(buf, x + pad, cy, ln, 2, INK)
        cy += 17
    if scene is not None:
        scene(buf, x + 8, y + h - scene_h - 8, w - 16, scene_h)


def build():
    buf = new_canvas()
    # outer frame
    rect_outline(buf, 8, 8, W - 16, H - 16, INK, 3)

    # masthead
    draw_text_centered(buf, W // 2, 22, "THE WORLD TODAY", 7, INK)
    fill_rect(buf, 24, 76, W - 48, 2, INK)
    fill_rect(buf, 24, 80, W - 48, 1, INK)
    draw_text_centered(buf, W // 2, 86, "SATURDAY, 21 NOVEMBER 2026", 3, RED)
    draw_text(buf, 24, 86, "ONE DAY", 2, INK)
    draw_text(buf, W - 24 - text_w("ONE PAGE", 2), 86, "ONE PAGE", 2, INK)
    fill_rect(buf, 24, 112, W - 48, 2, INK)

    # ---- lead story ----
    ly = 120
    draw_text(buf, 24, ly, "THE GULF - WAR IN THE MIDDLE EAST", 2, RED)
    draw_text(buf, 24, ly + 20, "IRAN STRIKES BAHRAIN", 6, INK)
    deck = ("IRAN'S REVOLUTIONARY GUARDS SAY MISSILES AND DRONES HIT U.S. "
            "POSITIONS AT AL-RIFFA AND AWALI. BAHRAIN SAYS A CIVILIAN "
            "INDUSTRIAL SITE WAS HIT AND SET ON FIRE. NO INJURIES REPORTED. "
            "AIR DEFENCES DOWNED OTHER ATTACKS.")
    draw_block(buf, 24, ly + 68, deck, 2, INK, 80, 17)
    bahrain_scene(buf, 24, ly + 126, W - 48, 112)

    # ---- row 2: Hormuz + Riyadh ----
    ry = 368
    pw, ph = 482, 190
    panel(buf, 24, ry, pw, ph,
          "STRAIT OF HORMUZ",
          "TWO TANKERS HIT OFF KHASAB",
          "TWO TANKERS HIT 50 MINUTES APART: ONE IN THE STERN, ONE IN THE "
          "ENGINE ROOM. NO CASUALTIES.",
          tanker_scene, 56)
    panel(buf, 24 + pw + 12, ry, pw, ph,
          "SAUDI ARABIA",
          "3 MISSILES AT RIYADH STOPPED",
          "THREE BALLISTIC MISSILES FIRED AT THE CAPITAL WERE DOWNED EARLY "
          "SATURDAY, TWO DAYS AFTER THE PIF TOWER WAS HIT.",
          riyadh_scene, 56)

    # ---- row 3: Kryvyi Rih + Mexico ----
    ry = 567
    panel(buf, 24, ry, pw, ph,
          "UKRAINE",
          "MISSILE HITS ZELENSKYY'S HOMETOWN",
          "A RUSSIAN STRIKE KILLED 2, INCLUDING A 7-YEAR-OLD BOY, AND "
          "WOUNDED ABOUT 60. FOLLOW-UP STRIKES HIT RESCUERS.",
          kryvyi_scene, 56)
    panel(buf, 24 + pw + 12, ry, pw, ph,
          "MEXICO",
          "MEXICO CAPTURES 'EL CHAPO ISIDRO'",
          "FBI MOST-WANTED BOSS FAUSTO ISIDRO MEZA FLORES SEIZED IN "
          "GUASAVE. 11 DEAD: 7 GUNMEN, 4 SOLDIERS.",
          mexico_scene, 56)

    # ---- row 4: gold + COP31 ----
    ry = 766
    panel(buf, 24, ry, pw, ph,
          "MARKETS - GOLD",
          "GOLD'S WORST WEEK IN 8 MONTHS",
          "SPOT GOLD CLOSED FRIDAY AT $3,538, DOWN ABOUT 9% ON THE WEEK.",
          gold_chart, 72)
    panel(buf, 24 + pw + 12, ry, pw, ph,
          "CLIMATE - COP31",
          "CLIMATE TALKS DEEP IN OVERTIME",
          "NEGOTIATORS IN ANTALYA MISS THE FRIDAY DEADLINE AS THE DRAFT "
          "DEAL DROPS ALL MENTION OF FOSSIL FUELS.",
          cop31_scene, 56)

    # ---- footer ticker ----
    fy = 966
    fill_rect(buf, 24, fy - 4, W - 48, 1, INK)
    draw_text(buf, 24, fy + 4,
              "ALSO: U.S. STOCKS IN CORRECTION IN AI SELL-OFF - "
              "TRUMP WEIGHS NEW IRAN STRIKES", 2, INK)
    draw_text(buf, 24, fy + 22,
              "SOURCES: REUTERS, AP, AFP, UKMTO - ALL EVENTS SATURDAY "
              "21 NOVEMBER 2026", 1, GREY)
    return buf


def write_png(path, buf):
    raw = b"".join(b"\x00" + bytes(buf[y * W * 3:(y + 1) * W * 3])
                   for y in range(H))

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        return out + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "out"
    os.makedirs(outdir, exist_ok=True)
    buf = build()
    n = write_png(os.path.join(outdir, "entry.png"), buf)
    print(f"wrote {os.path.join(outdir, 'entry.png')} ({n} bytes)")


if __name__ == "__main__":
    main()
