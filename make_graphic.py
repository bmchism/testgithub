#!/usr/bin/env python3
"""Instagram graphic for the Tequila Roam app — matched to the real app branding.

Palette, logo (amber tile + white agave sprout), elegant serif, and the
"Learn it. Taste it. Host it." hero line are all drawn from the app screenshots.
"""
from PIL import Image, ImageDraw, ImageFont
import math

W = H = 1080
FONT_DIR = "/mnt/skills/examples/canvas-design/canvas-fonts"

# --- Brand palette (sampled from the app) ---
CREAM   = (246, 241, 233)
CREAM_D = (237, 231, 221)
AMBER   = (170, 105, 47)
AMBER_L = (184, 119, 58)
GREEN   = (78, 109, 97)
PURPLE  = (134, 95, 156)
DARK    = (42, 33, 26)
MUTED   = (120, 104, 88)

def font(name, size):
    return ImageFont.truetype(f"{FONT_DIR}/{name}", size)

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

img = Image.new("RGB", (W, H), CREAM)
draw = ImageDraw.Draw(img, "RGBA")

# --- Soft cream vertical gradient + corner vignette for warmth ---
px = img.load()
for y in range(H):
    c = lerp(CREAM, CREAM_D, y / H)
    for x in range(W):
        px[x, y] = c
draw = ImageDraw.Draw(img, "RGBA")

# ---------- helpers ----------
def text_w(t, f):
    return draw.textlength(t, font=f)

def centered(y, t, f, fill, ls=0, stroke=0, stroke_fill=None):
    if ls:
        ws = [text_w(ch, f) for ch in t]
        total = sum(ws) + ls * (len(t) - 1)
        x = (W - total) / 2
        for ch, w in zip(t, ws):
            draw.text((x, y), ch, font=f, fill=fill,
                      stroke_width=stroke, stroke_fill=stroke_fill)
            x += w + ls
        return total
    w = text_w(t, f)
    draw.text(((W - w) / 2, y), t, font=f, fill=fill,
              stroke_width=stroke, stroke_fill=stroke_fill)
    return w

def qbezier(p0, p1, p2, n=24):
    pts = []
    for i in range(n + 1):
        t = i / n
        x = (1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0]
        y = (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1]
        pts.append((x, y))
    return pts

def leaf(base, tip, c_out, c_in, fill):
    """A leaf filled between two bezier edges base->tip (outer) and tip->base (inner)."""
    poly = qbezier(base, c_out, tip) + qbezier(tip, c_in, base)
    draw.polygon(poly, fill=fill)

# ---------- LOGO: amber tile + white agave sprout ----------
def draw_logo(cx, cy, tile=150):
    half = tile / 2
    x0, y0 = cx - half, cy - half
    # tile with subtle top-light gradient
    tile_img = Image.new("RGBA", (tile, tile), (0, 0, 0, 0))
    td = ImageDraw.Draw(tile_img)
    for i in range(tile):
        td.line([(0, i), (tile, i)], fill=lerp(AMBER_L, AMBER, i / tile))
    # round the corners via mask
    mask = Image.new("L", (tile, tile), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, tile-1, tile-1],
                                           radius=int(tile*0.30), fill=255)
    img.paste(tile_img, (int(x0), int(y0)), mask)

    # white agave sprout, centered in tile
    white = (250, 248, 243)
    s = tile
    bx, by = cx, cy + s*0.30          # base point of the sprout
    # central spear (tall pointed blade)
    spear_tip = (cx, cy - s*0.34)
    leaf((cx - s*0.045, by), spear_tip, (cx - s*0.12, cy - s*0.05),
         (cx, cy - s*0.05), white)
    leaf((cx + s*0.045, by), spear_tip, (cx + s*0.12, cy - s*0.05),
         (cx, cy - s*0.05), white)
    base = (bx, by)
    # two basal leaves curving outward & up (the sprout cup)
    # left
    leaf(base, (cx - s*0.205, cy - s*0.07),
         (cx - s*0.03, cy + s*0.17), (cx - s*0.15, cy + s*0.15), white)
    # right
    leaf(base, (cx + s*0.205, cy - s*0.07),
         (cx + s*0.03, cy + s*0.17), (cx + s*0.15, cy + s*0.15), white)
    # inner small leaves hugging the spear
    leaf(base, (cx - s*0.105, cy - s*0.17),
         (cx - s*0.015, cy + s*0.04), (cx - s*0.075, cy + s*0.01), white)
    leaf(base, (cx + s*0.105, cy - s*0.17),
         (cx + s*0.015, cy + s*0.04), (cx + s*0.075, cy + s*0.01), white)
    return x0, y0, tile

