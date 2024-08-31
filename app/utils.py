from rag import My_Chroma_RAG
from agent import Agent_sql
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
from langchain_community.llms.tongyi import Tongyi
from langchain_community.chat_models import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings

# llm大模型
llm = Tongyi(model = "qwen-max",temperature=0.1,top_p=0.7,max_tokens=1024,api_key="sk-2be00aba82564503af9ca25d22cda9cd")
# chat大模型
chat = ChatTongyi(model = "qwen-max",temperature=0.1,top_p=0.7,max_tokens=1024,api_key="sk-2be00aba82564503af9ca25d22cda9cd")
# embedding大模型
embed = DashScopeEmbeddings(model="text-embedding-v3",dashscope_api_key="sk-2be00aba82564503af9ca25d22cda9cd")


def get_fresult(input,rag,agent):
    """融合信息"""
    messages = [
    SystemMessagePromptTemplate.from_template(template="你是一个信息融合机器人"),
        HumanMessagePromptTemplate.from_template(template="请将{role}中的信息进行融合，其中输入的信息为3部分：用户输入/回答结果/回答结果，请讲输入的信息融合，用更加          合理通顺的语句讲信息整合在一起，如果有一部分信息含义没有意义请忽略,只保留得到的与问题相关的信息，删除掉没有的信息例如：是的今天天气非常好，温度为24摄氏度。"),
    ]
    
    prompt = ChatPromptTemplate.from_messages(messages = messages)
    
    chain = prompt | chat
    
    result = chain.invoke(input = {"role":input+rag+agent})
    return result.content


# 意图识别
def recognition(input):
    """返回格式str："rag_question***珠海健帆生物科技股份有限公司的首席科学家是谁？"""
    ##调用模型
    base_url = "http://direct.virtaicloud.com:45181/v1"
    api_key = "xxxx"
    llm = ChatOpenAI(base_url=base_url,
                    api_key=api_key,
                    model="Qwen2_7B-chat-sft2",
                    temperature=0.01,
                    max_tokens=512)
    
    examples = [
        {"inn":"我想知道东方阿尔法优势产业混合C基金，在2021年年度报告中，前10大重仓股中，有多少只股票在报告期内取得正收益。","out":"rag_question***我想知道东方阿尔法优势产业混合C基金，在2021年年度报告中，前10大重仓股中，有多少只股票在报告期内取得正收益。"},
        {"inn":"森赫电梯股份有限公司产品生产材料是什么？","out":"rag_question***森赫电梯股份有限公司产品生产材料是什么？"},
        {"inn":"20210930日，一级行业为机械的股票的成交金额合计是多少？取整。","out":"agent_question***20210930日，一级行业为机械的股票的成交金额合计是多少？取整。"},
        {"inn":"请查询在20200623日期，中信行业分类下汽车一级行业中，当日收盘价波动最大（即最高价与最低价之差最大）的股票代码是什么？取整。","out":"agent_question***请查询在20200623日期，中信行业分类下汽车一级行业中，当日收盘价波动最大（即最高价与最低价之差最大）的股票代码是什么？取整。"},
        {"inn":"在2021年12月年报(含半年报)中，宝盈龙头优选股票A基金持有市值最多的前10只股票中，所在证券市场是上海证券交易所的有几个？取整。","out":"agent_question***在2021年12月年报(含半年报)中，宝盈龙头优选股票A基金持有市值最多的前10只股票中，所在证券市场是上海证券交易所的有几个？取整。"},
        {"inn":"青海互助青稞酒股份有限公司报告期内面临的最重要风险因素是什么？","out":"rag_question***在2021年12月年报(含半年报)中，宝盈龙头优选股票A基金持有市值最多的前10只股票中，所在证券市场是上海证券交易所的有几个？取整。"},
        {"inn":"我想知道海富通基金管理有限公司在2020年成立了多少只管理费率小于0.8%的基金？","out":"agent_question***我想知道海富通基金管理有限公司在2020年成立了多少只管理费率小于0.8%的基金？"},
        {"inn":"为什么广东银禧科技股份有限公司核心技术大部分为非专利技术？","out":"rag_question***为什么广东银禧科技股份有限公司核心技术大部分为非专利技术？"},
        {"inn":"在2021年报中，平安安享灵活配置混合C基金第八大重仓股的代码和股票名称是什么？","out":"agent_question***在2021年报中，平安安享灵活配置混合C基金第八大重仓股的代码和股票名称是什么？"},
        {"inn":"浙江双飞无油轴承股份有限公司的主要原材料是什么？","out":"rag_question***浙江双飞无油轴承股份有限公司的主要原材料是什么？"},
        {"inn":"珠海健帆生物科技股份有限公司的首席科学家是谁？","out":"rag_question***珠海健帆生物科技股份有限公司的首席科学家是谁？"},
    ]
    
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
                    ('system', '请学习我给定的样例，并据此回答我提出的问题,如果既不属于agent_question也不属于rag_question,就回答other,你只能回答agent_question***原始输入、rag_question***原始输入或者other***原始输入，例如: other***今天天气真好:\n"""'),
                    few_shot_prompt,
                    ('human', '{input}'),
                ]
            )
    chain = final_prompt | llm
    return chain.invoke(input=input).content

# 分类
def classify(input):
    if input.split("***")[0] == 'agent_question':
        agent = Agent_sql(path="/gemini/code/smart-finance-bot/app/data/博金杯比赛数据.db")
        print("是agent_question")
        result,result_list = agent.get_result(input = input.split("***")[1])
        return result
        
    if input.split("***")[0] == 'rag_question':
        rag = My_Chroma_RAG(data_path = "/gemini/code/my_chroma")
        print("是rag_question")
        result =  rag.get_result(input = input.split("***")[1])
        return result
        
    if input.split("***")[0] == 'other':
        print('other')
        result = chat.invoke(input = input.split("***")[1]).content
        return result




if __name__ == "__main__":
    data_chroma = My_Chroma(data_path = "/gemini/code/my_chroma")
    result = data_chroma.get_result(input = "云南沃森生物技术股份有限公司负责产品研发的是什么部门？")
    print(result)
