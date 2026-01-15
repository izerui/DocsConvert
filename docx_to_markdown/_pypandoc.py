from pathlib import Path
from typing import Optional, List
import pypandoc


def convert_docx_to_markdown(
    docx_file: str,
    output_file: Optional[str] = None,
    extract_media: bool = True,
    media_dir: Optional[str] = None,
    math_format: str = "tex_math_dollars",
    extra_args: Optional[List[str]] = None,
    pandoc_path: Optional[str] = None,
    filters: Optional[List[str]] = None,
    wrap_none: bool = False,
    smart: bool = True,
    standalone: bool = False,
    preserve_formatting: bool = True,
    track_changes: bool = False,
    tab_stop: int = 4,
    reference_doc: Optional[str] = None,
    include_toc: bool = True,
    include_sections: bool = True
) -> str:
    """使用 pypandoc 将 DOCX 直接转换为 Markdown

    支持以下功能：
    - 公式提取：自动将 Word 中的公式转换为 LaTeX 格式
    - 图片提取：自动提取图片并保存到指定目录
    - 格式保留：保留表格、脚注、定义列表、代码块等格式
    - 文档结构：保留标题层级、段落缩进、制表符等
    - 修订标记：可选择性保留 Word 的修订标记

    Args:
        docx_file: DOCX 文件路径
        output_file: 输出 Markdown 文件路径，默认为同名 .md 文件
        extract_media: 是否提取媒体文件（图片等）
        media_dir: 媒体文件提取目录，默认为输出目录下的 media 子目录
        math_format: 公式格式选项，可选值：
            - "tex_math_dollars": 使用 $...$ 行内公式，$$...$$ 块级公式（默认）
            - "tex_math_single_backslash": 使用 \\(...\\) 行内公式，\\[...\\] 块级公式
            - "tex_math_double_backslash": 使用 \\\\...\\\\ 行内公式，\\\\[...\\\\] 块级公式
            - "raw_tex": 保持原始 TeX 格式
            - "mathjax": 使用 MathJax 兼容格式
        extra_args: 传递给 pandoc 的额外命令行参数
        pandoc_path: 自定义 pandoc 可执行文件路径
        filters: pandoc 过滤器列表
        wrap_none: 是否不自动换行（推荐论文使用）
        smart: 是否使用智能标点符号
        standalone: 是否输出完整的独立文档（包含元数据）
        preserve_formatting: 是否保留所有格式（表格、脚注、定义列表、HTML等），默认为 True
        track_changes: 是否保留 Word 文档的修订标记（如删除线、新增内容等）
        tab_stop: 制表符宽度（空格数），默认为 4，用于保留缩进
        reference_doc: 参考文档路径（如 custom-reference.docx），用于精确控制输出样式（页边距、字体、行距等）
        include_toc: 是否在转换时提取并保留目录结构
        include_sections: 是否保留章节标签和文档结构标记

    Returns:
        转换后的 Markdown 内容字符串

    Raises:
        FileNotFoundError: 当输入文件不存在时
        RuntimeError: 当 pandoc 未安装或转换失败时

    Example:
        >>> # 基本转换
        >>> md = convert_docx_to_markdown("input.docx", "output.md")
        >>> # 不提取图片，使用 LaTeX 单斜杠公式格式
        >>> md = convert_docx_to_markdown(
        ...     "input.docx",
        ...     extract_media=False,
        ...     math_format="tex_math_single_backslash"
        ... )
        >>> # 指定图片提取目录
        >>> md = convert_docx_to_markdown(
        ...     "input.docx",
        ...     media_dir="custom_media_dir"
        ... )
        >>> # 论文格式保留模式
        >>> md = convert_docx_to_markdown(
        ...     "thesis.docx",
        ...     wrap_none=True,
        ...     preserve_formatting=True,
        ...     tab_stop=4
        ... )
    """
    # 转换为 Path 对象
    docx_path = Path(docx_file)

    # 检查文件是否存在
    if not docx_path.exists():
        raise FileNotFoundError(f"Word 文档不存在: {docx_path}")

    # 确定输出路径
    if output_file is None:
        output_path = docx_path.with_suffix(".md")
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
    
    # 输出格式：markdown + 多种扩展
    to_format = "markdown"
    
    # 公式扩展
    if math_format:
        to_format += f"+{math_format}"
    
    # 智能标点（将直引号转换为弯引号等）
    if smart:
        to_format += "+smart"
    
    # 格式保留扩展（论文重要）
    if preserve_formatting:
        # 表格格式
        to_format += "+pipe_tables+simple_tables+multiline_tables+grid_tables"
        # 代码块格式
        to_format += "+fenced_code_blocks+backtick_code_blocks+inline_code_attributes"
        # 列表格式
        to_format += "+definition_lists+fenced_code_blocks+task_lists"
        # 脚注
        to_format += "+footnotes"
        # 原始 HTML（保留 Word 的样式标记）
        to_format += "+raw_html"
        # 原始 TeX（保留 LaTeX 公式）
        to_format += "+raw_tex"
        # 下标上标
        to_format += "+subscript+superscript"
        # 删除线
        to_format += "+strikeout"
        # 保留行内代码属性
        to_format += "+bracketed_spans+raw_attribute"

    # 添加图片提取参数
    if extract_media:
        # 确保 media 目录存在
        media_path.mkdir(parents=True, exist_ok=True)
        args.append(f"--extract-media={media_path}")

    # 添加其他 pandoc 选项
    if wrap_none:
        args.append("--wrap=none")
    if standalone:
        args.append("--standalone")
    
    # 保留制表符和缩进（论文格式重要）
    args.append("--preserve-tabs")
    args.append(f"--tab-stop={tab_stop}")
    
    # 修订标记处理
    if track_changes:
        args.append("--track-changes=all")
    else:
        args.append("--track-changes=accept")
    
    # 参考文档（用于精确样式控制）
    if reference_doc:
        ref_doc_path = Path(reference_doc)
        if not ref_doc_path.exists():
            print(f"警告: 参考文档不存在: {reference_doc}")
        else:
            args.append(f"--reference-doc={ref_doc_path}")
    
    # 目录和文档结构保留
    if include_toc:
        args.append("--toc")
        args.append("--toc-depth=6")  # 保留到6级标题
    if include_sections:
        args.append("--section-divs")  # 用 <div> 标签包裹章节，便于后续处理

    # 添加用户提供的额外参数
    if extra_args:
        args.extend(extra_args)

    try:
        # 执行转换
        markdown_content = pypandoc.convert_file(
            source_file=str(docx_path),
            to=to_format,
            format="docx",
            outputfile=str(output_path) if output_path else None,
            extra_args=args if args else None,
            filters=filters,
        )

        return markdown_content

    except RuntimeError as e:
        if "pandoc is not installed" in str(e):
            raise RuntimeError(
                "pandoc 未安装。请先安装 pandoc：\n"
                "  macOS: brew install pandoc\n"
                "  Ubuntu: sudo apt-get install pandoc\n"
                "  Windows: 从 https://pandoc.org/installing.html 下载安装"
            ) from e
        else:
            raise RuntimeError(f"DOCX 转 Markdown 失败: {e}") from e
    except Exception as e:
        raise RuntimeError(f"转换过程中发生错误: {e}") from e


