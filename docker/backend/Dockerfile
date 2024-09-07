# 使用 Python 官方镜像
FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 更新包列表并安装 netcat-openbsd
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

# 复制 wait-for-it.sh 脚本
COPY ./scripts/wait-for-it.sh /usr/local/bin/wait-for-it

# 给予执行权限
RUN chmod +x /usr/local/bin/wait-for-it

# 复制 requirements.txt 文件并安装依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制应用代码
COPY app/. .

# 暴露服务端口
EXPOSE 8082

# 设置容器启动命令，等待 chroma 服务启动
CMD ["wait-for-it", "chroma:8000", "--", "python", "server.py"]