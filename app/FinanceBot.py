import logging
import os
from rag import My_Chroma_RAG
from agent import Agent_SQL
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import SystemMessagePromptTemplate #系统消息模板
from langchain_core.prompts import HumanMessagePromptTemplate #用户消息模板
from langchain_core.prompts import AIMessagePromptTemplate #挖空模板，一般不用
from langchain_core.prompts import ChatMessagePromptTemplate #通用消息模板
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage #三个消息
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import FewShotChatMessagePromptTemplate
from langchain_openai import ChatOpenAI
from utils.util import get_qwen_models
from langchain_community.llms.tongyi import Tongyi
from langchain_community.chat_models import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings

# 连接大模型
llm, chat, embed = get_qwen_models()


BASE_URL = "http://direct.virtaicloud.com:45181/v1"
API_KEY = "EMPTY"
MODEL = "Qwen2_7B-chat-sft2"

CHROMA_HOST = "localhost"
CHROMA_PORT = 8000

current_directory = os.getcwd()
SQLDATABASE_URI = os.path.join(current_directory, "app/dataset/dataset/博金杯比赛数据.db")

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class FinanceBot:
    def __init__(self, llm=llm, chat=chat, embed=embed):
        self.llm = llm                      
        self.chat = chat
        self.embed = embed

        # 单独创建一个意图识别的大模型连接
        self.llm_recognition = self.init_recognition(base_url=BASE_URL, 
                                                 api_key=API_KEY, 
                                                 model=MODEL)                 
        
        self.rag = My_Chroma_RAG(host=CHROMA_HOST, port=CHROMA_PORT, llm=llm, chat=chat, embed=embed)

        # 单独创建一个agent的大模型连接
        self.agent = Agent_SQL(path=SQLDATABASE_URI, llm=llm, chat=chat, embed=embed)                       


    def init_recognition(self, base_url, api_key, model):
        """
        初始化意图识别的大模型
        """
        
        # 创建意图识别的大模型连接
        base_url = base_url
        api_key = api_key
        llm_recognition = ChatOpenAI(base_url=base_url,
                        api_key=api_key,
                        model=model,
                        temperature=0.01,
                        max_tokens=512
                        )
        # 测试连接
        try:
            # 发送一个简单的消息
            response = llm_recognition("你是谁？")
            print("Response from the model:", response)
            return llm_recognition
        except Exception as e:
            print("连接意图识别大模型失败:", e)
            return None

    def recognize_intent(self, input):
        """
        意图识别
        输入：用户输入的问题
        输出：识别出的意图，可选项：
        - rag_question
        - agent_question
        - other
        """

        # 如果意图识别的大模型连接失败，则直接使用Qwen大模型
        if self.llm_recognition is None:
            llm = self.llm
        else:
            llm = self.llm_recognition


        # 准备few-shot样例
        examples = [
            {"inn":"我想知道东方阿尔法优势产业混合C基金，在2021年年度报告中，前10大重仓股中，有多少只股票在报告期内取得正收益。",
             "out":"rag_question***我想知道东方阿尔法优势产业混合C基金，在2021年年度报告中，前10大重仓股中，有多少只股票在报告期内取得正收益。"},
            {"inn":"森赫电梯股份有限公司产品生产材料是什么？",
             "out":"rag_question***森赫电梯股份有限公司产品生产材料是什么？"},
            {"inn":"20210930日，一级行业为机械的股票的成交金额合计是多少？取整。",
             "out":"agent_question***20210930日，一级行业为机械的股票的成交金额合计是多少？取整。"},
            {"inn":"请查询在20200623日期，中信行业分类下汽车一级行业中，当日收盘价波动最大（即最高价与最低价之差最大）的股票代码是什么？取整。",
             "out":"agent_question***请查询在20200623日期，中信行业分类下汽车一级行业中，当日收盘价波动最大（即最高价与最低价之差最大）的股票代码是什么？取整。"},
            {"inn":"在2021年12月年报(含半年报)中，宝盈龙头优选股票A基金持有市值最多的前10只股票中，所在证券市场是上海证券交易所的有几个？取整。",
             "out":"agent_question***在2021年12月年报(含半年报)中，宝盈龙头优选股票A基金持有市值最多的前10只股票中，所在证券市场是上海证券交易所的有几个？取整。"},
            {"inn":"青海互助青稞酒股份有限公司报告期内面临的最重要风险因素是什么？",
             "out":"rag_question***在2021年12月年报(含半年报)中，宝盈龙头优选股票A基金持有市值最多的前10只股票中，所在证券市场是上海证券交易所的有几个？取整。"},
            {"inn":"我想知道海富通基金管理有限公司在2020年成立了多少只管理费率小于0.8%的基金？",
             "out":"agent_question***我想知道海富通基金管理有限公司在2020年成立了多少只管理费率小于0.8%的基金？"},
            {"inn":"为什么广东银禧科技股份有限公司核心技术大部分为非专利技术？",
             "out":"rag_question***为什么广东银禧科技股份有限公司核心技术大部分为非专利技术？"},
            {"inn":"在2021年报中，平安安享灵活配置混合C基金第八大重仓股的代码和股票名称是什么？",
             "out":"agent_question***在2021年报中，平安安享灵活配置混合C基金第八大重仓股的代码和股票名称是什么？"},
            {"inn":"浙江双飞无油轴承股份有限公司的主要原材料是什么？",
             "out":"rag_question***浙江双飞无油轴承股份有限公司的主要原材料是什么？"},
            {"inn":"珠海健帆生物科技股份有限公司的首席科学家是谁？",
             "out":"rag_question***珠海健帆生物科技股份有限公司的首席科学家是谁？"},
        ]
        
        # 定义样本模板
        examples_prompt = ChatPromptTemplate.from_messages(
                [
                    ("human", "{inn}"),
                    ("ai", "{out}"),
                ]
        )
        few_shot_prompt = FewShotChatMessagePromptTemplate(example_prompt=examples_prompt,
                                                examples=examples)
        final_prompt = ChatPromptTemplate.from_messages(
                    [
                        ('system', """
                         请学习我给定的样例，并据此回答我提出的问题:
                         如果既不属于agent_question也不属于rag_question,就回答other;
                         你只能回答agent_question***原始输入、rag_question***原始输入或者other***原始输入，
                         例如: other***今天天气真好:\n"""),
                        few_shot_prompt,
                        ('human', '{input}'),
                    ]
                )
        
        chain = final_prompt | llm

        result = chain.invoke(input=input)

        # 容错处理
        if hasattr(result, 'content'):
            # 如果 result 有 content 属性，使用它
            return result.content
        else:
            # 否则，直接返回 result
            return result


    def do_action(self, input):
        """
        根据意图执行相应的操作
        """
        
        if len(input.split("***")) != 2:
            return "other"
        
        question = input.split("***")[1]
        intent = input.split("***")[0]

        if intent == "rag_question":
            # 如果是RAG相关的问题
            result = self.rag.get_result(input=question)

            return result
        
        elif intent == "agent_question":
            # 如果是Agent相关的问题
            result, result_list = self.agent.get_result(input=question)

            return result
        else:
            # 其他类问题
            result = self.chat.invoke(input=question).content
            return result

    def get_fresult(self, input, intent, result):
        """
        融合信息
        """
        messages = [
            SystemMessagePromptTemplate.from_template(template="你是一个信息融合机器人"),
            HumanMessagePromptTemplate.from_template("""
                                                     请将{role}中的信息进行融合，其中输入的信息为3部分：
                                                     用户输入/回答结果/回答结果，
                                                     请将输入的信息融合，用更加合理通顺的语句将信息整合在一起，
                                                     如果有一部分信息含义没有意义请忽略,只保留得到的与问题相关的信息，删除掉没有的信息
                                                     例如：是的今天天气非常好，温度为24摄氏度。"""),
        ]
        
        prompt = ChatPromptTemplate.from_messages(messages=messages)
        
        chain = prompt | self.chat
        
        result = chain.invoke(input={"role": input + intent + result})
        
        return result.content

    def handle_query(self, query):
        """
        处理用户查询
        """
        intent = self.recognize_intent(query)
        logging.info(f"意图识别结果: {intent}")  

        logging.info(f"根据意图开展Action: {intent}")   
        result = self.do_action(intent)
        logging.info(f"经过Action执行结果: {result}") 
        
        final_result = self.get_fresult(input=query, intent=intent, result=result)
        logging.info(f"融合后的结果: {final_result}")
        
        return final_result
    

if __name__ == "__main__":

    query = "云南沃森生物技术股份有限公司负责产品研发的是什么部门？"

    financebot = FinanceBot(llm, chat, embed)
    final_result = financebot.handle_query(query)

    print(final_result)