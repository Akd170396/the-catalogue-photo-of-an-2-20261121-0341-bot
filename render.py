#!/usr/bin/env python3
"""Render the catalogue photograph: a battery that runs on a battery.

Studio product shot, drawn from scratch with PIL. Deterministic output.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = H = 1024


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
        except Exception:
            pass
    return ImageFont.load_default()


def vgradient(size, top, bottom):
    w, h = size
    base = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(1, h - 1)
        base.putpixel((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return base.resize((w, h))


def cyl_shade(w, h, dark, mid, light):
    """Horizontal cylinder shading: dark - light - mid - dark."""
    img = Image.new("RGB", (w, h))
    px = img.load()
    for x in range(w):
        t = x / max(1, w - 1)
        if t < 0.32:
            k = t / 0.32
            c = tuple(int(dark[i] + (light[i] - dark[i]) * k) for i in range(3))
        elif t < 0.62:
            k = (t - 0.32) / 0.30
            c = tuple(int(light[i] + (mid[i] - light[i]) * k) for i in range(3))
        else:
            k = (t - 0.62) / 0.38
            c = tuple(int(mid[i] + (dark[i] - mid[i]) * k) for i in range(3))
        for y in range(h):
            px[x, y] = c
    return img


def rounded_mask(size, radius):
    m = Image.new("L", size, 0)
    d = ImageDraw.Draw(m)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return m


def draw_battery(img, x, y, w, h, brand="VOLTAIC", size_label="AA", sub="1.5V"):
    """Draw one AA-style battery standing upright with top-left at (x, y)."""
    d = ImageDraw.Draw(img, "RGBA")
    # body with cylindrical shading, clipped to rounded rect
    body = cyl_shade(w, h, (28, 30, 38), (70, 76, 92), (196, 204, 218))
    img.paste(body, (x, y), rounded_mask((w, h), 26))
    # copper top band
    band_h = int(h * 0.30)
    band = cyl_shade(w, band_h, (96, 44, 8), (176, 92, 30), (250, 196, 120))
    band_mask = Image.new("L", (w, band_h), 0)
    bd = ImageDraw.Draw(band_mask)
    bd.rounded_rectangle([0, 0, w - 1, band_h + 26], radius=26, fill=255)
    img.paste(band, (x, y), band_mask)
    # terminal nub
    nub_w, nub_h = int(w * 0.30), int(h * 0.045)
    nx, ny = x + (w - nub_w) // 2, y - nub_h + 6
    d.rounded_rectangle([nx, ny, nx + nub_w, ny + nub_h], radius=8, fill=(210, 214, 222))
    d.rounded_rectangle([nx, ny, nx + nub_w, ny + nub_h], radius=8, outline=(120, 126, 140), width=2)
    d.text((x + w // 2, ny + nub_h // 2), "+", font=font(int(nub_h * 0.9), True),
           fill=(60, 64, 76), anchor="mm")
    # separator line under band
    d.line([x + 8, y + band_h, x + w - 8, y + band_h], fill=(18, 20, 26), width=3)
    # label text
    d.text((x + w // 2, y + int(band_h * 0.52)), brand, font=font(int(w * 0.16), True),
           fill=(255, 244, 224), anchor="mm")
    d.text((x + w // 2, y + band_h + int(h * 0.20)), size_label, font=font(int(w * 0.42), True),
           fill=(240, 244, 250), anchor="mm")
    d.text((x + w // 2, y + band_h + int(h * 0.36)), sub, font=font(int(w * 0.11)),
           fill=(170, 178, 196), anchor="mm")
    # lightning bolt mark
    bx, by, bs = x + w // 2, y + band_h + int(h * 0.47), int(w * 0.10)
    bolt = [(bx + bs * 0.3, by - bs), (bx - bs * 0.5, by + bs * 0.25), (bx - bs * 0.05, by + bs * 0.25),
            (bx - bs * 0.3, by + bs), (bx + bs * 0.5, by - bs * 0.25), (bx + bs * 0.05, by - bs * 0.25)]
    d.polygon(bolt, fill=(250, 196, 60))
    # soft highlight stripe (composited, not pasted, so transparency blends)
    hl = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    hd = ImageDraw.Draw(hl)
    hd.rounded_rectangle([int(w * 0.16), 14, int(w * 0.30), h - 14], radius=18, fill=(255, 255, 255, 52))
    img.alpha_composite(hl, (x, y))
    # outline
    d.rounded_rectangle([x, y, x + w - 1, y + h - 1], radius=26, outline=(14, 16, 22), width=3)


def main():
    # studio backdrop: light seamless gradient + floor
    img = vgradient((W, H), (238, 240, 244), (196, 201, 212)).convert("RGBA")
    d = ImageDraw.Draw(img, "RGBA")
    floor_y = 800
    d.rectangle([0, floor_y, W, H], fill=(214, 218, 228, 255))
    d.line([0, floor_y, W, floor_y], fill=(170, 176, 190, 255), width=2)

    # soft shadows
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([300, 786, 640, 846], fill=(30, 34, 48, 110))   # hero battery
    sd.ellipse([660, 806, 900, 852], fill=(30, 34, 48, 90))    # accessory
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    img.alpha_composite(shadow)

    # hero: big battery, upright
    draw_battery(img, 340, 300, 260, 500)

    # open battery compartment on the hero, with a mini battery inside
    d = ImageDraw.Draw(img, "RGBA")
    cx0, cy0, cx1, cy1 = 392, 648, 548, 786
    d.rounded_rectangle([cx0, cy0, cx1, cy1], radius=14, fill=(16, 18, 24, 255))
    d.rounded_rectangle([cx0, cy0, cx1, cy1], radius=14, outline=(8, 9, 12, 255), width=3)
    # mini battery inside the compartment
    draw_battery(img, 440, 664, 60, 112)
    # compartment door, swung open to the left
    d.polygon([(cx0, cy0 + 6), (cx0 - 58, cy0 + 26), (cx0 - 58, cy1 - 10), (cx0, cy1 - 4)],
              fill=(52, 58, 72, 255), outline=(14, 16, 22, 255))
    d.ellipse([cx0 - 46, cy0 + 40, cx0 - 34, cy0 + 52], outline=(190, 198, 212, 255), width=2)
    d.ellipse([cx0 - 46, cy1 - 52, cx0 - 34, cy1 - 40], outline=(190, 198, 212, 255), width=2)

    # the one accessory: a spare mini battery lying on its side
    acc = Image.new("RGBA", (300, 160), (0, 0, 0, 0))
    draw_battery(acc, 30, 20, 74, 130)
    acc = acc.rotate(90, expand=True, resample=Image.BICUBIC)
    img.alpha_composite(acc, (648, 724))

    img.convert("RGB").save("entry.png", "PNG", optimize=True)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
