# Nougat PDF 转 Markdown 转换器使用说明

## 简介

`_nougat.py` 是基于 [Nougat](https://github.com/facebookresearch/nougat) 的科学文档 PDF 到 Markdown 转换器。Nougat 是由 Facebook Research (Meta AI) 开发的开源工具，专为处理学术论文和技术文档而设计，特别擅长识别和转换数学公式。

## 功能特性

- ✅ **数学公式处理**：业界领先的数学公式识别和 LaTeX 格式输出
- ✅ **深度学习模型**：基于 Vision Transformer (ViT) 的高精度识别
- ✅ **科学文档优化**：专为学术论文、技术文档优化
- ✅ **结构保留**：保留文档的标题、段落、列表、引用等结构
- ✅ **多模型支持**：支持 base 模型和 small 模型
- ✅ **重流模式**：适合移动端阅读的重流输出
- ✅ **元数据管理**：自动提取文档元数据
- ✅ **Front Matter**：支持 YAML 格式的元数据头部
- ✅ **批处理支持**：可调节批处理大小以优化性能

## 安装依赖

### 方法 1：使用 pip 安装（推荐）

```bash
pip install nougat-ocr
```

### 方法 2：从源码安装

```bash
pip install git+https://github.com/facebookresearch/nougat
```

### 验证安装

安装完成后，运行以下命令验证：

```bash
nougat --help
```

如果显示帮助信息，说明安装成功。

## 基本使用

### 方式 1：直接调用函数

```python
from pdf_to_markdown._nougat import convert_pdf_to_markdown

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
from pdf_to_markdown import convert_with_nougat

result = convert_with_nougat("document.pdf", output_file="output.md")
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
| `model` | `str/None` | `None` | Nougat 模型名称（如 '0.1.0-base', '0.1.0-small'） |
| `batch_size` | `int/None` | `None` | 批处理大小（影响内存使用和速度） |
| `no_skipping` | `bool` | `False` | 是否跳过已经存在的输出 |
| `reflow` | `bool` | `False` | 是否使用重流模式（适合移动端阅读） |
| `timeout` | `int` | `300` | 转换超时时间（秒） |

## 使用示例

### 示例 1：基本转换（默认设置）

```python
from pdf_to_markdown._nougat import convert_pdf_to_markdown

result = convert_pdf_to_markdown("arxiv_paper.pdf")
```

输出文件：`arxiv_paper.md`

### 示例 2：使用 Small 模型（更快）

```python
result = convert_pdf_to_markdown(
    "document.pdf",
    model="0.1.0-small",  # 使用 small 模型
    output_file="output_small.md"
)
```

**注意**：Small 模型速度更快，但质量略低于 base 模型。

### 示例 3：使用重流模式

```python
result = convert_pdf_to_markdown(
    "document.pdf",
    reflow=True,  # 重流模式，适合移动端
    output_file="output_reflow.md"
)
```

### 示例 4：调整批处理大小

```python
# 大批处理（更快，但需要更多内存）
result = convert_pdf_to_markdown(
    "document.pdf",
    batch_size=8,
    output_file="output_fast.md"
)

# 小批处理（较慢，但内存占用少）
result = convert_pdf_to_markdown(
    "large_document.pdf",
    batch_size=1,
    output_file="output_low_memory.md"
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
        "institution": "清华大学",
        "keywords": ["深度学习", "NLP", "Transformers"],
        "arxiv_id": "2401.12345"
    }
)
```

### 示例 7：设置更长超时时间

```python
result = convert_pdf_to_markdown(
    "very_large_document.pdf",
    timeout=600,  # 10分钟超时
    output_file="large_output.md"
)
```

## 输出格式

### Front Matter 示例

转换后的 Markdown 文件会包含以下元数据：

```yaml
---
title: "Attention Is All You Need"
author: "Ashish Vaswani"
year: "2017"
source_file: "attention_paper.pdf"
converted_date: "2024-01-15T10:30:00.123456"
converter: "nougat"
conversion_options:
  model: "0.1.0-base"
  batch_size: null
  no_skipping: false
  reflow: false
total_lines: 1234
total_chars: 56789
estimated_formulas: 45
---

# Attention Is All You Need

## Document Information

**Author**: Ashish Vaswani
**Year**: 2017
**Source**: attention_paper.pdf
**Lines**: 1234
**Characters**: 56789
**Estimated Formulas**: 45
**Converted**: 2024-01-15T10:30:00.123456

---

[文档内容...]
```

### Markdown 格式示例

Nougat 输出的 Markdown 格式：

```markdown
# Abstract

The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...

## 1. Introduction

