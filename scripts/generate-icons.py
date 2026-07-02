#!/usr/bin/env python3
"""Generate favicons and app icons for the gh-aw book site from the brand mark.

Brand mark: a rounded square with a diagonal blue->green gradient and a dark "aw",
matching the badge on assets/cover.svg and site/favicon.svg.

Outputs (into site/):
  favicon.ico            16/32/48 rounded badge (transparent corners), legacy fallback
  icon-192.png           192x192 rounded badge, transparent  (PWA "any")
  icon-512.png           512x512 rounded badge, transparent  (PWA "any")
  apple-touch-icon.png   180x180 full-bleed gradient, opaque  (iOS masks the corners)
  icon-maskable-512.png  512x512 full-bleed gradient, opaque, safe padding (PWA maskable)

favicon.svg is authored by hand (scalable) and committed alongside these rasters.
Reproducible: `python scripts/generate-icons.py` (requires Pillow). Commit the output.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"

BLUE = (0x78, 0xA6, 0xFF)
GREEN = (0x4A, 0xDE, 0x80)
INK = (0x0B, 0x10, 0x20)
SS = 4  # supersample factor for crisp edges + text


def _font(px: int) -> ImageFont.FreeTypeFont:
    candidates = (
        "consolab.ttf", "arialbd.ttf", "seguisb.ttf",
        r"C:\Windows\Fonts\consolab.ttf", r"C:\Windows\Fonts\arialbd.ttf",
    )
    for name in candidates:
        try:
            return ImageFont.truetype(name, px)
        except OSError:
            continue
    return ImageFont.load_default()


def _gradient(size: int) -> Image.Image:
    """Diagonal blue->green gradient at `size`x`size` (built small, scaled up)."""
    base = 128
    grad = Image.new("RGB", (base, base))
    px = grad.load()
    maxd = 2 * (base - 1) or 1
    for y in range(base):
        for x in range(base):
            t = (x + y) / maxd
            px[x, y] = (
                round(BLUE[0] + (GREEN[0] - BLUE[0]) * t),
                round(BLUE[1] + (GREEN[1] - BLUE[1]) * t),
                round(BLUE[2] + (GREEN[2] - BLUE[2]) * t),
            )
    return grad.resize((size, size), Image.BILINEAR)


def _draw_aw(img: Image.Image, frac: float) -> None:
    draw = ImageDraw.Draw(img)
    size = img.width
    font = _font(round(size * frac))
    bbox = draw.textbbox((0, 0), "aw", font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((size - w) / 2 - bbox[0], (size - h) / 2 - bbox[1]), "aw", font=font, fill=INK)


def badge(size: int) -> Image.Image:
    """Rounded-square gradient badge with transparent corners (RGBA)."""
    s = size * SS
    grad = _gradient(s).convert("RGBA")
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, s - 1, s - 1], radius=round(s * 0.22), fill=255)
    out = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    out.paste(grad, (0, 0), mask)
    _draw_aw(out, 0.5)
    return out.resize((size, size), Image.LANCZOS)


def fullbleed(size: int, aw_frac: float) -> Image.Image:
    """Full-bleed opaque gradient square with a centered 'aw' (RGB)."""
    s = size * SS
    img = _gradient(s).convert("RGBA")
    _draw_aw(img, aw_frac)
    return img.resize((size, size), Image.LANCZOS).convert("RGB")


def main() -> None:
    SITE.mkdir(parents=True, exist_ok=True)
    badge(512).save(SITE / "icon-512.png")
    badge(192).save(SITE / "icon-192.png")
    badge(64).save(SITE / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    fullbleed(180, 0.50).save(SITE / "apple-touch-icon.png")
    fullbleed(512, 0.42).save(SITE / "icon-maskable-512.png")
    print(f"Wrote favicon.ico, icon-192/512, apple-touch-icon, icon-maskable-512 to {SITE}")


if __name__ == "__main__":
    main()
