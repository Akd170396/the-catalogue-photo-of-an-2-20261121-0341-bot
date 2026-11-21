#!/usr/bin/env python3
"""CubeShade catalogue shot.

Renders one studio-style catalogue photograph of an impossible gadget:
the CubeShade, a miniature beach umbrella engineered to shade exactly
one ice cube in a drinking glass. One accessory: a tiny deckchair.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math

W = H = 1024
OUT = "entry.png"

# ---- palette -------------------------------------------------------------
BG_TOP = (238, 240, 242)
BG_BOT = (214, 219, 224)
FLOOR = (206, 211, 217)
CORAL = (238, 96, 74)
CORAL_D = (206, 70, 52)
CREAM = (252, 247, 236)
GLASS_EDGE = (168, 186, 196)
GLASS_FILL = (224, 238, 244)
WATER = (186, 219, 232)
ICE = (240, 250, 252)
ICE_EDGE = (176, 208, 220)
WOOD = (176, 132, 84)
WOOD_D = (146, 106, 62)
INK = (52, 58, 64)


def vgradient(top, bottom):
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        t = y / (H - 1)
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        for x in range(W):
            px[x, y] = c
    return img


def soft_ellipse(img, box, color, blur=18):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse(box, fill=color + (255,))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"), (0, 0))


def font(size, bold=False):
    names = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for n in names:
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    img = vgradient(BG_TOP, BG_BOT)
    d = ImageDraw.Draw(img)

    # seamless studio sweep: floor band + horizon glow
    d.rectangle([0, 700, W, H], fill=FLOOR)
    soft_ellipse(img, [80, 660, 944, 760], (226, 231, 236), blur=30)
    d = ImageDraw.Draw(img)

    cx = 470                      # hero centre x
    floor_y = 838                 # where products stand

    # ---- contact shadows -------------------------------------------------
    soft_ellipse(img, [cx - 210, floor_y - 26, cx + 210, floor_y + 30], (150, 158, 166), blur=16)
    soft_ellipse(img, [690, floor_y - 14, 920, floor_y + 22], (150, 158, 166), blur=14)
    d = ImageDraw.Draw(img)

    # ---- the glass --------------------------------------------------------
    gx0, gx1 = cx - 150, cx + 150          # rim
    gy0, gy1 = 470, floor_y - 8            # rim y .. base y
    bx0, bx1 = cx - 118, cx + 118          # base
    # water body
    wy = 560
    wx0 = gx0 + (bx0 - gx0) * (wy - gy0) / (gy1 - gy0)
    wx1 = gx1 + (bx1 - gx1) * (wy - gy0) / (gy1 - gy0)
    d.polygon([(wx0, wy), (wx1, wy), (bx1, gy1), (bx0, gy1)], fill=WATER)
    # glass walls
    d.polygon([(gx0, gy0), (gx1, gy0), (bx1, gy1), (bx0, gy1)], outline=GLASS_EDGE, width=7)
    d.line([(gx0, gy0), (gx1, gy0)], fill=GLASS_EDGE, width=9)
    d.line([(bx0, gy1 - 14), (bx1, gy1 - 14)], fill=GLASS_EDGE, width=5)
    # glass highlight streak
    d.line([(gx0 + 26, gy0 + 30), (bx0 + 24, gy1 - 60)], fill=(248, 252, 253), width=10)

    # ---- the single ice cube (the customer) ------------------------------
    ix, iy, s = cx - 52, 600, 104
    d.rounded_rectangle([ix, iy, ix + s, iy + s], radius=18, fill=ICE, outline=ICE_EDGE, width=5)
    d.rounded_rectangle([ix + 16, iy + 14, ix + 58, iy + 40], radius=10, fill=(255, 255, 255))
    d.line([(ix + 20, iy + s - 18), (ix + s - 22, iy + 30)], fill=ICE_EDGE, width=3)

    # ---- umbrella pole (goes into the glass, behind the cube) ------------
    pole_x = cx + 64
    d.line([(pole_x, 320), (pole_x - 26, 690)], fill=(120, 126, 132), width=9)
    d.line([(pole_x, 320), (pole_x - 26, 690)], fill=(196, 202, 208), width=3)

    # ---- canopy: scalloped half-dome with alternating panels -------------
    top_y = 132
    rim_y = 336
    half_w = 330
    panels = 8
    for i in range(panels):
        a0 = math.pi * i / panels
        a1 = math.pi * (i + 1) / panels
        pts = [(cx, top_y)]
        steps = 14
        for k in range(steps + 1):
            a = a0 + (a1 - a0) * k / steps
            x = cx + half_w * math.cos(a)
            y = rim_y - (rim_y - top_y) * math.sin(a)
            pts.append((x, y))
        fill = CORAL if i % 2 == 0 else CREAM
        d.polygon(pts, fill=fill)
    # scalloped valance along the rim
    for i in range(panels):
        a = math.pi * (i + 0.5) / panels
        x = cx + half_w * math.cos(a)
        y = rim_y - (rim_y - top_y) * math.sin(a)
        r = 22
        d.ellipse([x - r, y - 4, x + r, y + r], fill=CORAL_D if i % 2 == 0 else (232, 222, 200))
    # canopy outline + finial
    arc = []
    for k in range(61):
        a = math.pi * k / 60
        arc.append((cx + half_w * math.cos(a), rim_y - (rim_y - top_y) * math.sin(a)))
    d.line(arc, fill=CORAL_D, width=4)
    d.line([(cx, top_y - 34), (cx, top_y + 4)], fill=(120, 126, 132), width=7)
    d.ellipse([cx - 11, top_y - 48, cx + 11, top_y - 26], fill=CORAL)

    # ---- brand printed on the canopy (product branding only) -------------
    f = font(44, bold=True)
    label = "CubeShade"
    tw = d.textlength(label, font=f)
    d.text((cx - tw / 2, 196), label, font=f, fill=(255, 255, 255))
    f2 = font(19, bold=True)
    sub = "EST. 2026"
    tw2 = d.textlength(sub, font=f2)
    d.text((cx - tw2 / 2, 248), sub, font=f2, fill=(255, 255, 255))

    # ---- the one accessory: a tiny deckchair ------------------------------
    chx, chy = 716, floor_y
    # frame legs
    d.line([(chx, chy), (chx + 54, chy - 96)], fill=WOOD_D, width=9)
    d.line([(chx + 150, chy), (chx + 108, chy - 96)], fill=WOOD_D, width=9)
    d.line([(chx + 30, chy - 52), (chx + 132, chy - 52)], fill=WOOD, width=7)
    # striped sling
    sling = [(chx + 54, chy - 96), (chx + 108, chy - 96), (chx + 128, chy - 46), (chx + 34, chy - 46)]
    d.polygon(sling, fill=CREAM)
    for i in range(4):
        t0 = i / 4
        t1 = (i + 0.5) / 4
        p = []
        for (ax, ay), (bx, by) in [(sling[0], sling[3]), (sling[1], sling[2])]:
            pass
        x_top0 = sling[0][0] + (sling[1][0] - sling[0][0]) * t0
        x_top1 = sling[0][0] + (sling[1][0] - sling[0][0]) * t1
        x_bot0 = sling[3][0] + (sling[2][0] - sling[3][0]) * t0
        x_bot1 = sling[3][0] + (sling[2][0] - sling[3][0]) * t1
        d.polygon([(x_top0, chy - 96), (x_top1, chy - 96), (x_bot1, chy - 46), (x_bot0, chy - 46)], fill=CORAL)
    d.polygon(sling, outline=WOOD_D, width=3)

    # ---- gentle vignette for the photographed feel ------------------------
    vig = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vig)
    vd.ellipse([-260, -260, W + 260, H + 260], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(120))
    dark = Image.new("RGB", (W, H), (198, 204, 210))
    img = Image.composite(img, dark, vig)

    img.save(OUT, "PNG", optimize=True)
    print("wrote", OUT, img.size)


if __name__ == "__main__":
    main()
