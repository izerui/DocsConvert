# GROBID 图片提取完整指南

## 📸 GROBID 对图片的支持情况

### GROBID 能做什么

✅ **可以做到：**
- 识别图片和表格的位置（坐标）
- 提取图片标题和说明文字
- 标记图片在 PDF 中的精确位置
- 区分图片（figure）和表格（table）

❌ **不能做到：**
- 直接提取图片文件本身
- OCR 识别图片内的文字
- 理解图片内容

## 🔧 完整解决方案

### 方案 1：使用提供的 Python 脚本（推荐）

我已经创建了一个完整的工具 `grobid_extract_images.py`，它可以：

1. 使用 GROBID 获取图片信息和坐标
2. 从 PDF 中提取实际图片文件
3. 保存图片说明文字
4. 生成结构化的元数据（JSON）

#### 安装依赖

```bash
pip install requests pymupdf4llm beautifulsoup4
```

#### 使用方法

```bash
# 基本用法
python grobid_extract_images.py paper.pdf

# 指定输出目录
python grobid_extract_images.py paper.pdf -o ./output

# 指定 GROBID 服务地址
python grobid_extract_images.py paper.pdf -u http://localhost:8070
```

#### 输出结构

```
output/
├── images/
│   ├── page1_img1.png
│   ├── page1_img2.png
│   ├── page3_img1.png
│   └── ...
└── metadata.json
```

#### metadata.json 示例

```json
{
  "pdf_path": "paper.pdf",
  "total_figures": 5,
  "figures": [
    {
      "filename": "page1_img1.png",
      "path": "output/images/page1_img1.png",
      "page": 1,
      "label": "Figure 1",
      "caption": "Architecture of the proposed deep learning model...",
      "format": "png",
      "size": 123456
    },
    {
      "filename": "page3_img1.png",
      "path": "output/images/page3_img1.png",
      "page": 3,
      "label": "Table 1",
      "caption": "Comparison of different approaches...",
      "format": "png",
      "size": 234567
    }
  ]
}
```

### 方案 2：手动使用 GROBID API

#### 步骤 1：获取包含图片坐标的 TEI XML

```bash
curl -X POST \
  -F "input=@paper.pdf" \
  -F "teiCoordinates=figure" \
  -F "teiCoordinates=formula" \
  http://localhost:8070/api/processFulltextDocument > output.xml
```

#### 步骤 2：解析 TEI XML 获取图片信息

```python
from bs4 import BeautifulSoup

with open('output.xml', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'xml')

# 查找所有图片
for fig in soup.find_all('figure'):
    fig_id = fig.get('xml:id', '')
    coords = fig.get('coords', '')
    
    # 获取标签
    label = fig.find('label')
    if label:
        print(f"标签: {label.get_text(strip=True)}")
    
    # 获取说明
    caption = fig.find('figDesc')
    if caption:
        print(f"说明: {caption.get_text(strip=True)}")
    
    # 解析坐标
    if coords:
        parts = coords.split(';')[0].split(',')
        page_num = int(parts[0])
        x, y, w, h = map(float, parts[1:5])
        print(f"位置: 第{page_num}页, ({x}, {y}, {w}x{h})")
```

#### 步骤 3：使用 PyMuPDF 提取图片

```python
import fitz  # PyMuPDF

doc = fitz.open("paper.pdf")

for page in doc:
    image_list = page.get_images(full=True)
    
    for img_index, img in enumerate(image_list):
        xref = img[0]
        base_image = doc.extract_image(xref)
        
        if base_image:
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            # 保存图片
            filename = f"page{page.number + 1}_img{img_index + 1}.{image_ext}"
            with open(filename, "wb") as img_file:
                img_file.write(image_bytes)
            
            print(f"保存: {filename}")

doc.close()
```

### 方案 3：使用专门的 PDF 图片提取工具

如果只需要提取图片，不需要说明文字，可以使用：

#### pdfimages (Poppler 工具包)

```bash
# 安装
# Ubuntu/Debian: sudo apt install poppler-utils
# macOS: brew install poppler

# 提取所有图片
pdfimages -all paper.pdf images/

# 输出：
# images-000.png
# images-001.png
# ...
```

#### PyMuPDF 直接提取

```python
import fitz

def extract_all_images(pdf_path, output_dir):
    doc = fitz.open(pdf_path)
    
    for page_index in range(len(doc)):
        page = doc[page_index]
        image_list = page.get_images(full=True)
        
        for image_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            
            if base_image:
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                filename = f"{output_dir}/page{page_index + 1}_{image_index + 1}.{image_ext}"
                with open(filename, "wb") as f:
                    f.write(image_bytes)

# 使用
extract_all_images("paper.pdf", "./images")
```

