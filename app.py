from __future__ import annotations

import json

import streamlit as st
from PIL import Image

from text_style_analyzer import TextStyleAnalyzer, draw_annotations


st.set_page_config(page_title="图片文字样式分析器", layout="wide")
st.title("图片文字样式分析器")
st.caption("识别图片中的文字、文字颜色、背景色和估算字号（像素）。")

uploaded = st.file_uploader("选择图片", type=["png", "jpg", "jpeg", "bmp", "webp"])
min_confidence = st.slider("最小 OCR 置信度", 0.0, 1.0, 0.50, 0.05)

if uploaded:
    image = Image.open(uploaded).convert("RGB")
    st.image(image, caption="原图", use_column_width=True)
    if st.button("开始分析", type="primary"):
        with st.spinner("正在加载 OCR 模型并分析图片…"):
            analyzer = TextStyleAnalyzer()
            items = analyzer.analyze_pil(image, min_confidence=min_confidence)
            annotated = draw_annotations(image, items)

        left, right = st.columns(2)
        with left:
            st.image(annotated, caption="检测结果（框内依次为文字颜色 / 背景色 / 字号）", use_column_width=True)
        with right:
            st.subheader(f"识别到 {len(items)} 处文字")
            st.dataframe(
                [
                    {
                        "文字": item.text,
                        "置信度": round(item.confidence, 3),
                        "文字色": item.text_color.hex,
                        "背景色": item.background_color.hex,
                        "估算字号(px)": item.font_size_px,
                    }
                    for item in items
                ],
                use_container_width=True,
            )
            payload = json.dumps([item.to_dict() for item in items], ensure_ascii=False, indent=2)
            st.download_button("下载 JSON", payload, "text-styles.json", "application/json")
