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
from utils.logger_config import LoggerManager
from rag.vector_db import ChromaDB, MilvusDB

logger = LoggerManager().logger

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

    # Chroma的配置
    db_config = {
        "chroma_server_type": "http",
        "host": "localhost",
        "port": 8000,
        "persist_path": "chroma_db",
        "collection_name": "langchaintest",
    }

    # 普通检索器
    # rag_manager = RagManager(vector_db_class=ChromaDB, db_config=db_config, llm=llm, embed=embed)
    
    # 多查询检索器
    rag_manager = RagManager(vector_db_class=ChromaDB, db_config=db_config, llm=llm, embed=embed,
                             etriever_cls=MultiQueryRetrieverWrapper)


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
    financebot = FinanceBot()

    # example_query = "根据武汉兴图新科电子股份有限公司招股意向书，电子信息行业的上游涉及哪些企业？"
    example_query = "武汉兴图新科电子股份有限公司"
    # example_query = "云南沃森生物技术股份有限公司负责产品研发的是什么部门？"

    final_result = financebot.handle_query(example_query)

    print(final_result)

# 测试 FinanceBotEx 主流程
def test_financebot_ex():
    # 使用Chroma 的向量库
    financebot = FinanceBotEx()

    # 使用milvus 的向量库
    # financebot = FinanceBotEx(vector_db_type='milvus')


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
    from utils.util import get_bge_chat_model

    # llm = get_qwen_models()
    # chat = get_zhipu_models()
    chat = get_bge_chat_model()
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
                   persist_directory='chroma_db',
                        embedding_function=settings.EMBED,
                        client=client)
    # 增加时间戳
    logger.info(f"Start searching at {datetime.datetime.now()}")
    query = "安徽黄山胶囊有限公司"
    docs = store.similarity_search(query, k=3)
    logger.info(f"End searching at {datetime.datetime.now()}")
    # 打印结果
    for doc in docs:
        logger.info("="*100)
        logger.info(doc.page_content)

    logger.info(f'检索文档个数：{len(docs)}')
# 测试Milvus的基础使用方法
def test_milvus_connect():
    from langchain_community.document_loaders import PyMuPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter


    mdb = MilvusDB(collection_name="LangChainCollectionImportTest", embed=settings.EMBED)
    
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
        # mdb.add_with_langchain(docs=batch)  # 入库
    
    # 查询
    # 增加时间戳
    logger.info(f"Start searching at {datetime.datetime.now()}")
    query = "安徽黄山胶囊有限公司"
    milvus_store = mdb.get_store()
    docs = milvus_store.similarity_search(query, k=3)
    logger.info(f"End searching at {datetime.datetime.now()}")
    # 打印结果
    for doc in docs:
        logger.info("="*100)
        logger.info(doc.page_content)

    logger.info(f'检索文档个数：{len(docs)}')

def clean_test_result():
    import json
    # 读取json文件
    test_file_path = os.path.join(os.getcwd(), "test_result/测试结果汇总/TestPlan_embed_bge_chat_glmlong_0_405_financebotex_by_dongming/answer_id_0_999.json")
    test_file_save_path = os.path.join(os.getcwd(), "test_result/测试结果汇总/TestPlan_embed_bge_chat_glmlong_0_405_financebotex_by_dongming/answer_id_0_999_clean.json")

    data_to_write = []

    with open(test_file_path, mode='r', encoding='utf-8') as f:
        for line in f:
            # 解析每一行的 JSON 数据
            record = json.loads(line)
            # print(record)
            answer = record.get("answer")

            # 将answer中"最终答案："字符之前的内容剔除掉
            if "最终答案：" in answer:
                answer = answer.split("最终答案：")[1]
                record["answer"] = answer
                print(record)
            data_to_write.append(record)
    with open(test_file_save_path, mode='w', encoding='utf-8') as f:
        for record in data_to_write:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    pass


if __name__ == "__main__":
    # test_agent()
    # test_rag()
    # test_import()
    # test_financebot()
    # test_financebot_ex()
    # test_llm_api()
    # test_chroma_connect()
    # test_milvus_connect()
    # test_answer_question()
    clean_test_result()
