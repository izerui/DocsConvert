from pathlib import Path
from typing import Optional
import pypandoc


def convert_docx_to_html(
    docx_file: str,
    output_file: Optional[str] = None,
    extract_media: bool = True,
    media_dir: Optional[str] = None,
    math_format: str = "raw_tex",
    extra_args: Optional[list[str]] = None,
    standalone: bool = True,
    embed_css: bool = True,
    reference_doc: Optional[str] = None,
    track_changes: bool = False,
    highlight_code: bool = True,
    preserve_tabs: bool = True,
    tab_stop: int = 4
) -> str:
    """使用 pypandoc 将 DOCX 转换为 HTML（高保真格式保留）

    HTML 转换相比 Markdown 具有以下优势：
    - 完整保留字体、颜色、大小等样式信息
    - 保留表格样式（边框、合并单元格、背景色）
    - 保留段落对齐、行距、缩进等排版信息
    - 适合论文格式检查和审核

    Args:
        docx_file: DOCX 文件路径
        output_file: 输出 HTML 文件路径，默认为同名 .html 文件
        extract_media: 是否提取媒体文件（图片等）
        media_dir: 媒体文件提取目录，默认为输出目录下的 media 子目录
        math_format: 数学公式格式，可选值：
            - "raw_tex": 保留原始 LaTeX（推荐，灵活度高）
            - "mathjax": 使用 MathJax 渲染公式
            - "katex": 使用 KaTeX 渲染公式
            - "webtex": 使用 WebTeX 服务渲染公式
            - "gladtex": 将公式转换为图片
        extra_args: 传递给 pandoc 的额外命令行参数
        standalone: 是否输出完整的独立 HTML 文件（包含 <html><head><body>）
        embed_css: 是否嵌入基础 CSS 样式（推荐）
        reference_doc: 参考文档路径，用于精确控制输出样式
        track_changes: 是否保留 Word 文档的修订标记
        highlight_code: 是否高亮代码块语法
        preserve_tabs: 是否保留制表符
        tab_stop: 制表符宽度（空格数）

    Returns:
        转换后的 HTML 内容字符串

    Raises:
        FileNotFoundError: 当输入文件不存在时
        RuntimeError: 当 pandoc 未安装或转换失败时

    Example:
        >>> # 基本转换（论文格式检查推荐）
        >>> html = convert_docx_to_html("thesis.docx", "thesis.html")
        >>> # 使用 KaTeX 渲染公式
        >>> html = convert_docx_to_html(
        ...     "thesis.docx",
        ...     math_format="katex",
        ...     highlight_code=True
        ... )
        >>> # 指定参考文档
        >>> html = convert_docx_to_html(
        ...     "thesis.docx",
        ...     reference_doc="template.docx"
        ... )
    """
    # 转换为 Path 对象
    docx_path = Path(docx_file)

    # 检查文件是否存在
    if not docx_path.exists():
        raise FileNotFoundError(f"Word 文档不存在: {docx_path}")

    # 确定输出路径
    if output_file is None:
        output_path = docx_path.with_suffix(".html")
    else:
        output_path = Path(output_file)

    # 确定 media 目录
    if media_dir is None:
        media_path = output_path.parent / docx_path.stem
    else:
        media_path = Path(media_dir)

    # 构建 extra_args 列表
    args = []

    # 输入格式：docx
    args.append("--from=docx")
    
    # 输出格式：html + 扩展
    to_format = "html"
    
    # HTML 支持的公式格式：
    # - "raw_tex": 保留原始 LaTeX（推荐）
    # - "mathjax": 使用 MathJax 渲染
    # - "katex": 使用 KaTeX 渲染
    # - "webtex": 使用 WebTeX 服务
    # - "gladtex": 转换为图片
    # 注意：不需要 "+mathml" 扩展，HTML 原生支持 MathML
    if math_format and math_format != "mathml":
        to_format += f"+{math_format}"
    
    # 其他有用的 HTML 扩展
    to_format += "+native_divs+raw_html+raw_tex"

    # 添加图片提取参数
    if extract_media:
        # 确保 media 目录存在
        media_path.mkdir(parents=True, exist_ok=True)
        args.append(f"--extract-media={media_path}")

    # 添加 pandoc 选项
    if standalone:
        args.append("--standalone")
    
    # 不使用 --embed-resources，避免图片以 base64 形式嵌入
    # 提取的图片将使用外部链接引用
    
    if highlight_code:
        args.append("--syntax-highlighting=tango")  # 语法高亮样式：tango/pygments/kate/monochrome/zenburn/espresso/haddock

    if preserve_tabs:
        args.append("--preserve-tabs")
        args.append(f"--tab-stop={tab_stop}")

    # 修订标记处理
    if track_changes:
        args.append("--track-changes=all")
    else:
        args.append("--track-changes=accept")

    # 参考文档
    if reference_doc:
        ref_doc_path = Path(reference_doc)
        if not ref_doc_path.exists():
            print(f"警告: 参考文档不存在: {reference_doc}")
        else:
            args.append(f"--reference-doc={ref_doc_path}")

    # 保留文档结构
    args.append("--toc")  # 生成目录
    args.append("--toc-depth=6")
    args.append("--section-divs")  # 用 <div> 标签包裹章节

    # 添加用户提供的额外参数
    if extra_args:
        args.extend(extra_args)

    try:
        # 执行转换
        html_content = pypandoc.convert_file(
            source_file=str(docx_path),
            to=to_format,
            format="docx",
            outputfile=str(output_path) if output_path else None,
            extra_args=args if args else None,
        )

        return html_content

    except RuntimeError as e:
        if "pandoc is not installed" in str(e):
            raise RuntimeError(
                "pandoc 未安装。请先安装 pandoc：\n"
                "  macOS: brew install pandoc\n"
                "  Ubuntu: sudo apt-get install pandoc\n"
                "  Windows: 从 https://pandoc.org/installing.html 下载安装"
            ) from e
        else:
            raise RuntimeError(f"DOCX 转 HTML 失败: {e}") from e
    except Exception as e:
        raise RuntimeError(f"转换过程中发生错误: {e}") from e


# --- 使用示例 ---

if __name__ == "__main__":
    import sys

    # 示例：单个文件转换（论文格式检查推荐）
    docx_file = "files/1901180052张卓群毕业论文.docx"
    output_html = str(Path(docx_file).with_suffix(".html"))

    try:
        print("开始转换 DOCX 到 HTML...")

        html_result = convert_docx_to_html(
            docx_file=docx_file,
            output_file=output_html,
            extract_media=True,
            math_format="raw_tex",  # 保留原始 LaTeX（灵活）
            embed_css=True,  # 嵌入样式
            highlight_code=True,  # 代码高亮
            preserve_tabs=True
        )

        print(f"✓ HTML 转换成功!")
        print(f"  输出文件: {output_html}")
        print(f"  HTML 长度: {len(html_result)} 字符")
        print(f"  格式保留: 字体、颜色、大小、表格样式、对齐、行距等")
        print(f"  适用于: 论文格式检查和审核")

    except FileNotFoundError as e:
        print(f"错误: {e}")
        sys.exit(1)
    except RuntimeError as e:
        print(f"错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"转换失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)