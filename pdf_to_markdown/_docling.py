"""
基于 Docling 的 PDF 到 Markdown 转换器

Docling 是一个先进的文档处理库，支持：
- 先进的 PDF 布局分析
- 自动表格识别和转换
- 图片提取和处理
- OCR 支持
- 多种文档格式支持

安装依赖：
    pip install docling

更多信息：
    https://github.com/docling-project/docling
"""

from pathlib import Path
from typing import Optional
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling_core.types.doc import ImageRefMode


def convert_pdf_to_markdown(
    pdf_file: str,
    output_file: Optional[str] = None,
    *,
    ocr_enabled: bool = False,
    ocr_langs: Optional[list[str]] = 'zh',
    do_table_structure: bool = True,
    do_code_enrichment: bool = False,
    do_formula_enrichment: bool = True,
    generate_picture_images: bool = True,
    images_scale: float = 2.0,
    debug: bool = False,
) -> str:
    """
    将 PDF 文件转换为 Markdown 格式

    Args:
        pdf_file: PDF 文件路径（支持本地文件或 URL）
        output_file: 输出 Markdown 文件路径，默认为同名 .md 文件
        ocr_enabled: 是否启用 OCR（光学字符识别），默认 False
        ocr_langs: OCR 使用的语言列表，例如 ["en", "zh"]。默认为 ["zh"]
        do_table_structure: 是否启用表格结构识别，默认 True
        do_code_enrichment: 是否启用代码富集（识别代码块），默认 False
        do_formula_enrichment: 是否启用公式富集（识别数学公式），默认 True
        generate_picture_images: 是否生成图片，默认 True
        images_scale: 图片缩放比例，默认 2.0
        debug: 是否开启调试模式，输出详细信息

    Returns:
        转换后的 Markdown 内容

    Raises:
        FileNotFoundError: PDF 文件不存在（仅对本地文件）
        Exception: 转换过程中出现错误

    Example:
        >>> # 基本转换
        >>> md_text = convert_pdf_to_markdown("input.pdf")
        >>> 
        >>> # 启用 OCR 识别中英文
        >>> md_text = convert_pdf_to_markdown(
        ...     "input.pdf",
        ...     ocr_enabled=True,
        ...     ocr_langs=["en", "zh"]
        ... )
        >>> 
        >>> # 启用表格结构和代码识别
        >>> md_text = convert_pdf_to_markdown(
        ...     "input.pdf",
        ...     do_table_structure=True,
        ...     do_code_enrichment=True
        ... )
        >>> 
        >>> # 从 URL 转换
        >>> md_text = convert_pdf_to_markdown(
        ...     "https://arxiv.org/pdf/2408.09869",
        ...     output_file="output.md"
        ... )
    """
    # 转换为 Path 对象
    pdf_path = Path(pdf_file)

    # 检查文件是否存在（仅对本地文件）
    if not pdf_file.startswith(('http://', 'https://')):
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF 文档不存在: {pdf_file}")

    # 配置管道选项
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = ocr_enabled
    pipeline_options.do_table_structure = do_table_structure
    pipeline_options.do_code_enrichment = do_code_enrichment
    pipeline_options.do_formula_enrichment = do_formula_enrichment
    pipeline_options.generate_picture_images = generate_picture_images
    pipeline_options.images_scale = images_scale

    # 设置 OCR 语言
    if ocr_enabled:
        if ocr_langs is None:
            ocr_langs = ["en"]  # 默认支持英文
        if hasattr(pipeline_options, 'ocr_options'):
            # 使用 EasyOCR 风格的语言设置
            from docling.datamodel.pipeline_options import EasyOcrOptions
            pipeline_options.ocr_options = EasyOcrOptions(lang=ocr_langs)

    if debug:
        print(f"docling - 开始转换: {pdf_file}")
        print(f"docling - OCR: {'启用' if ocr_enabled else '禁用'}")
        if ocr_enabled:
            print(f"docling - OCR 语言: {ocr_langs}")
        print(f"docling - 表格结构: {'启用' if do_table_structure else '禁用'}")
        print(f"docling - 代码富集: {'启用' if do_code_enrichment else '禁用'}")
        print(f"docling - 公式富集: {'启用' if do_formula_enrichment else '禁用'}")
        print(f"docling - 生成图片: {'启用' if generate_picture_images else '禁用'}")

    # 创建文档转换器
    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    # 确定输出路径
    if output_file is None:
        # 如果是 URL，从 URL 中提取文件名
        if pdf_file.startswith(('http://', 'https://')):
            from urllib.parse import urlparse
            parsed = urlparse(pdf_file)
            filename = Path(parsed.path).name
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            output_path = Path("output") / Path(filename).with_suffix('.md')
        else:
            output_path = pdf_path.with_suffix('.md')
    else:
        output_path = Path(output_file)

    # 自动创建父目录
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # 执行转换
        print(f"docling - 正在处理 PDF 文档...")
        result = converter.convert(pdf_file)
        
        # 保存为 Markdown 文件（包含图片）
        print(f"docling - 保存 Markdown 文件和图片到: {output_path.parent}")
        if generate_picture_images:
            # REFERENCED 模式：图片保存为独立文件，Markdown 中使用相对路径引用
            result.document.save_as_markdown(
                output_path,
                image_mode=ImageRefMode.REFERENCED
            )
        else:
            # 不生成图片时使用普通保存
            result.document.save_as_markdown(
                output_path,
                image_mode=ImageRefMode.PLACEHOLDER
            )
        
        # 读取生成的 Markdown 内容用于返回
        md_text = output_path.read_text(encoding='utf-8')
        print(f"docling - 转换完成，共 {len(md_text)} 字符")

    except Exception as e:
        print(f"docling - 转换失败: {str(e)}")
        raise

    return md_text


