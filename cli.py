from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

from text_style_analyzer import TextStyleAnalyzer, draw_annotations


def main() -> None:
    parser = argparse.ArgumentParser(description="识别图片中的文字、颜色、背景色和字号")
    parser.add_argument("image", type=Path)
    parser.add_argument("--json", type=Path, default=Path("text-styles.json"))
    parser.add_argument("--annotated", type=Path, default=Path("annotated.png"))
    parser.add_argument("--min-confidence", type=float, default=0.5)
    args = parser.parse_args()

    image = Image.open(args.image).convert("RGB")
    items = TextStyleAnalyzer().analyze_pil(image, args.min_confidence)
    args.json.write_text(json.dumps([item.to_dict() for item in items], ensure_ascii=False, indent=2), encoding="utf-8")
    draw_annotations(image, items).save(args.annotated)
    print(f"完成：{len(items)} 条文字。JSON: {args.json}; 标注图: {args.annotated}")


if __name__ == "__main__":
    main()
