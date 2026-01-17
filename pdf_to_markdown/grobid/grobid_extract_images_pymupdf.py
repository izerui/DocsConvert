#!/usr/bin/env python3
"""
GROBID 图片提取工具（使用新版 pymupdf）
从 PDF 中提取图片、表格，并使用 GROBID 获取图片说明
"""

import os
import json
import requests
from pathlib import Path
import pymupdf  # 新版 PyMuPDF (不是 fitz)
from bs4 import BeautifulSoup
from typing import List, Dict
import argparse


class GrobidImageExtractor:
    """使用 GROBID 提取 PDF 中的图片和说明"""
    
    def __init__(self, grobid_url: str = "http://localhost:8070"):
        self.grobid_url = grobid_url
        
    def process_pdf(self, pdf_path: str, output_dir: str = "./output") -> Dict:
        """
        处理 PDF 文件，提取图片和相关信息
        
        Args:
            pdf_path: PDF 文件路径
            output_dir: 输出目录
            
        Returns:
            包含图片信息和元数据的字典
        """
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # 1. 使用 GROBID 获取 TEI XML（包含图片坐标和说明）
        print(f"📄 正在使用 GROBID 处理 {pdf_path}...")
        tei_xml = self._get_tei_with_coordinates(pdf_path)
        
        # 2. 解析 TEI XML，提取图片信息
        print("🔍 正在解析 TEI XML...")
        figures_info = self._parse_figures_from_tei(tei_xml)
        
        # 3. 从 PDF 中提取图片
        print(f"🖼️  正在提取图片...")
        extracted_images = self._extract_images_from_pdf(
            pdf_path, 
            figures_info, 
            output_path / "images"
        )
        
        # 4. 保存元数据
        metadata = {
            "pdf_path": pdf_path,
            "pdf_name": Path(pdf_path).name,
            "total_figures": len(extracted_images),
            "figures": extracted_images
        }
        
        # 保存为 JSON
        metadata_file = output_path / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 完成！提取了 {len(extracted_images)} 个图片")
        print(f"📁 输出目录: {output_dir}")
        
        return metadata
    
    def _get_tei_with_coordinates(self, pdf_path: str) -> str:
        """使用 GROBID API 获取包含坐标的 TEI XML"""
        url = f"{self.grobid_url}/api/processFulltextDocument"
        
        with open(pdf_path, 'rb') as f:
            files = {'input': f}
            # 请求图片和表格的坐标
            data = {
                'teiCoordinates': ['figure', 'formula'],
                'segmentSentences': '0'
            }
            
            response = requests.post(url, files=files, data=data)
            
            if response.status_code == 200:
                return response.text
            else:
                raise Exception(f"GROBID API 错误: {response.status_code}")
    
    def _parse_figures_from_tei(self, tei_xml: str) -> List[Dict]:
        """从 TEI XML 中解析图片信息"""
        soup = BeautifulSoup(tei_xml, 'xml')
        figures = []
        
        # 查找所有 figure 元素
        for fig in soup.find_all('figure'):
            fig_info = {
                'id': fig.get('xml:id', ''),
                'coords': fig.get('coords', ''),
                'label': '',
                'caption': '',
                'page': None,
                'type': 'figure'
            }
            
            # 判断是表格还是图片
            if 'table' in fig_info['id'].lower():
                fig_info['type'] = 'table'
            
            # 提取坐标信息
            if fig_info['coords']:
                coords_list = fig_info['coords'].split(';')
                coords = coords_list[0]
                parts = coords.split(',')
                if len(parts) >= 2:
                    fig_info['page'] = int(parts[0])
                    fig_info['bbox'] = {
                        'x': float(parts[1]) if len(parts) > 1 else 0,
                        'y': float(parts[2]) if len(parts) > 2 else 0,
                        'width': float(parts[3]) if len(parts) > 3 else 0,
                        'height': float(parts[4]) if len(parts) > 4 else 0
                    }
            
            # 提取标签
            label = fig.find('label')
            if label:
                fig_info['label'] = label.get_text(strip=True)
            
            # 提取说明文字
            caption = fig.find('figDesc')
            if caption:
                fig_info['caption'] = caption.get_text(strip=True)
            
            # 如果没有 figDesc，尝试获取其他文本内容
            if not fig_info['caption']:
                text_parts = []
                for child in fig.children:
                    if child.name and child.name not in ['label']:
                        text = child.get_text(strip=True)
                        if text:
                            text_parts.append(text)
                fig_info['caption'] = ' '.join(text_parts)
            
            if fig_info['page']:
                figures.append(fig_info)
        
        return figures
    
    def _extract_images_from_pdf(
        self, 
        pdf_path: str, 
        figures_info: List[Dict], 
        output_dir: Path
    ) -> List[Dict]:
        """从 PDF 中提取图片并保存（使用新版 pymupdf）"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 使用新版 pymupdf 打开 PDF
        doc = pymupdf.open(pdf_path)
        
        extracted = []
        image_counter = 0
        
        # 按页码分组
        figures_by_page = {}
        for fig in figures_info:
            page_num = fig['page']
            if page_num:
                if page_num not in figures_by_page:
                    figures_by_page[page_num] = []
                figures_by_page[page_num].append(fig)
        
        print(f"📊 找到 {len(figures_by_page)} 页包含图片")
        
        # 遍历每一页
        for page_num in sorted(figures_by_page.keys()):
            page_index = page_num - 1  # pymupdf 页码从 0 开始
            page = doc[page_index]
            
            # 获取页面上的所有图片
            image_list = page.get_images(full=True)
            
            print(f"   第 {page_num} 页: 找到 {len(image_list)} 个图片")
            
            # 提取图片
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    
                    # 新版 pymupdf 使用 extract_image() 方法
                    base_image = doc.extract_image(xref)
                    
                    if base_image:
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        # 生成文件名
                        image_counter += 1
                        image_filename = f"page{page_num}_img{img_index + 1}.{image_ext}"
                        image_path = output_dir / image_filename
                        
                        # 保存图片
                        with open(image_path, "wb") as img_file:
                            img_file.write(image_bytes)
                        
                        # 查找对应的说明文字
                        figures_on_page = figures_by_page.get(page_num, [])
                        caption = ""
                        label = ""
                        fig_type = "image"
                        
                        if figures_on_page and img_index < len(figures_on_page):
                            caption = figures_on_page[img_index].get('caption', '')
                            label = figures_on_page[img_index].get('label', '')
                            fig_type = figures_on_page[img_index].get('type', 'image')
                        
                        img_size = len(image_bytes)
                        
                        # 获取图片尺寸
                        try:
                            import io
                            from PIL import Image
                            img_pil = Image.open(io.BytesIO(image_bytes))
                            img_width, img_height = img_pil.size
                        except:
                            img_width, img_height = 0, 0
                        
                        extracted.append({
                            'filename': image_filename,
                            'path': str(image_path),
                            'page': page_num,
                            'index': img_index + 1,
                            'label': label,
                            'caption': caption,
                            'type': fig_type,
                            'format': image_ext,
                            'size': img_size,
                            'width': img_width,
                            'height': img_height,
                            'xref': xref
                        })
                        
                        print(f"      ✓ 提取: {image_filename} ({img_size} bytes)")
                
                except Exception as e:
                    print(f"      ✗ 提取图片 {img_index} 失败: {e}")
                    continue
        
        doc.close()
        
        return extracted
    
    def extract_all_images_simple(
        self, 
        pdf_path: str, 
        output_dir: str = "./images"
    ) -> List[Dict]:
        """简单模式：提取所有图片，不使用 GROBID"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"📄 正在处理 {pdf_path}...")
        doc = pymupdf.open(pdf_path)
        
        extracted = []
        image_counter = 0
        
        # 遍历每一页
        for page_index, page in enumerate(doc):
            page_num = page_index + 1
            image_list = page.get_images(full=True)
            
            if image_list:
                print(f"   第 {page_num} 页: 找到 {len(image_list)} 个图片")
            
            for img_index, img in enumerate(image_list):
                try:
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    
                    if base_image:
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        image_counter += 1
                        image_filename = f"page{page_num}_img{img_index + 1}.{image_ext}"
                        image_path = output_path / image_filename
                        
                        with open(image_path, "wb") as img_file:
                            img_file.write(image_bytes)
                        
                        extracted.append({
                            'filename': image_filename,
                            'path': str(image_path),
                            'page': page_num,
                            'index': img_index + 1,
                            'format': image_ext,
                            'size': len(image_bytes),
                            'xref': xref
                        })
                        
                        print(f"      ✓ {image_filename}")
                
                except Exception as e:
                    print(f"      ✗ 失败: {e}")
        
        doc.close()
        
        print(f"\n✅ 完成！共提取 {len(extracted)} 个图片")
        print(f"📁 保存位置: {output_dir}")
        
        return extracted


