"""
PDF 到 Markdown 转换工具包

支持多种转换引擎：
- markitdown: Microsoft 开源的文档转换工具
- pymupdf4llm: 基于 PyMuPDF 的高性能转换器
- docling: 基于 AI 的文档转换
- pdfplumber: 基于 pdfplumber 和 PyMuPDF 的转换
- marker: 高质量 PDF 转 Markdown 工具，支持表格、公式、代码块等复杂结构
- nougat: Facebook Research 开发的科学文档转换工具，擅长处理数学公式
"""

from . import _markitdown
from . import _pymupdf4llm
from . import _docling
from . import _pdfplumber_pymupdf
from . import _marker
from . import _nougat

# 导出主要转换函数
from ._markitdown import convert_pdf_to_markdown as convert_with_markitdown
from ._pymupdf4llm import convert_pdf_to_markdown as convert_with_pymupdf4llm
from ._pdfplumber_pymupdf import convert_pdf_to_markdown as convert_with_pdfplumber
from ._marker import convert_pdf_to_markdown as convert_with_marker
from ._nougat import convert_pdf_to_markdown as convert_with_nougat

__all__ = [
    'convert_with_markitdown',
    'convert_with_pymupdf4llm',
    'convert_with_pdfplumber',
    'convert_with_marker',
    'convert_with_nougat',
]