from dotenv import load_dotenv
import os
import settings
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import XinferenceEmbeddings
# 同义Qwen
from langchain_community.llms.tongyi import Tongyi
from langchain_community.chat_models import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings

# 百度千帆
from langchain_community.llms import QianfanLLMEndpoint
from langchain_community.chat_models import QianfanChatEndpoint
from langchain_community.embeddings import QianfanEmbeddingsEndpoint

# 百川
from langchain_community.chat_models import ChatBaichuan

# 智谱
from langchain_community.chat_models import ChatZhipuAI



# 获取当前文件的目录
current_dir = os.path.dirname(__file__)

# 构建到 conf/.qwen 的相对路径
conf_file_path_qwen = os.path.join(current_dir, '..', 'conf', '.qwen')

# 构建到 conf/.ernie 的相对路径
conf_file_path_ernie = os.path.join(current_dir, '..', 'conf', '.ernie')

# 构建到 conf/.baichuan 的相对路径
conf_file_path_baichuan = os.path.join(current_dir, '..', 'conf', '.baichuan')

# 构建到 conf/.baichuan 的相对路径
conf_file_path_zhipu = os.path.join(current_dir, '..', 'conf', '.zhipu')

# 加载千问环境变量
load_dotenv(dotenv_path=conf_file_path_qwen)

# 加载文心环境变量
load_dotenv(dotenv_path=conf_file_path_ernie)

# 加载百川环境变量
load_dotenv(dotenv_path=conf_file_path_baichuan)

# 加载智普环境变量
load_dotenv(dotenv_path=conf_file_path_zhipu)


def get_qwen_models(model="qwen-max"):
    """
    加载千问系列大模型
    """

    llm = Tongyi(model=model, temperature=0.1, top_p=0.7, max_tokens=1024)

    chat = ChatTongyi(model=model, temperature=0.01, top_p=0.2, max_tokens=1024)


    return llm, chat

def get_ernie_models(model="ERNIE-Bot-turbo"):
    """
    加载文心系列大模型
    """

    llm = QianfanLLMEndpoint(model=model, temperature=0.1, top_p=0.2)
    
    chat = QianfanChatEndpoint(model=model, top_p=0.2, temperature=0.1)

    return llm, chat

def get_erine_embeddings(model="bge-large-zh"):
    """
    加载文心系列嵌入模型
    """
    embeddings = DashScopeEmbeddings(model=model)

    return embeddings

def get_qwen_embeddings(model="text-embedding-v3"):
    """
    加载千问系列嵌入模型
    """
    embeddings = DashScopeEmbeddings(model=model)

    return embeddings

def get_huggingface_embeddings(model_name="bert-base-chinese"):
    """
    加载嵌入模型
    """
    from langchain_community.embeddings import HuggingFaceEmbeddings

    embeddings = HuggingFaceEmbeddings(model_name=model_name)

    return embeddings

def get_bge_embeddings():
    server_url=settings.SERVER_URL_BGE
    model_uid=settings.MODEL_UID_BGE

    embed = XinferenceEmbeddings(server_url=server_url, model_uid=model_uid)
    return embed

def get_bce_embeddings():
    server_url=settings.SERVER_URL_BCE
    model_uid=settings.MODEL_UID_BCE

    embed = XinferenceEmbeddings(server_url=server_url, model_uid=model_uid)
    return embed


def get_zhipu_models(model="glm-4-plus"):
    """
    加载智普系列大模型
    """

    zhipuai_chat = ChatZhipuAI(
        temperature=0.5,
        model=model,
    )

    return zhipuai_chat

def get_baichuan_chat(model="Baichuan4"):
    """
    加载百川大模型
    """

    chat = ChatBaichuan(model=model, temperature=0.1, top_p=0.7, max_tokens=1024)

    return chat

