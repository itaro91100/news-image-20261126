#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""news-image-20261126 -- one-page front page of Thursday 26 November 2026.

Pure Python 3 standard library, no network, no dependencies: it draws a
1024x1024 newspaper front page in code (5x7 bitmap font, vector scenes) and
writes it to ``$MAKEFUN_OUTPUT_DIR/entry.png`` (default ``/output``).

Run locally:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

Every story on the page was checked against live coverage of 25-26 November
2026 (Reuters, AP, The Guardian, Euronews, Xinhua, ESA/JAXA). The page names
its day in the masthead and cites its sources in the footer.
"""

import os
import struct
import zlib
from pathlib import Path

W, H = 1024, 1024

# ---------------------------------------------------------------- palette ---
PAPER = (247, 243, 234)   # warm newsprint
INK = (18, 18, 20)        # near-black text
RED = (178, 34, 34)       # kicker / alert red
NAVY = (20, 33, 61)       # masthead band
GOLD = (201, 162, 39)     # masthead rule
GREY = (90, 88, 82)       # secondary text
LIGHT = (232, 227, 214)   # panel tint
WHITE = (255, 255, 255)
SKY = (28, 38, 66)        # night sky for the lead scene
FLAME = (232, 110, 30)    # explosion orange
FLAME2 = (245, 196, 66)   # explosion yellow
SMOKE = (120, 118, 112)
STEEL = (70, 84, 110)
GREEN = (46, 125, 50)
TEAL = (0, 105, 120)

# ------------------------------------------------- 5x7 bitmap font (A-Z) ---
# Each glyph is 7 rows of 5 bits. Text is rendered in capitals only, in the
# manner of a newspaper headline font; lowercase input is upper-cased.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
}

FONT.update({
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ";": ("00000", "01100", "00000", "01100", "00000", "00100", "01000"),
    ":": ("00000", "01100", "00000", "01100", "00000", "01100", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
})
BLANK = ("00000", "00000", "00000", "00000", "00000", "00000", "00000")


# ------------------------------------------------------------ canvas + PNG --
class Canvas:
    """An RGB raster with a tiny vector drawing kit and a PNG writer."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        for yy in range(max(0, y), min(self.h, y + h)):
            base = (yy * self.w + max(0, x)) * 3
            span = min(self.w, x + w) - max(0, x)
            if span > 0:
                self.px[base:base + span * 3] = bytes(c) * span

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        """Bresenham line, inclusive of both ends."""
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill and d <= r * r:
                    self.set(xx, yy, c)
                elif not fill and abs(d - r * r) <= r:
                    self.set(xx, yy, c)

    def triangle(self, pts, c):
        """Scanline-filled triangle from three (x, y) points."""
        (x0, y0), (x1, y1), (x2, y2) = pts
        ymin, ymax = min(y0, y1, y2), max(y0, y1, y2)
        for yy in range(ymin, ymax + 1):
            xs = []
            for (ax, ay), (bx, by) in (((x0, y0), (x1, y1)),
                                       ((x1, y1), (x2, y2)),
                                       ((x2, y2), (x0, y0))):
                if ay == by:
                    continue
                if min(ay, by) <= yy < max(ay, by):
                    xs.append(ax + (yy - ay) * (bx - ax) / (by - ay))
            if len(xs) >= 2:
                xa, xb = int(min(xs)), int(max(xs))
                self.rect(xa, yy, xb - xa + 1, 1, c)

    def starburst(self, cx, cy, r_out, r_in, points, c):
        """A spiky explosion star: alternating outer/inner radii."""
        import math
        pts = []
        for i in range(points * 2):
            r = r_out if i % 2 == 0 else r_in
            a = math.pi * i / points - math.pi / 2
            pts.append((cx + int(r * math.cos(a)), cy + int(r * math.sin(a))))
        for i in range(1, len(pts) - 1):
            self.triangle((pts[0], pts[i], pts[i + 1]), c)

    def to_png(self):
        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)
            raw += self.px[y * stride:(y + 1) * stride]

        def chunk(kind, data):
            out = struct.pack(">I", len(data)) + kind + data
            return out + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
                + chunk(b"IEND", b""))


