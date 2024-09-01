# 光环结业项目

## 介绍
金融千问机器人是一个 基于 `LLM` + `Agent` + `RAG` 的智能问答系统，该项目源于阿里天池的挑战赛。

- **赛事内容地址**：https://tianchi.aliyun.com/competition/entrance/532172

- **开源参考代码**：https://github.com/Tongyi-EconML/FinQwen

- **项目计划地址**：https://docs.qq.com/sheet/DTGVMSWtkendacmRl?tab=3qh6in


## 项目架构
根据之前参赛项目的经验，该项目预计的项目架构图如下：
![](doc/framework_1.jpg)


## 目录说明

```bash
smart-finance-bot \
    |- doc \  # 该目录用于保存文档类文件，例如：需求文档、说明文档、数据文档
    |- app \   # 该目录用于服务端代码
        |- agent \ # 该目录用于保存agent相关代码
        |- rag \   # 该目录用于保存rag相关代码
        |- ir \   # 该目录用于保存意图识别(Intent Recognition)相关代码
        |- data \  # 该目录用于保存PDF以及SQLite数据
        |- conf \  # 该目录用于保存配置文件
            |- .qwen # 该文件保存QWen的配置文件(请自行添加对应的API KEY)
            |- .ernie # 该文件保存百度千帆的配置文件(请自行添加对应的API KEY)
    |- chatweb \   # 该目录用于保存前端页面代码
    |- scripts \   # 该目录用于保存脚本文件，例如：启动脚本、导入向量数据库脚本等
```

## 使用说明

### 1、拉取代码
**第一步**：拉取代码到本地
```shell
git clone https://gitee.com/deadwalk/smart-finance-bot.git
```

> Git客户端[gitee使用教程](https://blog.csdn.net/weixin_50470247/article/details/133585369)

**第二步**：安装相关组件

在当前目录下启动命令行，在命令行中运行如下命令

```bash
# 安装依赖前，强烈建议使用conda虚拟环境，例如：
# conda create --name langchain python=3.10
# conda activate langchain

pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2、配置大模型的APIKey
**第一步**：打开配置文件 conf/.qwen，配置自己的API Key.

**第二步**：运行API-KEY测试脚本

Linux/Mac用户：
```shell
# 切换/保持当前目录为 smart-finance-bot
cd smart-finance-bot

# 给shell脚本赋予运行权限
chmod +x ./scripts/run_test_llm.sh

# 运行测试脚本
./scripts/test_llm.sh

```

Windows用户：
```bash
# 运行测试脚本
scripts\run_test_llm.bat
```


### 3、启动Chroma数据库
Linux/Mac用户：
```shell
# 切换/保持当前目录为 smart-finance-bot
cd smart-finance-bot

# 给shell脚本赋予运行权限
chmod +x ./scripts/start_chroma.sh

# 启动Chroma数据库
./scripts/start_chroma.sh
```

Windows用户：
```bash
scripts\start_chroma.bat
```

### 4、批量导入数据到向量数据库
Linux/Mac用户：
```shell
# 切换/保持当前目录为 smart-finance-bot
cd smart-finance-bot

# 给shell脚本赋予运行权限
chmod +x ./scripts/import_pdf.sh

# 启动批量导入脚本
./scripts/import_pdf.sh
```

Windows用户：
```bash

```

### 5、启动后端服务

```bash
# 切换/保持当前目录为 smart-finance-bot
cd smart-finance-bot

# 启动服务
python app/server.py

```

### 6、启动前端服务
**第一步**：安装Node.js
- 访问https://nodejs.cn/download/
- 按照页面提示下载Node.js到本地后进行安装

**第二步**：安装依赖包
```bash
# 进入chatweb目录
cd chatweb

# 安装依赖包
npm install
```

**第三步**：启动服务
```bash
# 启动服务
npm run dev
```
