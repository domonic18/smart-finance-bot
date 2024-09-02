import logging
import os
import datetime
from langgraph.prebuilt import create_react_agent
from langchain.tools.retriever import create_retriever_tool
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from rag import My_Chroma_RAG
from langchain_community.embeddings import HuggingFaceEmbeddings
from utils.util import get_qwen_models

# 连接大模型
llm, chat, embed = get_qwen_models()

embeddings = HuggingFaceEmbeddings(model_name="bert-base-chinese")


CHROMA_HOST = "localhost"
CHROMA_PORT = 8000

current_directory = os.getcwd()
SQLDATABASE_URI = os.path.join(current_directory, "app/dataset/dataset/博金杯比赛数据.db")

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 定义调用函数
def get_datetime() -> str:
    """
    获取当前时间
    """
    now = datetime.datetime.now()
    formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")

    return formatted_date

class FinanceBotEx:
    def __init__(self, llm=llm, chat=chat, embed=embed):
        self.llm = llm                      
        self.chat = chat
        self.embed = embed               
        self.tools = []

        self.rag = My_Chroma_RAG(host=CHROMA_HOST, port=CHROMA_PORT, llm=llm, chat=chat, embed=embed)
        
        self.agent_executor = self.init_agent()

    def init_rag_tools(self):

        # 给大模型 RAG 检索器工具
        retriever = self.rag.get_retriever()
        retriever_tool = create_retriever_tool(
            retriever=retriever,
            name="rag_search",
            description="按照用户的问题搜索相关的资料，对于招股书类的问题，you must use this tool!",
            # document_prompt=rag_prompt,
        )
        return retriever_tool

    def init_sql_tool(self, path):
        # 连接数据库
        path = SQLDATABASE_URI
        db = SQLDatabase.from_uri(f"sqlite:///{path}")
        toolkit = SQLDatabaseToolkit(db=db, llm=self.llm)
        sql_tools = toolkit.get_tools() # 工具
        
        return sql_tools

    def create_prompt(self):
        system_prompt = """你是一位金融助手，可以帮助用户查询数据库中的信息。
            你要尽可能的回答用户提出的问题，为了更好的回答问题，你可以使用工具进行多轮的尝试。
                                                
            # 关于retriever_tool工具的使用：
            1、你需要结合对检索出来的上下文进行回答问题。
            2、如果你不知道答案，就说你不知道。请使用不超过三句话的简洁回答。
            
            # 关于sql类工具的使用： 
            ## 工具使用规则                                     
            1、你需要根据用户的问题，创建一个语法正确的SQLite查询来运行，然后查看查询的结果并返回答案。
            2、除非用户指定了他们希望获得的特定数量的示例，否则总是将查询限制为最多5个结果。
            3、您可以按相关列对结果进行排序，以返回数据库中最有趣的示例。
            4、永远不要查询指定表的所有列以避免查询性能问题，你只查询给定问题的相关列即可。
            5、你必须在执行查询之前仔细检查查询。如果执行查询时出现错误，请重新编写查询并重试。
            6、请勿对数据库进行任何DML语句（INSERT，UPDATE，DELETE，DROP等）。
            
            ## 工具使用过程
            1、首先，你应该始终查看数据库中的表，看看可以查询什么，这一步骤很重要，注意不要跳过。
            2、然后，你应该查询最相关表的schema。
            
            ## 工具使用注意事项：
            1、如果生成的SQL语句中，字段带有英文括号()，请使用双引号包裹起来，例如：收盘价(元) 双引号包裹为 "收盘价(元)"。
            2、如果查询过程中SQL语句有语法错误，减少查询量,总体查询次数应控制在15次以内。      
                                                
            # 关于你的思考和行动过程，请按照如下格式：
            问题：你必须回答的输入问题
            思考：你应该总是考虑该怎么做
            行动：你应该采取的行动，应该是以下工具之一：{tool_names}
            行动输入：行动的输入
            观察：行动的结果
            ... (这个思考/行动/行动输入/观察可以重复N次)
            思考: 我现在知道最终答案了
            最终答案：原始输入问题的最终答案

            
            Begin!
                            
            """
        return system_prompt

    def init_agent(self):
        # 创建Agent
        retriever_tool = self.init_rag_tools()
        sql_tools = self.init_sql_tool(SQLDATABASE_URI)
        system_prompt = self.create_prompt()

        agent_executor = create_react_agent(
            self.chat, 
            tools=[get_datetime, retriever_tool] + sql_tools, 
            state_modifier = system_prompt
            )
        return agent_executor

    def handle_query(self, example_query):
        # 流式处理事件
        events = self.agent_executor.stream(
            {"messages": [("user", example_query)]},
            stream_mode="values",
        )

        # 打印流式事件的消息
        for event in events:
            event["messages"][-1].pretty_print()



if __name__ == "__main__":
    # example_query = "现在几点了？"
    # example_query = "湖南长远锂科股份有限公司变更设立时作为发起人的法人有哪些？"
    # example_query = "根据联化科技股份有限公司招股意见书，精细化工产品的通常利润率是多少？"
    example_query = "20210304日，一级行业为非银金融的股票的成交量合计是多少？取整。"
    
    finnance_bot_ex = FinanceBotEx(llm=llm, chat=chat, embed=embeddings)
    finnance_bot_ex.handle_query(example_query)


