# 引入
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
# ES需要导入的库
from typing import List
import re
import jieba
import nltk
from nltk.corpus import stopwords
import time
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, AuthenticationException
from elasticsearch import helpers
import settings
from utils.logger_config import LoggerManager
import os
import warnings

warnings.simplefilter("ignore")  # 屏蔽 ES 的一些Warnings

# 方式一：自动下载停用词
nltk.download('stopwords')

# 方式二：手动下载并指定 NLTK 数据目录
# 1. 从https://share.weiyun.com/wa3QocyY 下载stopwords.zip
# 2. 解压到C:\nltk_data\corpora\stopwords目录下。(mac/linux注意改为对应的目录)
# 3. 注释掉方式一的代码，启用下面的代码

# nltk_data_path = "C:\\nltk_data"
# nltk.data.path.append(nltk_data_path)
# try:
#     chinese_stopwords = stopwords.words('chinese')
#     print(chinese_stopwords)
# except Exception as e:
#     print(f"Error: {e}")


logger = LoggerManager().logger


class TraditionDB:
    def add_documents(self, docs):
        """
        将文档添加到数据库
        """
        raise NotImplementedError("Subclasses should implement this method!")

    def get_store(self):
        """
        获得向量数据库的对象实例
        """
        raise NotImplementedError("Subclasses should implement this method!")


class ElasticsearchDB(TraditionDB):
    def __init__(self,
                 schema=settings.ELASTIC_SCHEMA,
                 host=settings.ELASTIC_HOST,
                 port=settings.ELASTIC_PORT,
                 index_name=settings.ELASTIC_INDEX_NAME,
                 k=3
                 #  docs=docs
                 ):
        # 定义索引名称
        self.index_name = index_name
        self.k = k

        try:
            url = f"{schema}://elastic:{settings.ELASTIC_PASSWORD}@{host}:{port}"
            logger.info(f'初始化ES服务连接：{url}')

            self.es = Elasticsearch(
                url,
                verify_certs=False,
                # ca_certs="./docker/elasticsearch/certs/ca/ca.crt",
                # basic_auth=("elastic", settings.ELASTIC_PASSWORD)
            )

            response = self.es.info()  # 尝试获取信息
            logger.info(f'ES服务响应: {response}')
        except (ConnectionError, AuthenticationException) as e:
            logger.error(f'连接 Elasticsearch 失败: {e}')
            raise
        except Exception as e:
            logger.error(f'发生其他错误: {e}')
            logger.error(f'异常类型: {type(e).__name__}')  # 记录异常类型
            raise

    def to_keywords(self, input_string):
        """将句子转成检索关键词序列"""
        # 按搜索引擎模式分词
        word_tokens = jieba.cut_for_search(input_string)
        # 加载停用词表
        stop_words = set(stopwords.words('chinese'))
        # 去除停用词
        filtered_sentence = [w for w in word_tokens if not w in stop_words]
        return ' '.join(filtered_sentence)

    def sent_tokenize(self, input_string):
        """按标点断句,没有用到"""
        # 按标点切分
        sentences = re.split(r'(?<=[。！？；?!])', input_string)
        # 去掉空字符串
        return [sentence for sentence in sentences if sentence.strip()]

    def create_index(self):
        """如果索引不存在，则创建索引"""
        if not self.es.indices.exists(index=self.index_name):
            # 创建索引
            self.es.indices.create(index=self.index_name, ignore=400)

    def bluk_data(self, paragraphs):
        """批量进行数据灌库"""
        # 灌库指令
        actions = [
            {
                "_index": self.index_name,
                "_source": {
                    "keywords": self.to_keywords(para.page_content),
                    "text": para.page_content
                }
            }
            for para in paragraphs
        ]
        # 文本灌库
        helpers.bulk(self.es, actions)
        # # 灌库是异步的
        # time.sleep(2)

    def flush(self):
        # 刷新数据,数据入库完成以后刷新数据
        self.es.indices.flush()

    def search(self, query_string):
        """关键词检索"""
        # ES 的查询语言
        search_query = {
            "match": {
                "keywords": self.to_keywords(query_string)
            }
        }
        res = self.es.search(index=self.index_name, query=search_query, size=self.k)
        return [hit["_source"]["text"] for hit in res["hits"]["hits"]]

    def delete(self):
        """如果索引存在，则删除索引"""
        if self.es.indices.exists(index=self.index_name):
            # 创建索引
            self.es.indices.delete(index=self.index_name, ignore=400)

    def add_documents(self, docs):
        self.bluk_data(docs)
        self.flush()