# Logo lockup (tile + "Roam" / "TEQUILA"), centered as a group near top
serif_word = font("Lora-Bold.ttf", 96)
caps = font("Lora-Regular.ttf", 33)
tile = 150
gap = 34
roam_w = text_w("Roam", serif_word)
teq = "TEQUILA"
teq_ls = 12
teq_w = sum(text_w(c, caps) for c in teq) + teq_ls * (len(teq) - 1)
text_block_w = max(roam_w, teq_w)
group_w = tile + gap + text_block_w
gx = (W - group_w) / 2
logo_cy = 150
draw_logo(gx + tile/2, logo_cy, tile)
# wordmark to the right
tx = gx + tile + gap
draw.text((tx, logo_cy - 64), "Roam", font=serif_word, fill=DARK)
# TEQUILA caps, amber, letterspaced, aligned under Roam
cxp = tx + 4
for ch in teq:
    draw.text((cxp, logo_cy + 26), ch, font=caps, fill=AMBER)
    cxp += text_w(ch, caps) + teq_ls

# ---------- Kicker ----------
kick = font("Outfit-Bold.ttf", 30)
centered(286, "GUIDED TEQUILA TASTINGS", kick, AMBER, ls=10)

# small divider rule
rule_w = 90
draw.line([(W/2 - rule_w/2, 336), (W/2 + rule_w/2, 336)], fill=AMBER_L, width=3)

# ---------- Hero headline: Learn it. Taste it. Host it. ----------
head = font("Lora-Bold.ttf", 142)
lines = [("Learn it.", AMBER), ("Taste it.", GREEN), ("Host it.", PURPLE)]
y = 352
for txt, col in lines:
    centered(y, txt, head, col)
    y += 152

# ---------- Subhead ----------
sub = font("Outfit-Regular.ttf", 38)
sub_lines = [
    "Turn any get-together into a guided tasting —",
    "pour, score, and crown a winner.",
]
sy = 808
for ln in sub_lines:
    centered(sy, ln, sub, DARK)
    sy += 50

# ---------- CTA pill (echoes the app's "Start your free tasting") ----------
cta_font = font("Outfit-Bold.ttf", 38)
cta_text = "Start your free tasting"
arrow = "  →"
cw = text_w(cta_text + arrow, cta_font)
pad_x, pad_y = 48, 24
pw, ph = cw + pad_x*2, 38 + pad_y*2
pxp = (W - pw) / 2
pyp = 912
draw.rounded_rectangle([pxp+3, pyp+6, pxp+pw+3, pyp+ph+6], radius=ph/2,
                       fill=(120, 80, 40, 55))
draw.rounded_rectangle([pxp, pyp, pxp+pw, pyp+ph], radius=ph/2, fill=AMBER)
draw.text(((W-cw)/2, pyp+pad_y-4), cta_text + arrow, font=cta_font,
          fill=(250, 246, 240))

# ---------- URL ----------
url_font = font("Outfit-Bold.ttf", 36)
centered(1018, "tequila.roamthrough.com", url_font, DARK, ls=2)

img.save("tequila_roam_instagram.png", "PNG")
print("saved", img.size)
