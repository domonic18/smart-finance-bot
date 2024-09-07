# 使用 Node.js 官方镜像
FROM node:16

# 设置工作目录
WORKDIR /chatweb

# 复制 package.json 和 package-lock.json 文件并安装依赖
COPY package*.json ./
RUN npm install

# 复制应用代码
COPY . .

# 暴露服务端口
EXPOSE 5173