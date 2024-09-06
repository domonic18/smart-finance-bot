import os
import datetime
import settings
from agent.agent import AgentSql
from rag.rag import RagManager
from rag.pdf_processor import PDFProcessor
from utils.util import get_qwen_models
from utils.util import get_huggingface_embeddings
from test.question_answer import TestQuestion
from finance_bot_ex import FinanceBotEx
from finance_bot import FinanceBot
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import XinferenceEmbeddings



# 测试Agent主流程
def test_agent():
    # 从配置文件取出模型
    llm, chat, embed = settings.LLM, settings.CHAT, settings.EMBED
    sql_path = settings.SQLDATABASE_URI
    agent = AgentSql(sql_path=sql_path, llm=chat, embed=embed)


    example_query = "请帮我查询出20210415日，建筑材料一级行业涨幅超过5%（不包含）的股票数量"

    result, result_list = agent.get_result(example_query)

    print(result)
    print(result_list)


# 测试RAG主流程
def test_rag():
    from rag.retrievers import MultiQueryRetrieverWrapper

    llm, chat, embed = settings.LLM, settings.CHAT, settings.EMBED

    # 普通检索器
    rag_manager = RagManager(host="localhost", port=8000, llm=llm, embed=embed)

    # 多查询检索器
    rag_manager = RagManager(host="localhost", port=8000, llm=llm, embed=embed,
                             retriever_cls=MultiQueryRetrieverWrapper)

    example_query = "湖南长远锂科股份有限公司"
    example_query = "根据联化科技股份有限公司招股意见书，精细化工产品的通常利润率是多少？"

    result = rag_manager.get_result(example_query)

    print(result)


# 测试导入PDF到向量库主流程
def test_import():
    llm, chat, embed = settings.LLM, settings.CHAT, settings.EMBED

    directory = "./app/dataset/pdf"
    persist_path = "chroma_db"
    server_type = "local"

    # 创建 PDFProcessor 实例
    pdf_processor = PDFProcessor(directory=directory,
                                 chroma_server_type=server_type,
                                 persist_path=persist_path,
                                 embed=embed)

    # 处理 PDF 文件
    pdf_processor.process_pdfs()


# 测试 FinanceBot主流程
def test_financebot():
    llm, chat, embed = settings.LLM, settings.CHAT, settings.EMBED

    financebot = FinanceBot(llm=llm, chat=chat, embed=embed)

    # example_query = "根据武汉兴图新科电子股份有限公司招股意向书，电子信息行业的上游涉及哪些企业？"
    example_query = "武汉兴图新科电子股份有限公司"
    # example_query = "云南沃森生物技术股份有限公司负责产品研发的是什么部门？"

    final_result = financebot.handle_query(example_query)

    print(final_result)

# 测试 FinanceBotEx 主流程
def test_financebot_ex():
    llm, chat, embed = settings.LLM, settings.CHAT, settings.EMBED

    financebot = FinanceBotEx(llm=llm, chat=chat, embed=embed)

    # example_query = "现在几点了？"
    # example_query = "湖南长远锂科股份有限公司变更设立时作为发起人的法人有哪些？"
    # example_query = "根据联化科技股份有限公司招股意见书，精细化工产品的通常利润率是多少？"
    # example_query = "20210304日，一级行业为非银金融的股票的成交量合计是多少？取整。"
    # example_query = "云南沃森生物技术股份有限公司负责产品研发的是什么部门？"
    example_query = "根据武汉兴图新科电子股份有限公司招股意向书，电子信息行业的上游涉及哪些企业？"

    financebot.handle_query(example_query)


def test_answer_question():
    current_path = os.getcwd()

    input_file_path = os.path.join(current_path, "app/dataset/question.json")

    test_question = TestQuestion(input_file_path, test_case_start=0, test_case_end=10)
    test_question.run_cases()


def test_llm_api():
    from utils.util import get_qwen_models
    from utils.util import get_ernie_models
    from utils.util import get_huggingface_embeddings
    from utils.util import get_bge_embeddings
    from utils.util import get_bce_embeddings
    from utils.util import get_qwen_embeddings
    from utils.util import get_erine_embeddings
    from utils.util import get_zhipu_models

    # llm = get_qwen_models()
    chat = get_zhipu_models()
    # embed = get_qwen_embeddings()
    # embed = get_bge_embeddings()
    # embed = get_bce_embeddings()

    # print(llm.invoke(input="你好"))
    print(chat.invoke(input="你好"))
    # print(embed.embed_query(text="你好"))

def test_chroma_connect():
    import chromadb
    from chromadb import Settings
    from langchain_chroma import Chroma

    client = chromadb.HttpClient(host='localhost', port=8000)

    store = Chroma(collection_name='langchain',
                        embedding_function=settings.EMBED,
                        client=client)

# 测试Milvus的基础使用方法
def test_milvus():
    from langchain_community.document_loaders import PyMuPDFLoader
    from rag.milvus_conn import MilvusDB
    from langchain_text_splitters import RecursiveCharacterTextSplitter


    mdb = MilvusDB(collection_name="LangChainCollectionTest", embed=settings.EMBED)
    
    pdf_path = os.path.join(os.getcwd(), "app/dataset/pdf/0b46f7a2d67b5b59ad67cafffa0e12a9f0837790.pdf")

    pdf_loader = PyMuPDFLoader(file_path=pdf_path)
    documents = pdf_loader.load()

    chunksize = 500  # 切分文本的大小
    overlap = 100  # 切分文本的重叠大小

    # 切分文档
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunksize,
        chunk_overlap=overlap,
        length_function=len,
        add_start_index=True,
    )
    docs = text_splitter.split_documents(documents)

    batch_size = 6  # 每次处理的样本数量
    # 分批入库
    for i in range(0, len(docs), batch_size):
        batch = docs[i:i + batch_size]  # 获取当前批次的样本
        mdb.add_with_langchain(docs=batch)  # 入库
    
    # 查询
    query = "湖南长远锂科股份有限公司"
    milvus_store = mdb.get_store()
    docs = milvus_store.similarity_search(query, k=3)

    print(len(docs))

    # 打印结果
    for doc in docs:
        print("="*100)
        print(doc.page_content)


def test_import_with_milvus():
    from rag.pdf_processor import PDFProcessor
    from rag.milvus_conn import MilvusDB

    directory = "./app/dataset/pdf"
    persist_path = "milvus_db"
    server_type = "local"

    # 创建 PDFProcessor 实例
    pdf_processor = PDFProcessor(directory=directory,
                                 chroma_server_type=server_type,
                                 persist_path=persist_path,
                                 embed=settings.EMBED)

    # 处理 PDF 文件
    pdf_processor.process_pdfs()


if __name__ == "__main__":
    # test_agent()
    # test_rag()
    # test_import()
    # test_financebot()
    # test_financebot_ex()
    # test_llm_api()
    # test_chroma_connect()
    # test_answer_question()
    # test_milvus()
    test_import_with_milvus()