from langchain_core.callbacks import CallbackManagerForRetrieverRun
from utils.logger_config import LoggerManager
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from rag.elasticsearch_db import ElasticsearchDB
# ES需要导入的库
from typing import List
import logging
import settings
from langchain_community.document_transformers import (
    LongContextReorder,
)
from utils.util import get_rerank_model

logger = LoggerManager().logger


class SimpleRetrieverWrapper():
    """自定义检索器实现"""

    def __init__(self, store, llm, **kwargs):
        self.store = store
        self.llm = llm
        logger.info(f'检索器所使用的Chat模型：{self.llm}')

    def create_retriever(self):
        logger.info(f'初始化自定义的Retriever')

        # 初始化一个空的检索器列表
        retrievers = []
        weights = []

        # Step1：创建一个 多路召回检索器 MultiQueryRetriever
        chromadb_retriever = self.store.as_retriever()
        mq_retriever = MultiQueryRetrieverWrapper.from_llm(retriever=chromadb_retriever, llm=self.llm)

        # Step2：创建一个 上下文压缩检索器ContextualCompressionRetriever
        if settings.COMPRESSOR_ENABLE is True:
            compressor = LLMChainExtractor.from_llm(llm=self.llm)
            compression_retriever = ContextualCompressionRetrieverWrapper(
                base_compressor=compressor, base_retriever=mq_retriever
            )
            # 开启开关就使用压缩检索器
            retrievers.append(compression_retriever)
            weights.append(0.5)
            logger.info(f'已启用 ContextualCompressionRetriever')
        else:
            # 关闭开关就使用多路召回检索器
            retrievers.append(mq_retriever)
            weights.append(0.5)
            logger.info(f'已启用 MultiQueryRetriever')

        # Step3：创建一个 ES 检索器
        if settings.ELASTIC_ENABLE_ES is True:
            es_retriever = ElasticsearchRetriever()
            if settings.COMPRESSOR_ENABLE is True:
                # 如果开启了压缩检索器，就将ES检索器的权重调整为0.3
                es_compressor = LLMChainExtractor.from_llm(llm=self.llm)
                es_compression_retriever = ContextualCompressionRetrieverWrapper(
                    base_compressor=compressor, base_retriever=es_retriever
                )
                # 开启开关就使用压缩检索器
                retrievers.append(es_compression_retriever)
                weights.append(0.5)
                logger.info(f'已启用 ES的ContextualCompressionRetriever')
            else:
                retrievers.append(es_retriever)
                weights.append(0.5)
                logger.info(f'已启用 ElasticsearchRetriever')
        
        # 使用集成检索器，将所有启用的检索器集合在一起
        ensemble_retriever = EnsembleRetriever(retrievers=retrievers, weights=weights)
        return ensemble_retriever

class ElasticsearchRetriever(BaseRetriever):
    def _get_relevant_documents(self, query: str, ) -> List[Document]:
        """Return the first k documents from the list of documents"""
        es_connector = ElasticsearchDB()
        query_result = es_connector.search(query)
        
        # 增加长上下文重排序
        reordering = LongContextReorder()
        reordered_docs = reordering.transform_documents(query_result)
        # logger.info(f"ElasticSearch检索到的原始文档：")
        # for poriginal in query_result:
        #     logger.info(f"{poriginal}")

        logger.info(f"ElasticSearch检索重排后的文档：")
        for preordered in reordered_docs:
            logger.info(f"{preordered}")

        logger.info(f"ElasticSearch检索到资料文件个数：{len(query_result)}")

        if reordered_docs:
            return [Document(page_content=doc) for doc in reordered_docs]
        return []

    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        """(Optional) async native implementation."""
        es_connector = ElasticsearchDB()
        query_result = es_connector.search(query)
        if query_result:
            return [Document(page_content=doc) for doc in query_result]
        return []



class MultiQueryRetrieverWrapper(MultiQueryRetriever):
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
    ) -> List[Document]:
        """
        对MultiQueryRetriever进行重写，增加日志打印
        """
        queries = self.generate_queries(query, run_manager)
        if self.include_original:
            queries.append(query)
        documents = self.retrieve_documents(queries, run_manager)

        # 增加长上下文重排序
        reordering = LongContextReorder()
        reordered_docs = reordering.transform_documents(documents)

        logger.info(f'MultiQuery生成的检索语句：')
        for q in queries:
            logger.info(f"{q}")
        logger.info(f'MultiQuery检索到的资料文件：')
        for doc in documents:
            logger.info(f"{doc}")
        logger.info(f"MultiQuery检索到资料文件个数：{len(documents)}")

        return self.unique_union(reordered_docs)
        # return self.unique_union(documents)


class ContextualCompressionRetrieverWrapper(ContextualCompressionRetriever):
    from typing import Any, List
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun,
        **kwargs: Any,
    ) -> List[Document]:
        """
        对ContextualCompressionRetriever进行重写，增加日志打印
        """

        docs = self.base_retriever.invoke(
            query, config={"callbacks": run_manager.get_child()}, **kwargs
        )
        if docs:
            compressed_docs = self.base_compressor.compress_documents(
                docs, query, callbacks=run_manager.get_child()
            )
            logger.info(f'压缩后的文档长度：{len(compressed_docs)}')
            logger.info(f'压缩后的文档：{compressed_docs}')
            return list(compressed_docs)
        else:
            return []
    