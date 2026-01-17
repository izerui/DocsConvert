#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于 Microsoft MarkItDown 的 PDF 到 Markdown 转换器

MarkItDown 是微软开源的文档转换工具，支持多种格式（PDF、Word、PowerPoint、Excel 等）
转换为 Markdown 格式，同时保留文档的结构和格式信息。

安装依赖：
    pip install markitdown

特性：
- 自动提取文档标题
- 保留表格、列表、代码块等结构
- 支持图片提取（可选择保存或嵌入）
- 简单易用的 API
"""

from pathlib import Path
from typing import Optional, Dict, Any
from markitdown import MarkItDown


def extract_metadata_from_filename(filename: str) -> Dict[str, str]:
    """
    从文件名提取元数据
    
    支持模式：Author_Year_Title.pdf
    
    Args:
        filename: 文件名
    
    Returns:
        包含元数据的字典
    
    Example:
        >>> extract_metadata_from_filename("Smith_2023_Machine_Learning.pdf")
        {'year': '2023', 'author': 'Smith', 'title': 'Machine Learning'}
    """
    metadata = {}
    
    # 移除扩展名
    name = Path(filename).stem
    
    # 尝试提取年份
    import re
    year_match = re.search(r'\b(19|20)\d{2}\b', name)
    if year_match:
        metadata['year'] = year_match.group()
    
    # 按下划线或短横线分割
    parts = re.split(r'[_\-]', name)
    if len(parts) >= 2:
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
) -> str:
    """
    将 PDF 文件转换为 Markdown 格式
    
    使用 Microsoft MarkItDown 库进行转换，支持自动提取文档标题、保留文档结构，
    并可选择性添加元数据和 front matter。
    
    Args:
        pdf_file: PDF 文件路径
        output_file: 输出 Markdown 文件路径，默认为同名 .md 文件
        extract_metadata: 是否从文件名提取元数据（作者、年份等）
        add_front_matter: 是否添加 YAML front matter（包含文档元数据）
        custom_metadata: 自定义元数据字典，会与提取的元数据合并
    
    Returns:
        转换后的 Markdown 内容
    
    Raises:
        FileNotFoundError: PDF 文件不存在
        Exception: 转换过程中出现错误
    
    Example:
        >>> # 基本转换
        >>> md_text = convert_pdf_to_markdown("input.pdf")
        >>> 
        >>> # 不提取元数据，不添加 front matter
        >>> md_text = convert_pdf_to_markdown(
        ...     "input.pdf",
        ...     output_file="simple.md",
        ...     extract_metadata=False,
        ...     add_front_matter=False
        ... )
        >>> 
        >>> # 添加自定义元数据
        >>> md_text = convert_pdf_to_markdown(
        ...     "input.pdf",
        ...     custom_metadata={
        ...         "tags": ["research", "AI"],
        ...         "category": "paper"
        ...     }
        ... )
    """
    # 转换为 Path 对象
    pdf_path = Path(pdf_file)
    
    # 检查文件是否存在
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF 文档不存在: {pdf_file}")
    
    # 创建 MarkItDown 实例
    md_converter = MarkItDown()
    
    print(f"markitdown - 正在转换: {pdf_path.name}")
    
    # 执行转换
    try:
        result = md_converter.convert(str(pdf_path))
        md_text = result.text_content
        print(f"markitdown - 转换完成，共 {len(md_text)} 字符")
    except Exception as e:
        print(f"markitdown - 转换失败: {str(e)}")
        raise
    
    # 准备元数据
    metadata = {}
    
    # 从文件名提取元数据
    if extract_metadata:
        metadata.update(extract_metadata_from_filename(pdf_path.name))
    
    # 添加文件信息
    metadata['source_file'] = pdf_path.name
    
    # 如果转换结果包含标题，优先使用
    if result.title and ('title' not in metadata or not metadata['title'].strip()):
        metadata['title'] = result.title
    
    # 合并自定义元数据
    if custom_metadata:
        metadata.update(custom_metadata)
    
    # 构建 Markdown 内容
    if add_front_matter:
        # 创建 YAML front matter
        content = "---\n"
        for key, value in metadata.items():
            if isinstance(value, str):
                content += f'{key}: "{value}"\n'
            elif isinstance(value, list):
                # 处理列表类型
                value_str = ', '.join([f'"{v}"' if isinstance(v, str) else str(v) for v in value])
                content += f'{key}: [{value_str}]\n'
            else:
                content += f'{key}: {value}\n'
        content += "---\n\n"
        
        # 添加标题
        if 'title' in metadata:
            content += f"# {metadata['title']}\n\n"
        
        # 添加文档信息部分
        content += "## Document Information\n\n"
        if 'author' in metadata:
            content += f"**Author**: {metadata['author']}\n"
        if 'year' in metadata:
            content += f"**Year**: {metadata['year']}\n"
        content += f"**Source**: {metadata['source_file']}\n"
        content += "\n---\n\n"
        
        # 添加转换后的内容
        content += md_text
    else:
        # 不添加 front matter，直接返回转换内容
        content = md_text
    
    # 确定输出路径
    if output_file is None:
        output_path = pdf_path.with_suffix('.md')
    else:
        output_path = Path(output_file)
    
    # 自动创建父目录
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 写入文件
    print(f"markitdown - 写入输出文件: {output_path}")
    output_path.write_text(content, encoding='utf-8')
    
    return content


# --- 使用示例 ---

if __name__ == "__main__":
    import sys
    
    # 替换为你的 PDF 文件路径
    pdf_file = "files/20210701012009-王怡入-拉格朗日中值定理在考研数学中的应用.pdf"
    output_file = "files/20210701012009-王怡入-拉格朗日中值定理在考研数学中的应用-markitdown.md"
    
    try:
        # 示例 1: 基本转换（包含元数据和 front matter）
        # print("=" * 60)
        # print("示例 1: 基本转换（包含元数据和 front matter）")
        # print("=" * 60)
        # result1 = convert_pdf_to_markdown(
        #     pdf_file,
        #     output_file=output_file,
        # )
        # print(f"\n转换结果长度: {len(result1)} 字符")
        # print(f"\n前 500 字符:\n{result1[:500]}")
        
        # 示例 2: 简洁模式（不添加 front matter）
        print("\n" + "=" * 60)
        print("示例 2: 简洁模式（不添加 front matter）")
        print("=" * 60)
        result2 = convert_pdf_to_markdown(
            pdf_file,
            output_file=output_file,
            add_front_matter=False,
            extract_metadata=True
        )
        print(f"\n转换结果长度: {len(result2)} 字符")
        print(f"\n前 300 字符:\n{result2[:300]}")
        
        # # 示例 3: 添加自定义元数据
        # print("\n" + "=" * 60)
        # print("示例 3: 添加自定义元数据")
        # print("=" * 60)
        # result3 = convert_pdf_to_markdown(
        #     pdf_file,
        #     output_file="files/output_custom.md",
        #     custom_metadata={
        #         "tags": ["mathematics", "calculus", "考试"],
        #         "category": "学术论文",
        #         "difficulty": "中级",
        #         "language": "中文"
        #     }
        # )
        # print(f"\n转换结果长度: {len(result3)} 字符")
        # print(f"\n前 600 字符:\n{result3[:600]}")
        
    except FileNotFoundError as e:
        print(f"错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"转换失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)