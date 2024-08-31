# Chroma 原生操作
import chromadb
from chromadb import Client
from chromadb import Settings
from langchain_core.prompts import ChatPromptTemplate
#引入Chroma向量数据库
from langchain_chroma import Chroma
#字符串格式化输出（解析器）
from langchain_core.output_parsers import StrOutputParser
#可运行对象（占位符）
from langchain_core.runnables import RunnablePassthrough
# 文档切分器
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pylibmagic
import magic

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import SystemMessagePromptTemplate #系统消息模板
from langchain_core.prompts import HumanMessagePromptTemplate #用户消息模板
from langchain_core.prompts import AIMessagePromptTemplate #挖空模板，一般不用
from langchain_core.prompts import ChatMessagePromptTemplate #通用消息模板
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage #三个消息

from langchain_core.runnables.base import RunnableLambda
from langchain_core.runnables.base import RunnableMap

from langchain_community.llms.tongyi import Tongyi
from langchain_community.chat_models import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings

# llm大模型
llm = Tongyi(model = "qwen-max",temperature=0.1,top_p=0.7,max_tokens=1024,api_key="sk-2be00aba82564503af9ca25d22cda9cd")
# chat大模型
chat = ChatTongyi(model = "qwen-max",temperature=0.1,top_p=0.7,max_tokens=1024,api_key="sk-2be00aba82564503af9ca25d22cda9cd")
# embedding大模型
embed = DashScopeEmbeddings(model="text-embedding-v3",dashscope_api_key="sk-2be00aba82564503af9ca25d22cda9cd")

from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import SystemMessage
# 智能体Agent初始化（使用预构建的LangGraph Agent来构建）
from langgraph.prebuilt import create_react_agent

# agent
class Agent_sql():
    
    def __init__(self,path):
        """连接本地数据库"""
        self.db = SQLDatabase.from_uri(f"sqlite:///{path}")
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=llm)
        self.tools = self.toolkit.get_tools() # 工具
        self.SQL_PREFIX = """You are an agent designed to interact with a SQL database.
            Given an input question, create a syntactically correct SQLite query to run, then look at the results of the query and return the answer.
            Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
            You can order the results by a relevant column to return the most interesting examples in the database.
            Never query for all the columns from a specific table, only ask for the relevant columns given the question.
            You have access to tools for interacting with the database.
            Only use the below tools. Only use the information returned by the below tools to construct your final answer.
            You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.
            
            DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
            
            To start you should ALWAYS look at the tables in the database to see what you can query.
            Do NOT skip this step.
            Then you should query the schema of the most relevant tables.
            如果所有表中都没有查询到相关的信息，就停止查询，返回没有查询到结果即可"""
        
        self.system_message = SystemMessage(content=self.SQL_PREFIX)
        self.agent_executor = create_react_agent(chat, self.tools, state_modifier =self.system_message)

    def get_result(self,input):
        """查询 Agent"""
        example_query = input#"请帮我查询出20210415日，建筑材料一级行业涨幅超过5%（不包含）的股票数量"
        #"上海华铭智能终端设备股份有限公司的首发战略配售结果如何？"
        
        events = self.agent_executor.stream(
            {"messages": [("user", example_query)]},
            stream_mode="values",
        )
        result_list = []
        for event in events:
            result_list.append(event["messages"][-1].content)
        return event["messages"][-1].content,result_list