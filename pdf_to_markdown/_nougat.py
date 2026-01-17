#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于 Nougat 的 PDF 到 Markdown 转换器

安装依赖：
    pip install nougat-ocr

特性：
- 专为科学文档设计，擅长处理数学公式
- 基于 Vision Transformer (ViT) 深度学习模型
- 保留文档结构（标题、段落、列表等）
- 支持数学公式的 LaTeX 格式输出
- 高精度的文本识别
- 适合学术论文、技术文档等
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
import re
import subprocess
import sys
from datetime import datetime
import shutil


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


def check_nougat_available() -> bool:
    """检查 nougat 命令是否可用"""
    return shutil.which('nougat') is not None


def run_nougat_conversion(
    pdf_path: str,
    output_path: str,
    model: Optional[str] = None,
    batch_size: Optional[int] = None,
    no_skipping: bool = False,
    reflow: bool = False
) -> str:
    """运行 nougat 命令进行转换
    
    Args:
        pdf_path: PDF 文件路径
        output_path: 输出文件路径
        model: 使用的模型名称（如 '0.1.0-base', '0.1.0-small'）
        batch_size: 批处理大小
        no_skipping: 是否跳过已经存在的输出
        reflow: 是否使用重流模式
        
    Returns:
        转换后的 Markdown 内容
    """
    cmd = ['nougat', pdf_path, '-o', output_path]
    
    if model:
        cmd.extend(['--model', model])
    if batch_size:
        cmd.extend(['--batchsize', str(batch_size)])
    if no_skipping:
        cmd.append('--no-skipping')
    if reflow:
        cmd.append('--reflow')
    
    print(f"nougat - 执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=300  # 5分钟超时
        )
        
        # 检查输出文件
        output_file = Path(output_path)
        if output_file.exists():
            return output_file.read_text(encoding='utf-8')
        else:
            # 尝试从标准输出获取结果
            if result.stdout:
                return result.stdout
            raise RuntimeError("Nougat 转换未生成输出文件")
            
    except subprocess.TimeoutExpired:
        raise RuntimeError("Nougat 转换超时（超过5分钟）")
    except subprocess.CalledProcessError as e:
        error_msg = f"Nougat 转换失败 (退出码: {e.returncode})"
        if e.stderr:
            error_msg += f"\n错误信息: {e.stderr}"
        raise RuntimeError(error_msg)


def convert_pdf_to_markdown(
    pdf_file: str,
    output_file: Optional[str] = None,
    *,
    extract_metadata: bool = True,
    add_front_matter: bool = True,
    custom_metadata: Optional[Dict[str, Any]] = None,
    model: Optional[str] = None,
    batch_size: Optional[int] = None,
    no_skipping: bool = False,
    reflow: bool = False,
    timeout: int = 300
) -> str:
    """将 PDF 文件转换为 Markdown 格式
    
    Args:
        pdf_file: PDF 文件路径
        output_file: 输出 Markdown 文件路径（可选，默认为同名 .md 文件）
        extract_metadata: 是否从文件名提取元数据
        add_front_matter: 是否添加 front matter（YAML 元数据）
        custom_metadata: 自定义元数据字典
        model: Nougat 模型名称（如 '0.1.0-base', '0.1.0-small'）
        batch_size: 批处理大小（影响内存使用和速度）
        no_skipping: 是否跳过已经存在的输出
        reflow: 是否使用重流模式（适合移动端阅读）
        timeout: 转换超时时间（秒）
    
    Returns:
        转换后的 Markdown 内容
    """
    # 检查 nougat 是否可用
    if not check_nougat_available():
        raise RuntimeError(
            "Nougat 未安装或不在 PATH 中。\n"
            "请安装: pip install nougat-ocr\n"
            "更多信息: https://github.com/facebookresearch/nougat"
        )
    
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
    
    print(f"nougat - 正在转换: {pdf_path.name}")
    print(f"nougat - 输出文件: {output_path}")
    
    try:
        # 运行 nougat 转换
        md_text = run_nougat_conversion(
            str(pdf_path),
            str(output_path),
            model=model,
            batch_size=batch_size,
            no_skipping=no_skipping,
            reflow=reflow
        )
        
        print(f"nougat - 转换完成，共 {len(md_text)} 字符")
        
    except RuntimeError as e:
        print(f"nougat - 转换失败: {str(e)}")
        raise
    
    # 准备元数据
    metadata = {}
    
    if extract_metadata:
        metadata.update(extract_metadata_from_filename(pdf_path.name))
    
    metadata['source_file'] = pdf_path.name
    metadata['converted_date'] = datetime.now().isoformat()
    
    # 添加转换器信息
    metadata['converter'] = 'nougat'
    metadata['conversion_options'] = {
        'model': model or 'default',
        'batch_size': batch_size,
        'no_skipping': no_skipping,
        'reflow': reflow
    }
    
    if custom_metadata:
        metadata.update(custom_metadata)
    
    # 计算 Markdown 统计信息
    lines = md_text.split('\n')
    metadata['total_lines'] = len(lines)
    metadata['total_chars'] = len(md_text)
    
    # 估算公式数量（检测 $$ 包裹的内容）
    formula_count = md_text.count('$$') // 2
    metadata['estimated_formulas'] = formula_count
    
    # 构建 Markdown 内容
    if add_front_matter:
        content = "---\n"
        for key, value in metadata.items():
            if key == 'conversion_options':
                content += f"{key}:\n"
                for opt_key, opt_value in value.items():
                    if isinstance(opt_value, str):
                        content += f"  {opt_key}: \"{opt_value}\"\n"
                    elif opt_value is not None:
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
        content += f"**Source**: {metadata['source_file']}\n"
        if 'total_lines' in metadata:
            content += f"**Lines**: {metadata['total_lines']}\n"
        if 'total_chars' in metadata:
            content += f"**Characters**: {metadata['total_chars']}\n"
        if 'estimated_formulas' in metadata and metadata['estimated_formulas'] > 0:
            content += f"**Estimated Formulas**: {metadata['estimated_formulas']}\n"
        content += f"**Converted**: {metadata['converted_date']}\n"
        content += "\n---\n\n"
        
        content += md_text
    else:
        content = md_text
    
    # 写入文件
    print(f"nougat - 写入输出文件: {output_path}")
    output_path.write_text(content, encoding='utf-8')
    
    return content


