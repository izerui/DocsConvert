#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于 Microsoft MarkItDown 的 DOCX 到 Markdown 转换器

安装依赖：
    pip install markitdown

特性：
- 自动提取文档标题
- 保留表格、列表、代码块等结构
- 支持图片提取（可选择保存为独立文件或嵌入为 base64）
- 简单易用的 API
- 完美支持 DOCX 格式
"""

from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from markitdown import MarkItDown
import re
import base64
from datetime import datetime


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


def extract_and_save_base64_images(
    markdown_content: str,
    docx_filename: str,
    image_output_dir: Path
) -> Tuple[str, List[str]]:
    """从 Markdown 内容中提取并保存 base64 编码的图片"""
    image_output_dir.mkdir(parents=True, exist_ok=True)
    
    # 查找所有 data:image/xxx;base64, 的位置
    pattern = r'data:image/([^;]+);base64,'
    positions = []
    pos = 0
    while True:
        pos = markdown_content.find(pattern, pos)
        if pos == -1:
            break
        positions.append(pos + len(pattern))  # 保存 ;base64, 后面的位置
        pos += len(pattern)
    
    if not positions:
        print("markitdown - 未检测到图片")
        return markdown_content, []
    
    docx_stem = Path(docx_filename).stem
    saved_images = []
    updated_content = markdown_content
    image_count = 0
    
    # 从后往前处理，避免位置偏移
    for data_start_pos in reversed(positions):
        try:
            # 找到对应的 )，忽略换行符
            # 从 data_start_pos 开始搜索，跳过 ';base64,' (8字符)
            search_start = data_start_pos + 8
            
            # 搜索 )，忽略空白
            paren_pos = len(markdown_content)
            for i, char in enumerate(markdown_content[search_start:], search_start):
                if char == ')':
                    paren_pos = search_start + i
                    break
            
            if paren_pos == len(markdown_content):
                continue  # 未找到 )
            
            # 提取图片类型
            image_type = markdown_content[data_start_pos + 11:data_start_pos + 11]  # 跳过 'data:image/'
            
            # base64 数据从 ';base64,' 后面开始，到 ')' 之前
            base64_data = markdown_content[search_start:paren_pos]
            
            # 移除所有空白（包括换行）用于解码
            base64_data_clean = ''.join(base64_data.split())
            
            # 解码
            image_bytes = base64.b64decode(base64_data_clean)
            
            # 保存图片
            image_count += 1
            image_filename = f"{docx_stem}_image{image_count:03d}.{image_type}"
            image_path = image_output_dir / image_filename
            image_path.write_bytes(image_bytes)
            
            print(f"markitdown - 已保存图片: {image_path}")
            saved_images.append(str(image_path))
            
            # 替换：从 data:image/ 到 ) 的整个内容
            old_full = markdown_content[data_start_pos:paren_pos + 1]
            relative_path = f"images/{image_filename}"
            new_link = f"({relative_path})"
            
            updated_content = updated_content.replace(old_full, new_link, 1)
            
        except Exception as e:
            print(f"markitdown - 警告: 图片 {image_count} 保存失败: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"markitdown - 共提取 {len(saved_images)} 张图片")
    return updated_content, saved_images


def convert_docx_to_markdown(
    docx_file: str,
    output_file: Optional[str] = None,
    *,
    extract_metadata: bool = True,
    add_front_matter: bool = True,
    custom_metadata: Optional[Dict[str, Any]] = None,
    extract_images: bool = True,
    image_output_dir: Optional[str] = None,
    use_relative_image_paths: bool = True
) -> str:
    """将 DOCX 文件转换为 Markdown 格式"""
    docx_path = Path(docx_file)
    
    if not docx_path.exists():
        raise FileNotFoundError(f"DOCX 文档不存在: {docx_file}")
    
    if not docx_path.suffix.lower() == '.docx':
        raise ValueError(f"文件必须是 DOCX 格式: {docx_file}")
    
    md_converter = MarkItDown()
    
    print(f"markitdown - 正在转换: {docx_path.name}")
    
    try:
        result = md_converter.convert(str(docx_path))
        md_text = result.text_content
        print(f"markitdown - 转换完成，共 {len(md_text)} 字符")
    except Exception as e:
        print(f"markitdown - 转换失败: {str(e)}")
        raise
    
    # 提取并保存图片（如果需要）
    extracted_images = []
    if extract_images:
        if image_output_dir is None:
            if output_file is None:
                output_path = docx_path.with_suffix('.md')
            else:
                output_path = Path(output_file)
            images_dir = output_path.parent / 'images'
        else:
            images_dir = Path(image_output_dir)
        
        print(f"markitdown - 提取图片到: {images_dir}")
        md_text, extracted_images = extract_and_save_base64_images(
            md_text,
            docx_path.name,
            images_dir
        )
    
    # 准备元数据
    metadata = {}
    
    if extract_metadata:
        metadata.update(extract_metadata_from_filename(docx_path.name))
    
    metadata['source_file'] = docx_path.name
    metadata['converted_date'] = datetime.now().isoformat()
    
    if result.title and ('title' not in metadata or not metadata['title'].strip()):
        metadata['title'] = result.title
    
    if extracted_images:
        metadata['extracted_images'] = len(extracted_images)
        metadata['image_count'] = len(extracted_images)
    
    if custom_metadata:
        metadata.update(custom_metadata)
    
    # 构建 Markdown 内容
    if add_front_matter:
        content = "---\n"
        for key, value in metadata.items():
            if isinstance(value, str):
                content += f'{key}: "{value}"\n'
            elif isinstance(value, list):
                value_str = ', '.join([f'"{v}"' if isinstance(v, str) else str(v) for v in value])
                content += f'{key}: [{value_str}]\n'
            elif isinstance(value, int):
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
        if 'extracted_images' in metadata:
            content += f"**Images**: {metadata['extracted_images']} extracted\n"
        content += f"**Converted**: {metadata['converted_date']}\n"
        content += "\n---\n\n"
        
        content += md_text
    else:
        content = md_text
    
    if output_file is None:
        output_path = docx_path.with_suffix('.md')
    else:
        output_path = Path(output_file)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"markitdown - 写入输出文件: {output_path}")
    output_path.write_text(content, encoding='utf-8')
    
    return content


if __name__ == "__main__":
    import sys
    
    docx_file = "files/2023070101ZB203.docx"
    
    if not Path(docx_file).exists():
        print(f"警告: 测试文件 {docx_file} 不存在")
        sys.exit(0)
    
    try:
        # 示例 1: 基本转换（包含元数据和 front matter，图片嵌入为 base64）
        print("=" * 60)
        print("示例 1: 基本转换（包含元数据和 front matter，图片嵌入为 base64）")
        print("=" * 60)
        result1 = convert_docx_to_markdown(docx_file)
        print(f"\n转换结果长度: {len(result1)} 字符")
        
        # 示例 2: 提取图片到独立文件
        print("\n" + "=" * 60)
        print("示例 2: 提取图片到独立文件")
        print("=" * 60)
        result2 = convert_docx_to_markdown(
            docx_file,
            output_file="files/output_with_images.md",
            extract_images=True
        )
        print(f"\n转换结果长度: {len(result2)} 字符")
        
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
