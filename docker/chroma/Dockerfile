# 使用官方的 Python 3.10 基础镜像
FROM python:3.10

# 设置工作目录
WORKDIR /app

# 复制应用代码
COPY app/. .

# 安装所需的 Python 包
RUN pip install --no-cache-dir langchain_chroma chromadb

# 暴露 Chroma 服务端口
EXPOSE 8000

# 运行 Chroma 服务
CMD ["chroma", "run", "--path", "chroma_db", "--port", "8000", "--host", "0.0.0.0"]