# --- 使用示例 ---

if __name__ == "__main__":
    import sys

    # 替换为你的 PDF 文件路径
    pdf_file = "files/20210701012009-王怡入-拉格朗日中值定理在考研数学中的应用.pdf"
    output_file = str(Path(pdf_file).with_suffix(".md"))

    try:
        # 示例 1: 基本转换
        print("=" * 60)
        print("示例 1: 基本转换")
        print("=" * 60)
        result1 = convert_pdf_to_markdown(
            pdf_file,
            output_file=output_file
        )
        print(f"\n转换结果长度: {len(result1)} 字符")
        print(f"\n前 300 字符:\n{result1[:300]}")

        # # 示例 2: 启用 OCR
        # print("\n" + "=" * 60)
        # print("示例 2: 启用 OCR（识别中英文）")
        # print("=" * 60)
        # result2 = convert_pdf_to_markdown(
        #     pdf_file,
        #     output_file="output_ocr.md",
        #     ocr_enabled=True,
        #     ocr_langs=["en", "zh"]
        # )
        # print(f"\nOCR 转换结果长度: {len(result2)} 字符")

        # # 示例 3: 启用表格结构和代码识别
        # print("\n" + "=" * 60)
        # print("示例 3: 启用表格结构和代码识别")
        # print("=" * 60)
        # result3 = convert_pdf_to_markdown(
        #     pdf_file,
        #     output_file="output_table_code.md",
        #     do_table_structure=True,
        #     do_code_enrichment=True
        # )
        # print(f"\n转换结果长度: {len(result3)} 字符")

        # # 示例 4: 从 URL 转换
        # print("\n" + "=" * 60)
        # print("示例 4: 从 URL 转换")
        # print("=" * 60)
        # url = "https://arxiv.org/pdf/2408.09869"
        # result4 = convert_pdf_to_markdown(
        #     url,
        #     output_file="output_url.md"
        # )
        # print(f"\nURL 转换结果长度: {len(result4)} 字符")

        # # 示例 5: 生成图片
        # print("\n" + "=" * 60)
        # print("示例 5: 生成图片")
        # print("=" * 60)
        # result5 = convert_pdf_to_markdown(
        #     pdf_file,
        #     output_file="output_images.md",
        #     generate_picture_images=True,
        #     images_scale=2.0
        # )
        # print(f"\n转换结果长度: {len(result5)} 字符")

        # # 示例 6: 启用公式富集
        # print("\n" + "=" * 60)
        # print("示例 6: 启用公式富集")
        # print("=" * 60)
        # result6 = convert_pdf_to_markdown(
        #     pdf_file,
        #     output_file="output_formula.md",
        #     do_formula_enrichment=True
        # )
        # print(f"\n转换结果长度: {len(result6)} 字符")

        # # 示例 7: 调试模式
        # print("\n" + "=" * 60)
        # print("示例 7: 调试模式")
        # print("=" * 60)
        # result7 = convert_pdf_to_markdown(
        #     pdf_file,
        #     output_file="output_debug.md",
        #     debug=True
        # )

    except FileNotFoundError as e:
        print(f"错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"转换失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)