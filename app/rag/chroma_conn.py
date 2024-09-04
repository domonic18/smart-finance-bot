import chromadb
from chromadb import Settings
from langchain_chroma import Chroma


class ChromaDB:
    def __init__(self,
                 chroma_server_type="local",  # 服务器类型：http是http方式连接方式，local是本地读取文件方式
                 host="localhost", port=8000,  # 服务器地址，http方式必须指定
                 persist_path="chroma_db",  # 数据库的路径：如果是本地连接，需要指定数据库的路径
                 collection_name="langchain",  # 数据库的集合名称
                 embed=None  # 数据库的向量化函数
                 ):

        self.host = host
        self.port = port
        self.path = persist_path
        self.embed = embed
        self.store = None

        # 如果是http协议方式连接数据库
        if chroma_server_type == "http":
            client = chromadb.HttpClient(host=host, port=port)

            self.store = Chroma(collection_name=collection_name,
                                embedding_function=embed,
                                client=client)

        if chroma_server_type == "local":
            self.store = Chroma(collection_name=collection_name,
                                embedding_function=embed,
                                persist_directory=persist_path)

        if self.store is None:
            raise ValueError("Chroma store init failed!")

    def add_with_langchain(self, docs):
        """
        将文档添加到数据库
        """
        self.store.add_documents(documents=docs)

    def async_add_with_langchain(self, docs):
        """
        异步添加文档到数据库
        """
        self.store.aadd_documents(documents=docs)

    def get_store(self):
        """
        获得向量数据库的对象实例
        """
        return self.store
