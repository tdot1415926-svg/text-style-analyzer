import cv2
import numpy as np

from text_style_analyzer.analyzer import estimate_colors


def test_estimate_colors_on_dark_text_and_light_background():
    image = np.full((80, 260, 3), (245, 240, 220), dtype=np.uint8)
    cv2.putText(image, "Test", (25, 56), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (18, 40, 120), 3, cv2.LINE_8)
    text, background = estimate_colors(image, [(20, 15), (170, 15), (170, 65), (20, 65)])
    assert background.rgb[0] > 220 and background.rgb[1] > 220
    assert text.rgb[2] > text.rgb[0] + 40


def test_estimate_colors_on_light_text_and_dark_background():
    image = np.full((80, 260, 3), (30, 40, 55), dtype=np.uint8)
    cv2.putText(image, "Test", (25, 56), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (240, 210, 50), 3, cv2.LINE_8)
    text, background = estimate_colors(image, [(20, 15), (170, 15), (170, 65), (20, 65)])
    assert background.rgb[0] < 70
    assert text.rgb[0] > 150 and text.rgb[1] > 150
