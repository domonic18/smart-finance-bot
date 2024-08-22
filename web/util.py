from dotenv import load_dotenv

load_dotenv(dotenv_path="./conf/.qwen_key")

def get_qwen_models():
    # llm 大模型
    from langchain_community.llms.tongyi import Tongyi

    llm = Tongyi(model="qwen-max", temperature=0.1, top_p=0.7, max_tokens=1024)

    # chat 大模型
    from langchain_community.chat_models import ChatTongyi

    chat = ChatTongyi(model="qwen-max", temperature=0.1, top_p=0.7, max_tokens=1024)
    # embedding 大模型
    from langchain_community.embeddings import DashScopeEmbeddings

    embed = DashScopeEmbeddings(model="text-embedding-v3")

    return llm, chat, embed