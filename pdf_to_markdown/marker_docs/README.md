# Marker PDF 转 Markdown 转换器使用说明

## 简介

`_marker.py` 是基于 [Marker](https://github.com/datalab-to/marker) 的高质量 PDF 到 Markdown 转换器。Marker 是一个快速且准确的文档转换工具，特别擅长处理复杂的文档结构。

## 功能特性

- ✅ **高质量转换**：智能识别文档结构，保留格式
- ✅ **表格支持**：准确提取和转换表格
- ✅ **公式支持**：保留数学公式格式（LaTeX 风格）
- ✅ **代码块识别**：自动识别代码块并高亮
- ✅ **图片提取**：可将图片保存为独立文件
- ✅ **多语言支持**：完美支持中文等多种语言
- ✅ **OCR 支持**：可选的 OCR 功能用于扫描文档
- ✅ **页面选择**：支持指定页面范围转换
- ✅ **元数据管理**：自动提取文档元数据
- ✅ **Front Matter**：支持 YAML 格式的元数据头部

## 安装依赖

```bash
pip install marker-pdf
```

## 基本使用

### 方式 1：直接调用函数

```python
from pdf_to_markdown._marker import convert_pdf_to_markdown

# 基本转换
result = convert_pdf_to_markdown("document.pdf")

# 指定输出文件
result = convert_pdf_to_markdown(
    "document.pdf",
    output_file="output.md"
)
```

### 方式 2：通过包导入

```python
from pdf_to_markdown import convert_with_marker

result = convert_with_marker("document.pdf", output_file="output.md")
```

## 参数说明

### 必需参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `pdf_file` | `str` | PDF 文件路径 |

### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `output_file` | `str/None` | `None` | 输出 Markdown 文件路径（默认为同名 .md 文件） |
| `extract_metadata` | `bool` | `True` | 是否从文件名提取元数据 |
| `add_front_matter` | `bool` | `True` | 是否添加 YAML front matter |
| `custom_metadata` | `dict/None` | `None` | 自定义元数据字典 |
| `extract_images` | `bool` | `True` | 是否提取图片到外部文件 |
| `image_output_dir` | `str/None` | `None` | 图片输出目录（默认为输出文件同目录下的 images 子目录） |
| `force_ocr` | `bool` | `False` | 是否强制 OCR（Marker 特有） |
| `paginate_output` | `bool` | `True` | 是否分页输出（Marker 特有） |
| `paginate_output` | `bool` | `True` | 是否分页输出（Marker 特有） |
| `page_range` | `str/None` | `None` | 指定页面范围（如 "0,5-10"，Marker 特有） |

## 使用示例

### 示例 1：基本转换（默认设置）

```python
from pdf_to_markdown._marker import convert_pdf_to_markdown

result = convert_pdf_to_markdown("document.pdf")
```

输出文件：`document.md`

### 示例 2：指定输出文件和图片目录

```python
result = convert_pdf_to_markdown(
    "document.pdf",
    output_file="docs/converted.md",
    image_output_dir="docs/images"
)
```

### 示例 3：转换指定页面范围

```python
# 只转换前 3 页
result = convert_pdf_to_markdown(
    "document.pdf",
    page_range="0-2"
)

# 转换第 1、5、6-10 页
result = convert_pdf_to_markdown(
    "document.pdf",
    page_range="0,5-10"
)
```

### 示例 4：使用 OCR 处理扫描文档

```python
result = convert_pdf_to_markdown(
    "scanned_document.pdf",
    force_ocr=True,
    output_file="scanned_output.md"
)
```

### 示例 5：不添加 Front Matter

```python
result = convert_pdf_to_markdown(
    "document.pdf",
    add_front_matter=False,
    output_file="plain_output.md"
)
```

### 示例 6：添加自定义元数据

```python
result = convert_pdf_to_markdown(
    "document.pdf",
    custom_metadata={
        "author": "张三",
        "category": "技术文档",
        "tags": ["PDF", "转换", "Markdown"]
    }
)
```

### 示例 7：禁用图片提取

```python
result = convert_pdf_to_markdown(
    "document.pdf",
    extract_images=False,
    output_file="no_images.md"
)
```

## 输出格式

### Front Matter 示例

转换后的 Markdown 文件会包含以下元数据：

```yaml
---
title: "Document Title"
author: "John Doe"
year: "2024"
source_file: "document.pdf"
converted_date: "2024-01-15T10:30:00.123456"
total_pages: 25
total_chars: 123456
total_words: 23456
converter: "marker"
conversion_options:
  force_ocr: false
  paginate_output: true
  page_range: null
extracted_images: 5
image_count: 5
image_dir: "images"
---

# Document Title

## Document Information

**Author**: John Doe
**Year**: 2024
**Source**: document.pdf
**Pages**: 25
**Characters**: 123456
**Words**: 23456
**Images**: 5 extracted
**Converted**: 2024-01-15T10:30:00.123456

---

[文档内容...]
```

## 文件名元数据提取

转换器会自动从文件名中提取元数据，支持的命名格式：

| 文件名格式 | 提取的元数据 |
|------------|--------------|
| `2024_张三_文档标题.pdf` | year=2024, author=张三, title=文档标题 |
| `李四_研究报告_2023.pdf` | year=2023, author=李四, title=研究报告 |
| `简单标题.pdf` | title=简单标题 |

## 图片处理

### 图片命名规则

提取的图片会按以下规则命名：

```
{文件名}_image_1.png
{文件名}_image_2.png
...
```

### 图片引用格式

Markdown 中的图片链接会自动更新为相对路径：

```markdown
![图片描述](images/document_image_1.png)
```

## 性能优化建议

### 1. 大文件处理

对于大型 PDF 文件，建议：

```python
# 分批转换页面
for i in range(0, total_pages, 10):
    page_range = f"{i}-{min(i+9, total_pages-1)}"
    convert_pdf_to_markdown(
        "large_document.pdf",
        output_file=f"output_part_{i//10+1}.md",
        page_range=page_range
    )
```

### 2. 禁用不必要的功能

如果不需要某些功能，可以禁用以提升性能：

```python
# 最快转换（无图片、无元数据）
result = convert_pdf_to_markdown(
    "document.pdf",
    extract_images=False,
    add_front_matter=False,
    extract_metadata=False
)
```

### 3. 指定页面范围

只转换需要的页面：

```python
# 只转换目录部分（假设在前 5 页）
convert_pdf_to_markdown(
    "document.pdf",
    page_range="0-4",
    output_file="table_of_contents.md"
)
```

## 错误处理

### 常见错误

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| `FileNotFoundError` | 文件不存在 | 检查文件路径是否正确 |
| `ValueError` | 文件不是 PDF 格式 | 确认文件扩展名是 .pdf |
| `OSError` | 文件被占用或权限不足 | 关闭文件或检查权限 |

### 错误处理示例

```python
try:
    result = convert_pdf_to_markdown("document.pdf")
except FileNotFoundError as e:
    print(f"文件不存在: {e}")
except ValueError as e:
    print(f"参数错误: {e}")
except Exception as e:
    print(f"转换失败: {e}")
    import traceback
    traceback.print_exc()
```

## 与其他转换器对比

| 特性 | Marker | PyMuPDF4LLM | MarkItDown |
|------|--------|-------------|------------|
| 表格质量 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 公式支持 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 代码块识别 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 转换速度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| OCR 支持 | ✅ | ❌ | ❌ |
| 中文支持 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**推荐场景：**

- **Marker**: 需要最高转换质量，特别是表格、公式、代码块较多的技术文档
- **PyMuPDF4LLM**: 需要快速批量处理，对转换质量要求中等
- **MarkItDown**: 需要元数据管理，文献综述等场景

## 注意事项

1. **首次运行**: 首次运行时，Marker 会下载必要的模型文件，可能需要一些时间和网络连接
2. **内存占用**: 处理大型 PDF 文件时可能需要较多内存（建议至少 4GB 可用内存）
3. **OCR 性能**: 启用 `force_ocr` 会显著增加转换时间，仅在必要时使用
4. **图片大小**: 提取的图片可能较大，如需压缩请自行处理
5. **编码问题**: 确保 PDF 文件使用 UTF-8 或兼容编码

## 测试脚本

运行内置测试：

```bash
python pdf_to_markdown/_marker.py
```

运行对比测试：

```bash
python pdf_to_markdown/test_converters.py files/example.pdf
```

## 参考资料

- [Marker GitHub 仓库](https://github.com/datalab-to/marker)
- [Marker 官方文档](https://marker.readthedocs.io/)

## 许可证

本代码遵循 MIT 许可证。Marker 库使用 Apache 2.0 许可证。

## 问题反馈

如有问题或建议，请提交 Issue 或 Pull Request。