def main():
    parser = argparse.ArgumentParser(
        description='从 PDF 中提取图片和说明（使用新版 pymupdf）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用 GROBID 提取图片和说明
  python grobid_extract_images_pymupdf.py paper.pdf
  
  # 简单模式：仅提取图片
  python grobid_extract_images_pymupdf.py paper.pdf --simple
  
  # 指定输出目录
  python grobid_extract_images_pymupdf.py paper.pdf -o ./output
  
  # 指定 GROBID 服务地址
  python grobid_extract_images_pymupdf.py paper.pdf -u http://localhost:8070
        """
    )
    
    parser.add_argument('pdf_path', help='PDF 文件路径')
    parser.add_argument('-o', '--output', default='./output', 
                       help='输出目录（默认：./output）')
    parser.add_argument('-u', '--url', default='http://localhost:8070', 
                       help='GROBID 服务 URL（默认：http://localhost:8070）')
    parser.add_argument('--simple', action='store_true',
                       help='简单模式：仅提取图片，不使用 GROBID')
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    if not os.path.exists(args.pdf_path):
        print(f"❌ 错误：文件不存在 - {args.pdf_path}")
        return
    
    # 创建提取器
    extractor = GrobidImageExtractor(grobid_url=args.url)
    
    # 处理 PDF
    try:
        if args.simple:
            # 简单模式
            print("="*50)
            print("🚀 简单模式：提取所有图片")
            print("="*50)
            metadata = extractor.extract_all_images_simple(args.pdf_path, args.output)
            
            # 保存元数据
            metadata_file = Path(args.output) / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'pdf_path': args.pdf_path,
                    'total_images': len(metadata),
                    'images': metadata
                }, f, indent=2, ensure_ascii=False)
        else:
            # 完整模式（使用 GROBID）
            print("="*50)
            print("🚀 完整模式：提取图片和说明")
            print("="*50)
            metadata = extractor.process_pdf(args.pdf_path, args.output)
        
        # 打印摘要
        print("\n" + "="*50)
        print("📊 提取摘要")
        print("="*50)
        
        if 'figures' in metadata:
            print(f"总图片数: {metadata['total_figures']}")
            print("\n图片列表:")
            for i, fig in enumerate(metadata['figures'][:10], 1):
                print(f"\n{i}. {fig['filename']}")
                print(f"   页码: {fig['page']}")
                if fig.get('label'):
                    print(f"   标签: {fig['label']}")
                if fig.get('caption'):
                    caption_preview = fig['caption'][:80] + "..." if len(fig['caption']) > 80 else fig['caption']
                    print(f"   说明: {caption_preview}")
                print(f"   大小: {fig['size']:,} bytes")
                if fig.get('width') and fig.get('height'):
                    print(f"   尺寸: {fig['width']} x {fig['height']} px")
            
            if len(metadata['figures']) > 10:
                print(f"\n... 还有 {len(metadata['figures']) - 10} 个图片")
        else:
            print(f"总图片数: {metadata['total_images']}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
