#!/usr/bin/env python3
"""Generate a 1080x1080 Instagram graphic for the Tequila Roam app."""
from PIL import Image, ImageDraw, ImageFont
import math

W = H = 1080
FONT_DIR = "/mnt/skills/examples/canvas-design/canvas-fonts"

def font(name, size):
    return ImageFont.truetype(f"{FONT_DIR}/{name}", size)

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

img = Image.new("RGB", (W, H))
px = img.load()

# --- Sky: vertical sunset gradient (deep night -> magenta -> amber) ---
top = (35, 18, 64)        # deep indigo night
mid = (181, 51, 84)       # sunset magenta
low = (240, 140, 66)      # warm amber
horizon = (255, 201, 112) # glow near horizon
HZ = int(H * 0.70)        # horizon line
for y in range(H):
    if y < HZ:
        t = y / HZ
        if t < 0.55:
            c = lerp(top, mid, t / 0.55)
        else:
            c = lerp(mid, low, (t - 0.55) / 0.45)
    else:
        # ground: deep dusk
        t = (y - HZ) / (H - HZ)
        c = lerp((58, 26, 49), (28, 14, 33), t)
    for x in range(W):
        px[x, y] = c

draw = ImageDraw.Draw(img, "RGBA")

# --- Sun glow + disc ---
sun_cx, sun_cy, sun_r = W // 2, int(H * 0.34), 135
# soft glow
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
gd = ImageDraw.Draw(glow)
for r in range(sun_r + 220, sun_r, -4):
    a = int(60 * (1 - (r - sun_r) / 220))
    gd.ellipse([sun_cx - r, sun_cy - r, sun_cx + r, sun_cy + r],
               fill=(255, 214, 140, max(a, 0)))
img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"), (0, 0))
draw = ImageDraw.Draw(img, "RGBA")
# sun disc (slightly muted/warmer so it doesn't wash out the title)
draw.ellipse([sun_cx - sun_r, sun_cy - sun_r, sun_cx + sun_r, sun_cy + sun_r],
             fill=(244, 178, 120))
# retro sun stripes (cut bottom half with horizon-colored bars)
for i, yb in enumerate(range(sun_cy + 30, sun_cy + sun_r, 26)):
    bh = 10 + i * 2
    # sample sky color at that y for the bar
    c = px[sun_cx, yb]
    draw.rectangle([sun_cx - sun_r, yb, sun_cx + sun_r, yb + bh], fill=c)

# --- Distant mountain ridge silhouette ---
ridge = (74, 34, 60)
pts = [(0, HZ)]
import random
random.seed(7)
x = 0
y = HZ
peaks = [(0, HZ), (150, HZ - 70), (320, HZ - 30), (480, HZ - 110),
         (640, HZ - 40), (820, HZ - 90), (1000, HZ - 35), (W, HZ - 60)]
ridge_pts = peaks + [(W, H), (0, H)]
draw.polygon(ridge_pts, fill=ridge)

# closer ground band
draw.rectangle([0, HZ + 60, W, H], fill=(30, 15, 34))

# --- Agave / cactus silhouettes in foreground ---
def agave(cx, base_y, scale, color):
    # rosette of pointed leaves
    leaves = 11
    for i in range(leaves):
        ang = math.pi * (i / (leaves - 1))  # 0..pi fanning upward
        length = scale * (1.0 - 0.35 * abs(0.5 - i / (leaves - 1)) * 2 * 0.4)
        tipx = cx + math.cos(ang) * length * 1.15
        tipy = base_y - math.sin(ang) * length
        w = scale * 0.16
        # leaf as a triangle
        perp = ang + math.pi / 2
        bx1 = cx + math.cos(perp) * w
        by1 = base_y - math.sin(perp) * w * 0.3
        bx2 = cx - math.cos(perp) * w
        by2 = base_y + math.sin(perp) * w * 0.3
        draw.polygon([(bx1, by1), (tipx, tipy), (bx2, by2)], fill=color)

