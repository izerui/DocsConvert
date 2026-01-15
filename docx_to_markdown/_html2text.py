from pathlib import Path
from typing import Optional
import html2text


from docx_to_html._mammoth import convert_docx_to_html


def convert_html_to_markdown(
    html_content: str,
    output_file: str,
    body_width: int = 0,
    ignore_images: bool = False,
    ignore_links: bool = False,
    ignore_emphasis: bool = False,
    code_snippets: bool = False,
    escape_snob: bool = False,
    bypass_tables: bool = False,
    google_doc: bool = False,
    ul_item_mark: str = '-',
    emphasis_mark: str = '*',
    strong_mark: str = '**'
) -> str:
    """使用 html2text 将 HTML 转换为 Markdown

    Args:
        html_content: HTML 内容字符串
        output_file: 输出 Markdown 文件路径（必填）
        body_width: 自动换行宽度，0 表示不自动换行
        ignore_images: 是否忽略图片（不转换为 Markdown）
        ignore_links: 是否忽略链接
        ignore_emphasis: 是否忽略强调
        code_snippets: 是否使用代码块
        escape_snob: 是否转义特殊字符
        bypass_tables: 是否解析表格
        google_doc: 是否使用 Google Docs 模式
        ul_item_mark: 无序列表标记
        emphasis_mark: 强调标记
        strong_mark: 粗体标记

    Returns:
        Markdown 内容字符串
    """
    try:
        # 创建 html2text 转换器
        h = html2text.HTML2Text()

        # 设置选项
        h.body_width = body_width
        h.ignore_images = ignore_images
        h.ignore_links = ignore_links
        h.ignore_emphasis = ignore_emphasis
        h.code_snippets = code_snippets
        h.escape_snob = escape_snob
        h.bypass_tables = bypass_tables
        h.google_doc = google_doc
        h.ul_item_mark = ul_item_mark
        h.emphasis_mark = emphasis_mark
        h.strong_mark = strong_mark

        # 转换 HTML 到 Markdown
        markdown_content = h.handle(html_content)

        # 确定输出路径
        output_path = Path(output_file)
        
        # 自动创建父目录
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 写入文件
        output_path.write_text(markdown_content, encoding='utf-8')

        return markdown_content
    except Exception as e:
        raise Exception(f"HTML 转 Markdown 失败: {e}")


def convert_docx_to_markdown(
    docx_file: str,
    output_file: str,
    format_html: bool = True,
    save_images: bool = True,
    ignore_empty_paragraphs: bool = False,
    external_file_access: bool = True,
    style_map: Optional[str] = None,
    # html2text 选项
    body_width: int = 0,
    ignore_images: bool = False,
    ignore_links: bool = False,
    ignore_emphasis: bool = False,
    code_snippets: bool = False,
    escape_snob: bool = False,
    bypass_tables: bool = False,
    google_doc: bool = False,
    ul_item_mark: str = '-',
    emphasis_mark: str = '*',
    strong_mark: str = '**'
) -> str:
    """执行 DOCX 到 Markdown 的转换

    Args:
        docx_file: DOCX 文件路径
        output_file: 输出 Markdown 文件路径（必填）
        format_html: 是否格式化 HTML（传递给 mammoth）
        save_images: 是否保存图片到 images 目录（mammoth 参数）
        ignore_empty_paragraphs: 是否忽略空段落
        external_file_access: 是否允许外部文件访问
        style_map: mammoth 自定义样式映射字符串
        # html2text 选项
        body_width: 自动换行宽度，0 表示不自动换行
        ignore_images: 是否忽略图片转换到 Markdown（html2text 参数）
        ignore_links: 是否忽略链接
        ignore_emphasis: 是否忽略强调
        code_snippets: 是否使用代码块
        escape_snob: 是否转义特殊字符
        bypass_tables: 是否解析表格
        google_doc: 是否使用 Google Docs 模式
        ul_item_mark: 无序列表标记
        emphasis_mark: 强调标记
        strong_mark: 粗体标记

    Returns:
        转换后的 Markdown 内容
    """
    # 转换为 Path 对象
    docx_path = Path(docx_file)
    output_path = Path(output_file)

    # 检查文件是否存在
    if not docx_path.exists():
        raise FileNotFoundError(f"Word 文档不存在: {docx_path}")

    # 步骤1: DOCX 转 HTML（使用 mammoth，保存到 HTML 文件并自动删除）
    html_temp_file = output_path.with_suffix('.html')
    html_content = convert_docx_to_html(
        docx_file=docx_file,
        output_file=str(html_temp_file),
        format_html=format_html,
        save_images=save_images,
        ignore_empty_paragraphs=ignore_empty_paragraphs,
        external_file_access=external_file_access,
        style_map=style_map,
        delete_html=True  # 转换完成后自动删除 HTML 文件，保留 images 目录
    )

    # 步骤2: HTML 转 Markdown
    markdown_content = convert_html_to_markdown(
        html_content=html_content,
        output_file=output_file,
        body_width=body_width,
        ignore_images=ignore_images,
        ignore_links=ignore_links,
        ignore_emphasis=ignore_emphasis,
        code_snippets=code_snippets,
        escape_snob=escape_snob,
        bypass_tables=bypass_tables,
        google_doc=google_doc,
        ul_item_mark=ul_item_mark,
        emphasis_mark=emphasis_mark,
        strong_mark=strong_mark
    )

    return markdown_content


# --- 使用示例 ---

if __name__ == "__main__":
    import sys

    # 转换 DOCX 文件
    docx_file = "files/1901180052张卓群毕业论文.docx"
    output_file = str(Path(docx_file).with_suffix(".md"))

    try:
        # 转换 DOCX 到 Markdown
        result = convert_docx_to_markdown(docx_file, output_file)
        print(f"DOCX 转换结果长度: {len(result)} 字符")
    except FileNotFoundError as e:
        print(f"错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"DOCX 转换失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)