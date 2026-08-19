# 图片文字样式分析器

上传一张图片，工具会逐行识别文字，并给出：

- 识别文本与置信度
- 文字前景色（RGB、HEX）
- 文字所在区域的背景色（RGB、HEX）
- 估算字号（像素）与文字框高度

项目使用 [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) 进行中英文 OCR，使用 [OpenCV](https://github.com/opencv/opencv) 做颜色聚类和标注。颜色和字号是基于图片像素的估算值，不是原始 UI/CSS 字体属性；抗锯齿、渐变、阴影或复杂背景会降低准确度。

## 安装与运行

建议使用 Python 3.10 或 3.11。依赖已锁定为 Windows / Python 3.11 可直接安装的 CPU 版本，无需安装 Microsoft C++ Build Tools：

```powershell
cd D:\MyCode\text-style-analyzer
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

第一次分析时 PaddleOCR 会下载其开源模型。若只需命令行：

```powershell
python cli.py path\to\image.png --json result.json --annotated result.png
```

## Docker

镜像构建阶段会安装 CPU 依赖，并预下载中文 PP-OCRv4 的检测、识别和方向分类模型；容器启动后无需联网下载模型。

```powershell
docker build -t text-style-analyzer:latest .
docker run --rm -p 8501:8501 text-style-analyzer:latest
```

然后在浏览器打开 `http://localhost:8501`。如需导出可移植镜像包：

```powershell
docker save -o text-style-analyzer.tar text-style-analyzer:latest
```

推送到 GitHub 后，GitHub Actions 会构建并上传镜像至 GitHub Container Registry。构建成功后可拉取：

```powershell
docker pull ghcr.io/tdot1415926-svg/text-style-analyzer:latest
```

## 输出说明

`font_size_px` 以文字检测框的可见字符高度为基础计算，适合比较同一截图中不同文字的相对大小。`text_color` 和 `background_color` 为该文字框的主色估计；透明、渐变、描边字体的结果会标注为近似。

## 项目结构

```text
app.py                 Streamlit 上传界面
cli.py                 可脚本化的命令行入口
text_style_analyzer/   OCR 适配、颜色/字号分析、可视化
tests/                 不依赖 OCR 模型的颜色估计单元测试
```
