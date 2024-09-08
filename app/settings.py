import os
from utils.util import get_qwen_models
from utils.util import get_ernie_models
from utils.util import get_huggingface_embeddings
from utils.util import get_bge_embeddings
from utils.util import get_bce_embeddings
from utils.util import get_qwen_embeddings
from utils.util import get_erine_embeddings
from utils.util import get_zhipu_models
from utils.util import get_zhipu_embeddings
from utils.util import get_zhipu_chat_model

"""
大模型相关的配置
"""

# 连接大模型
# 如果想更换模型，在配置中进行相应修改即可
# ---------------------------------------------------------------------------------------------------------------------

# 阿里千问系列模型
# 默认使用qwen-max模型
#   模型调用-输入:0.04/text_token（千个）
#   模型调用-输出:0.12/text_token（千个）
# qwen-long模型
#   模型调用-输入:0.0005/text_token（千个）
#   模型调用-输出:0.002/text_token（千个）

LLM = get_qwen_models(model="qwen-max")[0]
CHAT = get_qwen_models(model="qwen-max")[1]

# ---------------------------------------------------------------------------------------------------------------------
# 百度文心一言系列模型
# 默认模型：ERNIE-Bot-turbo
#  免费
# ERNIE-4.0-8K 模型
#   模型调用-输入:¥0.04元/千tokens
#   模型调用-输出:¥0.12元/千tokens
# ERNIE-3.5-8K 模型
#   模型调用-输入:¥0.004元/千tokens
#   模型调用-输出:¥0.012元/千tokens

# MODEL = "ERNIE-Bot-turbo"
# LLM = get_ernie_models()[0]
# CHAT = get_ernie_models()[1]
# EMBED = get_erine_embeddings()

# ---------------------------------------------------------------------------------------------------------------------
# 智普对话模型
# 活动：注册送500万tokens, 新客专享充值99元 1000万tokens
# GLM-4-Plus模型
#   单价：0.05 元 / 千tokens
# GLM-4-Air模型
#   单价：0.001 元 / 千tokens
#   Batch API 定价：0.0005元 / 千tokens

# LLM = get_zhipu_models(model="glm-4-plus")
# CHAT = get_zhipu_models(model="glm-4-flash")
# EMBED = get_zhipu_embeddings(model="embedding-3")

SERVER_URL_BGE_CHAT = "http://sy-direct.virtaicloud.com:42796/v1"
MODEL_UID_BGE_CHAT = "glm-4-9b-chat"
# CHAT = get_zhipu_chat_model()

# ---------------------------------------------------------------------------------------------------------------------
# 使用Qwen的embedding
EMBED = get_qwen_embeddings()

# 使用智普bge-m3的向量化模型
#  本地部署：免费
SERVER_URL_BGE = "http://sy-direct.virtaicloud.com:49173"
MODEL_UID_BGE = "bge-m3"
# EMBED = get_bge_embeddings()

# 使用网易的bce for rag向量化模型
#  本地部署：免费

SERVER_URL_BCE = "http://sy-direct.virtaicloud.com:49173"
MODEL_UID_BCE = "bce-embedding-base_v1"
# EMBED = get_bce_embeddings()

# 使用Huggingface的embedding
# EMBED = get_huggingface_embeddings()

"""
Chroma向量数据库使用时的相关的配置
"""
# 默认的ChromaDB的服务器类别
CHROMA_SERVER_TYPE = "http"
# 默认本地数据库的持久化目录
CHROMA_PERSIST_DB_PATH = "chroma_db"

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))
CHROMA_COLLECTION_NAME = "langchain"

CHROMA_SERVER_TYPE_IMPORT = "local"

"""
Milvus向量数据库使用时的相关的配置
"""
# 默认的ChromaDB的服务器类别
MILVUS_SERVER_TYPE = "http"
MILVUS_HOST = "localhost"
MILVUS_PORT = 19530
MILVUS_COLLECTION_NAME = "langchain"


"""
本地SQLite数据库相关的配置
"""
# 连接数据库db文件的地址根据需要需要更换
# SQLDATABASE_URI = os.path.join(os.getcwd(), "dataset/dataset/博金杯比赛数据.db")
import os

# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)

# 向上取两级找到根目录
root_directory = os.path.dirname(os.path.dirname(current_file_path))

# 拼接最终的数据库路径
SQLDATABASE_URI = os.path.join(root_directory, "dataset", "dataset", "博金杯比赛数据.db")


# 意图识别问答模型的配置
BASE_URL = "http://direct.virtaicloud.com:45181/v1"
API_KEY = "EMPTY"
MODEL = "Qwen2_7B-chat-sft2"

"""
ES数据库相关的配置
"""
ELASTIC_PASSWORD = os.getenv("ELASTIC_PASSWORD", "123abc")
ELASTIC_HOST = os.getenv("ELASTIC_HOST", "localhost")
ELASTIC_PORT = os.getenv("ELASTIC_PORT", 9200)
ELASTIC_SCHEMA = "https"
ELASTIC_INDEX_NAME = "demo_index0"