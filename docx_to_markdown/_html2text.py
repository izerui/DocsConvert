from pathlib import Path
from typing import override, Dict, List
import html2text

from base import BaseConverter
from docx_to_html._mammoth import DOCX2HTML


class DOCX2HTML2Markdown(BaseConverter):
    """DOCX 转 Markdown 工具类
    基于 DOCX2HTML 和 html2text 实现
    DOCX2HTML 将 DOCX 转换为 HTML，html2text 将 HTML 转换为 Markdown
    """

    def __init__(self, format_html=True):
        """初始化转换器

        Args:
            format_html: 是否格式化 HTML（传递给 DOCX2HTML）
        """
        # 创建 DOCX2HTML 转换器实例
        self.docx2html = DOCX2HTML(format_html=format_html)

        # 默认 html2text 配置
        self.html2text_options = {
            'body_width': 0,  # 不自动换行
            'ignore_images': False,  # 保留图片
            'ignore_links': False,  # 保留链接
            'ignore_emphasis': False,  # 保留强调
            'code_snippets': False,  # 使用代码块
            'escape_snob': False,  # 不转义特殊字符
            'bypass_tables': False,  # 解析表格
            'google_doc': False,  # 不使用 Google Docs 模式
            'ul_item_mark': '-',  # 无序列表使用 -
            'emphasis_mark': '*',  # 强调使用 *
            'strong_mark': '**',  # 粗体使用 **
        }

        # 存储 mammoth 的转换消息（从 DOCX2HTML 获取）
        self.messages: List[Dict[str, str]] = []

    @override
    def support(self, suffix):
        """检查是否支持该文件类型

        Args:
            suffix: 文件后缀名

        Returns:
            是否支持该文件类型
        """
        return suffix.lower() == ".docx"


    def _convert_docx_to_html(self, docx_path: Path) -> str:
        """使用 DOCX2HTML 转换器将 DOCX 转换为 HTML

        Args:
            docx_path: DOCX 文件路径

        Returns:
            HTML 内容字符串
        """
        try:
            # 使用 DOCX2HTML 转换器
            html_content = self.docx2html._convert_docx_to_html(docx_path)
            
            # 获取转换消息
            self.messages = self.docx2html.messages
            
            return html_content
        except Exception as e:
            raise Exception(f"DOCX 转 HTML 失败: {e}")

    def _convert_html_to_markdown(self, html_content: str) -> str:
        """使用 html2text 将 HTML 转换为 Markdown

        Args:
            html_content: HTML 内容字符串

        Returns:
            Markdown 内容字符串
        """
        try:
            # 创建 html2text 转换器
            h = html2text.HTML2Text()

            # 设置选项
            for key, value in self.html2text_options.items():
                setattr(h, key, value)

            # 转换 HTML 到 Markdown
            markdown_content = h.handle(html_content)

            return markdown_content
        except Exception as e:
            raise Exception(f"HTML 转 Markdown 失败: {e}")

    def convert(self, docx_file: str, output_file) -> str:
        """执行 DOCX 到 Markdown 的转换

        Args:
            docx_file: DOCX 文件路径
            output_file: 输出 Markdown 文件路径，默认为同名 .md 文件

        Returns:
            转换后的 Markdown 内容
        """

        # 转换为 Path 对象
        docx_path = Path(docx_file)

        # 检查文件是否存在
        if not docx_path.exists():
            raise FileNotFoundError(f"Word 文档不存在: {docx_path}")

        # 确定输出路径
        if output_file is None:
            output_path = docx_path.with_suffix('.md')
        else:
            output_path = Path(output_file)

        # 保存当前输出路径，用于图片保存
        if self.docx2html:
            self.docx2html._current_output_path = output_path

        # 步骤1: DOCX 转 HTML
        html_content = self._convert_docx_to_html(docx_path)

        # 步骤2: HTML 转 Markdown
        markdown_content = self._convert_html_to_markdown(html_content)

        # 自动创建父目录
        output_path.parent.mkdir(parents=True, exist_ok=True)
        # 写入文件
        output_path.write_text(markdown_content, encoding='utf-8')

        return markdown_content





# --- 使用示例 ---

if __name__ == "__main__":
    import sys

    # 替换为你的 DOCX 文件路径
    docx_file = "files/1901180052张卓群毕业论文.docx"
    output_file = str(Path(docx_file).with_suffix(".md"))

    try:
        # 方式1：创建转换器并转换（默认输出到同名 .md 文件）
        converter = DOCX2HTML2Markdown()
        result = converter.convert(docx_file, output_file)
        print(f"\n转换结果长度: {len(result)} 字符")


    except FileNotFoundError as e:
        print(f"错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"转换失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)