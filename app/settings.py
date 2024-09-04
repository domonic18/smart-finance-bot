import os
from utils.util import get_qwen_models
from utils.util import get_ernie_models
from utils.util import get_huggingface_embeddings
from utils.util import get_bge_embeddings
from utils.util import get_bce_embeddings

"""
大模型相关的配置
"""

# 连接大模型
# 如果想更换模型，在配置中进行相应修改即可

# 阿里千问系列模型
LLM = get_qwen_models()[0]
CHAT = get_qwen_models()[1]
# EMBED = get_qwen_models()[2] 

# 百度文心一言系列模型
# LLM = get_ernie_models()[0]
# CHAT = get_ernie_models()[1]
# EMBED = get_ernie_models()[2] 


# 使用智普bge-m3的向量化模型
EMBED = get_bge_embeddings()

# 使用网易的bce for rag向量化模型
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
