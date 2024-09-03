from dotenv import load_dotenv
import os

# 获取当前文件的目录
current_dir = os.path.dirname(__file__)

# 构建到 conf/.qwen 的相对路径
conf_file_path_qwen = os.path.join(current_dir, '..', 'conf', '.qwen')

# 构建到 conf/.ernie 的相对路径
conf_file_path_ernie = os.path.join(current_dir, '..', 'conf', '.ernie')

# 加载千问环境变量
load_dotenv(dotenv_path=conf_file_path_qwen)

# 加载文心环境变量
load_dotenv(dotenv_path=conf_file_path_ernie)


def get_qwen_models():
    """
    加载千问系列大模型
    """
    # llm 大模型
    from langchain_community.llms.tongyi import Tongyi

    llm = Tongyi(model="qwen-max", temperature=0.1, top_p=0.7, max_tokens=1024)

    # chat 大模型
    from langchain_community.chat_models import ChatTongyi

    chat = ChatTongyi(model="qwen-max", temperature=0.01, top_p=0.2, max_tokens=1024)
    # embedding 大模型
    from langchain_community.embeddings import DashScopeEmbeddings

    embed = DashScopeEmbeddings(model="text-embedding-v3")

    return llm, chat, embed

def get_ernie_models():
    """
    加载文心系列大模型
    """
    # LLM 大语言模型（单轮对话版）
    from langchain_community.llms import QianfanLLMEndpoint

    # Chat 聊天版大模型（支持多轮对话）
    from langchain_community.chat_models import QianfanChatEndpoint

    # Embeddings 嵌入模型
    from langchain_community.embeddings import QianfanEmbeddingsEndpoint

    llm = QianfanLLMEndpoint(model="ERNIE-Bot-turbo", temperature=0.1, top_p=0.2)
    chat = QianfanChatEndpoint(model="ERNIE-Lite-8K", top_p=0.2, temperature=0.1)

    embed = QianfanEmbeddingsEndpoint(model="bge-large-zh")

    return llm, chat, embed

def get_huggingface_embeddings():
    """
    加载嵌入模型
    """
    from langchain_community.embeddings import HuggingFaceEmbeddings

    embeddings = HuggingFaceEmbeddings(model_name="bert-base-chinese")

    return embeddings


if __name__ == "__main__":
    llm, chat, embed = get_qwen_models()
    print(llm.invoke(input="你好"))
    print(chat.invoke(input="你好"))
    print(embed.embed_query(text="你好"))
