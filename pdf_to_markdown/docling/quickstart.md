# Docling 快速安装使用指南

## 📖 项目简介

Docling 是一个强大的文档处理工具，专门为生成式 AI 应用设计。它可以解析多种文档格式（包括 PDF、DOCX、PPTX、XLSX、HTML、图像等），并提供统一的文档表示格式，支持导出为 Markdown、HTML 和 JSON 等格式。

**主要特性：**
- 🗂️ 支持多种文档格式（PDF、DOCX、PPTX、XLSX、HTML、WAV、MP3、VTT、图像等）
- 📑 高级 PDF 理解能力（页面布局、阅读顺序、表格结构、代码、公式等）
- 🧬 统一的 DoclingDocument 表示格式
- ↪️ 多种导出格式（Markdown、HTML、DocTags、JSON）
- 🔒 本地执行能力，保护敏感数据
- 🤖 与 LangChain、LlamaIndex、Crew AI、Haystack 等框架集成
- 🔍 强大的 OCR 支持
- 👓 支持视觉语言模型（如 GraniteDocling）
- 🎙️ 音频支持（ASR 模型）
- 💻 简单易用的命令行界面

---

## 🚀 快速安装

### 系统要求
- **操作系统**：macOS、Linux、Windows
- **架构**：x86_64 和 arm64
- **Python**：建议使用 Python 3.8+

### 安装方法

#### 方法 1：使用 pip 安装（推荐）

```bash
pip install docling
```

安装完成后，您可以通过以下命令验证安装：

```bash
docling --help
```

#### 方法 2：使用 Docker 部署

Docling 官方提供了 Docker 支持，您可以使用 Docker 容器运行 Docling，这样可以避免环境配置问题，并且更适合生产环境部署。

**使用官方 Docker 镜像：**

```bash
# 拉取官方镜像
docker pull ghcr.io/docling-project/docling:latest

# 基本使用 - 转换本地文件
docker run --rm -v $(pwd):/documents ghcr.io/docling-project/docling:latest /documents/input.pdf

# 转换并保存到输出文件
docker run --rm -v $(pwd):/documents ghcr.io/docling-project/docling:latest /documents/input.pdf -o /documents/output.md

# 转换在线文档
docker run --rm ghcr.io/docling-project/docling:latest https://arxiv.org/pdf/2206.01062

# 使用 VLM 模型
docker run --rm -v $(pwd):/documents ghcr.io/docling-project/docling:latest --pipeline vlm --vlm-model granite_docling /documents/input.pdf
```

**Windows 用户使用 Docker：**

```cmd
# 转换本地文件（Windows CMD）
docker run --rm -v %cd%:C:\documents ghcr.io/docling-project/docling:latest C:\documents\input.pdf

# 转换本地文件（Windows PowerShell）
docker run --rm -v "${PWD}:C:\documents" ghcr.io/docling-project/docling:latest C:\documents\input.pdf
```

**从源码构建 Docker 镜像：**

```bash
# 克隆仓库
git clone https://github.com/docling-project/docling.git
cd docling

# 构建镜像
docker build -t docling:latest .

# 使用构建的镜像
docker run --rm -v $(pwd):/documents docling:latest /documents/input.pdf
```

**Docker Compose 部署示例：**

创建 `docker-compose.yml` 文件：

```yaml
version: '3.8'

services:
  docling:
    image: ghcr.io/docling-project/docling:latest
    container_name: docling-service
    volumes:
      - ./documents:/documents
      - ./output:/output
    working_dir: /documents
    # 可选：添加资源限制
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
```

使用 Docker Compose：

```bash
# 启动服务
docker-compose up -d

# 执行转换
docker-compose run docling input.pdf -o /output/output.md

# 停止服务
docker-compose down
```

**Docker 部署的优势：**
- ✅ 环境隔离，避免依赖冲突
- ✅ 跨平台一致性
- ✅ 易于部署和扩展
- ✅ 适合 CI/CD 集成
- ✅ 资源限制和管理
- ✅ 快速回滚和版本管理

---

## 💡 基础使用

### 1. 命令行使用（CLI）

Docling 提供了简单易用的命令行界面，可以快速转换文档。

#### 基本转换

