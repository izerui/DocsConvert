#!/usr/bin/env python3
"""
Docling 批量处理脚本
演示如何高效地批量处理多个文档，复用模型实例

使用方法：
    # 处理单个文件
    python docling_batch_processor.py document.pdf -o output/

    # 处理整个目录
    python docling_batch_processor.py ./input_docs/ -o ./output/

    # 使用本地模型
    python docling_batch_processor.py ./docs/ -o ./output/ --model-path /path/to/models

    # 限制页数
    python docling_batch_processor.py ./docs/ -o ./output/ --max-pages 50

    # 禁用某些功能以加快速度
    python docling_batch_processor.py ./docs/ -o ./output/ --no-table-structure --no-ocr
"""

import os
import sys
from pathlib import Path
from typing import List
import logging
import argparse

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.datamodel.document import ConversionStatus

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BatchProcessor:
    """
    Docling 批量处理器

    关键优化：
    1. 只初始化一次 DocumentConverter（模型只加载一次）
    2. 使用 convert_all 方法批量处理（支持并发）
    3. 及时释放资源（节省内存）
    """

    def __init__(
        self,
        model_path: str = None,
        max_pages: int = None,
        enable_table_structure: bool = True,
        enable_ocr: bool = True,
        num_threads: int = 4,
    ):
        """
        初始化批量处理器

        Args:
            model_path: 模型路径（可选）
            max_pages: 每个文档最大页数限制
            enable_table_structure: 是否启用表格结构识别
            enable_ocr: 是否启用 OCR
            num_threads: CPU 线程数
        """
        # 设置 CPU 线程数
        os.environ["OMP_NUM_THREADS"] = str(num_threads)

        self.converter = self._create_converter(
            model_path=model_path,
            enable_table_structure=enable_table_structure,
            enable_ocr=enable_ocr,
        )
        self.max_pages = max_pages

        logger.info(f"BatchProcessor initialized with {num_threads} threads")

    def _create_converter(
        self,
        model_path: str = None,
        enable_table_structure: bool = True,
        enable_ocr: bool = True,
    ) -> DocumentConverter:
        """创建并配置 DocumentConverter（只执行一次）"""

        pipeline_options = PdfPipelineOptions(
            artifacts_path=model_path,
            do_table_structure=enable_table_structure,
            do_ocr=enable_ocr,
            generate_picture_images=False,  # 节省内存
            generate_parsed_pages=False,  # 节省内存
        )

        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

        logger.info("DocumentConverter initialized successfully (models loaded once)")
        return converter

    def process_files(
        self,
        file_paths: List[str],
        output_dir: str = None,
        continue_on_error: bool = True,
    ) -> dict:
        """
        批量处理文件（复用已加载的模型）

        Args:
            file_paths: 文件路径列表
            output_dir: 输出目录（可选）
            continue_on_error: 遇到错误是否继续

        Returns:
            处理结果统计
        """
        results = {
            "total": len(file_paths),
            "success": 0,
            "failed": 0,
            "errors": []
        }

        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

        logger.info(f"Starting batch processing of {len(file_paths)} files...")

        # 使用 convert_all 方法批量处理（模型已加载，直接使用）
        results_iter = self.converter.convert_all(
            source=file_paths,
            raises_on_error=not continue_on_error,
            max_num_pages=self.max_pages or sys.maxsize,
        )

        for result in results_iter:
            file_name = result.input.file.name

            if result.status == ConversionStatus.SUCCESS:
                results["success"] += 1
                logger.info(f"✓ Converted: {file_name}")

                # 导出为 Markdown
                doc = result.document
                markdown = doc.export_to_markdown()

                # 保存到文件
                if output_dir:
                    output_file = output_path / f"{Path(file_name).stem}.md"
                    output_file.write_text(markdown, encoding="utf-8")
                    logger.info(f"  Saved to: {output_file}")

                # 及时释放资源
                del doc
                del result

            else:
                results["failed"] += 1
                error_msg = f"{file_name}: {result.status}"
                results["errors"].append(error_msg)
                logger.error(f"✗ Failed: {error_msg}")

                if result.errors:
                    for err in result.errors:
                        logger.error(f"  Error: {err.error_message}")

        return results

    def process_directory(
        self,
        input_dir: str,
        output_dir: str = None,
        pattern: str = "*.pdf",
        **kwargs
    ) -> dict:
        """
        处理目录中的所有文件

        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            pattern: 文件匹配模式
            **kwargs: 其他参数传递给 process_files
        """
        input_path = Path(input_dir)
        file_paths = [str(f) for f in input_path.glob(pattern)]

        logger.info(f"Found {len(file_paths)} files matching '{pattern}'")

        return self.process_files(
            file_paths=file_paths,
            output_dir=output_dir,
            **kwargs
        )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="Docling Batch Processor - 高效批量处理文档",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  %(prog)s document.pdf -o output/
  %(prog)s ./input_docs/ -o ./output/
  %(prog)s ./docs/ -o ./output/ --model-path /path/to/models
  %(prog)s ./docs/ -o ./output/ --max-pages 50
  %(prog)s ./docs/ -o ./output/ --no-table-structure --no-ocr
        """
    )

    parser.add_argument(
        "input",
        help="输入文件或目录"
    )
    parser.add_argument(
        "-o", "--output",
        help="输出目录（默认：不保存文件，只打印结果）",
        default=None
    )
    parser.add_argument(
        "--model-path",
        help="模型路径（默认：使用缓存目录）",
        default=None
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        help="每个文档最大页数限制",
        default=None
    )
    parser.add_argument(
        "--no-table-structure",
        action="store_true",
        help="禁用表格结构识别（加快速度）"
    )
    parser.add_argument(
        "--no-ocr",
        action="store_true",
        help="禁用 OCR（加快速度）"
    )
    parser.add_argument(
        "--threads",
        type=int,
        help="CPU 线程数（默认：4）",
        default=4
    )
    parser.add_argument(
        "--pattern",
        help="文件匹配模式（默认：*.pdf）",
        default="*.pdf"
    )

    args = parser.parse_args()

    # 创建处理器（模型在此加载一次）
    logger.info("="*60)
    logger.info("Initializing Docling Batch Processor")
    logger.info("="*60)

    processor = BatchProcessor(
        model_path=args.model_path,
        max_pages=args.max_pages,
        enable_table_structure=not args.no_table_structure,
        enable_ocr=not args.no_ocr,
        num_threads=args.threads,
    )

    # 处理文件或目录
    input_path = Path(args.input)

    if not input_path.exists():
        logger.error(f"输入路径不存在: {args.input}")
        sys.exit(1)

    logger.info(f"Processing: {args.input}")

    if input_path.is_file():
        results = processor.process_files(
            file_paths=[str(input_path)],
            output_dir=args.output,
        )
    elif input_path.is_dir():
        results = processor.process_directory(
            input_dir=str(input_path),
            output_dir=args.output,
            pattern=args.pattern,
        )
    else:
        logger.error(f"无效的输入: {args.input}")
        sys.exit(1)

    # 打印统计
    print("\n" + "="*60)
    print("处理统计:")
    print(f"  总文件数: {results['total']}")
    print(f"  成功: {results['success']}")
    print(f"  失败: {results['failed']}")

    if results['errors']:
        print("\n错误列表:")
        for error in results['errors']:
            print(f"  - {error}")

    print("="*60)

    # 返回退出码
    sys.exit(0 if results['failed'] == 0 else 1)


if __name__ == "__main__":
    main()
