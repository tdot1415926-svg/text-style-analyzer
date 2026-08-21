from __future__ import annotations

from typing import Iterable

import cv2
import numpy as np
import pytesseract
from PIL import Image
from pytesseract import Output

from .models import Color, TextStyle

def _to_color(values: np.ndarray) -> Color:
    rgb = tuple(int(np.clip(round(float(v)), 0, 255)) for v in values)
    return Color(rgb)  # type: ignore[arg-type]


def _box_height(polygon: np.ndarray) -> float:
    left = np.linalg.norm(polygon[0] - polygon[3])
    right = np.linalg.norm(polygon[1] - polygon[2])
    return float((left + right) / 2)


def estimate_colors(image_rgb: np.ndarray, polygon: Iterable[Iterable[int]]) -> tuple[Color, Color]:
    """Estimate glyph and local background colors from a detected text quadrilateral.

    Border pixels are the strongest evidence for the background. K-means on the
    interior separates the background cluster from the lower-coverage glyph color.
    """
    points = np.asarray(list(polygon), dtype=np.int32)
    h, w = image_rgb.shape[:2]
    x, y, bw, bh = cv2.boundingRect(points)
    pad = max(1, int(round(min(bw, bh) * 0.06)))
    x0, y0, x1, y1 = max(0, x - pad), max(0, y - pad), min(w, x + bw + pad), min(h, y + bh + pad)
    crop = image_rgb[y0:y1, x0:x1]
    if crop.size == 0:
        black = Color((0, 0, 0))
        return black, black

    # Estimate background from a thin rectangular ring around the OCR box.
    ring = np.zeros(crop.shape[:2], dtype=np.uint8)
    thickness = max(1, min(crop.shape[:2]) // 10)
    cv2.rectangle(ring, (0, 0), (crop.shape[1] - 1, crop.shape[0] - 1), 255, thickness)
    ring_pixels = crop[ring > 0].reshape(-1, 3).astype(np.float32)
    bg = np.median(ring_pixels, axis=0) if len(ring_pixels) else np.median(crop.reshape(-1, 3), axis=0)

    # Work in Lab because its Euclidean distance better reflects visible contrast.
    pixels = crop.reshape(-1, 3)
    if len(pixels) < 3:
        return _to_color(pixels[0]), _to_color(bg)
    lab = cv2.cvtColor(crop, cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float32)
    k = min(4, len(lab))
    _, labels, centers_lab = cv2.kmeans(lab, k, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.5), 3, cv2.KMEANS_PP_CENTERS)
    centers_rgb = cv2.cvtColor(centers_lab.reshape(1, -1, 3).astype(np.uint8), cv2.COLOR_LAB2RGB).reshape(-1, 3)
    bg_lab = cv2.cvtColor(np.uint8([[bg]]), cv2.COLOR_RGB2LAB)[0, 0].astype(float)
    distances = np.linalg.norm(centers_lab - bg_lab, axis=1)
    counts = np.bincount(labels.ravel(), minlength=k)

    # Glyphs usually cover less area than the background but are visibly distinct.
    # Avoid tiny anti-aliasing clusters by favoring clusters with at least 1% coverage.
    valid = counts >= max(2, int(len(lab) * 0.01))
    scores = distances * np.sqrt(counts / len(lab))
    scores[~valid] = -1
    foreground_index = int(np.argmax(scores))
    if scores[foreground_index] <= 0:
        foreground_index = int(np.argmax(distances))
    return _to_color(centers_rgb[foreground_index]), _to_color(bg)


class TextStyleAnalyzer:
    def analyze_pil(self, image: Image.Image, min_confidence: float = 0.5) -> list[TextStyle]:
        image_rgb = np.asarray(image.convert("RGB"))
        try:
            raw = pytesseract.image_to_data(
                image,
                lang="chi_sim+eng",
                config="--oem 1 --psm 11",
                output_type=Output.DICT,
            )
        except pytesseract.TesseractNotFoundError as exc:
            raise RuntimeError("未找到 Tesseract OCR。请安装 Tesseract 并配置到 PATH，或使用 Docker 镜像运行。") from exc

        items: list[TextStyle] = []
        for index, text in enumerate(raw["text"]):
            value = str(text).strip()
            try:
                confidence = float(raw["conf"][index]) / 100
            except (TypeError, ValueError):
                continue
            if confidence < min_confidence or not value:
                continue
            x, y = int(raw["left"][index]), int(raw["top"][index])
            width, height_px = int(raw["width"][index]), int(raw["height"][index])
            if width <= 0 or height_px <= 0:
                continue
            rounded_polygon = [(x, y), (x + width, y), (x + width, y + height_px), (x, y + height_px)]
            polygon = np.asarray(rounded_polygon, dtype=float)
            text_color, background_color = estimate_colors(image_rgb, rounded_polygon)
            height = _box_height(polygon)
            # OCR boxes enclose visible glyphs; 0.95 makes the number closer to
            # conventional raster font pixel size without pretending it is exact.
            font_size = max(1, int(round(height * 0.95)))
            items.append(TextStyle(value, confidence, rounded_polygon, text_color, background_color, font_size, round(height, 2)))
        return items
