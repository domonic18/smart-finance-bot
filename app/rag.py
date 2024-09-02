import logging
from langchain_core.prompts import ChatPromptTemplate
#字符串格式化输出（解析器）
from langchain_core.output_parsers import StrOutputParser
#可运行对象（占位符）
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.base import RunnableLambda
from langchain_core.runnables.base import RunnableMap
from utils.chroma_util import ChromaDB
from utils.util import get_qwen_models

# 连接大模型
llm, chat, embed = get_qwen_models()

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class RAG_Manager():
    def __init__(self, chroma_server_type="http", host="localhost", port=8000, persist_path="chroma_db", 
                llm=llm, chat=chat, embed=embed):

        self.llm = llm
        self.chat = chat
        self.embed = embed
        self.store = None
        chrom_db = ChromaDB(chroma_server_type=chroma_server_type, host=host, port=port, persist_path=persist_path)
        self.store = chrom_db.get_store()

    def get_chain(self, retriever):
        """获取RAG查询链"""
        
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
        logging.info(f"检索到资料文件个数：{len(docs)}")
        retrieved_files = "\n".join([doc.metadata["source"] for doc in docs])
        logging.info(f"资料文件分别是:\n{retrieved_files}")

        retrieved_content = "\n\n".join(doc.page_content for doc in docs)
        logging.info(f"检索到的资料为:\n{retrieved_content}")

        return retrieved_content

    def get_retriever(self, k=4, mutuality=0.3):

        retriever = self.store.as_retriever(search_type="similarity_score_threshold",
                        search_kwargs={"k": k, "score_threshold":mutuality})     
        
        return retriever

    def get_multi_query_retriever(self):
        from langchain.retrievers.multi_query import MultiQueryRetriever

        # 把向量操作封装为一个基本检索器
        retriever = self.get_retriever()

        retriever_from_llm = MultiQueryRetriever.from_llm(
            retriever=retriever, llm=self.chat
        )
        
        return retriever_from_llm
    
    def get_result(self, question, k=4, mutuality=0.3):
        """获取RAG查询结果"""

        retriever = self.get_retriever(k, mutuality)
        
        rag_chain = self.get_chain(retriever)

        return rag_chain.invoke(input=question)

    def get_result_by_multi_query(self, question):
        
        retriever = self.get_multi_query_retriever()

        rag_chain = self.get_chain(retriever)

        unique_docs = retriever.get_relevant_documents(query=question)

        return rag_chain.invoke(input=question)


if __name__ == "__main__":

    rag = RAG_Manager(host="localhost", port=8000, llm=llm, chat=chat, embed=embed)
    
    result = rag.get_result("湖南长远锂科股份有限公司变更设立时作为发起人的法人有哪些？")
    
    result = rag.get_result_by_multi_query("湖南长远锂科股份有限公司变更设立时作为发起人的法人有哪些？")

    print(result)