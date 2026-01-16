#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 到 Markdown 转换器对比测试

该脚本用于测试和对比不同转换器的性能和输出质量：
- MarkItDown: Microsoft 开源的文档转换工具
- PyMuPDF4LLM: 基于 PyMuPDF 的高性能转换器
- Docling: 基于 AI 的文档转换
- PDFPlumber: 基于 pdfplumber 和 PyMuPDF 的转换
"""

import time
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# 导入所有转换器
from _markitdown import convert_pdf_to_markdown as convert_with_markitdown
from _pymupdf4llm import convert_pdf_to_markdown as convert_with_pymupdf4llm
from _docling import convert_pdf_to_markdown as convert_with_docling
from _pdfplumber_pymupdf import convert_pdf_to_markdown as convert_with_pdfplumber
from _marker import convert_pdf_to_markdown as convert_with_marker


class ConverterTest:
    """转换器测试类"""
    
    def __init__(self, pdf_file: str, output_dir: str = "test_output"):
        self.pdf_file = Path(pdf_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 测试结果
        self.results: Dict[str, Dict] = {}
        
    def test_converter(
        self,
        name: str,
        converter_func,
        **kwargs
    ) -> Tuple[bool, float, str]:
        """
        测试单个转换器
        
        Args:
            name: 转换器名称
            converter_func: 转换函数
            **kwargs: 传递给转换器的参数
            
        Returns:
            (是否成功, 耗时(秒), 输出文件路径)
        """
        output_file = self.output_dir / f"{self.pdf_file.stem}_{name}.md"
        
        print(f"\n{'='*60}")
        print(f"测试转换器: {name}")
        print(f"{'='*60}")
        
        start_time = time.time()
        success = False
        error_msg = ""
        
        try:
            result = converter_func(
                str(self.pdf_file),
                output_file=str(output_file),
                **kwargs
            )
            success = True
            elapsed = time.time() - start_time
            
            print(f"✓ 转换成功")
            print(f"✓ 耗时: {elapsed:.2f} 秒")
            print(f"✓ 输出大小: {len(result):,} 字符")
            print(f"✓ 输出文件: {output_file}")
            
            return True, elapsed, str(output_file)
            
        except FileNotFoundError as e:
            error_msg = f"文件不存在: {e}"
            print(f"✗ 错误: {error_msg}")
            elapsed = time.time() - start_time
            
        except Exception as e:
            error_msg = f"转换失败: {str(e)}"
            print(f"✗ 错误: {error_msg}")
            elapsed = time.time() - start_time
            
            # 打印详细错误信息
            import traceback
            print("\n详细错误信息:")
            traceback.print_exc()
        
        return False, elapsed, error_msg
    
    def test_all(self):
        """测试所有转换器"""
        print("\n" + "="*60)
        print("开始对比测试")
        print("="*60)
        print(f"测试文件: {self.pdf_file}")
        print(f"输出目录: {self.output_dir}")
        print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 测试配置
        test_configs = [
            {
                "name": "markitdown",
                "func": convert_with_markitdown,
                "kwargs": {}
            },
            {
                "name": "marker",
                "func": convert_with_marker,
                "kwargs": {
                    "force_ocr": False
                }
            },
            {
                "name": "pymupdf4llm_legacy",
                "func": convert_with_pymupdf4llm,
                "kwargs": {
                    "use_layout": False,
                    "write_images": False,
                    "embed_images": False
                }
            },
            {
                "name": "pymupdf4llm_layout",
                "func": convert_with_pymupdf4llm,
                "kwargs": {
                    "use_layout": True,
                    "write_images": False,
                    "embed_images": False
                }
            },
            {
                "name": "docling",
                "func": convert_with_docling,
                "kwargs": {
                    "ocr_enabled": False
                }
            },
            {
                "name": "pdfplumber",
                "func": convert_with_pdfplumber,
                "kwargs": {}
            }
        ]
        
        # 执行测试
        for config in test_configs:
            success, elapsed, output = self.test_converter(
                config["name"],
                config["func"],
                **config["kwargs"]
            )
            
            self.results[config["name"]] = {
                "success": success,
                "elapsed": elapsed,
                "output": output,
                "config": config["kwargs"]
            }
        
        # 生成报告
        self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("测试报告")
        print("="*60)
        
        # 统计成功和失败
        success_count = sum(1 for r in self.results.values() if r["success"])
        total_count = len(self.results)
        
        print(f"\n总测试数: {total_count}")
        print(f"成功: {success_count}")
        print(f"失败: {total_count - success_count}")
        print(f"成功率: {success_count/total_count*100:.1f}%")
        
        # 按耗时排序
        sorted_results = sorted(
            self.results.items(),
            key=lambda x: x[1]["elapsed"] if x[1]["success"] else float('inf')
        )
        
        print(f"\n{'转换器':<25} {'状态':<8} {'耗时(秒)':<12} {'输出大小(字符)':<15}")
        print("-"*60)
        
        for name, result in sorted_results:
            if result["success"]:
                # 计算输出文件大小
                output_file = Path(result["output"])
                if output_file.exists():
                    size = output_file.stat().st_size
                    print(f"{name:<25} {'成功':<8} {result['elapsed']:<12.2f} {size:<15,}")
                else:
                    print(f"{name:<25} {'成功':<8} {result['elapsed']:<12.2f} {'N/A':<15}")
            else:
                print(f"{name:<25} {'失败':<8} {'N/A':<12} {'N/A':<15}")
        
        # 性能对比
        successful = {k: v for k, v in self.results.items() if v["success"]}
        if successful:
            fastest = min(successful.items(), key=lambda x: x[1]["elapsed"])
            slowest = max(successful.items(), key=lambda x: x[1]["elapsed"])
            
            print(f"\n最快转换器: {fastest[0]} ({fastest[1]['elapsed']:.2f}秒)")
            print(f"最慢转换器: {slowest[0]} ({slowest[1]['elapsed']:.2f}秒)")
            
            if slowest[1]["elapsed"] > 0:
                speedup = slowest[1]["elapsed"] / fastest[1]["elapsed"]
                print(f"性能提升: {fastest[0]} 比 {slowest[0]} 快 {speedup:.2f}x")
        
        # 保存报告到文件
        report_file = self.output_dir / "test_report.md"
        self.save_report_to_file(report_file)
        print(f"\n✓ 详细报告已保存到: {report_file}")
    
    def save_report_to_file(self, report_file: Path):
        """将报告保存到文件"""
        from datetime import datetime
        
        content = f"""# PDF 到 Markdown 转换器测试报告

