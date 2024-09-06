from pymilvus import MilvusClient
from langchain_community.vectorstores.milvus import Milvus

class MilvusDB:
    def __init__(self,
                 milvus_server_type="local",  # 服务器类型：http是http方式连接方式，local是本地读取文件方式
                 host="localhost", port=19530,  # 服务器地址，http方式必须指定
                 persist_path="milvus.db",  # 数据库的路径：如果是本地连接，需要指定数据库的路径
                 collection_name="LangChainCollection",  # 数据库的集合名称
                 embed=None  # 数据库的向量化函数
                 ):

        self.host = host
        self.port = port
        self.embed = embed
        self.collection_name = collection_name


        # NOTICE: langchain_milvus不支持local方式连接,要使用本地连接得用milvus原生API
        # if milvus_server_type == "http":
        #     connection_args={"uri": f"http://{host}:{port}"}


        # if milvus_server_type == "local":
        #     connection_args={"uri": f"tcp://{host}:{port}"}

        self.store = Milvus(
            collection_name=self.collection_name,
            connection_args={"uri": f"http://{host}:{port}"},
            embedding_function=self.embed,
            auto_id = True
        )

    def add_with_langchain(self, docs):
        self.store.add_documents(documents=docs)

    def get_store(self):
        return self.store