if __name__ == "__main__":
    import sys
    
    pdf_file = "files/20210701012009-王怡入-拉格朗日中值定理在考研数学中的应用.pdf"
    output_file = "files/20210701012009-王怡入-拉格朗日中值定理在考研数学中的应用-nougat.md"

    if not Path(pdf_file).exists():
        print(f"警告: 测试文件 {pdf_file} 不存在")
        print("请将 PDF 文件放在 {pdf_file} 或修改代码中的路径")
        sys.exit(0)
    
    try:
        # 检查 nougat 是否可用
        if not check_nougat_available():
            print("=" * 60)
            print("Nougat 未安装！")
            print("=" * 60)
            print("\n请安装 nougat-ocr:")
            print("  pip install nougat-ocr")
            print("\n或者从源码安装:")
            print("  pip install git+https://github.com/facebookresearch/nougat")
            print("\n更多信息: https://github.com/facebookresearch/nougat")
            sys.exit(0)
        
        # 示例 1: 基本转换（包含元数据和 front matter）
        # print("=" * 60)
        # print("示例 1: 基本转换（包含元数据和 front matter）")
        # print("=" * 60)
        # result1 = convert_pdf_to_markdown(pdf_file)
        # print(f"\n转换结果长度: {len(result1)} 字符")
        
        # 示例 2: 使用 small 模型（更快，质量略低）
        print("\n" + "=" * 60)
        print("示例 2: 使用 small 模型")
        print("=" * 60)
        result2 = convert_pdf_to_markdown(
            pdf_file,
            output_file=output_file,
            model="0.1.0-small"
        )
        print(f"\n转换结果长度: {len(result2)} 字符")
        
        # 示例 3: 不添加 front matter
        # print("\n" + "=" * 60)
        # print("示例 3: 不添加 front matter")
        # print("=" * 60)
        # result3 = convert_pdf_to_markdown(
        #     pdf_file,
        #     output_file="files/output_nougat_plain.md",
        #     add_front_matter=False
        # )
        # print(f"\n转换结果长度: {len(result3)} 字符")
        
        # 示例 4: 使用重流模式
        # print("\n" + "=" * 60)
        # print("示例 4: 使用重流模式（适合移动端）")
        # print("=" * 60)
        # result4 = convert_pdf_to_markdown(
        #     pdf_file,
        #     output_file="files/output_nougat_reflow.md",
        #     reflow=True
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