## 测试信息

- **测试文件**: `{self.pdf_file}`
- **文件大小**: {self.pdf_file.stat().st_size:,} 字节
- **测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **输出目录**: `{self.output_dir}`

## 测试结果摘要

- **总测试数**: {len(self.results)}
- **成功**: {sum(1 for r in self.results.values() if r['success'])}
- **失败**: {sum(1 for r in self.results.values() if not r['success'])}
- **成功率**: {sum(1 for r in self.results.values() if r['success'])/len(self.results)*100:.1f}%

## 详细结果

| 转换器 | 状态 | 耗时(秒) | 输出文件 | 备注 |
|--------|------|----------|----------|------|
"""
        
        for name, result in sorted(self.results.items()):
            if result["success"]:
                output_file = Path(result["output"])
                if output_file.exists():
                    size = output_file.stat().st_size
                    status = "✅ 成功"
                    output_link = f"[{output_file.name}]({output_file.name})"
                    note = f"{size:,} 字节"
                else:
                    status = "✅ 成功"
                    output_link = "N/A"
                    note = "文件未找到"
            else:
                status = "❌ 失败"
                output_link = "-"
                note = result["output"][:50] if isinstance(result["output"], str) else "错误"
            
            content += f"| {name} | {status} | {result['elapsed']:.2f} | {output_link} | {note} |\n"
        
        # 性能分析
        content += "\n## 性能分析\n\n"
        successful = {k: v for k, v in self.results.items() if v["success"]}
        
        if successful:
            fastest = min(successful.items(), key=lambda x: x[1]["elapsed"])
            slowest = max(successful.items(), key=lambda x: x[1]["elapsed"])
            
            content += f"### 性能排名\n\n"
            for i, (name, result) in enumerate(sorted(
                successful.items(),
                key=lambda x: x[1]["elapsed"]
            ), 1):
                content += f"{i}. **{name}**: {result['elapsed']:.2f} 秒\n"
            
            content += f"\n- **最快**: {fastest[0]} ({fastest[1]['elapsed']:.2f}秒)\n"
            content += f"- **最慢**: {slowest[0]} ({slowest[1]['elapsed']:.2f}秒)\n"
            
            if slowest[1]["elapsed"] > 0:
                speedup = slowest[1]["elapsed"] / fastest[1]["elapsed"]
                content += f"- **性能提升**: {fastest[0]} 比 {slowest[0]} 快 {speedup:.2f}x\n"
        else:
            content += "没有成功完成的转换。\n"
        
        # 输出文件对比
        content += "\n## 输出文件对比\n\n"
        content += "所有输出文件已保存到测试目录，可以手动对比转换质量：\n\n"
        
        for name, result in sorted(self.results.items()):
            if result["success"]:
                output_file = Path(result["output"])
                if output_file.exists():
                    content += f"- [{name}]({output_file.name})\n"
        
        # 推荐建议
        content += "\n## 使用建议\n\n"
        
        if successful:
            if "markitdown" in successful and "pymupdf4llm_legacy" in successful:
                markitdown_time = successful["markitdown"]["elapsed"]
                pymupdf_time = successful["pymupdf4llm_legacy"]["elapsed"]
                
                content += "### 选择建议\n\n"
                content += "**MarkItDown** 适合以下场景：\n"
                content += "- 需要元数据管理和 front matter\n"
                content += "- 文献综述和学术笔记\n"
                content += "- 快速原型开发\n\n"
                
                content += "**PyMuPDF4LLM** 适合以下场景：\n"
                content += "- 需要高质量的表格和图片提取\n"
                content += "- 批量处理大量文件\n"
                content += "- 需要更好的布局保留\n\n"
                
                if pymupdf_time < markitdown_time:
                    speedup = markitdown_time / pymupdf_time
                    content += f"注意：PyMuPDF4LLM 比 MarkItDown 快 {speedup:.2f}x，适合大批量处理。\n\n"
        
        content += "---\n\n"
        content += f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        report_file.write_text(content, encoding='utf-8')


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="对比测试不同的 PDF 到 Markdown 转换器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 测试单个文件
  python test_converters.py input.pdf
  
  # 指定输出目录
  python test_converters.py input.pdf -o test_results
  
  # 测试多个文件
  python test_converters.py files/*.pdf
        """
    )
    
    parser.add_argument(
        'pdf_files',
        nargs='+',
        type=str,
        help='PDF 文件路径（支持多个文件）'
    )
    parser.add_argument(
        '-o', '--output-dir',
        type=str,
        default='test_output',
        help='输出目录（默认: test_output）'
    )
    
    args = parser.parse_args()
    
    # 测试每个文件
    for pdf_file in args.pdf_files:
        pdf_path = Path(pdf_file)
        
        if not pdf_path.exists():
            print(f"❌ 文件不存在: {pdf_file}")
            continue
        
        if not pdf_path.is_file() or pdf_path.suffix.lower() != '.pdf':
            print(f"❌ 不是 PDF 文件: {pdf_file}")
            continue
        
        # 为每个文件创建独立的输出目录
        file_output_dir = Path(args.output_dir) / pdf_path.stem
        
        # 运行测试
        tester = ConverterTest(str(pdf_path), str(file_output_dir))
        tester.test_all()
    
    print("\n" + "="*60)
    print("所有测试完成！")
    print("="*60)


if __name__ == "__main__":
    main()