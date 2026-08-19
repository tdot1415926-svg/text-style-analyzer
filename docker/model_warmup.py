"""Download the OCR models once while the Docker image is being built."""

from paddleocr import PaddleOCR


if __name__ == "__main__":
    PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)
    print("PaddleOCR Chinese detection, recognition and classification models are cached.")
