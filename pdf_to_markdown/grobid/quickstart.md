# GROBID 快速安装运行说明

## 什么是 GROBID？

GROBID 是一个用于解析和提取学术 PDF 文档信息的机器学习库，特别擅长：
- 提取论文标题、作者、摘要、参考文献
- 解析引用上下文
- 识别全文结构
- 处理学术元数据

---

## 方式一：Docker 安装（推荐）

### 前置要求
- 已安装 Docker（[安装指南](https://docs.docker.com/get-docker/)）
- Linux/Mac/Windows 系统均可

### 选择镜像版本

GROBID 提供两种 Docker 镜像：

#### 1. Full 版本（高精度，需要 GPU）
- **大小**：约 8GB
- **适用场景**：需要最高精度，有 GPU 或处理少量 PDF
- **特点**：包含深度学习模型，精度提升 2-5 F1-score

```bash
# 拉取镜像
docker pull grobid/grobid:0.8.2-full

# 运行（带 GPU 支持，仅 Linux）
docker run --rm --gpus all --init --ulimit core=0 -p 8070:8070 grobid/grobid:0.8.2-full

# 运行（仅 CPU，适用于 Mac/Windows）
docker run --rm --init --ulimit core=0 -p 8070:8070 grobid/grobid:0.8.2-full
```

#### 2. Lightweight 版本（高性能，CPU only）
- **大小**：约 500MB
- **适用场景**：批量处理大量 PDF，资源有限
- **特点**：仅使用 CRF 模型，速度快但精度略低

```bash
# 拉取镜像
docker pull grobid/grobid:0.8.2-crf

# 运行
docker run --rm --init --ulimit core=0 -p 8070:8070 grobid/grobid:0.8.2-crf
```

### 端口映射说明

默认端口 `8070`，可映射到主机 `8080`：

```bash
docker run --rm --init --ulimit core=0 -p 8080:8070 grobid/grobid:0.8.2-crf
```

### 验证安装

浏览器访问：
- 服务首页：http://localhost:8080
- 健康检查：http://localhost:8081

---

## 方式二：从源码编译

### 前置要求
- **JDK 21 或更高版本**
- 路径中不能包含空格

### 安装 JDK 21

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install openjdk-21-jdk
```

**Linux (CentOS/RHEL/Fedora):**
```bash
sudo dnf install java-21-openjdk-devel
```

**macOS (Homebrew):**
```bash
brew install openjdk@21
export JAVA_HOME=$(brew --prefix)/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home
```

**验证安装:**
```bash
java -version
javac -version
```

### 获取源码

**稳定版本 (0.8.2):**
```bash
wget https://github.com/kermitt2/grobid/archive/0.8.2.zip
unzip 0.8.2.zip
```

**开发版本:**
```bash
git clone https://github.com/kermitt2/grobid.git
```

### 编译

```bash
cd grobid
./gradlew clean install
```

### 运行服务

```bash
./gradlew run
```

服务将启动在 http://localhost:8070

---

## 快速使用

### 0. 在线体验（无需安装）

如果想先体验 GROBID 的功能，可以直接访问在线演示：
- **[https://kermitt2-grobid.hf.space/](https://kermitt2-grobid.hf.space/)** - 官方演示站点
- 上传 PDF 文件即可看到解析结果

### 1. 通过 Web 界面测试

本地安装后，访问 http://localhost:8080，上传 PDF 文件进行解析。

### 2. 通过 API 调用

**处理完整文档：**
```bash
curl -X POST -F "input=@/path/to/paper.pdf" http://localhost:8080/api/processFulltextDocument
```

**仅提取头部信息：**
```bash
curl -X POST -F "input=@/path/to/paper.pdf" http://localhost:8080/api/processHeaderDocument
```

**解析参考文献：**
```bash
curl -X POST -F "input=@/path/to/paper.pdf" http://localhost:8080/api/processReferences
```

### 3. 使用 Python 客户端

```python
# 安装客户端
pip install pygrobid

# 使用示例
from pygrobid import GrobidClient

client = GrobidClient()
client.process("processFulltextDocument", "./path/to/pdfs", output="./output")
```

### 4. 获取 Markdown 格式

**注意**：GROBID 原生不支持直接输出 Markdown 格式，主要输出 TEI XML。如需 Markdown，有以下方案：

#### 方案 A：TEI XML 转 Markdown（推荐）

```bash
# 1. 获取 TEI XML
curl -X POST -F "input=@paper.pdf" \
  http://localhost:8080/api/processFulltextDocument > output.xml

# 2. 使用 pandoc 转换
pandoc -f tei -t markdown output.xml -o output.md
```

#### 方案 B：使用 Python 脚本

```python
from bs4 import BeautifulSoup

def tei_to_markdown(tei_file):
    with open(tei_file, 'r') as f:
        soup = BeautifulSoup(f, 'xml')
    
    # 提取标题
    title = soup.find('title', {'level': 'a'})
    title = title.text if title else "Untitled"
    
    # 提取摘要
    abstract = soup.find('abstract')
    abstract_text = abstract.get_text() if abstract else ""
    
    # 提取正文
    paragraphs = soup.find_all('p')
    body_text = '\n\n'.join([p.get_text() for p in paragraphs])
    
    # 组合 Markdown
    markdown = f"# {title}\n\n"
    if abstract_text:
        markdown += f"## Abstract\n\n{abstract_text}\n\n"
    markdown += body_text
    
    return markdown

# 使用
markdown = tei_to_markdown('output.xml')
with open('output.md', 'w') as f:
    f.write(markdown)
```

#### 方案 C：使用专门的 PDF 转 Markdown 工具

如果主要目标是获取 Markdown，可以考虑：
- **marker** - 高精度 PDF 转 Markdown 工具
- **pdfplumber** - Python PDF 解析库
- **pdf2md** - 简单的 PDF 转 Markdown 工具

---

## 常见问题

### 内存不足

**问题**：容器被杀死或处理失败

**解决方案**：
- 增加 Docker 内存分配（推荐 4-8GB）
- macOS：通过 Docker Desktop 设置增加内存
- 使用 lightweight 版本减少内存需求

### CPU 指令集错误

**错误信息**：`The TensorFlow library was compiled to use SSE4.1 instructions`

**解决方案**：
- 更新虚拟机 CPU 配置以支持 SSE4.1、SSE4.2 和 AVX 指令集
- 或使用 GPU 版本避免此问题

### 端口冲突

**问题**：端口 8070 或 8080 已被占用

**解决方案**：
```bash
# 映射到其他端口
docker run --rm --init --ulimit core=0 -p 9999:8070 grobid/grobid:0.8.2-crf
```

---

## 生产环境建议

1. **资源配置**：
   - Full 版本：至少 4GB RAM，推荐 GPU
   - Lightweight 版本：2GB RAM 足够
   - 批量处理：建议 6-8GB RAM

2. **性能优化**：
   - 使用 GPU 加速（Full 版本）
   - 批量处理时调整并发数
   - 考虑使用 consolidation 服务（需注意性能影响）

3. **配置文件**：
   - 挂载自定义 `grobid.yaml` 配置文件
   ```bash
   docker run --rm -gpus all --init -p 8080:8070 \
     -v /path/to/grobid.yaml:/opt/grobid/grobid-home/config/grobid.yaml:ro \
     grobid/grobid:0.8.2-full
   ```

---

## 在线体验（无需安装）

无需安装任何软件，直接访问以下在线演示地址体验 GROBID 功能：

- **[GROBID 官方演示](https://kermitt2-grobid.hf.space/)** - 主要演示站点
- **[GROBID HuggingFace Space](https://huggingface.co/spaces/lfoppiano/grobid)** - 备用演示站点
- **[GROBID Space Mirror](https://huggingface.co/spaces/lfoppiano/grobid2)** - 镜像站点

> ⚠️ **注意**：这些在线演示仅用于功能测试和体验，不适合生产环境使用。如需处理大量文档或用于生产，请部署本地版本。

---

## 更多资源

- [官方文档](https://grobid.readthedocs.io/)
- [GitHub 仓库](https://github.com/kermitt2/grobid)
- [Docker Hub](https://hub.docker.com/r/grobid/grobid)
- [API 文档](https://grobid.readthedocs.io/en/latest/Grobid-service/)
- [在线演示](https://kermitt2-grobid.hf.space/)

---

**版本信息**：本文档基于 GROBID 0.8.2 版本编写
