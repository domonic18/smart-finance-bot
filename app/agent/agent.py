# import logging
import pprint
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
from utils.logger_config import LoggerManager

logger = LoggerManager().logger

class AgentSql:
    
    def __init__(self, sql_path, llm, embed):
        self.llm = llm
        self.embed = embed

        """连接本地数据库"""
        self.db = SQLDatabase.from_uri(f"sqlite:///{sql_path}")
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
        self.agent_executor = create_react_agent(self.llm, self.tools, state_modifier=self.system_message)

    def get_chain(self):
        """获取链"""
        return self.agent_executor

    def get_result(self, input):
        """查询 Agent"""
        
        example_query = input
        logger.info(f"查询输入: {example_query}")

        events = self.agent_executor.stream(
            {"messages": [("user", example_query)]},
            stream_mode="values",
        )
        
        result_list = []
        try:
            for event in events:
                logger.info(event["messages"][-1].pretty_print())

                result_list.append(event["messages"][-1].content)
        except Exception as e:
            logger.error(f"处理事件时发生错误: {e}")
        
        final_result = event["messages"][-1].content if result_list else None
        logger.info(f"查询过程: {result_list}")
        logger.info(f"最终结果: {final_result}")
        return final_result, result_list
