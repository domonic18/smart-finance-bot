import os
import datetime
import settings
from utils.logger_config import LoggerManager

logger = LoggerManager().logger


# 测试Agent主流程
def test_agent():
    from agent.agent import AgentSql
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
    from rag.rag import RagManager
    from rag.vector_db import ChromaDB
    from rag.retrievers import SimpleRetrieverWrapper
    llm, chat, embed = settings.LLM, settings.CHAT, settings.EMBED

    # Chroma的配置
    db_config = {
        "chroma_server_type": "http",
        "host": "localhost",
        "port": 8000,
        "persist_path": "chroma_db",
        "collection_name": "langchaintest",
    }

    # 多查询检索器
    rag_manager = RagManager(vector_db_class=ChromaDB, db_config=db_config, llm=llm, embed=embed,
                             etriever_cls=SimpleRetrieverWrapper)

    # example_query = "湖南长远锂科股份有限公司"
    example_query = "根据联化科技股份有限公司招股意见书，精细化工产品的通常利润率是多少？"

    result = rag_manager.get_result(example_query)

    print(result)


# 测试导入PDF到向量库主流程
def test_import_vector_db():
    from rag.pdf_processor import PDFProcessor
    from rag.vector_db import ChromaDB
    # from rag.vector_db import MilvusDB
    # from rag.vector_db import VectorDB
    llm, chat, embed = settings.LLM, settings.CHAT, settings.EMBED

    # 导入文件的文件目录
    directory = "./dataset/pdf"

    db_config = {
        "chroma_server_type": "local",
        "host": settings.CHROMA_HOST,
        "port": settings.CHROMA_PORT,
        "persist_path": "chroma_db",
        "collection_name": settings.CHROMA_COLLECTION_NAME,
    }
    # 创建向量数据库实例
    vector_db = ChromaDB(**db_config, embed=embed)

    # 创建 PDFProcessor 实例
    pdf_processor = PDFProcessor(directory=directory,
                                 vector_db=vector_db,
                                 es_client=None,
                                 embed=embed)

    # 处理 PDF 文件
    pdf_processor.process_pdfs()


def test_import_elasticsearch():
    # from rag.elasticsearch_db import TraditionDB
    from rag.elasticsearch_db import ElasticsearchDB
    from rag.pdf_processor import PDFProcessor

    llm, chat, embed = settings.LLM, settings.CHAT, settings.EMBED

    # 导入文件的文件目录
    directory = "./dataset/pdf"

    # 创建 Elasticsearch 数据库实例
    es_db = ElasticsearchDB()

    # 创建 PDFProcessor 实例
    pdf_processor = PDFProcessor(directory=directory,
                                 db_type="es",
                                 es_client=es_db,
                                 embed=embed)

    # 处理 PDF 文件
    pdf_processor.process_pdfs()


# 测试 FinanceBot主流程
def test_financebot():
    from finance_bot import FinanceBot
    financebot = FinanceBot()

    example_query = "根据武汉兴图新科电子股份有限公司招股意向书，电子信息行业的上游涉及哪些企业？"
    # example_query = "武汉兴图新科电子股份有限公司"
    # example_query = "云南沃森生物技术股份有限公司负责产品研发的是什么部门？"

    final_result = financebot.handle_query(example_query)

    print(final_result)


# 测试 FinanceBotEx 主流程
def test_financebot_ex():
    from finance_bot_ex import FinanceBotEx
    # 使用Chroma 的向量库
    financebot = FinanceBotEx()

    # 使用milvus 的向量库
    # financebot = FinanceBotEx(vector_db_type='milvus')

    # example_query = "现在几点了？"
    # example_query = "湖南长远锂科股份有限公司变更设立时作为发起人的法人有哪些？"
    # example_query = "根据联化科技股份有限公司招股意见书，精细化工产品的通常利润率是多少？"
    # example_query = "20210304日，一级行业为非银金融的股票的成交量合计是多少？取整。"
    example_query = "云南沃森生物技术股份有限公司负责产品研发的是什么部门？"
    # example_query = "根据武汉兴图新科电子股份有限公司招股意向书，电子信息行业的上游涉及哪些企业？"
    # example_query = "常熟风范电力设备股份有限公司的机器设备成新率是多少？"
    # example_query = "我想了解博时研究优选灵活配置混合(LOF)A基金,在2021年四季度的季报第3大重股。该持仓股票当个季度的涨跌幅?请四舍五入保留百分比到小数点两位。"
    # example_query = "帮我查一下鹏扬景科混合A基金在20201126的资产净值和单位净值是多少?"
    # example_query = "多晶硅成本约占宁波立立电子股份有限公司2007年度产品原材料成本的多大比例？"

    financebot.handle_query(example_query)


