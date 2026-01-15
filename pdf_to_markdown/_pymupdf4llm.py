"""
基于 pymupdf4llm 的 PDF 到 Markdown 转换器

支持两种模式：
1. Legacy Mode：标准模式，使用 PyMuPDF 基础功能
2. Layout Mode：激活 PyMuPDF-Layout，提供 AI 驱动的改进页面布局分析，
   支持更高的表格识别准确率和自动 OCR

安装依赖：
    pip install -U pymupdf4llm              # 基础版本
    pip install -U pymupdf4llm[ocr,layout]  # 完整版本（含 OCR 和 Layout）
"""

from pathlib import Path
from typing import Optional, List
import pymupdf4llm


def _import_layout():
    """
    尝试导入 pymupdf.layout 以激活 Layout Mode。
    
    如果安装了 pymupdf-layout，这将激活 AI 驱动的改进页面布局分析。
    如果未安装，则回退到 Legacy Mode。
    
    Returns:
        bool: Layout Mode 是否可用
    """
    try:
        import pymupdf.layout
        return True
    except ImportError:
        return False


def convert_pdf_to_markdown(
    pdf_file: str,
    output_file: Optional[str] = None,
    *,
    use_layout: bool = False,
    header: bool = True,
    footer: bool = True,
    pages: Optional[List[int]] = None,
    write_images: bool = True,
    embed_images: bool = False,
    image_path: str = "images",
    image_format: str = "png",
    filename: str = "",
    force_text: bool = True,
    page_chunks: bool = False,
    page_separators: bool = True,
    dpi: int = 150,
    ocr_dpi: int = 400,
    page_width: float = 612,
    page_height: Optional[float] = None,
    ignore_code: bool = False,
    show_progress: bool = False,
    use_ocr: bool = True,
    ocr_language: str = "chi_sim",
) -> str:
    """
    将 PDF 文件转换为 Markdown 格式
    
    Args:
        pdf_file: PDF 文件路径
        output_file: 输出 Markdown 文件路径，默认为同名 .md 文件
        use_layout: 是否使用 Layout Mode（默认 False，传统模式）
        header: 是否包含页眉
        footer: 是否包含页脚
        pages: 指定要转换的页码列表（从 0 开始），None 表示转换所有页面
        write_images: 是否提取并保存图片到文件
        embed_images: 是否将图片嵌入到 Markdown 中（base64 编码）
        image_path: 图片保存路径，默认为 PDF 文件所在目录
        image_format: 图片格式，默认为 "png"
        filename: 输出文件名（用于内部命名），通常无需设置
        force_text: 是否强制提取文本
        page_chunks: 是否按页分块返回
        page_separators: 是否在页面之间添加分隔符
        dpi: 图片提取的 DPI（点每英寸）
        ocr_dpi: OCR 的 DPI
        page_width: 页面宽度（点）
        page_height: 页面高度（点），None 表示自动检测
        ignore_code: 是否忽略代码块检测
        show_progress: 是否显示进度条
        use_ocr: 是否使用 OCR 进行文本识别
        ocr_language: OCR 使用的语言，默认为 "eng"（英语）
                   可选值："eng"(英语)、"chi_sim"(简体中文)、"chi_tra"(繁体中文)等
    
    Returns:
        转换后的 Markdown 内容
    
    Raises:
        FileNotFoundError: PDF 文件不存在
        ValueError: write_images 和 embed_images 不能同时为 True
        Exception: 转换过程中出现错误
    
    Example:
        >>> # 默认使用 Legacy Mode - 传统模式
        >>> md_text = convert_pdf_to_markdown("input.pdf")
        >>> 
        >>> # 启用 Layout Mode - 更好的转换效果（需要 pymupdf-layout）
        >>> md_text = convert_pdf_to_markdown("input.pdf", use_layout=True)
        >>> 
        >>> # 提取图片到文件
        >>> md_text = convert_pdf_to_markdown(
        ...     "input.pdf",
        ...     write_images=True,
        ...     image_path="images",
        ...     use_layout=True
        ... )
        >>> 
        >>> # 嵌入图片（base64）
        >>> md_text = convert_pdf_to_markdown(
        ...     "input.pdf",
        ...     embed_images=True,
        ...     use_layout=True
        ... )
        >>> 
        >>> # 使用 OCR 识别中文（Layout Mode）
        >>> md_text = convert_pdf_to_markdown(
        ...     "input.pdf",
        ...     use_layout=True,
        ...     use_ocr=True,
        ...     ocr_language="chi_sim"
        ... )
        >>> 
        >>> # 只转换第 0-2 页
        >>> md_text = convert_pdf_to_markdown("input.pdf", pages=[0, 1, 2])
    """
    # 检查参数冲突
    if write_images and embed_images:
        raise ValueError("Cannot both write_images and embed_images")
    
    # 转换为 Path 对象
    pdf_path = Path(pdf_file)
    
    # 检查文件是否存在
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF 文档不存在: {pdf_file}")
    
    # 尝试激活 Layout Mode
    if use_layout:
        if not _import_layout():
            print("pymupdf4llm - 警告: pymupdf-layout 未安装，回退到 Legacy Mode")
            print("pymupdf4llm - 安装命令: pip install pymupdf4llm[layout]")
        else:
            print("pymupdf4llm - Layout Mode 已激活（PyMuPDF-Layout）")
    
    
    # 准备 pymupdf4llm.to_markdown 的参数
    pymupdf_args = {
        'doc': str(pdf_path),
        'write_images': write_images,
        'embed_images': embed_images,
        'image_path': image_path,
        'image_format': image_format,
        'filename': pdf_path.name,
        'force_text': force_text,
        'page_chunks': page_chunks,
        'page_separators': page_separators,
        'dpi': dpi,
        'page_width': page_width,
        'ignore_code': ignore_code,
        'show_progress': show_progress,
    }
    
    # 只在 Layout Mode 下添加以下参数
    # pymupdf_args['header'] = header
    # pymupdf_args['footer'] = footer
    # pymupdf_args['ocr_dpi'] = ocr_dpi
    # pymupdf_args['use_ocr'] = use_ocr
    # pymupdf_args['ocr_language'] = ocr_language
    
    # 如果指定了页面，添加 pages 参数
    if pages is not None:
        pymupdf_args['pages'] = pages
    
    # 如果指定了页面高度，添加 page_height 参数
    if page_height is not None:
        pymupdf_args['page_height'] = page_height
    
    # Layout Mode 已在上面处理，这里不需要重复
    
    # 执行转换
    try:
        md_text = pymupdf4llm.to_markdown(**pymupdf_args)
        
        # 处理分块返回的情况
        if page_chunks:
            # 如果是分块模式，合并所有块的文本
            if isinstance(md_text, list):
                combined = ""
                for i, chunk in enumerate(md_text, 1):
                    if isinstance(chunk, dict) and 'text' in chunk:
                        combined += chunk['text'] + "\n\n"
                        if show_progress:
                            print(f"pymupdf4llm - 已处理第 {i} 页")
                    elif isinstance(chunk, str):
                        combined += chunk + "\n\n"
                md_text = combined
        
        print(f"pymupdf4llm - 转换完成，共 {len(md_text)} 字符")
    
    except Exception as e:
        print(f"pymupdf4llm - 转换失败: {str(e)}")
        raise
    
    # 确定输出路径
    if output_file is None:
        output_path = pdf_path.with_suffix('.md')
    else:
        output_path = Path(output_file)
    
    # 自动创建父目录
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 写入文件
    print(f"pymupdf4llm - 写入输出文件: {output_path}")
    output_path.write_text(md_text, encoding='utf-8')
    
    return md_text


