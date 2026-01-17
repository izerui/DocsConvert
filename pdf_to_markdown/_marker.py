#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于 Marker 的 PDF 到 Markdown 转换器

安装依赖：
    pip install marker-pdf

特性：
- 高质量的 PDF 到 Markdown 转换
- 自动识别并保留表格、公式、代码块等结构
- 支持图片提取并保存为独立文件
- 支持中文等多语言文档
- 保留文档结构和格式
- 简单易用的 API
"""

from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.output import text_from_rendered, save_output
import re
from datetime import datetime
import os


def extract_metadata_from_filename(filename: str) -> Dict[str, str]:
    """从文件名提取元数据"""
    metadata = {}
    name = Path(filename).stem
    
    year_match = re.search(r'\b(19|20)\d{2}\b', name)
    if year_match:
        metadata['year'] = year_match.group()
    
    parts = re.split(r'[_\-]', name)
    
    if len(parts) >= 3 and 'year' in metadata:
        metadata['author'] = parts[0].replace('_', ' ')
        metadata['title'] = ' '.join(parts[2:]).replace('_', ' ')
    elif len(parts) >= 2:
        metadata['author'] = parts[0].replace('_', ' ')
        metadata['title'] = ' '.join(parts[1:]).replace('_', ' ')
    else:
        metadata['title'] = name.replace('_', ' ')
    
    return metadata


def convert_pdf_to_markdown(
    pdf_file: str,
    output_file: Optional[str] = None,
    *,
    extract_metadata: bool = True,
    add_front_matter: bool = True,
    custom_metadata: Optional[Dict[str, Any]] = None,
    extract_images: bool = True,
    image_output_dir: Optional[str] = None,
    force_ocr: bool = False,
    paginate_output: bool = True,
    page_range: Optional[str] = None
) -> str:
    """将 PDF 文件转换为 Markdown 格式
    
    Args:
        pdf_file: PDF 文件路径
        output_file: 输出 Markdown 文件路径（可选，默认为同名 .md 文件）
        extract_metadata: 是否从文件名提取元数据
        add_front_matter: 是否添加 front matter（YAML 元数据）
        custom_metadata: 自定义元数据字典
        extract_images: 是否提取图片到外部文件
        image_output_dir: 图片输出目录（默认为输出文件同目录下的 images 子目录）
        force_ocr: 是否强制 OCR（Marker 特有）
        paginate_output: 是否分页输出（Marker 特有）
        page_range: 指定页面范围（如 "0,5-10"，Marker 特有）
    
    Returns:
        转换后的 Markdown 内容
    """
    pdf_path = Path(pdf_file)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF 文档不存在: {pdf_file}")
    
    if pdf_path.suffix.lower() != '.pdf':
        raise ValueError(f"文件必须是 PDF 格式: {pdf_file}")
    
    # 确定输出路径
    if output_file is None:
        output_path = pdf_path.with_suffix('.md')
    else:
        output_path = Path(output_file)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 确定图片输出目录
    if image_output_dir is None:
        images_dir = output_path.parent / 'images'
    else:
        images_dir = Path(image_output_dir)
    
    images_dir.mkdir(parents=True, exist_ok=True)
    
    # 初始化 Marker 转换器
    print(f"marker - 正在初始化转换器...")
    converter = PdfConverter(
        artifact_dict=create_model_dict(),
        config={
            "output_format": "markdown",
            "force_ocr": force_ocr,
            "paginate_output": paginate_output,
            "page_range": page_range
        }
    )
    
    print(f"marker - 正在转换: {pdf_path.name}")
    
    try:
        # 执行转换
        rendered = converter(str(pdf_path))
        print(f"marker - 转换完成，共 {len(rendered.metadata.get('page_stats', []))} 页")
        
        # 提取文本、文件扩展名和图片
        text, file_ext, images = text_from_rendered(rendered)
        md_text = text
        
    except Exception as e:
        print(f"marker - 转换失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
    
    # 处理图片
    saved_images = []
    if extract_images and images:
        print(f"marker - 提取图片到: {images_dir}")
        for img_name, img in images.items():
            try:
                img_path = images_dir / img_name
                img.save(img_path, "PNG")
                saved_images.append(str(img_path))
                print(f"marker - 已保存图片: {img_path}")
                
                # 更新 Markdown 中的图片路径为相对路径
                relative_path = f"images/{img_name}"
                md_text = md_text.replace(f"![]({img_name})", f"![]({relative_path})")
                
            except Exception as e:
                print(f"marker - 警告: 图片 {img_name} 保存失败: {e}")
                continue
        
        print(f"marker - 共提取 {len(saved_images)} 张图片")
    else:
        if not extract_images:
            print("marker - 图片提取已禁用")
        else:
            print("marker - 未检测到图片")
    
    # 准备元数据
    metadata = {}
    
    if extract_metadata:
        metadata.update(extract_metadata_from_filename(pdf_path.name))
    
    metadata['source_file'] = pdf_path.name
    metadata['converted_date'] = datetime.now().isoformat()
    
    # 添加页面统计信息
    page_stats = rendered.metadata.get('page_stats', [])
    if page_stats:
        metadata['total_pages'] = len(page_stats)
        metadata['total_chars'] = sum(stat.get('chars', 0) for stat in page_stats)
        metadata['total_words'] = sum(stat.get('words', 0) for stat in page_stats)
    
    # 添加转换器信息
    metadata['converter'] = 'marker'
    metadata['conversion_options'] = {
        'force_ocr': force_ocr,
        'paginate_output': paginate_output,
        'page_range': page_range
    }
    
    if saved_images:
        metadata['extracted_images'] = len(saved_images)
        metadata['image_count'] = len(saved_images)
        metadata['image_dir'] = str(images_dir.relative_to(output_path.parent))
    
    if custom_metadata:
        metadata.update(custom_metadata)
    
    # 构建 Markdown 内容
    if add_front_matter:
        content = "---\n"
        for key, value in metadata.items():
            if key == 'conversion_options':
                content += f"{key}:\n"
                for opt_key, opt_value in value.items():
                    if isinstance(opt_value, str):
                        content += f"  {opt_key}: \"{opt_value}\"\n"
                    else:
                        content += f"  {opt_key}: {opt_value}\n"
            elif isinstance(value, str):
                content += f'{key}: "{value}"\n'
            elif isinstance(value, list):
                value_str = ', '.join([f'"{v}"' if isinstance(v, str) else str(v) for v in value])
                content += f'{key}: [{value_str}]\n'
            elif isinstance(value, (int, float)):
                content += f'{key}: {value}\n'
            else:
                content += f'{key}: {value}\n'
        content += "---\n\n"
        
        if 'title' in metadata:
            content += f"# {metadata['title']}\n\n"
        
        content += "## Document Information\n\n"
        if 'author' in metadata:
            content += f"**Author**: {metadata['author']}\n"
        if 'year' in metadata:
            content += f"**Year**: {metadata['year']}\n"
        if 'student_id' in metadata:
            content += f"**Student ID**: {metadata['student_id']}\n"
        if 'major' in metadata:
            content += f"**Major**: {metadata['major']}\n"
        content += f"**Source**: {metadata['source_file']}\n"
        if 'total_pages' in metadata:
            content += f"**Pages**: {metadata['total_pages']}\n"
        if 'total_chars' in metadata:
            content += f"**Characters**: {metadata['total_chars']}\n"
        if 'total_words' in metadata:
            content += f"**Words**: {metadata['total_words']}\n"
        if 'extracted_images' in metadata:
            content += f"**Images**: {metadata['extracted_images']} extracted\n"
        content += f"**Converted**: {metadata['converted_date']}\n"
        content += "\n---\n\n"
        
        content += md_text
    else:
        content = md_text
    
    # 写入文件
    print(f"marker - 写入输出文件: {output_path}")
    output_path.write_text(content, encoding='utf-8')
    
    return content


if __name__ == "__main__":
    import sys
    
    pdf_file = "files/20210701012009-王怡入-拉格朗日中值定理在考研数学中的应用.pdf"
    
    if not Path(pdf_file).exists():
        print(f"警告: 测试文件 {pdf_file} 不存在")
        print("请将 PDF 文件放在 {pdf_file} 或修改代码中的路径")
        sys.exit(0)
    
    try:
        # 示例 1: 基本转换（包含元数据和 front matter，提取图片）
        # print("=" * 60)
        # print("示例 1: 基本转换（包含元数据和 front matter，提取图片）")
        # print("=" * 60)
        # result1 = convert_pdf_to_markdown(pdf_file)
        # print(f"\n转换结果长度: {len(result1)} 字符")
        
        # 示例 2: 指定输出文件和自定义图片目录
        print("\n" + "=" * 60)
        print("示例 2: 指定输出文件和自定义图片目录")
        print("=" * 60)
        result2 = convert_pdf_to_markdown(
            pdf_file,
            output_file="files/output_marker.md",
            image_output_dir="files/custom_images",
            force_ocr=False
        )
        print(f"\n转换结果长度: {len(result2)} 字符")
        
        # # 示例 3: 转换指定页面范围
        # print("\n" + "=" * 60)
        # print("示例 3: 转换指定页面范围（前3页）")
        # print("=" * 60)
        # result3 = convert_pdf_to_markdown(
        #     pdf_file,
        #     output_file="files/output_marker_pages.md",
        #     page_range="0-2",
        #     extract_images=True
        # )
        # print(f"\n转换结果长度: {len(result3)} 字符")
        #
        # # 示例 4: 不添加 front matter
        # print("\n" + "=" * 60)
        # print("示例 4: 不添加 front matter")
        # print("=" * 60)
        # result4 = convert_pdf_to_markdown(
        #     pdf_file,
        #     output_file="files/output_marker_plain.md",
        #     add_front_matter=False,
        #     extract_images=True
        # )
        # print(f"\n转换结果长度: {len(result4)} 字符")
        
    except FileNotFoundError as e:
        print(f"错误: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"参数错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"转换失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)