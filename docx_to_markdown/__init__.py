"""
DOCX 到 Markdown 转换工具包

支持多种转换引擎：
- markitdown: Microsoft 开源的文档转换工具
- pypandoc: 基于 Pandoc 的转换器（支持公式、表格、图片）
- html2text: 通过 HTML 中间格式转换
"""

from . import _markitdown
from . import _pypandoc
from . import _html2text

# 导出主要转换函数
from ._markitdown import convert_docx_to_markdown as convert_with_markitdown
from ._pypandoc import convert_docx_to_markdown as convert_with_pypandoc
from ._html2text import convert_docx_to_markdown as convert_with_html2text

__all__ = [
    'convert_with_markitdown',
    'convert_with_pypandoc',
    'convert_with_html2text',
]