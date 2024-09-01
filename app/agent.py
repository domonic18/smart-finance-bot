import os
import sys
import logging
import pprint
from datetime import datetime
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage #三个消息
from langchain_core.runnables.base import RunnableMap
from langchain_community.llms.tongyi import Tongyi
from langchain_community.chat_models import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import SystemMessage
# 智能体Agent初始化（使用预构建的LangGraph Agent来构建）
from langgraph.prebuilt import create_react_agent

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
 

class Agent_SQL():
    
    def __init__(self, path, llm, chat, embed):
        self.llm = llm
        self.chat = chat
        self.embed = embed

        """连接本地数据库"""
        self.db = SQLDatabase.from_uri(f"sqlite:///{path}")
        self.toolkit = SQLDatabaseToolkit(db=self.db, llm=self.llm)
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
            特别注意：
            如果所有表中都没有查询到相关的信息，就停止查询，返回没有查询到结果即可。
            如果生成的SQL语句中，字段带有英文括号()，请使用双引号包裹起来，例如：收盘价(元) 双引号包裹为 "收盘价(元)"。
            如果查询过程中SQL语句有语法错误，减少查询量,总体查询次数应控制在15次以内。"""
        
        self.system_message = SystemMessage(content=self.SQL_PREFIX)
        self.agent_executor = create_react_agent(chat, self.tools, state_modifier =self.system_message)

    def get_chain(self):
        """获取链"""
        return self.agent_executor

    def get_result(self, input):
        """查询 Agent"""
        
        example_query = input
        logging.info(f"查询输入: {example_query}")

        events = self.agent_executor.stream(
            {"messages": [("user", example_query)]},
            stream_mode="values",
        )
        
        result_list = []
        try:
            for event in events:
                logging.info(pprint.pformat(event["messages"][-1].pretty_print()))
                result_list.append(event["messages"][-1].content)
        except Exception as e:
            logging.error(f"处理事件时发生错误: {e}")
        
        final_result = event["messages"][-1].content if result_list else None
        logging.info(f"最终结果: {final_result}")
        return final_result, result_list
    

if __name__ == "__main__":
    current_directory = os.getcwd()
    sql_path = os.path.join(current_directory, "app/dataset/dataset/博金杯比赛数据.db")
    agent = Agent_SQL(path=sql_path)
    input = "请帮我查询出20210415日，建筑材料一级行业涨幅超过5%（不包含）的股票数量"
    result,result_list = agent.get_result(input)
    print(result)