Recurrent neural networks, long short-term memory [13] and gated recurrent [7] neural networks in particular, have been firmly established as state of the art approaches in sequence modeling and transduction problems such as language modeling and machine translation [35, 2, 24].

### 1.1 Background

Let $x = (x_1, \ldots, x_n)$ be the input sequence.

$$
\text{Attention}(Q, K, V) = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V
$$

## 2. Model

The Transformer follows this overall architecture using an encoder-decoder structure.
```

**注意**：
- 数学公式使用 LaTeX 格式，用 `$$...$$` 包裹
- 标题使用 Markdown 的 `#`、`##`、`###` 等格式
- 列表使用 `-` 或数字编号

## 文件名元数据提取

转换器会自动从文件名中提取元数据，支持的命名格式：

| 文件名格式 | 提取的元数据 |
|------------|--------------|
| `2024_Vaswani_Attention_Is_All_You_Need.pdf` | year=2024, author=Vaswani, title=Attention Is All You Need |
| `DeepLearning_2023_Lec01.pdf` | year=2023, title=DeepLearning Lec01 |
| `simple_paper.pdf` | title=simple_paper |

## 模型选择

### Base 模型（默认）

```python
result = convert_pdf_to_markdown("paper.pdf", model="0.1.0-base")
```

- **特点**：最高精度
- **速度**：较慢
- **内存**：较大
- **适用场景**：需要最高质量的转换，数学公式复杂

### Small 模型

```python
result = convert_pdf_to_markdown("paper.pdf", model="0.1.0-small")
```

- **特点**：速度更快
- **速度**：快（约 2-3x）
- **内存**：较小
- **适用场景**：快速预览、大批量处理、设备资源有限

## 性能优化建议

### 1. 根据文档类型选择模型

```python
# 数学公式密集的学术论文 -> 使用 base 模型
result = convert_pdf_to_markdown(
    "math_paper.pdf",
    model="0.1.0-base"
)

# 普通技术文档 -> 使用 small 模型
result = convert_pdf_to_markdown(
    "technical_doc.pdf",
    model="0.1.0-small"
)
```

### 2. 调整批处理大小

```python
# 根据可用内存调整
import psutil

available_memory_gb = psutil.virtual_memory().available / (1024**3)

if available_memory_gb > 16:
    batch_size = 8
elif available_memory_gb > 8:
    batch_size = 4
else:
    batch_size = 1

result = convert_pdf_to_markdown(
    "document.pdf",
    batch_size=batch_size
)
```

### 3. 增加超时时间

对于大型文档：

```python
result = convert_pdf_to_markdown(
    "large_document.pdf",
    timeout=600  # 10分钟
)
```

### 4. 使用重流模式

如果需要在移动设备上阅读：

```python
result = convert_pdf_to_markdown(
    "document.pdf",
    reflow=True
)
```

## 错误处理

### 常见错误

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| `RuntimeError: Nougat 未安装` | nougat-ocr 未安装或不在 PATH 中 | 运行 `pip install nougat-ocr` |
| `FileNotFoundError` | 文件不存在 | 检查文件路径是否正确 |
| `ValueError` | 文件不是 PDF 格式 | 确认文件扩展名是 .pdf |
| `RuntimeError: Nougat 转换超时` | 转换时间过长 | 增加 `timeout` 参数或使用 small 模型 |
| `RuntimeError: CUDA out of memory` | GPU 内存不足 | 减小 `batch_size` 或使用 CPU |

### 错误处理示例

```python
try:
    result = convert_pdf_to_markdown("document.pdf")
except RuntimeError as e:
    if "Nougat 未安装" in str(e):
        print("请安装 nougat-ocr: pip install nougat-ocr")
    elif "超时" in str(e):
        print("转换超时，尝试增加超时时间或使用 small 模型")
    elif "CUDA out of memory" in str(e):
        print("GPU 内存不足，尝试减小 batch_size 或使用 CPU")
    else:
        print(f"转换失败: {e}")
except FileNotFoundError as e:
    print(f"文件不存在: {e}")
except ValueError as e:
    print(f"参数错误: {e}")
except Exception as e:
    print(f"未知错误: {e}")
    import traceback
    traceback.print_exc()
```

## 与其他转换器对比

| 特性 | Nougat | Marker | PyMuPDF4LLM |
|------|--------|--------|-------------|
| 数学公式 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 学术论文 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 表格质量 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 代码块 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| 转换速度 | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 中文支持 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| OCR 支持 | ❌ | ✅ | ❌ |

**推荐场景：**

