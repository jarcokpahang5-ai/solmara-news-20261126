#!/usr/bin/env python3
"""One image summing up the world news of Thursday 26 November 2026.

Pure Python 3.13 standard library only. It draws a newspaper front page
with a hand-defined 5x7 bitmap font and a hand-written PNG encoder
(struct + zlib), then writes it to /output/entry.png.

The five stories on the page are the real top world news of 26 November
2026, as reported that day by AP, Reuters and the BBC:
  1. The US announces broad new tariffs on China, the EU, Brazil and
     others over subsidised factories.
  2. A fuel tanker crash ignites a massive fire on a highway around
     Cairo, killing at least 30 people.
  3. An Israeli airstrike in Gaza kills a senior Hamas official and
     his family.
  4. Drone strikes in Sudan's Blue Nile state kill 19 civilians.
  5. The first Pakistani astronaut joins China's Tiangong space
     station aboard Shenzhou-24.

Deterministic: no network, no randomness, no clock. Running the program
twice writes byte-identical output.
"""

import binascii
import os
import struct
import zlib

# ---------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 rows of 5 cells; '#' is ink, '.' is blank.
# Only the characters this page needs are defined.
# ---------------------------------------------------------------------------

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
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
}

# ---------------------------------------------------------------------------
# Colours
# ---------------------------------------------------------------------------

PAPER = (247, 243, 232)
WHITE = (255, 255, 255)
INK = (26, 26, 26)
NAVY = (24, 42, 74)
GOLD = (201, 162, 39)
RED = (178, 34, 34)
ORANGE = (217, 93, 30)
DARKRED = (122, 31, 31)
BLUE = (46, 94, 140)
GREEN = (58, 125, 68)
GREY = (120, 120, 116)
LIGHTGREY = (200, 200, 194)
YELLOW = (240, 196, 25)
SKY = (135, 206, 235)

WIDTH = 1024
HEIGHT = 1024


