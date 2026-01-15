from pathlib import Path
from typing import override, Optional, Dict, Any, List
import time
import random
import mammoth
from lxml import html as lxml_html

from base import BaseConverter


class DOCX2HTML(BaseConverter):
    """DOCX 转 HTML 工具类
    基于 mammoth 实现
    mammoth 将 DOCX 转换为 HTML
    """

    def __init__(self, format_html=True):
        """初始化转换器

        Args:
            format_html: 是否格式化 HTML 输出
        """
        self.format_html = format_html

        # 默认 mammoth 配置
        self.mammoth_options = {
            "ignore_empty_paragraphs": False,
            "external_file_access": True,
            "ignore_empty_paragraphs": False,
        }

        # 存储 mammoth 的转换消息
        self.messages: List[Dict[str, str]] = []

        # 当前输出路径（用于确定图片保存目录）
        self._current_output_path = None
        # 是否保存图片
        self._save_images = True

    @override
    def support(self, suffix):
        """检查是否支持该文件类型

        Args:
            suffix: 文件后缀名

        Returns:
            是否支持该文件类型
        """
        return suffix.lower() == ".docx"

    def convert_image(self, image):
        """处理图片并保存到 images 目录"""
        try:
            # 检查输出路径是否已设置
            if self._current_output_path is None:
                return {}
            # 使用 image.open() 获取文件对象
            with image.open() as image_file:
                content_type = image.content_type  # 获取 MIME 类型 (e.g., image/png)
                
                # 根据 content_type 获取扩展名
                ext = content_type.split('/')[-1]
                if ext == 'jpeg':
                    ext = 'jpg'  # 修正常见类型
                
                # 使用时间戳 + 随机数生成唯一文件名，避免重复
                timestamp = int(time.time() * 1000)
                random_num = random.randint(1000, 9999)
                filename = f"image_{timestamp}_{random_num}.{ext}"
                
                # 创建 images 目录（相对于输出目录）
                images_dir = self._current_output_path.parent / "images"
                images_dir.mkdir(parents=True, exist_ok=True)
                
                # 保存图片文件
                image_path = images_dir / filename
                with open(image_path, 'wb') as f:
                    f.write(image_file.read())
            
            # 返回相对路径，用于生成 HTML img 标签
            return {
                "src": f"images/{filename}"
            }
        except Exception as e:
            # 返回空字典，告诉 mammoth 不生成图片标签
            return {
                "src": "images/unknow-file.jpg"
            }

    def _convert_docx_to_html(self, docx_path: Path) -> str:
        """使用 mammoth 将 DOCX 转换为 HTML

        Args:
            docx_path: DOCX 文件路径

        Returns:
            HTML 内容字符串（完整的 HTML 文档）
        """
        try:
            with open(docx_path, "rb") as docx_file:
                # 如果需要保存图片，则传入图片处理器
                if self._save_images:
                    options = self.mammoth_options.copy()
                    options['convert_image'] = mammoth.images.img_element(self.convert_image)
                else:
                    options = self.mammoth_options
                
                html_result = mammoth.convert_to_html(docx_file, **options)
                html_fragment = html_result.value

                # 存储转换消息
                self.messages = [
                    {
                        "type": msg.type,
                        "message": msg.message
                    }
                    for msg in html_result.messages
                ]

                # 将 HTML 片段包装成完整的 HTML 文档，并指定 UTF-8 编码
                html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{docx_path.stem}</title>
</head>
<body>
{html_fragment}
</body>
</html>"""

                # 格式化 HTML
                if self.format_html:
                    html_content = self._format_html(html_content)


                return html_content
        except Exception as e:
            raise Exception(f"DOCX 转 HTML 失败: {e}")

    def _format_html(self, html_content: str) -> str:
        """格式化 HTML，添加缩进和换行

        Args:
            html_content: 原始 HTML 内容

        Returns:
            格式化后的 HTML 内容
        """
        try:
            # 使用 lxml.html 解析并格式化
            tree = lxml_html.fromstring(html_content)
            
            # 格式化输出
            formatted = lxml_html.tostring(
                tree,
                encoding='unicode',
                pretty_print=True,
                method='html'
            )
            
            # 添加 DOCTYPE
            if not formatted.startswith('<!DOCTYPE'):
                formatted = '<!DOCTYPE html>\n' + formatted
            
            return formatted
        except Exception as e:
            # 如果格式化失败，返回原始 HTML
            return html_content

    def set_style_map(self, style_map: str):
        """设置 mammoth 自定义样式映射

        Args:
            style_map: 样式映射字符串
        """
        self.mammoth_options["style_map"] = style_map


    def convert(self, docx_file: str, output_file: str = None) -> str:
        """执行 DOCX 到 HTML 的转换

        Args:
            docx_file: DOCX 文件路径
            output_file: 输出 HTML 文件路径，默认为同名 .html 文件

        Returns:
            转换后的 HTML 内容
        """

        # 转换为 Path 对象
        docx_path = Path(docx_file)

        # 检查文件是否存在
        if not docx_path.exists():
            raise FileNotFoundError(f"Word 文档不存在: {docx_path}")

        # 确定输出路径
        if output_file is None:
            output_path = docx_path.with_suffix('.html')
        else:
            output_path = Path(output_file)

        # 保存当前输出路径，用于图片保存
        self._current_output_path = output_path

        # 启用图片保存
        self._save_images = True

        # DOCX 转 HTML
        html_content = self._convert_docx_to_html(docx_path)

        # 自动创建父目录
        output_path.parent.mkdir(parents=True, exist_ok=True)
        # 写入文件
        output_path.write_text(html_content, encoding='utf-8')

        return html_content


# --- 使用示例 ---

if __name__ == "__main__":
    import sys

    # 替换为你的 DOCX 文件路径
    docx_file = "files/1901180052张卓群毕业论文.docx"
    output_file = str(Path(docx_file).with_suffix(".html"))

    try:
        # 方式1：创建转换器并转换（默认输出到同名 .html 文件）
        converter = DOCX2HTML()
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