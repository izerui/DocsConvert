# Marker 快速安装使用指南

## 项目简介

Marker 是一个高精度、快速的文档转换工具，可以将 PDF、图片、PPTX、DOCX、XLSX、HTML、EPUB 等多种格式的文档转换为 Markdown、JSON、HTML 和 Chunks 格式。

**主要特性：**
- 支持所有语言的文档转换
- 自动格式化表格、公式、代码块、链接和引用
- 提取并保存图片
- 移除页眉/页脚等干扰元素
- 支持 GPU、CPU 和 MPS
- 可选 LLM 增强模式提升准确度

## 快速安装

### 环境要求
- Python 3.10+
- PyTorch

### 基础安装

```bash
pip install marker-pdf
```

### 完整安装（支持非 PDF 文档）

```bash
pip install marker-pdf[full]
```

## 基本使用

### 1. 命令行转换单个文件

```bash
marker_single /path/to/file.pdf
```

### 2. 批量转换文件夹

```bash
marker /path/to/input/folder
```

### 3. 交互式 GUI 界面

```bash
pip install streamlit streamlit-ace
marker_gui
```

## 常用参数

### 输出格式
```bash
--output_format [markdown|json|html|chunks]
```

### 指定输出目录
```bash
--output_dir PATH
```

### 页面范围
```bash
--page_range "0,5-10,20"  # 处理第0页、5-10页、第20页
```

### 强制 OCR（提升准确度）
```bash
--force_ocr  # 强制对所有内容进行 OCR
```

### 启用 LLM 增强（最高准确度）
```bash
--use_llm  # 使用 LLM 提升转换质量
```

### 禁用图片提取
```bash
--disable_image_extraction
```

## Python API 使用

### 基础转换

```python
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered

converter = PdfConverter(
    artifact_dict=create_model_dict(),
)
rendered = converter("FILEPATH")
text, _, images = text_from_rendered(rendered)
```

### 自定义配置

```python
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser

config = {
    "output_format": "json",
    "force_ocr": True
}
config_parser = ConfigParser(config)

converter = PdfConverter(
    config=config_parser.generate_config_dict(),
    artifact_dict=create_model_dict(),
)
rendered = converter("FILEPATH")
```

## 高级功能

### 1. 表格提取

```bash
marker_single FILENAME --converter_cls marker.converters.table.TableConverter --output_format json
```

### 2. 仅 OCR 处理

```bash
marker_single FILENAME --converter_cls marker.converters.ocr.OCRConverter
```

### 3. 多 GPU 并行处理

```bash
NUM_DEVICES=4 NUM_WORKERS=15 marker_chunk_convert ../pdf_in ../md_out
```

### 4. API 服务器

```bash
pip install -U uvicorn fastapi python-multipart
marker_server --port 8001
```

访问 `http://localhost:8001/docs` 查看 API 文档

## LLM 服务配置

使用 `--use_llm` 时，需要配置 LLM 服务：

### Gemini（默认）
```bash
--gemini_api_key YOUR_API_KEY
```

### OpenAI
```bash
--llm_service marker.services.openai.OpenAIService
--openai_api_key YOUR_API_KEY
--openai_model gpt-4
```

### Ollama（本地）
```bash
--llm_service marker.services.ollama.OllamaService
--ollama_base_url http://localhost:11434
--ollama_model llama2
```

## 环境变量

- `TORCH_DEVICE`: 指定设备（cuda/cpu/mps）
- `NUM_DEVICES`: GPU 数量
- `NUM_WORKERS`: 并行工作进程数

## 性能参考

- 单页处理时间：约 0.18 秒
- VRAM 使用：平均 3.5GB，峰值 5GB/worker
- H100 预期吞吐量：122 页/秒

## 故障排除

### 文本乱码
```bash
--force_ocr  # 重新 OCR 文档
```

### 内存不足
```bash
--workers 1  # 减少工作进程数
```

### 提升准确度
```bash
--use_llm --force_ocr  # 启用 LLM 和强制 OCR
```

## 输出格式说明

### Markdown
- 包含图片链接
- 格式化表格
- LaTeX 公式（用 `$$` 包围）
- 代码块（用三反引号包围）

### JSON
- 树状结构
- 包含块类型、位置、内容等详细信息
- 适合程序化处理

### HTML
- 类似 Markdown 结构
- 使用 `<math>` 标签表示公式
- 使用 `<pre>` 标签表示代码

## 许可证

- 模型权重：修改版 AI Pubs Open Rail-M 许可证
- 代码：GPL-3.0 许可证
- 商业使用需获得商业许可

## 更多资源

- GitHub: https://github.com/datalab-to/marker
- 官方平台: https://www.datalab.to
- Discord 社区: https://discord.gg/KuZwXNGnfH
