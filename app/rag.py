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

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.base import RunnableLambda
from langchain_core.runnables.base import RunnableMap

from langchain_community.llms.tongyi import Tongyi
from langchain_community.chat_models import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings

from utils.util import get_qwen_models
# 连接大模型
llm, chat, embed = get_qwen_models()

class My_Chroma_RAG():
    def __init__(self,start_chromdb_server, host="localhost", port=8000, noserver_path="gemini/code/my_chroma", llm=llm, chat=chat, embed=embed):
        """连接本地数据库"""
        self.llm = llm
        self.chat = chat
        self.embed = embed
        # 连接到 Chroma 数据库
        if start_chromdb_server == True:
            settings = Settings(chroma_server_host=host, chroma_server_http_port=port)
            self.client = chromadb.Client(settings)
            self.store = Chroma(collection_name="langchain", 
                           embedding_function=embed,
                           client=self.client)
        if start_chromdb_server == False:
            self.client = chromadb.PersistentClient(path=noserver_path)
            self.store = Chroma(collection_name="langchain", 
                       embedding_function=embed,
                       client=self.client)
        else:
            print("连接数据库失败")
            

    def get_result(self, input, k=4, mutuality=0.3):
        """获取RAG查询结果"""

        rag_chain = self.get_chain(k, mutuality)

        return rag_chain.invoke(input=input)

    def get_chain(self, k=4, mutuality=0.3):
        """获取RAG查询链"""

        # retriever = self.store.as_retriever(search_type="similarity_score_threshold",
        #                               search_kwargs={"k": 4, "score_threshold": 0.5})
        
        retriever = self.store.as_retriever()

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
            | self.chat
            | StrOutputParser()
        )

        return rag_chain

    # 把检索到的多条上下文的文本使用 \n\n 练成一个大的字符串
    def format_docs(self,docs):
        return "\n\n".join(doc.page_content for doc in docs)




if __name__ == "__main__":
    from utils.util import get_qwen_models

    llm , chat , embed = get_qwen_models()

    rag = My_Chroma_RAG(host="localhost", port=8000, llm=llm, chat=chat, embed=embed)
    
    result = rag.get_result("内蒙古君正能源化工股份有限公司的法定代表人是谁？")
    print(result)