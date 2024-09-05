import logging
import datetime
from langgraph.prebuilt import create_react_agent
from langchain.tools.retriever import create_retriever_tool
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from rag.rag import RagManager
import settings
from utils.logger_config import LoggerManager
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_core.prompts import HumanMessagePromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langgraph.checkpoint.memory import MemorySaver

logger = LoggerManager().logger


# 定义调用函数
def get_datetime() -> str:
    """
    获取当前时间
    """
    now = datetime.datetime.now()
    formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")

    return formatted_date

from typing import TypedDict, Annotated, List, Union
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
   # The input string
   input: str
   # The list of previous messages in the conversation
   chat_history: list[BaseMessage]
   # The outcome of a given call to the agent
   # Needs `None` as a valid type, since this is what this will start as
   agent_outcome: Union[AgentAction, AgentFinish, None]
   # List of actions and corresponding observations
   # Here we annotate this with `operator.add` to indicate that operations to
   # this state should be ADDED to the existing values (not overwrite it)
   intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]

class FinanceBotEx:
    def __init__(self, llm=settings.LLM, chat=settings.CHAT, embed=settings.EMBED):
        self.llm = llm
        self.chat = chat
        self.embed = embed
        self.tools = []

        self.rag = RagManager(llm=llm, embed=embed)

        self.agent_executor = self.init_agent()

    def init_rag_tools(self):
        # 给大模型 RAG 检索器工具
        # retriever = self.rag.get_retriever()
        retriever = self.rag.retriever_instance.create_retriever()
        
        retriever_tool = create_retriever_tool(
            retriever=retriever,
            name="rag_search",
            description="按照用户的问题搜索相关的资料，对于招股书类的问题，you must use this tool!",
        )
        return retriever_tool

    def init_sql_tool(self, path):
        # 连接数据库
        db = SQLDatabase.from_uri(f"sqlite:///{path}")
        toolkit = SQLDatabaseToolkit(db=db, llm=self.llm)
        sql_tools = toolkit.get_tools()  # 工具

        return sql_tools

    @staticmethod
    def create_sys_prompt():
        system_prompt = """你是一位金融助手，可以帮助用户查询数据库中的信息。
            你要尽可能的回答用户提出的问题，为了更好的回答问题，你可以使用工具进行多轮的尝试。
                                                
            # 关于retriever_tool工具的使用：
            1、你需要结合对检索出来的上下文进行回答问题。
            2、你可以使用检索工具来查找相关的资料，以便回答用户的问题。
            3、检索的词语最好使用命名实体，例如：公司名称、人名、产品名称等。
            
            # 关于sql类工具的使用： 
            ## 工具使用规则                                     
            1、你需要根据用户的问题，创建一个语法正确的SQLite查询来运行，然后查看查询的结果并返回答案。
            2、除非用户指定了他们希望获得的特定数量的示例，否则总是将查询限制为最多5个结果。
            3、您可以按相关列对结果进行排序，以返回数据库中最有趣的示例。
            4、永远不要查询指定表的所有列以避免查询性能问题，你只查询给定问题的相关列即可。
            5、你必须在执行查询之前仔细检查查询。如果执行查询时出现错误，请重新编写查询并重试。
            6、请勿对数据库进行任何DML语句（INSERT，UPDATE，DELETE，DROP等）。
            7、SQL查询的表名和字段名，请务必双引号包裹起来，例如：收盘价(元) 双引号包裹为 "收盘价(元)"。
            
            ## 工具使用过程
            1、首先，你可以从记忆中寻找数据库表的信息，看看可以查询什么；如果记忆中没有，你可以查看数据库中的表；这一步骤很重要，注意不要跳过。
            2、然后，你应该查询最相关表的schema。
            3、之后，请把有哪些表以及相关表的schema记住，以便下次查询时优先从记忆中获取。
            
            ## 工具使用注意事项：
            1、如果查询过程中SQL语句有语法错误，减少查询量,总体查询次数应控制在15次以内。 
            2、请注意SQL语句的查询性能，SQL语句中如果有`SUM`、`COUNT(*)`的情况，务必使用`WITH FilteredIndustry`先筛选出符合条件的数据，然后再进行计算。
            3、对于复杂查询，请在生成 SQL 语句后使用 EXPLAIN 来评估查询计划，避免使用全表扫描或其他低效操作。

            # 关于最终答案：
            1、如果你不知道答案，就说你不知道。请使用不超过三句话的简洁回答。
                                                
            # 关于你的思考和行动过程，请按照如下格式：
            问题：你必须回答的输入问题
            思考：你应该总是考虑该怎么做
            行动：你应该采取的行动，应该是以下工具之一：{tool_names}
            行动输入：行动的输入
            观察：行动的结果
            ... (这个思考/行动/行动输入/观察可以重复N次)
            最终答案：原始输入问题的最终答案

            
            Begin!
                            
            """
        return system_prompt

    def init_agent(self):
        # 初始化 RAG 工具
        retriever_tool = self.init_rag_tools()

        # 初始化 SQL 工具
        sql_tools = self.init_sql_tool(settings.SQLDATABASE_URI)

        # 创建系统Prompt提示语
        system_prompt = self.create_sys_prompt()

        # 创建Agent
        agent_executor = create_react_agent(
            self.chat,
            tools=[get_datetime, retriever_tool] + sql_tools,
            state_modifier=system_prompt,
            checkpointer=MemorySaver()
            # state_modifier=modify_state_messages,
        )
        return agent_executor

    def handle_query(self, example_query):
        # 流式处理事件
        config = {"configurable": {"thread_id": "thread-1"}}

        try:
            events = self.agent_executor.stream(
                {"messages": [("user", example_query)]},
                config=config,
                stream_mode="values",
            )
            result_list = []
            # 打印流式事件的消息
            for event in events:
                logger.info(event["messages"][-1].pretty_print())

                result_list.append(event["messages"][-1].content)
            
            final_result = event["messages"][-1].content if result_list else None
            logger.info(f"查询过程: {result_list}")
            logger.info(f"最终结果: {final_result}")
            return final_result
        except Exception as e:
            logger.error(f"处理查询时出错: {e}")
            return f'{example_query} 处理查询时出错: {e}'
        

    
    def create_agent(self):
        """
        使用langgraph创建Agent，该函数还未启用
        """
        from langchain.agents.format_scratchpad import format_to_openai_functions
        from langchain.prompts import MessagesPlaceholder, ChatPromptTemplate
        from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
        from langchain.tools.render import format_tool_to_openai_function 
        from langchain_core.output_parsers import StrOutputParser

        sys_msg = SystemMessagePromptTemplate.from_template(template=self.create_sys_prompt())
        user_msg = HumanMessagePromptTemplate.from_template(template="""
            问题：{input}
        """)
        messages = [sys_msg, user_msg]
        prompt = ChatPromptTemplate.from_messages(messages=messages) 

        retriever_tool = self.init_rag_tools()  
        sql_tools = self.init_sql_tool(settings.SQLDATABASE_URI)

        tools = [ retriever_tool] + sql_tools
        
        llm_with_tools = self.chat.bind(
            functions=[format_tool_to_openai_function(t) for t in tools]
        )

        # agent = {
        #     "input": lambda x: x["input"],
        #     "agent_scratchpad": lambda x: format_to_openai_functions(x['intermediate_steps']),
        #     # "chat_history": lambda x: x["chat_history"]
        # } | prompt | llm_with_tools | OpenAIFunctionsAgentOutputParser()
        

        # 使用代理
        from langchain.agents import AgentExecutor
        # agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        # agent_executor.invoke({"input": "关于color有多少个字母?"})
        
        # 创建Agent
        agent_executor = create_react_agent(
            self.chat,
            tools=[get_datetime, retriever_tool] + sql_tools,
            state_modifier=prompt
        )

        # return agent_executor
        # return prompt | agent_executor | StrOutputParser()

        # return prompt | self.chat | agent_executor | StrOutputParser()