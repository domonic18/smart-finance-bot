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

#rag
class My_Chroma_RAG():
    def __init__(self, host, port):
        """连接本地数据库"""
        settings = Settings(chroma_server_host=host, chroma_server_http_port=port)
        self.client = chromadb.Client(settings)
        self.store = Chroma(collection_name="langchain", 
                       embedding_function=embed,
                       client=self.client)


        # self.data_path = data_path
        # client = chromadb.PersistentClient(path=self.data_path)
        # self.store = Chroma(collection_name="langchain", 
        #                embedding_function=embed,
        #                client=client)

    def get_result(self,input,k=4,mutuality=0.5):
        """获取RAG查询结果"""
        # 第三个级别
        retriever = self.store.as_retriever(search_type="similarity_score_threshold",
                                      search_kwargs={"k": k, "score_threshold": mutuality})
        # RAG系统经典的 Prompt (A 增强的过程)
        prompt = ChatPromptTemplate.from_messages([
          ("human", """You are an assistant for question-answering tasks. Use the following pieces 
          of retrieved context to answer the question. 
          If you don't know the answer, just say that you don't know. 
          Use three sentences maximum and keep the answer concise.
          Question: {question} 
          Context: {context} 
          Answer:""")
        ])
        # 将 format_docs 方法包装为 Runnable
        format_docs_runnable = RunnableLambda(self.format_docs)
        # RAG 链
        rag_chain = (
            {"context": retriever | format_docs_runnable, 
             "question": RunnablePassthrough()}
            | prompt
            | chat
            | StrOutputParser()
        )
        
        return rag_chain.invoke(input=input)

    def get_chain(self):
        """获取RAG查询链"""

        retriever = self.store.as_retriever(search_type="similarity_score_threshold",
                                      search_kwargs={"k": 4, "score_threshold": 0.5})
        # RAG系统经典的 Prompt (A 增强的过程)
        prompt = ChatPromptTemplate.from_messages([
          ("human", """You are an assistant for question-answering tasks. Use the following pieces 
          of retrieved context to answer the question. 
          If you don't know the answer, just say that you don't know. 
          Use three sentences maximum and keep the answer concise.
          Question: {question} 
          Context: {context} 
          Answer:""")
        ])
        # 将 format_docs 方法包装为 Runnable
        format_docs_runnable = RunnableLambda(self.format_docs)
        # RAG 链
        rag_chain = (
            {"context": retriever | format_docs_runnable, 
             "question": RunnablePassthrough()}
            | prompt
            | chat
            | StrOutputParser()
        )

        return rag_chain

    # 把检索到的多条上下文的文本使用 \n\n 练成一个大的字符串
    def format_docs(self,docs):
        return "\n\n".join(doc.page_content for doc in docs)




