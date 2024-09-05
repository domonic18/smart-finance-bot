import os
from utils.util import get_qwen_models
from utils.util import get_ernie_models
from utils.util import get_huggingface_embeddings
from utils.util import get_bge_embeddings
from utils.util import get_bce_embeddings
from utils.util import get_qwen_embeddings
from utils.util import get_erine_embeddings
from utils.util import get_zhipu_models

"""
大模型相关的配置
"""

# 连接大模型
# 如果想更换模型，在配置中进行相应修改即可

# 阿里千问系列模型
# 默认使用qwen-max模型
#   模型调用-输入:0.04/text_token（千个）
#   模型调用-输出:0.12/text_token（千个）
# LLM = get_qwen_models()[0]
# CHAT = get_qwen_models()[1]
# EMBED = get_qwen_embeddings()

# qwen-long模型
#   模型调用-输入:0.0005/text_token（千个）
#   模型调用-输出:0.002/text_token（千个）
# LLM = get_qwen_models(model="qwen-long")[0]
CHAT = get_qwen_models(model="qwen-long")[1]

# 百度文心一言系列模型
# 默认模型：ERNIE-Bot-turbo
#  免费
# LLM = get_ernie_models()[0]
# CHAT = get_ernie_models()[1]
# EMBED = get_erine_embeddings()

# ERNIE-4.0-8K 模型
#   模型调用-输入:¥0.04元/千tokens
#   模型调用-输出:¥0.12元/千tokens
# LLM = get_ernie_models(model="ERNIE-4.0-8K")[0]
# CHAT = get_ernie_models(model="ERNIE-4.0-8K")[1]


# ERNIE-3.5-8K 模型
#   模型调用-输入:¥0.004元/千tokens
#   模型调用-输出:¥0.012元/千tokens
# LLM = get_ernie_models(model="ERNIE-3.5-8K")[0]
# CHAT = get_ernie_models(model="ERNIE-3.5-8K")[1]


# 智普对话模型
# 活动：注册送500万tokens, 新客专享充值99元 1000万tokens
# GLM-4-Plus模型
#   单价：0.05 元 / 千tokens
# LLM = get_zhipu_models()
# CHAT = get_zhipu_models()

# GLM-4-Air模型
#   单价：0.001 元 / 千tokens
#   Batch API 定价：0.0005元 / 千tokens
LLM = get_zhipu_models(model="GLM-4-Air")
CHAT = get_zhipu_models(model="GLM-4-Air")


# 使用智普bge-m3的向量化模型
#  本地部署：免费
EMBED = get_bge_embeddings()

# 使用网易的bce for rag向量化模型
#  本地部署：免费
# EMBED = get_bce_embeddings()

# 使用Huggingface的embedding
# EMBED = get_huggingface_embeddings()


# 意图识别问答模型的配置
BASE_URL = "http://direct.virtaicloud.com:45181/v1"
API_KEY = "EMPTY"
MODEL = "Qwen2_7B-chat-sft2"

"""
向量数据库使用时的相关的配置
"""
# 默认的ChromaDB的服务器类别
CHROMA_SERVER_TYPE = "http"
# 默认本地数据库的持久化目录
CHROMA_PERSIST_DB_PATH = "chroma_db"

CHROMA_HOST = "localhost"
CHROMA_PORT = 8000

CHROMA_SERVER_TYPE_IMPORT = "local"

"""
本地SQLite数据库相关的配置
"""
# 连接数据库db文件的地址根据需要需要更换
SQLDATABASE_URI = os.path.join(os.getcwd(), "app/dataset/dataset/博金杯比赛数据.db")
