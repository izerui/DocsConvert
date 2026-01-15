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
    standalone: bool = False
) -> str:
    """使用 pypandoc 将 DOCX 直接转换为 Markdown

    支持以下功能：
    - 公式提取：自动将 Word 中的公式转换为 LaTeX 格式
    - 图片提取：自动提取图片并保存到指定目录

    Args:
        docx_file: DOCX 文件路径
        output_file: 输出 Markdown 文件路径，默认为同名 .md 文件
        extract_media: 是否提取媒体文件（图片等）
        media_dir: 媒体文件提取目录，默认为输出目录下的 media 子目录
        math_format: 公式格式选项，可选值：
            - "tex_math_dollars": 使用 $...$ 行内公式，$$...$$ 块级公式
            - "tex_math_single_backslash": 使用 \\(...\\) 行内公式，\\[...\\] 块级公式
            - "tex_math_double_backslash": 使用 \\\\...\\\\ 行内公式，\\\\[...\\\\] 块级公式
            - "raw_tex": 保持原始 TeX 格式
            - "mathjax": 使用 MathJax 兼容格式
        extra_args: 传递给 pandoc 的额外命令行参数
        pandoc_path: 自定义 pandoc 可执行文件路径
        filters: pandoc 过滤器列表
        wrap_none: 是否不自动换行
        smart: 是否使用智能标点符号
        standalone: 是否输出完整的独立文档（包含元数据）

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
        media_path = output_path.parent / "media"
    else:
        media_path = Path(media_dir)

    # 构建 extra_args 列表
    args = []

    # 输入格式：docx
    args.append("--from=docx")
    
    # 输出格式：markdown + 公式扩展 + 智能标点
    to_format = "markdown"
    if math_format:
        to_format += f"+{math_format}"
    if smart:
        to_format += "+smart"

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

    # 示例1：单个文件转换
    docx_file = "files/3-数列的极限测试.docx"
    output_file = str(Path(docx_file).with_suffix(".md"))

    try:
        print("开始转换 DOCX 到 Markdown...")

        # 基本转换
        result = convert_docx_to_markdown(
            docx_file=docx_file,
            output_file=output_file,
            extract_media=True,
            math_format="tex_math_dollars"
        )

        print(f"✓ 转换成功!")
        print(f"  输出文件: {output_file}")
        print(f"  Markdown 长度: {len(result)} 字符")

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