def test_answer_question():
    from test.question_answer import TestQuestion
    current_path = os.getcwd()

    input_file_path = os.path.join(current_path, "dataset/question.json")

    test_question = TestQuestion(input_file_path, test_case_start=0, test_case_end=2)
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
    from utils.util import get_zhipu_chat_model

    # llm = get_qwen_models()
    # chat = get_zhipu_models()
    chat = get_zhipu_models()
    # embed = get_qwen_embeddings()
    # embed = get_bge_embeddings()
    # embed = get_bce_embeddings()

    # print(llm.invoke(input="你好"))
    print(chat.invoke(input="你好"))
    # print(embed.embed_query(text="你好"))


def test_chroma_connect():
    import chromadb
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
        logger.info("=" * 100)
        logger.info(doc.page_content)

    logger.info(f'检索文档个数：{len(docs)}')


def test_milvus_connect():
    from langchain_community.document_loaders import PyMuPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from rag.vector_db import MilvusDB

    mdb = MilvusDB(collection_name="LangChainCollectionImportTest", embed=settings.EMBED)

    pdf_path = os.path.join(os.getcwd(), "dataset/pdf/0b46f7a2d67b5b59ad67cafffa0e12a9f0837790.pdf")

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
        logger.info("=" * 100)
        logger.info(doc.page_content)

    logger.info(f'检索文档个数：{len(docs)}')


def test_clean_test_result():
    import json
    # 读取json文件
    test_file_path = os.path.join(os.getcwd(),
                                  "test_result/测试结果汇总/TestPlan_embed_bge_chat_glmlong_0_405_financebotex_by_dongming"
                                  "/answer_id_0_999.json")
    test_file_save_path = os.path.join(os.getcwd(),
                                       "test_result"
                                       "/测试结果汇总/TestPlan_embed_bge_chat_glmlong_0_405_financebotex_by_dongming"
                                       "/answer_id_0_999_clean.json")

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


def test_es_connect():
    from elasticsearch import Elasticsearch

    # Password for the 'elastic' user generated by Elasticsearch
    ELASTIC_PASSWORD = "123abc"
    host = "175.27.143.233"
    port = 9200
    schema = "https"
    # url = f"{schema}://{host}:{port}"
    url = f"{schema}://elastic:{ELASTIC_PASSWORD}@{host}:{port}"

    # Create the client instance
    client = Elasticsearch(
        url,
        verify_certs=False,
        # ca_certs="./docker/elasticsearch/certs/ca/ca.crt",
        # basic_auth=("elastic", ELASTIC_PASSWORD)
    )

    # Successful response!
    print(client.info())


def test_es_add():
    from langchain_community.document_loaders import PyMuPDFLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from rag.elasticsearch_db import ElasticsearchDB

    pdf_path = os.path.join(os.getcwd(), "dataset/pdf/0b46f7a2d67b5b59ad67cafffa0e12a9f0837790.pdf")

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

    # 将所有文本进行切割
    def splitFiles(docs):
        paragraphs = []
        for i in range(len(docs)):
            paragraphs.append(text_splitter.create_documents([docs[i].page_content]))
        return paragraphs

    paragraphs = splitFiles(docs)

    es_client = ElasticsearchDB()

    # 数据入库，完成后刷新
    for docs in paragraphs:
        es_client.bluk_data(docs)
    es_client.flush()


def test_es_search():
    from rag.retrievers import ElasticsearchRetriever
    from rag.rag import RagManager
    from rag.vector_db import ChromaDB
    llm, chat, embed = settings.LLM, settings.CHAT, settings.EMBED

    es_retriever = ElasticsearchRetriever()

    # Chroma的配置
    db_config = {
        "chroma_server_type": "http",
        "host": "localhost",
        "port": 8000,
        "persist_path": "chroma_db",
        "collection_name": "langchaintest",
    }

    # 多查询检索器
    rag_manager = RagManager(vector_db_class=ChromaDB, db_config=db_config, llm=llm, embed=embed,
                             etriever_cls=es_retriever)

    example_query = "湖南长远锂科股份有限公司"
    example_query = "根据联化科技股份有限公司招股意见书，精细化工产品的通常利润率是多少？"
    example_query = "昇兴集团股份有限公司本次发行的拟上市证券交易所是？"

    result = rag_manager.get_result(example_query)

    print(result)


if __name__ == "__main__":
    # test_chroma_connect()
    # test_es_connect()
    # test_es_add()
    # test_import_vector_db()
    # test_import_elasticsearch()
    # test_agent()
    # test_rag()
    # test_financebot()
    test_financebot_ex()
    # test_llm_api()
    # test_answer_question()
    # test_clean_test_result()
    # test_es_search()
