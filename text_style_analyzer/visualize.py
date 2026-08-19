from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from .models import TextStyle


def _font(size: int = 16):
    try:
        return ImageFont.truetype("msyh.ttc", size)
    except OSError:
        return ImageFont.load_default()


def draw_annotations(image: Image.Image, items: list[TextStyle]) -> Image.Image:
    canvas = image.convert("RGB").copy()
    draw = ImageDraw.Draw(canvas)
    font = _font()
    for item in items:
        points = item.polygon
        draw.line(points + [points[0]], fill=(0, 255, 255), width=2)
        x, y = points[0]
        label = f"{item.text_color.hex} / {item.background_color.hex} / {item.font_size_px}px"
        box = draw.textbbox((x, y), label, font=font)
        draw.rectangle(box, fill=(0, 0, 0))
        draw.text((x, y), label, fill=(255, 255, 255), font=font)
    return canvas
