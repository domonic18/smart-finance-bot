import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.runnables.base import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from .chroma_conn import ChromaDB
from .retrievers import SimpleRetriever

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class RagManager:
    def __init__(self,
                 chroma_server_type="http",
                 host="localhost", port=8000,
                 persist_path="chroma_db",
                 llm=None, embed=None,
                 retriever_cls=SimpleRetriever, **retriever_kwargs):
        self.llm = llm
        self.embed = embed

        chrom_db = ChromaDB(chroma_server_type=chroma_server_type,
                            host=host, port=port,
                            persist_path=persist_path,
                            embed=embed)
        self.store = chrom_db.get_store()
        self.retriever_instance = retriever_cls(self.store, self.llm, **retriever_kwargs)

    def get_chain(self, retriever):
        """获取RAG查询链"""
        prompt = ChatPromptTemplate.from_messages([
            ("human", """You are an assistant for question-answering tasks. Use the following pieces 
          of retrieved context to answer the question. 
          If you don't know the answer, just say that you don't know. 
          Use three sentences maximum and keep the answer concise.
          Question: {question} 
          Context: {context} 
          Answer:""")
        ])
        format_docs_runnable = RunnableLambda(self.format_docs)
        rag_chain = (
                {"context": retriever | format_docs_runnable,
                 "question": RunnablePassthrough()}
                | prompt
                | self.llm
                | StrOutputParser()
        )

        return rag_chain

    def format_docs(self, docs):
        """格式化文档"""
        logging.info(f"检索到资料文件个数：{len(docs)}")
        retrieved_files = "\n".join([doc.metadata["source"] for doc in docs])
        logging.info(f"资料文件分别是:\n{retrieved_files}")

        retrieved_content = "\n\n".join(doc.page_content for doc in docs)
        logging.info(f"检索到的资料为:\n{retrieved_content}")

        return retrieved_content

    def get_result(self, question):
        """获取RAG查询结果"""
        retriever = self.retriever_instance.create_retriever()
        rag_chain = self.get_chain(retriever)
        return rag_chain.invoke(input=question)