- **Nougat**: 数学公式密集的学术论文、技术文档、LaTeX 风格文档
- **Marker**: 需要表格、公式、代码块的通用文档，中文文档
- **PyMuPDF4LLM**: 需要快速批量处理，对转换质量要求中等

## 适用文档类型

### 最适合的文档

- ✅ **学术论文**：ArXiv 论文、期刊文章
- ✅ **数学文档**：包含大量公式的数学教材、论文
- ✅ **技术文档**：计算机科学、物理学等技术领域的文档
- ✅ **LaTeX 源码转换的 PDF**：从 LaTeX 生成的文档转换效果最佳

### 不太适合的文档

- ⚠️ **扫描版 PDF**：需要先使用 OCR 工具处理
- ⚠️ **多栏布局复杂**：如报纸、杂志
- ⚠️ **大量中文文档**：中文支持不如 Marker 和 PyMuPDF4LLM
- ⚠️ **需要图片提取**：Nougat 不提取图片到独立文件

## 注意事项

1. **首次运行**: 首次运行时，Nougat 会下载模型文件（约 1-2GB），需要网络连接和时间
2. **GPU 加速**: 如果有 GPU，Nougat 会自动使用 CUDA 加速（需要安装 CUDA）
3. **内存要求**: Base 模型建议至少 4GB 可用内存，Small 模型约 2GB
4. **处理时间**: 
   - Base 模型：约 5-15 秒/页（取决于硬件）
   - Small 模型：约 2-5 秒/页
5. **图片**: Nougat 不会提取图片，图片内容会被忽略或简单描述
6. **公式格式**: 公式输出为 LaTeX 格式，需要在支持 LaTeX 的环境中渲染
7. **重流模式**: 重流模式会改变文档布局，不适合需要保持原始结构的场景

## 批量处理示例

```python
from pathlib import Path
from pdf_to_markdown._nougat import convert_pdf_to_markdown

# 批量处理目录下的所有 PDF
pdf_dir = Path("papers")
output_dir = Path("markdown_outputs")
output_dir.mkdir(exist_ok=True)

for pdf_file in pdf_dir.glob("*.pdf"):
    try:
        output_file = output_dir / f"{pdf_file.stem}.md"
        print(f"正在处理: {pdf_file.name}")
        
        result = convert_pdf_to_markdown(
            str(pdf_file),
            output_file=str(output_file),
            model="0.1.0-small",  # 使用 small 模型加速
            batch_size=4,
            timeout=300
        )
        
        print(f"✓ 完成: {pdf_file.name} -> {output_file.name}")
        
    except Exception as e:
        print(f"✗ 失败: {pdf_file.name} - {e}")
        continue
```

## 测试脚本

运行内置测试：

```bash
python pdf_to_markdown/_nougat.py
```

运行对比测试：

```bash
python pdf_to_markdown/test_converters.py files/example.pdf
```

## 常见问题（FAQ）

### Q1: Nougat 转换速度太慢怎么办？

**A**: 尝试以下方法：
1. 使用 small 模型：`model="0.1.0-small"`
2. 增加批处理大小：`batch_size=8`（如果内存足够）
3. 对于预览目的，可以使用重流模式：`reflow=True`

### Q2: 数学公式转换不正确怎么办？

**A**: 
1. 确保使用 base 模型（默认）
2. 检查原始 PDF 的公式是否清晰可读
3. 对于扫描版 PDF，先使用 OCR 工具处理

### Q3: 中文文档转换效果不好怎么办？

**A**: Nougat 主要针对英文文档优化。对于中文文档，推荐使用：
- Marker：更好的中文支持
- PyMuPDF4LLM：快速的中文转换

### Q4: 如何提高转换质量？

**A**:
1. 使用高质量的 PDF（高 DPI、清晰文本）
2. 使用 base 模型而不是 small 模型
3. 确保文档是单栏布局（学术论文标准）

### Q5: 可以离线使用吗？

**A**: 可以。首次运行时会下载模型文件，之后可以离线使用。模型文件会缓存到本地。

## 参考资料

- [Nougat GitHub 仓库](https://github.com/facebookresearch/nougat)
- [Nougat 论文](https://arxiv.org/abs/2308.13418)
- [Nougat 官方文档](https://github.com/facebookresearch/nougat/blob/main/README.md)

## 许可证

本代码遵循 MIT 许可证。Nougat 库使用 Creative Commons Attribution-NonCommercial 4.0 International 许可证。

## 问题反馈

如有问题或建议，请提交 Issue 或 Pull Request。

## 致谢

- [Facebook Research (Meta AI)](https://research.fb.com/) - Nougat 的开发者
- [Hugging Face](https://huggingface.co/) - 提供模型托管和基础设施支持