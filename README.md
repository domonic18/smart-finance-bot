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
    |- dataset \  # 该目录用于保存PDF以及SQLite数据
    |- doc \  # 该目录用于保存文档类文件，例如：需求文档、说明文档、数据文档
    |- app \   # 该目录用于服务端代码
        |- agent \ # 该目录用于保存agent相关代码
        |- rag \   # 该目录用于保存rag相关代码
        |- test \   # 该目录用于保存测试类驱动相关代码
        |- conf \  # 该目录用于保存配置文件
            |- .qwen # 该文件保存QWen的配置文件(请自行添加对应的API KEY)
            |- .ernie # 该文件保存百度千帆的配置文件(请自行添加对应的API KEY)
    |- chatweb \   # 该目录用于保存前端页面代码
    |- scripts \   # 该目录用于保存脚本文件，例如：启动脚本、导入向量数据库脚本等
    |- test_result \   # 该目录用于保存测试结果
    |- docker \
        |- backend \ # 该目录对应后端python服务的Dockerfile
        |- frontend \ # 该目录对应前端python服务的Dockerfile
```

## 使用说明

### 拉取代码
**第一步**：拉取代码到本地
```shell
git clone --recurse-submodules https://gitee.com/deadwalk/smart-finance-bot.git
```

> Git客户端[gitee使用教程](https://blog.csdn.net/weixin_50470247/article/details/133585369)

### 服务部署
目前服务部署启动支持以下两种方式：
- 基于源码的运行：该方法需要手动安装相关依赖、启动Chroma数据库等。
- 基于Docker运行：该方法使用Docker-Compose 进行构建，主要用于快速在服务器上部署环境及体验。

#### 基于源码的运行
##### 1、安装Python的依赖
进入工程根目录后，通过命令行运行如下命令：

```bash
# 安装依赖前，强烈建议使用conda虚拟环境，例如：
# conda create --name langchain python=3.10
# conda activate langchain

pip install -r requirements.txt
```

> 注意：经过实际测试Python 3.11版本会存在依赖冲突问题，所以请将Python版本切换为3.10。

##### 2、配置大模型的APIKey
打开配置文件 app/conf的配置文件，配置自己的API Key即可。

> 备注：
> - `.qwen` 文件中对应QWen的API Key
> - `.ernie` 文件中对应百度千帆的API Key
> - `.zhipu` 文件中对应智谱的API Key

如果想测试API-KEY是否生效，可以参照 `附录` 中 `关于如何配置智谱大模型` 的章节内容。


##### 3、准备向量数据库
准备向量数据库有两种方式：
- 第一种：运行自动化命令批量导入
- 第二种：直接从网盘下载已经建好的向量数据库

**第一种：** 运行自动化命令批量导入
> ！！注意：执行导入脚本前，请确保没有使用命令行启动 `Chroma` 向量数据库。

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
scripts\import_pdf.bat
```

**第二种：** 运行自动化命令批量导入
1. 访问[同义金融大模型的向量数据库](https://platform.virtaicloud.com/gemini_web/workspace/space/jxmdlbjjdhj4/data/detail/486768881516830720)
2. 可以获取下载链接，下载对应的向量数据库
3. 下载后将数据库文件移动至当前工程目录下，例如：将`chroma_db_qwen`移动至`smart-finance-bot`目录下，并重命名为`chroma_db`即可在启动chromadb时加载使用。

##### 4、启动Chroma数据库
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

> 如果想复用已经建立的向量数据库，可以在启动chroma的脚本中修改启动的path。

##### 5、启动后端服务

```bash
# 切换/保持当前目录为 smart-finance-bot
cd smart-finance-bot

# 启动服务
python app/server.py

```

##### 6、启动前端服务
**第一步**：安装Node.js
- 访问https://nodejs.cn/download/
- 按照页面提示下载Node.js到本地后进行安装

**第二步**：安装依赖包(首次运行一次即可)
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

#### 基于Docker的运行
##### 1、准备Docker运行环境
安装Docker，具体方法不再赘述，可以查看[10分钟学会Docker的安装和使用](https://blog.csdn.net/yohnyang/article/details/138435593)

##### 2、下载Docker-Compose文件
命令行下运行
```bash
curl -L https://get.daocloud.io/docker/compose/releases/download/v2.14.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
```

##### 3、启动服务
```bash
docker-compose -f docker-compose-base.yaml up -d
```
> - `docker-compose-base.yaml` 对应是只启动基础的服务，包括python后端、nodejs前端、Chroma数据库服务。
> - `docker-compose-es.yaml` 对应是只启动ElasticSearch服务的配置
> - `docker-compose-all.yaml` 对应是启动所有服务的配置，包括Python后端服务、前端nodejs、ElasticSearch服务等。

## 附录

### 关于如何进行批量化问题提问的测试

第一步：给SQLite数据库建立索引
####  SQLite数据库批量建立索引方法
```bash 
# 切换/保持当前目录为 smart-finance-bot
cd smart-finance-bot

# 运行添加索引脚本
./scripts/run_addindexs.sh
```
> 注意：该项工作仅运行一次即可。


第二步：运行测试脚本
#### 执行批量化问题提问脚本的方法
```bash
# 切换/保持当前目录为 smart-finance-bot
cd smart-finance-bot

# 运行测试脚本
./scripts/run_test_cases.sh
```
> 说明：
> 1. 测试结果会保存在 `test_result` 目录中。
> 2. 如果想调整运行的测试用例，可以直接编辑 `run_test_cases.sh` 文件，修改 `--start` 和 `--end` 参数。


### 关于如何配置智谱大模型
1. 访问智谱开放平台https://bigmodel.cn/
2. 注册账号并且登录
3. 在 `API密钥` 中创建自己的API Key
4. 在 `conf/.zhipu` 文件中配置好第3步创建好的密钥
5. 在 `app/settings.py` 中修改全局配置CHAT的赋值，即： `CHAT = get_zhipu_models(model="glm-4-plus")`
6. 至此，大模型修改完毕，你可以使用 `test_framework.py` 中的 `test_llm_api()` 进行测试。

