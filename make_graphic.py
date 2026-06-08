#!/usr/bin/env python3
"""Simple Instagram graphic for Tequila Roam: logo + wordmark + agave photo + URL."""
from PIL import Image, ImageDraw, ImageFont

W = H = 1080
FONT_DIR = "/mnt/skills/examples/canvas-design/canvas-fonts"

CREAM   = (246, 241, 233)
CREAM_D = (237, 231, 221)
AMBER   = (170, 105, 47)
AMBER_L = (184, 119, 58)
DARK    = (42, 33, 26)

def font(name, size):
    return ImageFont.truetype(f"{FONT_DIR}/{name}", size)

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def qbezier(p0, p1, p2, n=24):
    out = []
    for i in range(n + 1):
        t = i / n
        out.append(((1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0],
                    (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1]))
    return out

img = Image.new("RGB", (W, H), CREAM)
px = img.load()
for y in range(H):
    c = lerp(CREAM, CREAM_D, y / H)
    for x in range(W):
        px[x, y] = c
draw = ImageDraw.Draw(img, "RGBA")

def text_w(t, f):
    return draw.textlength(t, font=f)

# ---------- logo mark: amber tile + white agave sprout ----------
def draw_logo(cx, cy, tile=130):
    half = tile / 2
    x0, y0 = cx - half, cy - half
    t_img = Image.new("RGBA", (tile, tile), (0, 0, 0, 0))
    td = ImageDraw.Draw(t_img)
    for i in range(tile):
        td.line([(0, i), (tile, i)], fill=lerp(AMBER_L, AMBER, i / tile))
    mask = Image.new("L", (tile, tile), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, tile-1, tile-1],
                                           radius=int(tile*0.30), fill=255)
    img.paste(t_img, (int(x0), int(y0)), mask)

    white = (250, 248, 243)
    s = tile
    by = cy + s*0.30
    base = (cx, by)
    spear_tip = (cx, cy - s*0.34)
    def leaf(b, tip, co, ci):
        draw.polygon(qbezier(b, co, tip) + qbezier(tip, ci, b), fill=white)
    leaf((cx - s*0.045, by), spear_tip, (cx - s*0.12, cy - s*0.05), (cx, cy - s*0.05))
    leaf((cx + s*0.045, by), spear_tip, (cx + s*0.12, cy - s*0.05), (cx, cy - s*0.05))
    leaf(base, (cx - s*0.205, cy - s*0.07), (cx - s*0.03, cy + s*0.17), (cx - s*0.15, cy + s*0.15))
    leaf(base, (cx + s*0.205, cy - s*0.07), (cx + s*0.03, cy + s*0.17), (cx + s*0.15, cy + s*0.15))
    leaf(base, (cx - s*0.105, cy - s*0.17), (cx - s*0.015, cy + s*0.04), (cx - s*0.075, cy + s*0.01))
    leaf(base, (cx + s*0.105, cy - s*0.17), (cx + s*0.015, cy + s*0.04), (cx + s*0.075, cy + s*0.01))

# ---------- logo lockup: [tile]  Tequila Roam ----------
wordmark = font("Lora-Bold.ttf", 78)
name = "Tequila Roam"
tile = 132
gap = 30
name_w = text_w(name, wordmark)
group_w = tile + gap + name_w
gx = (W - group_w) / 2
logo_cy = 196
draw_logo(gx + tile/2, logo_cy, tile)
draw.text((gx + tile + gap, logo_cy - 52), name, font=wordmark, fill=DARK)

# ---------- agave field photo (rounded card) ----------
photo = Image.open("agave_field.png").convert("RGB")
card_w, card_h = 900, 560
margin = (W - card_w) // 2
card_y = 360
# cover-fit
pr, cr = photo.width / photo.height, card_w / card_h
if pr > cr:
    nh = card_h; nw = int(nh * pr)
else:
    nw = card_w; nh = int(nw / pr)
photo = photo.resize((nw, nh), Image.LANCZOS)
left = (nw - card_w) // 2
top = (nh - card_h) // 2
photo = photo.crop((left, top, left + card_w, top + card_h))
# rounded mask
pmask = Image.new("L", (card_w, card_h), 0)
ImageDraw.Draw(pmask).rounded_rectangle([0, 0, card_w-1, card_h-1], radius=46, fill=255)
# soft shadow
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(shadow).rounded_rectangle(
    [margin+6, card_y+12, margin+card_w+6, card_y+card_h+12], radius=46,
    fill=(60, 40, 20, 60))
img.paste(Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB"), (0, 0))
img.paste(photo, (margin, card_y), pmask)
draw = ImageDraw.Draw(img, "RGBA")
# thin border
draw.rounded_rectangle([margin, card_y, margin+card_w, card_y+card_h],
                       radius=46, outline=(255, 255, 255, 90), width=2)

# ---------- URL ----------
url_font = font("Outfit-Bold.ttf", 44)
url = "tequila.roamthrough.com"
uw = text_w(url, url_font)
uy = 992
draw.text(((W - uw) / 2, uy), url, font=url_font, fill=AMBER)

img.save("tequila_roam_instagram.png", "PNG")
print("saved", img.size)