```bash
# 转换在线 PDF 文档
docling https://arxiv.org/pdf/2206.01062

# 转换本地文档
docling /path/to/your/document.pdf

# 转换并指定输出文件
docling input.pdf -o output.md
```

#### 使用视觉语言模型（VLM）

Docling 支持使用 GraniteDocling 和其他 VLMs 进行更高级的文档解析：

```bash
# 使用 GraniteDocling 模型
docling --pipeline vlm --vlm-model granite_docling https://arxiv.org/pdf/2206.01062
```

**注意**：在支持的 Apple Silicon 硬件上，这将使用 MLX 加速。

### 2. Python API 使用

#### 基本文档转换

```python
from docling.document_converter import DocumentConverter

# 定义文档来源（本地路径或 URL）
source = "https://arxiv.org/pdf/2408.09869"

# 创建转换器实例
converter = DocumentConverter()

# 执行转换
result = converter.convert(source)

# 导出为 Markdown
print(result.document.export_to_markdown())
```

#### 导出为不同格式

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("document.pdf")

# 导出为 Markdown
markdown_content = result.document.export_to_markdown()

# 导出为 HTML
html_content = result.document.export_to_html()

# 导出为 JSON（无损格式）
json_content = result.document.export_to_json()
```

#### 处理本地文件

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()

# 处理 PDF
result = converter.convert("/path/to/document.pdf")

# 处理 Word 文档
result = converter.convert("/path/to/document.docx")

# 处理图像文件（会自动应用 OCR）
result = converter.convert("/path/to/image.png")
```

---

## 🔧 高级功能

### 1. 高效批量处理（避免重复加载模型）

**⚠️ 重要提示**：Docling 会自动缓存已加载的模型，但前提是**复用同一个 DocumentConverter 实例**。

#### ❌ 错误方式（每次都重新加载模型）

```python
# 这样会导致每次都重新加载模型，效率极低！
for file in file_list:
    converter = DocumentConverter()  # ❌ 错误！每次都创建新实例
    result = converter.convert(file)
```

#### ✅ 正确方式（复用实例，模型只加载一次）

```python
from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.document_converter import PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions
from pathlib import Path

# 1. 初始化一次 DocumentConverter（模型在此加载）
pipeline_options = PdfPipelineOptions(
    do_table_structure=True,
    do_ocr=True,
    generate_picture_images=False,  # 节省内存
)

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

# 2. 批量处理多个文档（复用已加载的模型）
pdf_files = Path("documents").glob("*.pdf")

for pdf_file in pdf_files:
    result = converter.convert(str(pdf_file))

    # 保存为 Markdown
    output_file = pdf_file.stem + ".md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result.document.export_to_markdown())

    print(f"已转换: {pdf_file} -> {output_file}")
```

#### ✅✅ 最佳方式（使用 convert_all 方法）

```python
from docling.document_converter import DocumentConverter
from docling.datamodel.document import ConversionStatus

# 初始化转换器
converter = DocumentConverter()

# 使用 convert_all 批量处理（更高效，支持并发）
file_list = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]

results_iter = converter.convert_all(
    source=file_list,
    raises_on_error=False  # 遇到错误继续处理
)

for result in results_iter:
    if result.status == ConversionStatus.SUCCESS:
        print(f"✓ 转换成功: {result.input.file.name}")
        doc = result.document
        markdown = doc.export_to_markdown()
        # 处理文档...
    else:
        print(f"✗ 转换失败: {result.input.file.name} - {result.status}")
```

### 2. 性能优化配置

```python
import os
from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import PdfPipelineOptions

# 限制 CPU 线程数（避免资源争抢）
os.environ["OMP_NUM_THREADS"] = "4"

# 配置 pipeline 选项
pipeline_options = PdfPipelineOptions(
    # 表格结构识别
    do_table_structure=True,
    table_structure_options={
        "mode": "FAST"  # 或 "ACCURATE"
    },

    # OCR 选项
    do_ocr=True,
    ocr_options={
        "lang": ["en", "zh"],  # 指定语言
    },

    # 内存优化
    generate_picture_images=False,  # 不生成图片（节省内存）
    generate_parsed_pages=False,    # 不生成解析页面（节省内存）

    # 文档超时
    document_timeout=300,  # 5 分钟超时
)

converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)
```

