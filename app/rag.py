import logging
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
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="bert-base-chinese")

from utils.util import get_qwen_models
# 连接大模型
llm, chat, embed = get_qwen_models()

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class My_Chroma_RAG():
    def __init__(self, start_chromdb_server=False, host="localhost", port=8000, noserver_path="chroma_db", llm=llm, chat=chat, embed=embed):
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
            self.store = Chroma(collection_name="langchain", 
                       embedding_function=embed,
                       persist_directory=noserver_path
                       )
        else:
            print("连接数据库失败")
            

    def get_result(self, input, k=4, mutuality=0.3):
        """获取RAG查询结果"""


        logging.basicConfig()
        logging.getLogger("langchain.retrievers").setLevel(logging.INFO)

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

    def format_docs(self, docs):
        # 返回检索到的资料文件名称
        logger.info(f"检索到资料文件个数：{len(docs)}")
        retrieved_files = "\n".join([doc.metadata["source"] for doc in docs])
        logger.info(f"资料文件分别是:\n{retrieved_files}")

        retrieved_content = "\n\n".join(doc.page_content for doc in docs)
        logger.info(f"检索到的资料为:\n{retrieved_content}")

        return retrieved_content

    def MulQueryRetrieverQuery(self, question):
        from langchain.retrievers.multi_query import MultiQueryRetriever

        # 把向量操作封装为一个基本检索器
        retriever = self.get_retriever()

        retriever_from_llm = MultiQueryRetriever.from_llm(
            retriever=retriever, llm=self.chat
        )

        logging.basicConfig()
        logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)

        unique_docs = retriever_from_llm.get_relevant_documents(query=question)
        unique_docs

        print(f'返回的文档个数：{len(unique_docs)}')
        print(f'返回的文档内容：')
        for doc in unique_docs:
            print(doc.page_content)



if __name__ == "__main__":

    rag = My_Chroma_RAG(host="localhost", port=8000, llm=llm, chat=chat, embed=embed)
    
    result = rag.get_result("湖南长远锂科股份有限公司变更设立时作为发起人的法人有哪些？")
    print(result)
    # rag.MulQueryRetrieverQuery("湖南长远锂科股份有限公司")