# ------------------------------------------------------------ text helpers --
def text_w(text, s):
    return len(text) * 6 * s - s


def draw_text(cv, x, y, text, s, c):
    """Draw upper-case text at scale s (glyph cell 6*s wide, 7*s tall)."""
    for i, ch in enumerate(text.upper()):
        glyph = FONT.get(ch, BLANK)
        gx = x + i * 6 * s
        for r, row in enumerate(glyph):
            for col, bit in enumerate(row):
                if bit == "1":
                    cv.rect(gx + col * s, y + r * s, s, s, c)


def draw_centred(cv, cx, y, text, s, c):
    draw_text(cv, cx - text_w(text, s) // 2, y, text, s, c)


def wrap(text, s, max_w):
    """Greedy word wrap; returns lines that fit max_w pixels at scale s."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = word if not cur else cur + " " + word
        if text_w(trial, s) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def paragraph(cv, x, y, text, s, max_w, c, max_lines=None, lh=None):
    lines = wrap(text, s, max_w)
    if max_lines:
        lines = lines[:max_lines]
    step = lh if lh is not None else 10 * s
    for i, ln in enumerate(lines):
        draw_text(cv, x, y + i * step, ln, s, c)
    return y + len(lines) * step


def kicker(cv, x, y, text, s=2, c=RED):
    draw_text(cv, x, y, text, s, c)
    return y + 8 * s


# --------------------------------------------------------- scene drawing --
def scene_ukraine(cv, x, y, w, h):
    """Night sky over a city: drone trails, a refinery fire, black skyline."""
    cv.rect(x, y, w, h, SKY)
    for sx, sy in ((18, 22), (70, 40), (130, 16), (210, 48), (260, 26),
                   (300, 60), (40, 70), (180, 78), (330, 30)):
        cv.set(x + sx, y + sy, FLAME2)
    # drone trails arcing down to the blast
    cv.line(x + 30, y + 12, x + 190, y + 120, (150, 160, 200))
    cv.line(x + 320, y + 10, x + 230, y + 105, (150, 160, 200))
    cv.line(x + 340, y + 55, x + 250, y + 118, (150, 160, 200))
    for dx, dy in ((30, 12), (320, 10), (340, 55)):
        cv.rect(x + dx - 3, y + dy - 2, 7, 4, (200, 205, 215))
    # explosion
    cv.starburst(x + 215, y + 128, 58, 26, 9, FLAME)
    cv.starburst(x + 215, y + 128, 34, 16, 9, FLAME2)
    cv.circle(x + 215, y + 128, 16, WHITE)
    # refinery towers and skyline silhouettes
    cv.rect(x + 60, y + 150, 26, h - 150, INK)
    cv.rect(x + 96, y + 165, 18, h - 165, INK)
    cv.rect(x + 260, y + 158, 30, h - 158, INK)
    cv.rect(x + 300, y + 172, 22, h - 172, INK)
    cv.rect(x, y + 185, w, h - 185, INK)
    for wx in range(8, w - 10, 26):
        cv.rect(x + wx, y + 196, 8, 8, FLAME2)
    # smoke drifting right of the blast
    cv.circle(x + 300, y + 96, 12, SMOKE)
    cv.circle(x + 322, y + 78, 15, SMOKE)
    cv.circle(x + 340, y + 58, 12, SMOKE)


def scene_fire(cv, x, y, w, h):
    """A tanker fire on a highway: flames, smoke, charred road."""
    cv.rect(x, y, w, h, (44, 44, 52))
    cv.rect(x, y + h - 30, w, 30, (24, 24, 28))
    cv.rect(x, y + h - 32, w, 3, (220, 220, 210))
    # smoke first, so the flames stay in front of it
    cv.circle(x + 60, y + 12, 12, SMOKE)
    cv.circle(x + 95, y + 8, 14, SMOKE)
    cv.circle(x + 250, y + 12, 12, SMOKE)
    cv.circle(x + 285, y + 8, 13, SMOKE)
    # tanker lying across the road
    cv.rect(x + 30, y + h - 58, 150, 24, (150, 155, 165))
    cv.circle(x + 52, y + h - 32, 8, INK)
    cv.circle(x + 158, y + h - 32, 8, INK)
    # flames rising from the tanker (kept inside the scene)
    for fx, fh, fc in ((60, 30, FLAME), (95, 42, FLAME2), (130, 28, FLAME),
                       (165, 38, FLAME2), (200, 26, FLAME), (230, 34, FLAME2)):
        cv.triangle(((x + fx, y + h - 58), (x + fx + 22, y + h - 58),
                     (x + fx + 11, y + h - 58 - fh)), fc)
    # burnt cars
    cv.rect(x + 230, y + h - 52, 44, 18, (20, 20, 22))
    cv.rect(x + 280, y + h - 48, 36, 15, (30, 30, 34))


def scene_tariffs(cv, x, y, w, h):
    """Falling market bars under a red down arrow."""
    cv.rect(x, y, w, h, LIGHT)
    base = y + h - 30
    bars = [44, 56, 50, 38, 32, 22, 14]
    bw, gap = 26, 12
    for i, bh in enumerate(bars):
        bx = x + 24 + i * (bw + gap)
        cv.rect(bx, base - bh, bw, bh, STEEL if i < 4 else RED)
    cv.hline(x + 14, base, w - 28, INK, 2)
    # red down arrow over the bars
    ax = x + w - 78
    cv.vline(ax + 17, y + 18, 34, RED, 3)
    cv.line(ax + 17, y + 52, ax + 2, y + 38, RED)
    cv.line(ax + 17, y + 52, ax + 32, y + 38, RED)
    cv.line(ax + 2, y + 38, ax + 17, y + 52, RED)
    cv.line(ax + 32, y + 38, ax + 17, y + 52, RED)


def scene_sudan(cv, x, y, w, h):
    """A drone over rooftops at dusk, dust rising from a strike."""
    cv.rect(x, y, w, h, (196, 158, 110))
    cv.rect(x, y + h - 30, w, 30, (120, 84, 52))
    # rooftops
    for rx in range(0, w, 52):
        cv.rect(x + rx + 6, y + h - 58, 40, 28, (90, 62, 40))
        cv.triangle(((x + rx + 2, y + h - 58), (x + rx + 50, y + h - 58),
                     (x + rx + 26, y + h - 76)), (70, 46, 30))
    # drone with rotor blur
    dx, dy = x + w // 2, y + 18
    cv.rect(dx - 16, dy - 4, 32, 8, INK)
    cv.rect(dx - 3, dy - 12, 6, 24, INK)
    cv.hline(dx - 26, dy - 12, 52, INK, 2)
    cv.circle(dx, dy + 2, 5, RED)
    # dust cloud from the strike
    cv.circle(x + 60, y + h - 38, 12, (220, 200, 160))
    cv.circle(x + 84, y + h - 48, 15, (220, 200, 160))
    cv.circle(x + 110, y + h - 36, 10, (220, 200, 160))


def scene_gaza(cv, x, y, w, h):
    """A damaged apartment block at dawn, smoke over the roofline."""
    cv.rect(x, y, w, h, (226, 214, 196))
    cv.rect(x + 30, y + 28, 110, h - 28, (150, 140, 126))
    cv.rect(x + 160, y + 42, 90, h - 42, (170, 160, 146))
    cv.rect(x + 260, y + 56, 60, h - 56, (140, 130, 118))
    # windows in a regular grid, a few lit -- only where a block stands
    for wx in (x + 46, x + 74, x + 102):
        for wy in (y + 40, y + 56, y + 72):
            cv.rect(wx, wy, 10, 8, FLAME2 if (wx + wy) % 5 == 0 else INK)
    for wx in (x + 176, x + 204, x + 232):
        for wy in (y + 56, y + 72):
            cv.rect(wx, wy, 10, 8, FLAME2 if (wx + wy) % 5 == 0 else INK)
    cv.rect(x + 276, y + 72, 10, 8, INK)
    # smoke
    cv.circle(x + 90, y + 14, 10, SMOKE)
    cv.circle(x + 120, y + 8, 12, SMOKE)
    cv.circle(x + 150, y + 16, 9, SMOKE)


def scene_space(cv, x, y, w, h):
    """A rocket climbing past stars toward a ringed planet."""
    cv.rect(x, y, w, h, (12, 16, 44))
    for sx, sy in ((20, 14), (90, 30), (150, 12), (220, 44), (280, 18),
                   (40, 64), (260, 70), (120, 78), (200, 84), (330, 30)):
        cv.set(x + sx, y + sy, WHITE)
        cv.set(x + sx + 1, y + sy, WHITE)
    # ringed planet, lower right
    cv.circle(x + w - 62, y + h - 40, 30, TEAL)
    cv.line(x + w - 96, y + h - 26, x + w - 28, y + h - 54, FLAME2)
    cv.line(x + w - 92, y + h - 18, x + w - 32, y + h - 46, FLAME2)
    # rocket body climbing left of centre
    rx, ry = x + 96, y + 52
    cv.triangle(((rx, ry - 34), (rx - 12, ry - 8), (rx + 12, ry - 8)), WHITE)
    cv.rect(rx - 12, ry - 8, 24, 40, WHITE)
    cv.triangle(((rx - 12, ry + 20), (rx - 26, ry + 30), (rx - 12, ry + 30)), RED)
    cv.triangle(((rx + 12, ry + 20), (rx + 26, ry + 30), (rx + 12, ry + 30)), RED)
    cv.circle(rx, ry + 8, 6, NAVY)
    cv.triangle(((rx - 6, ry + 32), (rx + 6, ry + 32), (rx, ry + 38)), FLAME)
    # station arc
    cv.circle(x + 250, y + 40, 9, WHITE, fill=False)
    cv.line(x + 240, y + 40, x + 228, y + 34, WHITE)
    cv.line(x + 260, y + 40, x + 272, y + 34, WHITE)


# ---------------------------------------------------------------- stories --
# All facts checked against live coverage of 25-26 November 2026 (Reuters,
# AP, The Guardian, Euronews, Xinhua, ESA/JAXA). Nothing is invented; tolls
# are given as reported, with "at least" where the source says preliminary.
LEAD = {
    "kicker": "WAR IN UKRAINE - OVERNIGHT",
    "head": ["RUSSIAN DRONES KILL 7;", "KYIV HITS THREE", "REFINERIES IN REPLY"],
    "body": ("112 DRONES HIT ENERGY SITES ACROSS SIX REGIONS; 88 SHOT DOWN. "
             "UKRAINE STRUCK REFINERIES IN SAMARA AND ROSTOV AND THE "
             "SAVASLEYKA AIRBASE."),
}

ROW2 = [
    {
        "scene": scene_fire,
        "kicker": "EGYPT",
        "head": ["TANKER FIRE ON CAIRO", "RING ROAD KILLS 31"],
        "body": ("A PETROLEUM TANKER OVERTURNED IN GIZA; 27 VEHICLES "
                 "BURNED, 21 HURT."),
    },
    {
        "scene": scene_tariffs,
        "kicker": "TRADE - UNITED STATES",
        "head": ["TRUMP UNVEILS NEW", "TARIFFS; MARKETS SLIDE"],
        "body": ("NEW DUTIES AIM AT EXCESS FACTORY CAPACITY. STOCKS FELL "
                 "WORLDWIDE."),
    },
]

ROW3 = [
    {
        "scene": scene_sudan,
        "kicker": "SUDAN",
        "head": ["RSF DRONES", "KILL 19 IN SUDAN"],
        "body": ("HOMES HIT IN DAMAZIN, BLUE NILE, ON TUESDAY NIGHT; 20 "
                 "WOUNDED."),
    },
    {
        "scene": scene_gaza,
        "kicker": "GAZA",
        "head": ["HAMAS SECURITY", "CHIEF KILLED"],
        "body": ("ABU AL-OUF, HIS WIFE AND TWO DAUGHTERS, 13 AND 15, "
                 "DIED AT DAWN."),
    },
    {
        "scene": scene_space,
        "kicker": "SPACE",
        "head": ["FIRST PAKISTANI", "IN ORBIT"],
        "body": ("ZEESHAN ALI FLEW ON SHENZHOU-24, THE FIRST FOREIGNER "
                 "ON TIANGONG."),
    },
]

ALSO_TODAY = ("ALSO TODAY: THANKSGIVING IN THE U.S. - COLOMBIA MARKS 10 YEARS "
              "SINCE ITS PEACE DEAL - BANGLADESH RAISES GARMENT PAY 36% - "
              "BEPICOLOMBO DUE TO SHRINK ITS MERCURY ORBIT - U.N. TRIBUNAL: "
              "UNRWA SACKINGS RESTED ON UNPROVEN CLAIMS")
SOURCES = "SOURCES: REUTERS - AP - THE GUARDIAN - EURONEWS - XINHUA - ESA/JAXA"


# ---------------------------------------------------------------- layout ---
def panel(cv, x, y, w, h, story, scene_h, head_scale):
    cv.rect(x, y, w, h, WHITE)
    cv.hline(x, y, w, INK, 2)
    cv.hline(x, y + h - 1, w, INK, 2)
    cv.vline(x, y, h, INK, 2)
    cv.vline(x + w - 1, y, h, INK, 2)
    story["scene"](cv, x + 2, y + 2, w - 4, scene_h)
    ty = y + scene_h + 14
    ty = kicker(cv, x + 12, ty, story["kicker"])
    for ln in story["head"]:
        draw_text(cv, x + 12, ty, ln, head_scale, INK)
        ty += 8 * head_scale + 4
    paragraph(cv, x + 12, ty + 2, story["body"], 2, w - 24, INK)


def draw_page():
    cv = Canvas(W, H, PAPER)
    mx = 28  # page margin

    # --- masthead ---
    cv.hline(mx, 18, W - 2 * mx, INK, 3)
    draw_centred(cv, W // 2, 34, "THE WORLD IN ONE PAGE", 6, NAVY)
    cv.hline(mx, 88, W - 2 * mx, GOLD, 3)
    draw_centred(cv, W // 2, 100, "THURSDAY 26 NOVEMBER 2026", 3, RED)
    draw_centred(cv, W // 2, 128, "THE DAY'S WORLD NEWS - SIX STORIES, ONE PAGE",
                 2, GREY)
    cv.hline(mx, 150, W - 2 * mx, INK, 3)

    # --- lead story: picture left, words right ---
    ly, lh = 162, 220
    scene_ukraine(cv, mx, ly, 360, lh)
    cv.hline(mx, ly, 360, INK, 2)
    cv.hline(mx, ly + lh - 1, 360, INK, 2)
    cv.vline(mx, ly, lh, INK, 2)
    cv.vline(mx + 359, ly, lh, INK, 2)
    tx = mx + 380
    ty = kicker(cv, tx, ly + 6, LEAD["kicker"])
    for ln in LEAD["head"]:
        draw_text(cv, tx, ty, ln, 4, INK)
        ty += 8 * 4 + 4
    paragraph(cv, tx, ty + 6, LEAD["body"], 2, W - mx - tx, INK,
              max_lines=4, lh=20)
    cv.hline(mx, ly + lh + 12, W - 2 * mx, INK, 2)

    # --- row 2: two half-width stories ---
    ry, rh = 406, 240
    panel(cv, mx, ry, 474, rh, ROW2[0], 104, 3)
    panel(cv, mx + 494, ry, 474, rh, ROW2[1], 104, 3)

    # --- row 3: three third-width stories ---
    ry3, rh3 = 658, 252
    xs = (mx, mx + 322, mx + 644)
    for x, story in zip(xs, ROW3):
        panel(cv, x, ry3, 306, rh3, story, 92, 3)

    # --- footer ---
    fy = 922
    cv.hline(mx, fy, W - 2 * mx, INK, 2)
    paragraph(cv, mx, fy + 12, ALSO_TODAY, 2, W - 2 * mx, INK, lh=18)
    draw_centred(cv, W // 2, 984, SOURCES, 2, GREY)
    return cv


def main():
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
    out_dir.mkdir(parents=True, exist_ok=True)
    png = draw_page().to_png()
    target = out_dir / "entry.png"
    target.write_bytes(png)
    print(f"wrote {target} ({len(png)} bytes, {W}x{H})")


if __name__ == "__main__":
    main()