### 3. 预下载模型（离线环境）

```bash
# 预下载所有模型到本地
docling-tools models download

# 下载自定义模型
docling-tools models download-hf-repo ds4sd/SmolDocling-256M-preview

# 模型默认保存在：$HOME/.cache/docling/models
```

```python
# 使用本地模型
pipeline_options = PdfPipelineOptions(
    artifacts_path="/path/to/downloaded/models"  # 指定模型路径
)
```

### 4. 构建长期运行的转换服务

```python
from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import PdfPipelineOptions
from fastapi import FastAPI, UploadFile
from io import BytesIO
from docling.datamodel.base_models import DocumentStream

app = FastAPI()

# 全局初始化（只加载一次模型）
class DoclingService:
    def __init__(self):
        pipeline_options = PdfPipelineOptions(
            do_table_structure=True,
            do_ocr=True,
        )
        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

# 全局服务实例（模型只加载一次）
docling_service = DoclingService()

@app.post("/convert")
async def convert_document(file: UploadFile):
    """转换上传的文档"""
    content = await file.read()

    # 使用全局转换器（复用已加载的模型）
    buf = BytesIO(content)
    source = DocumentStream(name=file.filename, stream=buf)
    result = docling_service.converter.convert(source)

    return {
        "status": "success",
        "markdown": result.document.export_to_markdown()
    }
```

### 5. 批量处理文档（旧版，保留参考）

### 6. 与 AI 框架集成

#### LangChain 集成

```python
from langchain_community.document_loaders import DoclingLoader

loader = DoclingLoader("https://arxiv.org/pdf/2408.09869")
docs = loader.load()

for doc in docs:
    print(doc.page_content)
```

#### LlamaIndex 集成

```python
from llama_index.core import SimpleDirectoryReader
from llama_index.readers.docling import DoclingReader

reader = DoclingReader()
documents = SimpleDirectoryReader(
    input_files=["document.pdf"],
    file_extractor={".pdf": reader}
).load_data()
```

### 7. 使用 MCP 服务器

Docling 提供 MCP (Model Context Protocol) 服务器，可以连接到任何 AI 代理：

```bash
# 启动 MCP 服务器
docling-mcp-server
```

---

## 📊 性能对比：不同处理方式

| 处理方式 | 首次加载时间 | 后续处理时间 | 内存使用 | 适用场景 |
|---------|------------|------------|---------|---------|
| **每次创建新实例** | 慢（3-5秒） | 慢（3-5秒/文档） | 低 | ❌ 不推荐 |
| **复用单个实例** | 慢（3-5秒） | 快（0.5-2秒/文档） | 中 | ✅ 推荐（小批量） |
| **使用 convert_all** | 慢（3-5秒） | 最快（支持并发） | 中 | ✅✅ 最推荐（大批量） |
| **并行处理池** | 慢（3-5秒×实例数） | 快（并发处理） | 高 | 大规模生产环境 |

**关键要点**：
- 🎯 **模型只加载一次**：同一个 `DocumentConverter` 实例会自动缓存模型
- 🚀 **批量处理更快**：使用 `convert_all()` 方法可以并发处理多个文档
- 💾 **内存优化**：禁用不需要的功能（如 `generate_picture_images=False`）
- ⚡ **CPU 控制**：设置 `OMP_NUM_THREADS` 环境变量限制 CPU 使用

---

## 📚 支持的文档格式

| 格式类别 | 支持的格式 |
|---------|-----------|
| 文档 | PDF, DOCX, PPTX, XLSX, HTML |
| 图像 | PNG, TIFF, JPEG, 等 |
| 音频 | WAV, MP3 |
| 字幕 | VTT (WebVTT) |
| 其他 | Markdown, 纯文本 |

---

## 🎯 常见使用场景

### 场景 1：PDF 转 Markdown

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("research_paper.pdf")

# 保存为 Markdown
with open("research_paper.md", "w", encoding="utf-8") as f:
    f.write(result.document.export_to_markdown())
```

### 场景 2：批量处理扫描文档（OCR）

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()

# 处理扫描的 PDF 或图像
result = converter.convert("scanned_document.pdf")

# Docling 会自动应用 OCR 提取文本
text_content = result.document.export_to_markdown()
print(text_content)
```