class Canvas:
    """A plain RGB pixel buffer with tiny vector drawing helpers."""

    def __init__(self, width, height, bg):
        self.width = width
        self.height = height
        self.pixels = bytearray(width * height * 3)
        self.fill_rect(0, 0, width, height, bg)

    def px(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            i = (y * self.width + x) * 3
            self.pixels[i] = color[0]
            self.pixels[i + 1] = color[1]
            self.pixels[i + 2] = color[2]

    def fill_rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.width, x + w)
        y1 = min(self.height, y + h)
        for yy in range(y0, y1):
            base = (yy * self.width + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.pixels[i] = color[0]
                self.pixels[i + 1] = color[1]
                self.pixels[i + 2] = color[2]

    def rect_outline(self, x, y, w, h, color, thickness=2):
        self.fill_rect(x, y, w, thickness, color)
        self.fill_rect(x, y + h - thickness, w, thickness, color)
        self.fill_rect(x, y, thickness, h, color)
        self.fill_rect(x + w - thickness, y, thickness, h, color)

    def hline(self, x0, x1, y, color, thickness=1):
        self.fill_rect(x0, y, x1 - x0, thickness, color)

    def vline(self, x, y0, y1, color, thickness=1):
        self.fill_rect(x, y0, thickness, y1 - y0, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.px(x, y, color)
            if x == x1 and y == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def fill_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            half = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - half, cy + dy, half * 2 + 1, 1, color)

    def fill_triangle(self, x0, y0, x1, y1, x2, y2, color):
        # Scanline fill: sort vertices by y, then walk the edges.
        pts = sorted(((x0, y0), (x1, y1), (x2, y2)), key=lambda p: p[1])
        (ax, ay), (bx, by), (cx, cy) = pts
        if ay == cy:
            return
        for y in range(ay, cy + 1):
            if y < by:
                t1 = (y - ay) / (by - ay) if by != ay else 0.0
                xa = ax + (bx - ax) * t1
            else:
                t1 = (y - by) / (cy - by) if cy != by else 0.0
                xa = bx + (cx - bx) * t1
            t2 = (y - ay) / (cy - ay)
            xb = ax + (cx - ax) * t2
            lo, hi = (int(xa), int(xb)) if xa <= xb else (int(xb), int(xa))
            self.fill_rect(lo, y, hi - lo + 1, 1, color)

    # -- text ---------------------------------------------------------------

    def text_width(self, s, scale):
        return len(s) * 6 * scale

    def text(self, x, y, s, scale, color):
        cx = x
        for ch in s:
            glyph = FONT.get(ch)
            if glyph is None:
                cx += 6 * scale
                continue
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill_rect(
                            cx + col * scale, y + row * scale, scale, scale, color
                        )
            cx += 6 * scale

    def text_centered(self, cx, y, s, scale, color):
        self.text(cx - self.text_width(s, scale) // 2, y, s, scale, color)


# ---------------------------------------------------------------------------
# Pictograms (simple vector drawings, one per story)
# ---------------------------------------------------------------------------

def draw_ship(c, x, y, s):
    """Container ship on the sea, for the tariffs lead story."""
    w = 150 * s // 2
    # sea
    c.hline(x, x + w, y + 62, BLUE, 3)
    c.hline(x + 10, x + w - 10, y + 70, BLUE, 2)
    # containers
    c.fill_rect(x + 18, y + 8, 34, 16, RED)
    c.fill_rect(x + 56, y + 8, 34, 16, BLUE)
    c.fill_rect(x + 94, y + 8, 34, 16, GREEN)
    c.fill_rect(x + 36, y + 26, 34, 16, GOLD)
    c.fill_rect(x + 74, y + 26, 34, 16, ORANGE)
    # hull
    c.fill_triangle(x, y + 44, x + w, y + 44, x + w - 18, y + 62, NAVY)
    c.fill_rect(x + 6, y + 44, w - 12, 12, NAVY)
    # funnel + smoke
    c.fill_rect(x + 118, y + 28, 12, 16, INK)
    c.fill_circle(x + 122, y + 18, 6, GREY)
    c.fill_circle(x + 130, y + 10, 8, LIGHTGREY)


def draw_flame(c, x, y, s):
    """Fire flame, for the Cairo tanker fire."""
    c.fill_triangle(x + 10, y + 70, x + 45, y, x + 80, y + 70, ORANGE)
    c.fill_triangle(x + 25, y + 70, x + 45, y + 22, x + 65, y + 70, YELLOW)
    c.fill_triangle(x + 35, y + 70, x + 45, y + 42, x + 55, y + 70, RED)
    c.fill_rect(x, y + 70, 90, 6, INK)


def draw_building_smoke(c, x, y, s):
    """City buildings with a smoke plume, for the Gaza strike."""
    c.fill_rect(x + 8, y + 30, 30, 46, GREY)
    c.fill_rect(x + 44, y + 12, 34, 64, INK)
    c.fill_rect(x + 58, y + 44, 8, 8, YELLOW)
    c.fill_rect(x + 58, y + 58, 8, 8, YELLOW)
    c.fill_rect(x + 20, y + 44, 7, 7, YELLOW)
    c.fill_rect(x + 20, y + 58, 7, 7, YELLOW)
    c.fill_circle(x + 62, y + 2, 9, GREY)
    c.fill_circle(x + 74, y - 6, 12, LIGHTGREY)
    c.fill_rect(x, y + 76, 90, 4, INK)


def draw_drone(c, x, y, s):
    """Quadcopter drone, for the Sudan strikes."""
    c.line(x + 15, y + 20, x + 75, y + 60, INK)
    c.line(x + 75, y + 20, x + 15, y + 60, INK)
    c.fill_rect(x + 38, y + 32, 16, 16, INK)
    for cx, cy in ((15, 20), (75, 20), (15, 60), (75, 60)):
        c.fill_circle(x + cx, y + cy, 11, GREY)
        c.fill_circle(x + cx, y + cy, 4, INK)
    c.fill_circle(x + 46, y + 40, 4, RED)


def draw_rocket(c, x, y, s):
    """Rocket lifting off, for the first Pakistani astronaut."""
    c.fill_triangle(x + 30, y, x + 60, y, x + 45, y + 26, RED)
    c.fill_rect(x + 30, y + 26, 30, 34, WHITE)
    c.rect_outline(x + 30, y + 26, 30, 34, INK, 2)
    c.fill_circle(x + 45, y + 40, 7, SKY)
    c.fill_triangle(x + 30, y + 44, x + 18, y + 66, x + 30, y + 60, RED)
    c.fill_triangle(x + 60, y + 44, x + 72, y + 66, x + 60, y + 60, RED)
    c.fill_triangle(x + 36, y + 60, x + 54, y + 60, x + 45, y + 82, ORANGE)
    c.fill_triangle(x + 40, y + 60, x + 50, y + 60, x + 45, y + 74, YELLOW)


# ---------------------------------------------------------------------------
# Page layout
# ---------------------------------------------------------------------------

def draw_panel(c, x, y, w, h, accent, kicker, headlines, sublines, pictogram):
    c.fill_rect(x, y, w, h, WHITE)
    c.rect_outline(x, y, w, h, INK, 2)
    c.fill_rect(x, y, w, 10, accent)
    c.text(x + 20, y + 24, kicker, 2, accent)
    ty = y + 52
    for line in headlines:
        c.text(x + 20, ty, line, 3, INK)
        ty += 24
    ty += 6
    for line in sublines:
        c.text(x + 20, ty, line, 2, GREY)
        ty += 17
    pictogram(c, x + w - 130, y + h - 108, 1)


def draw_image():
    c = Canvas(WIDTH, HEIGHT, PAPER)

    # Masthead
    c.fill_rect(24, 24, 976, 128, NAVY)
    c.text_centered(512, 40, "THE WORLD TODAY", 6, WHITE)
    c.text_centered(512, 104, "THURSDAY 26 NOVEMBER 2026", 3, GOLD)
    c.hline(24, 1000, 156, GOLD, 4)

    # Lead story: US tariffs
    lx, ly, lw, lh = 24, 168, 976, 264
    c.fill_rect(lx, ly, lw, lh, WHITE)
    c.rect_outline(lx, ly, lw, lh, INK, 2)
    c.fill_rect(lx, ly, 14, lh, RED)
    c.text(lx + 36, ly + 26, "TRADE - LEAD STORY", 2, RED)
    c.text(lx + 36, ly + 56, "US HIKES TARIFFS ON", 4, INK)
    c.text(lx + 36, ly + 92, "CHINA, EU, BRAZIL", 4, INK)
    c.text(lx + 36, ly + 146, "TRUMP ADMINISTRATION UNVEILS BROAD NEW", 2, GREY)
    c.text(lx + 36, ly + 166, "TARIFFS ON IMPORTS OVER SUBSIDISED", 2, GREY)
    c.text(lx + 36, ly + 186, "FACTORIES - AP", 2, GREY)
    draw_ship(c, lx + 700, ly + 120, 2)

    # Four more stories in a 2x2 grid
    panels = [
        (24, 448, ORANGE, "EGYPT",
         ["FUEL TANKER", "FIRE KILLS 30", "IN CAIRO"],
         ["FUEL TANKER CRASH SPARKS", "HIGHWAY BLAZE AROUND", "THE CAPITAL - AP"],
         draw_flame),
        (532, 448, DARKRED, "GAZA",
         ["GAZA STRIKE", "KILLS SENIOR", "HAMAS OFFICIAL"],
         ["OFFICIAL AND FAMILY KILLED", "IN AIRSTRIKE - REUTERS"],
         draw_building_smoke),
        (24, 704, BLUE, "SUDAN",
         ["SUDAN DRONE", "STRIKES KILL", "19 CIVILIANS"],
         ["STRIKES HIT BLUE NILE", "STATE - REUTERS"],
         draw_drone),
        (532, 704, GREEN, "SPACE",
         ["FIRST PAKISTANI", "ASTRONAUT", "REACHES", "TIANGONG"],
         ["PAKISTAN'S FIRST ASTRONAUT", "JOINS CHINA'S STATION"],
         draw_rocket),
    ]
    for x, y, accent, kicker, headlines, sublines, pic in panels:
        draw_panel(c, x, y, 468, 240, accent, kicker, headlines, sublines, pic)

    # Footer
    c.hline(24, 1000, 962, INK, 2)
    c.text_centered(
        512, 976,
        "THE WORLD IN ONE IMAGE - 26 NOVEMBER 2026 - SOURCES: AP, REUTERS, BBC",
        2, INK,
    )
    return c


# ---------------------------------------------------------------------------
# Minimal PNG encoder: 8-bit RGB, no filtering, zlib level 9 (deterministic).
# ---------------------------------------------------------------------------

def chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", binascii.crc32(kind + data) & 0xFFFFFFFF)
    return out


def encode_png(canvas):
    width, height = canvas.width, canvas.height
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)  # filter: None
        start = y * stride
        raw += canvas.pixels[start:start + stride]
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    return png


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    png = encode_png(draw_image())
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
