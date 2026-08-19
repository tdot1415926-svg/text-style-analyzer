"""Download PP-OCR model archives without initializing Paddle inference."""

from pathlib import Path
from tarfile import open as open_tar
from urllib.request import urlretrieve


MODEL_ROOT = Path("/opt/paddleocr/whl")
MODELS = (
    (
        "https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/ch_PP-OCRv4_det_infer.tar",
        MODEL_ROOT / "det" / "ch" / "ch_PP-OCRv4_det_infer",
    ),
    (
        "https://paddleocr.bj.bcebos.com/PP-OCRv4/chinese/ch_PP-OCRv4_rec_infer.tar",
        MODEL_ROOT / "rec" / "ch" / "ch_PP-OCRv4_rec_infer",
    ),
    (
        "https://paddleocr.bj.bcebos.com/dygraph_v2.0/ch/ch_ppocr_mobile_v2.0_cls_infer.tar",
        MODEL_ROOT / "cls" / "ch_ppocr_mobile_v2.0_cls_infer",
    ),
)


def download_and_extract(url: str, target: Path) -> None:
    target.mkdir(parents=True, exist_ok=True)
    archive = target / url.rsplit("/", 1)[-1]
    urlretrieve(url, archive)
    with open_tar(archive) as tar:
        # Archives are fetched from PaddleOCR's official model host.
        tar.extractall(target)
    print(f"Cached {archive.name} in {target}")


if __name__ == "__main__":
    for model_url, model_target in MODELS:
        download_and_extract(model_url, model_target)
