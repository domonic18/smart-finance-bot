import os
from utils.util import get_qwen_models

"""
大模型相关的配置
"""


# 连接大模型
llm, chat, embed = get_qwen_models()

LLM = llm
CHAT = chat
EMBED = embed 

BASE_URL = "http://direct.virtaicloud.com:45181/v1"
API_KEY = "EMPTY"
MODEL = "Qwen2_7B-chat-sft2"

"""
向量数据库相关的配置
"""
# 默认的ChromaDB的服务器类别
CHROMA_SERVER_TYPE = "http"
# 默认本地数据库的持久化目录
CHROMA_PERSIST_DB_PATH = "chroma_db"

CHROMA_HOST = "localhost"
CHROMA_PORT = 8000

"""
本地SQLite数据库相关的配置
"""
# 连接数据库db文件的地址根据需要需要更换
SQLDATABASE_URI = os.path.join(os.getcwd(), "app/dataset/dataset/博金杯比赛数据.db")