## 📊 GROBID 图片坐标说明

### 坐标格式

GROBID 在 TEI XML 中使用 `coords` 属性标记图片位置：

```xml
<figure xml:id="fig1" coords="1,100.5,200.3,300.0,250.0">
    <label>Figure 1</label>
    <figDesc>Architecture overview</figDesc>
</figure>
```

坐标格式：`page,x,y,width,height`

- `page`: 页码（从 1 开始）
- `x`: 左上角 X 坐标
- `y`: 左上角 Y 坐标
- `width`: 宽度
- `height`: 高度

### 支持的元素

GROBID 可以为以下元素提供坐标：

- `figure` - 图片和表格
- `formula` - 数学公式
- `ref` - 引用标记
- `biblStruct` - 参考文献
- `persName` - 作者姓名
- `head` - 章节标题
- `p` - 段落
- `s` - 句子（需要 `segmentSentences=1`）

## 🎯 实际应用示例

### 示例 1：创建图片索引

```python
import json
from pathlib import Path

def create_image_index(metadata_file):
    """创建图片索引 HTML"""
    with open(metadata_file, 'r') as f:
        data = json.load(f)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>图片索引</title>
        <style>
            .figure { margin: 20px; border: 1px solid #ccc; padding: 10px; }
            .figure img { max-width: 100%; }
            .caption { font-style: italic; color: #666; }
        </style>
    </head>
    <body>
        <h1>图片索引</h1>
    """
    
    for fig in data['figures']:
        html += f"""
        <div class="figure">
            <img src="{fig['path']}" alt="{fig['label']}">
            <p class="caption">
                <strong>{fig['label']}</strong> (第{fig['page']}页)<br>
                {fig['caption']}
            </p>
        </div>
        """
    
    html += "</body></html>"
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

# 使用
create_image_index('output/metadata.json')
```

### 示例 2：批量处理多个 PDF

```python
from pathlib import Path
from grobid_extract_images import GrobidImageExtractor

def batch_process_pdfs(pdf_dir, output_base_dir):
    """批量处理多个 PDF"""
    extractor = GrobidImageExtractor()
    
    pdf_files = Path(pdf_dir).glob("*.pdf")
    
    for pdf_path in pdf_files:
        print(f"\n处理: {pdf_path.name}")
        output_dir = Path(output_base_dir) / pdf_path.stem
        
        try:
            metadata = extractor.process_pdf(
                str(pdf_path), 
                str(output_dir)
            )
            print(f"✅ 完成: {metadata['total_figures']} 个图片")
        except Exception as e:
            print(f"❌ 失败: {e}")

# 使用
batch_process_pdfs("./pdfs", "./output")
```

### 示例 3：与 AI 集成

```python
import openai
from grobid_extract_images import GrobidImageExtractor

def analyze_figures_with_ai(pdf_path):
    """使用 AI 分析图片内容"""
    # 1. 提取图片
    extractor = GrobidImageExtractor()
    metadata = extractor.process_pdf(pdf_path, "./temp")
    
    # 2. 使用 AI 分析每个图片
    for fig in metadata['figures']:
        # 读取图片
        with open(fig['path'], 'rb') as f:
            image_data = f.read()
        
        # 发送给 GPT-4V
        response = openai.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"请分析这张图片。论文中的说明是：{fig['caption']}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/{fig['format']};base64,{base64.b64encode(image_data).decode()}"
                            }
                        }
                    ]
                }
            ]
        )
        
        print(f"\n{fig['filename']}:")
        print(response.choices[0].message.content)

# 使用
analyze_figures_with_ai("paper.pdf")
```

## 📝 总结

### 推荐方案

| 需求 | 推荐方案 |
|------|---------|
| **提取图片 + 说明** | 使用 `grobid_extract_images.py` |
| **仅提取图片** | `pdfimages` 或 PyMuPDF |
| **仅获取说明** | GROBID API + 解析 TEI XML |
| **批量处理** | 脚本循环 + `grobid_extract_images.py` |
| **AI 分析** | 提取图片 + GPT-4V |

### 关键点

1. **GROBID 不直接提取图片文件**，但提供图片位置和说明
2. **需要结合 PyMuPDF 等工具**提取实际图片
3. **TEI XML 包含丰富的图片信息**（坐标、标签、说明）
4. **可以自动化整个流程**，实现批量处理

### 下一步

- 运行 `python grobid_extract_images.py your_paper.pdf` 测试
- 查看 `output/metadata.json` 了解提取结果
- 根据需求定制脚本功能