agave(210, H - 70, 230, (18, 9, 22))
agave(880, H - 50, 280, (12, 6, 16))
# a tall saguaro-ish cactus
def saguaro(cx, base_y, h, color):
    bw = h * 0.13
    draw.rounded_rectangle([cx - bw, base_y - h, cx + bw, base_y],
                           radius=bw, fill=color)
    # arms
    draw.rounded_rectangle([cx - bw - h*0.18, base_y - h*0.55,
                            cx - bw + bw*0.7, base_y - h*0.30],
                           radius=bw*0.6, fill=color)
    draw.rounded_rectangle([cx - bw - h*0.18, base_y - h*0.75,
                            cx - bw - h*0.18 + bw*1.4, base_y - h*0.50],
                           radius=bw*0.6, fill=color)
    draw.rounded_rectangle([cx + bw - bw*0.7, base_y - h*0.62,
                            cx + bw + h*0.16, base_y - h*0.40],
                           radius=bw*0.6, fill=color)
    draw.rounded_rectangle([cx + bw + h*0.16 - bw*1.4, base_y - h*0.82,
                            cx + bw + h*0.16, base_y - h*0.55],
                           radius=bw*0.6, fill=color)
saguaro(560, H - 40, 360, (10, 5, 14))

# --- Text ---
def center_text(y, text, fnt, fill, shadow=None, ls=0, stroke=0, stroke_fill=None):
    if ls:
        # manual letter spacing
        widths = [draw.textlength(ch, font=fnt) for ch in text]
        total = sum(widths) + ls * (len(text) - 1)
        x = (W - total) / 2
        if shadow:
            sx, sy, sc = shadow
            cx2 = x
            for ch, w in zip(text, widths):
                draw.text((cx2 + sx, y + sy), ch, font=fnt, fill=sc)
                cx2 += w + ls
        for ch, w in zip(text, widths):
            draw.text((x, y), ch, font=fnt, fill=fill,
                      stroke_width=stroke, stroke_fill=stroke_fill)
            x += w + ls
        return
    w = draw.textlength(text, font=fnt)
    x = (W - w) / 2
    if shadow:
        sx, sy, sc = shadow
        draw.text((x + sx, y + sy), text, font=fnt, fill=sc,
                  stroke_width=stroke, stroke_fill=sc)
    draw.text((x, y), text, font=fnt, fill=fill,
              stroke_width=stroke, stroke_fill=stroke_fill)

# Kicker
kick = font("NationalPark-Bold.ttf", 34)
center_text(96, "EXPLORE • SIP • WANDER", kick, (255, 224, 170), ls=10)

# Main title - two lines, big and bold, with a heavy dark outline for contrast
title = font("BigShoulders-Bold.ttf", 188)
outline = (46, 16, 34)  # deep maroon-brown outline
center_text(150, "TEQUILA", title, (255, 248, 235),
            shadow=(5, 7, (20, 8, 18, 220)), stroke=9, stroke_fill=outline)
center_text(330, "ROAM", title, (255, 248, 235),
            shadow=(5, 7, (20, 8, 18, 220)), stroke=9, stroke_fill=outline)

# Tagline (on its own translucent band for legibility)
tag = font("NationalPark-Regular.ttf", 40)
tag_text = "Your passport to the perfect pour"
tw = draw.textlength(tag_text, font=tag)
ty = 545
band = [(W - tw) / 2 - 30, ty - 14, (W + tw) / 2 + 30, ty + 56]
draw.rounded_rectangle(band, radius=35, fill=(30, 12, 30, 150))
center_text(ty, tag_text, tag, (255, 235, 205))

# --- URL pill ---
url_text = "Tequila.roamthrough.com"
uf = font("BigShoulders-Bold.ttf", 50)
uw = draw.textlength(url_text, font=uf)
pad_x, pad_y = 46, 24
pill_w = uw + pad_x * 2
pill_h = 50 + pad_y * 2
pill_x = (W - pill_w) / 2
pill_y = H - 150
draw.rounded_rectangle([pill_x, pill_y, pill_x + pill_w, pill_y + pill_h],
                       radius=pill_h / 2, fill=(255, 233, 170))
draw.text(((W - uw) / 2, pill_y + pad_y - 6), url_text, font=uf, fill=(40, 18, 38))

img.save("tequila_roam_instagram.png", "PNG")
print("saved tequila_roam_instagram.png", img.size)
