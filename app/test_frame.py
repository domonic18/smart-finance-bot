import os
import datetime
from agent.agent import AgentSql
from rag.rag import RagManager
from rag.pdf_processor import PDFProcessor
from utils.util import get_qwen_models
from utils.util import get_huggingface_embeddings
from test.question_answer import TestQuestion
from finance_bot_ex import FinanceBotEx
from finance_bot import FinanceBot


# 测试Agent主流程
def test_agent():
    llm, chat, embed = get_qwen_models()

    sql_path = os.path.join(os.getcwd(), "app/dataset/dataset/博金杯比赛数据.db")

    agent = AgentSql(sql_path=sql_path, llm=chat, embed=embed)

    input = "请帮我查询出20210415日，建筑材料一级行业涨幅超过5%（不包含）的股票数量"

    result, result_list = agent.get_result(input)
    print(result)


# 测试RAG主流程
def test_rag():
    llm, chat, embed = get_qwen_models()
    rag = RagManager(host="localhost", port=8000, llm=llm, embed=embed)

    rag.get_result("湖南长远锂科股份有限公司变更设立时作为发起人的法人有哪些？")

    result = rag.get_result_by_multi_query("湖南长远锂科股份有限公司变更设立时作为发起人的法人有哪些？")

    print(result)


# 测试导入PDF到向量库主流程
def test_import():
    # llm , chat , embed = get_qwen_models()
    embed = get_huggingface_embeddings()

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
    llm, chat, embed = get_qwen_models()
    financebot = FinanceBot(llm=llm, chat=chat, embed=embed)

    example_query = "云南沃森生物技术股份有限公司负责产品研发的是什么部门？"
    financebot.handle_query(example_query)

    query = "云南沃森生物技术股份有限公司负责产品研发的是什么部门？"
    final_result = financebot.handle_query(query)

    print(final_result)


def test_answer_question():
    current_path = os.getcwd()
    # 获取当前时间，以便生成以时间命名的文件夹
    current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    input_question_all_path = os.path.join(current_path, "app/dataset/question.json")
    out_answer_path = os.path.join(current_path, "app/test_result", current_time)

    if out_answer_path and not os.path.exists(out_answer_path):
        os.makedirs(out_answer_path)

    test_question = TestQuestion(input_question_all_path, out_answer_path)
    test_question.question_inference(start=0, end=1)


# 测试 FinanceBotEx 主流程
def test_financebot_ex():
    llm, chat, embed = get_qwen_models()
    financebot = FinanceBotEx(llm=llm, chat=chat, embed=embed)

    # example_query = "现在几点了？"
    # example_query = "湖南长远锂科股份有限公司变更设立时作为发起人的法人有哪些？"
    # example_query = "根据联化科技股份有限公司招股意见书，精细化工产品的通常利润率是多少？"
    example_query = "20210304日，一级行业为非银金融的股票的成交量合计是多少？取整。"

    financebot.handle_query(example_query)


if __name__ == "__main__":
    test_agent()
    test_rag()
    test_import()
    test_financebot()
    test_answer_question()
    test_financebot_ex()