### 场景 3：提取表格数据

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("financial_report.pdf")

# 导出为 Markdown 以保留表格结构
markdown_content = result.document.export_to_markdown()

# 表格会被转换为 Markdown 表格格式
print(markdown_content)
```

### 场景 4：音频转文字

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("meeting_recording.mp3")

# 使用 ASR 模型转录音频
text_content = result.document.export_to_markdown()
print(text_content)
```

---

## ⚙️ 配置选项

### 转换选项

```python
from docling.document_converter import DocumentConverter
from docling.pipeline.options import PipelineOptions

# 自定义管道选项
pipeline_options = PipelineOptions()
# 根据需要配置选项...

converter = DocumentConverter(pipeline_options=pipeline_options)
result = converter.convert("document.pdf")
```

### OCR 配置

Docling 支持多种 OCR 引擎，可以根据需要选择和配置。

---

## 🐛 故障排除

### 常见问题

1. **安装失败**
   - 确保使用最新版本的 pip：`pip install --upgrade pip`
   - 尝试使用虚拟环境
   - 如果本地安装有问题，尝试使用 Docker

2. **Docker 相关问题**
   - **权限问题**：确保有权限访问挂载的目录
     ```bash
     # Linux/Mac
     sudo docker run --rm -v $(pwd):/documents ghcr.io/docling-project/docling:latest /documents/input.pdf
     ```
   - **内存不足**：增加 Docker 容器的内存限制
     ```bash
     docker run --rm -v $(pwd):/documents --memory=4g ghcr.io/docling-project/docling:latest /documents/input.pdf
     ```
   - **路径问题**：使用绝对路径而不是相对路径
   - **网络问题**：如果无法拉取镜像，尝试使用镜像加速器

3. **内存不足**
   - 对于大型文档，考虑分批处理
   - 增加系统可用内存
   - Docker 用户可以增加容器内存限制

4. **OCR 准确率低**
   - 确保图像质量良好
   - 尝试使用不同的 OCR 选项
   - 考虑使用 VLM 管道获得更好的结果

5. **PDF 解析问题**
   - 尝试使用 VLM 管道：`--pipeline vlm`
   - 检查 PDF 是否加密或损坏
   - 尝试使用不同的解析选项

---

## 📖 更多资源

- **官方文档**：https://docling-project.github.io/docling/
- **GitHub 仓库**：https://github.com/docling-project/docling
- **技术报告**：https://arxiv.org/abs/2408.09869
- **Discord 社区**：https://docling.ai/discord
- **示例代码**：https://docling-project.github.io/docling/examples/

---

## 📄 许可证

Docling 代码库采用 MIT 许可证。对于各个模型的使用，请参考原始包中的模型许可证。

---

## 🙏 致谢

Docling 由 IBM Research Zurich 的 AI for knowledge 团队发起，现在是 LF AI & Data Foundation 的托管项目。

---

**版本**：v2.68.0 (最新版本)  
**更新日期**：2026-01-13

---

## 快速参考

### 最常用的命令

**本地安装：**

```bash
# 安装
pip install docling

# 基本转换
docling input.pdf

# 使用 VLM
docling --pipeline vlm --vlm-model granite_docling input.pdf

# 指定输出
docling input.pdf -o output.md
```

**Docker 部署：**

```bash
# 拉取镜像
docker pull ghcr.io/docling-project/docling:latest

# 基本转换
docker run --rm -v $(pwd):/documents ghcr.io/docling-project/docling:latest /documents/input.pdf

# 使用 VLM
docker run --rm -v $(pwd):/documents ghcr.io/docling-project/docling:latest --pipeline vlm --vlm-model granite_docling /documents/input.pdf

# 指定输出
docker run --rm -v $(pwd):/documents ghcr.io/docling-project/docling:latest /documents/input.pdf -o /documents/output.md
```

### 最常用的 Python 代码

```python
from docling.document_converter import DocumentConverter

converter = DocumentConverter()
result = converter.convert("document.pdf")
print(result.document.export_to_markdown())
```

---

**祝您使用愉快！** 🎉