def batch_convert_docx_to_markdown(
    docx_files: List[str],
    output_dir: Optional[str] = None,
    extract_media: bool = True,
    media_dir_name: str = "media",
    **kwargs
) -> List[str]:
    """批量转换多个 DOCX 文件为 Markdown

    Args:
        docx_files: DOCX 文件路径列表
        output_dir: 输出目录，默认为每个源文件的同一目录
        extract_media: 是否提取媒体文件
        media_dir_name: 媒体目录名称（当 output_dir 不为 None 时使用）
        **kwargs: 传递给 convert_docx_to_markdown 的其他参数

    Returns:
        成功转换的 Markdown 文件路径列表

    Raises:
        Exception: 当所有转换都失败时抛出异常
    """
    results = []
    errors = []

    for docx_file in docx_files:
        try:
            docx_path = Path(docx_file)

            # 确定输出文件路径
            if output_dir:
                output_path = Path(output_dir) / docx_path.with_suffix(".md").name
                # 为每个文件创建独立的 media 目录
                media_dir = Path(output_dir) / media_dir_name / docx_path.stem
            else:
                output_path = docx_path.with_suffix(".md")
                media_dir = None  # 使用默认位置

            # 执行转换
            result = convert_docx_to_markdown(
                docx_file=docx_file,
                output_file=str(output_path),
                extract_media=extract_media,
                media_dir=str(media_dir) if media_dir else None,
                **kwargs
            )

            results.append(str(output_path))

        except Exception as e:
            errors.append((docx_file, str(e)))

    # 如果有错误，打印警告
    if errors:
        print(f"\n警告: {len(errors)} 个文件转换失败:")
        for file, error in errors:
            print(f"  - {file}: {error}")

        if not results:
            raise Exception("所有文件转换失败")

    return results


# --- 使用示例 ---

if __name__ == "__main__":
    import sys

    # 示例1：单个文件转换（论文格式保留模式）
    docx_file = "files/1901180052张卓群毕业论文.docx"
    output_file = str(Path(docx_file).with_suffix(".md"))

    try:
        print("开始转换 DOCX 到 Markdown...")

        # 论文格式保留转换（推荐）
        result = convert_docx_to_markdown(
            docx_file=docx_file,
            output_file=output_file,
            extract_media=True,
            math_format="tex_math_dollars",
            preserve_formatting=True,  # 保留所有格式（表格、脚注、定义列表等）
            wrap_none=True,             # 不自动换行，保留原始行结构
            tab_stop=4,                 # 制表符宽度
            smart=True,                 # 智能标点
            track_changes=False,        # 不保留修订标记（已接受的变更）
            include_toc=True,           # 保留目录结构
            include_sections=True,      # 保留章节标签
            reference_doc=None          # 可选：指定参考文档路径以精确控制样式
        )

        print(f"✓ 转换成功!")
        print(f"  输出文件: {output_file}")
        print(f"  Markdown 长度: {len(result)} 字符")
        print(f"  格式保留: 表格、公式、列表、脚注、代码块等")

        # 示例2：批量转换（取消注释以测试）
        # docx_files = ["file1.docx", "file2.docx"]
        # results = batch_convert_docx_to_markdown(
        #     docx_files,
        #     output_dir="markdown_output",
        #     extract_media=True
        # )
        # print(f"批量转换完成，共 {len(results)} 个文件")

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