# --- 使用示例 ---

if __name__ == "__main__":
    import sys
    
    # 替换为你的 PDF 文件路径
    pdf_file = "files/20210701012009-王怡入-拉格朗日中值定理在考研数学中的应用.pdf"
    output_file = str(Path(pdf_file).with_suffix(".md"))
    
    try:
        # 示例 1: Legacy Mode - 默认转换
        print("=" * 60)
        print("示例 1: Legacy Mode - 默认转换")
        print("=" * 60)
        result1 = convert_pdf_to_markdown(
            pdf_file,
            output_file=output_file,
            show_progress=True,
            image_path="files/images"
        )
        print(f"\n转换结果长度: {len(result1)} 字符")
        print(f"\n前 300 字符:\n{result1[:300]}")
        

        # # 示例 2: Layout Mode - 启用 Layout（需要 pymupdf-layout）
        # print("\n" + "=" * 60)
        # print("示例 2: Layout Mode - 启用 Layout")
        # print("=" * 60)
        # result2 = convert_pdf_to_markdown(
        #     pdf_file,
        #     output_file="output_layout.md",
        #     use_layout=True,
        #     show_progress=True
        # )
        # print(f"\n转换结果长度: {len(result2)} 字符")
        # print(f"\n前 300 字符:\n{result2[:300]}")


        # # 示例 3: 只转换第 1 页
        # print("\n" + "=" * 60)
        # print("示例 3: 只转换第 1 页")
        # print("=" * 60)
        # result3 = convert_pdf_to_markdown(
        #     pdf_file,
        #     pages=[0],
        #     show_progress=True
        # )
        # print(f"转换结果（第 1 页）长度: {len(result3)} 字符")
        # print(f"\n前 200 字符:\n{result3[:200]}")



        # # 示例 4: 提取图片到文件
        # print("\n" + "=" * 60)
        # print("示例 4: 提取图片到文件")
        # print("=" * 60)
        # try:
        #     result4 = convert_pdf_to_markdown(
        #         pdf_file,
        #         output_file="output_with_images.md",
        #         write_images=True,
        #         image_path="images",
        #         show_progress=True
        #     )
        #     print(f"\n已保存到: output_with_images.md")
        #     print(f"图片已保存到: {Path(pdf_file).parent / 'images'}")
        #     print(f"转换结果长度: {len(result4)} 字符")
        # except Exception as e:
        #     print(f"\n图片提取失败: {e}")



        # # 示例 5: 使用 OCR 识别（需要 Tesseract-OCR）
        # print("\n" + "=" * 60)
        # print("示例 5: 使用 OCR 识别（需要 Tesseract-OCR）")
        # print("=" * 60)
        # print("注意: OCR 需要 Tesseract-OCR 已安装并配置正确")

        # 取消下面的注释来测试 OCR 功能
        # try:
        #     result5 = convert_pdf_to_markdown(
        #         pdf_file,
        #         use_layout=True,
        #         use_ocr=True,
        #         ocr_language="chi_sim",
        #         show_progress=True
        #     )
        #     print(f"\nOCR 转换结果长度: {len(result5)} 字符")
        # except Exception as e:
        #     print(f"\nOCR 失败: {e}")
        #     print("安装命令: pip install pymupdf4llm[ocr,layout]")
        
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