from langchain.retrievers.multi_query import MultiQueryRetriever
from utils.logger_config import LoggerManager

logger = LoggerManager().logger

class RetrieverBase:
    """检索器基类"""
    def __init__(self, store, llm, **kwargs):
        self.store = store
        self.llm = llm
        logger.info(f'检索器所使用的Embed模型：{self.llm}')

    def create_retriever(self):
        """创建检索器，子类需要实现这个方法"""
        raise NotImplementedError("子类必须实现 create_retriever 方法")


class SimpleRetriever(RetrieverBase):
    """简单检索器实现"""
    def create_retriever(self):
        return self.store.as_retriever()


class MultiQueryRetrieverWrapper(RetrieverBase):
    """使用 MultiQueryRetriever 的检索器实现"""
    def create_retriever(self):
        # 使用当前的 LLM 创建 MultiQueryRetriever
        return MultiQueryRetriever.from_llm(
            retriever=self.store.as_retriever(),  # 这里可以自定义其他检索器
            llm=self.llm
        )
