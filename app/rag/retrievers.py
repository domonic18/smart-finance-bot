from langchain.retrievers.multi_query import MultiQueryRetriever
from utils.logger_config import LoggerManager
from langchain_core.retrievers import BaseRetriever
from langchain.retrievers import EnsembleRetriever
from langchain_core.documents import Document
from rag.elasticsearch_db import ElasticsearchDB
# ES需要导入的库
from typing import List
import logging
import settings

logger = LoggerManager().logger


class RetrieverBase():
    """检索器基类"""

    def __init__(self, store, llm, **kwargs):
        self.store = store
        self.llm = llm
        logger.info(f'检索器所使用的Embed模型：{self.llm}')

    def create_retriever(self):
        """创建检索器，子类需要实现这个方法"""
        raise NotImplementedError("子类必须实现 create_retriever 方法")


class SimpleRetriever(RetrieverBase):
    """自定义检索器实现"""

    def create_retriever(self):
        logger.info(f'初始化SimpleRetriever')

        # 创建一个 MultiQueryRetriever
        chromadb_retriever = self.store.as_retriever()
        mq_retriever = MultiQueryRetriever.from_llm(retriever=chromadb_retriever, llm=self.llm)
        logging.basicConfig()
        logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)

        if settings.ELASTIC_ENABLE_USE is True:
            # 创建一个 ES 的 Retriever
            es_retriever = ElasticsearchRetriever()

            # 将集合在一起
            ensemble_retriever = EnsembleRetriever(
                retrievers=[es_retriever, mq_retriever], weights=[0.5, 0.5])

            logger.info(f'使用的检索器类: {ensemble_retriever.__class__.__name__}')
            return ensemble_retriever
        else:
            logger.info(f'使用的检索器类: {mq_retriever.__class__.__name__}')
            return mq_retriever


class ElasticsearchRetrieverWrapper(RetrieverBase):
    def create_retriever(self):
        return ElasticsearchRetriever()


class ElasticsearchRetriever(BaseRetriever):
    def _get_relevant_documents(self, query: str, ) -> List[Document]:
        """Return the first k documents from the list of documents"""
        es_connector = ElasticsearchDB()
        query_result = es_connector.search(query)
        if query_result:
            return [Document(page_content=doc) for doc in query_result]
        return []

    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        """(Optional) async native implementation."""
        es_connector = ElasticsearchDB()
        query_result = es_connector.search(query)
        if query_result:
            return [Document(page_content=doc) for doc in query_result]
            # return [Document(page_content=doc['content'], metadata={"source": doc['source']}) for doc in query_result]
        return []
