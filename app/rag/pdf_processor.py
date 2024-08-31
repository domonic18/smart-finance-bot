import os
import chromadb
import datetime
import logging
import uuid
from chromadb import Client
from chromadb import Settings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings


class HuggingFaceEmbeddingsFunction(EmbeddingFunction):
    def __init__(self, embedding_function):
        self.embedding_function = embedding_function

    def __call__(self, texts: Documents) -> Embeddings:
        embeddings = [self.embedding_function.embed_query(text) for text in texts]
        return embeddings


class ChromaDB:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.path = "chroma_db"
        self.collection_name = "langchain"
        self.client = self.__connect__()
        self.embedding_function = HuggingFaceEmbeddings(model_name="bert-base-chinese")


        # 将 embedding_function 传递给 HuggingFaceEmbeddingsFunction
        self.collect = self.client.create_collection(
            name=self.collection_name,
            embedding_function=HuggingFaceEmbeddingsFunction(self.embedding_function)
        )

    def __connect__(self):
        """
        连接到 Chroma 数据库
        """
        setting = Settings(chroma_server_host=self.host, chroma_server_http_port=self.port)

        try:
            self.client = Client(settings=setting)
        except chromadb.errors.APIError as e:
            print(f"Error connecting to ChromaDB: {e}")
            print("Trying to start a new instance...")
            # 如果连接失败，尝试启动一个新的实例
            self.client = Client(settings=setting)

        return self.client

    def clear_database(self):
        """
        清空 Chroma 数据库
        """
        self.client.delete_collection(name=self.collection_name)

    def add(self, docs):
        """
        将文档添加到数据库
        """
        documents = [doc.page_content for doc in docs]  # 提取文档内容
        metadata = [{'timestamp': datetime.datetime.now().isoformat(), 'source': doc.metadata.get('source', 'unknown')} for doc in docs]

        # 添加文档到数据库
        self.collect.add(
            documents=documents,
            metadatas=metadata,
            # 生成ids
            ids=[f"{uuid.uuid4()}" for _ in range(len(docs))]
        )

class PDFProcessor:
    def __init__(self, directory, host, port):
        self.directory = directory
        self.chroma_db = ChromaDB(host="localhost", port=8080)
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    def load_pdf_files(self):
        """
        加载目录下的所有PDF文件
        """
        pdf_files = [os.path.join(self.directory, file) for file in os.listdir(self.directory) if file.lower().endswith('.pdf')]
        logging.info(f"Found {len(pdf_files)} PDF files.")
        return pdf_files

    def load_pdf_content(self, pdf_path):
        """
        读取PDF文件内容
        """
        pdf_loader = PyMuPDFLoader(file_path=pdf_path)
        docs = pdf_loader.load()
        logging.info(f"Loading content from {pdf_path}.")
        return docs

    def split_text(self, documents):
        """
        将文本切分成小段
        """
        # 切分文档
        spliter = RecursiveCharacterTextSplitter(chunk_size=128, chunk_overlap=64)
        docs = spliter.split_documents(documents)

        logging.info("Split text into smaller chunks with RecursiveCharacterTextSplitter.")
        return docs
    
    def insert_docs_chromadb(self, docs, batch_size=6):
        """
        将文档插入到ChromaDB
        """
        # 分批入库
        logging.info(f"Inserting {len(docs)} documents into ChromaDB.")

        for i in range(0, len(docs), batch_size):
            batch = docs[i:i + batch_size]  # 获取当前批次的样本
            logging.info(f"Inserting batch {i+1} of {len(docs)} into ChromaDB.")
            # 将样本入库
            self.chroma_db.add(batch)
        

    def process_pdfs(self):
        # 获取目录下所有的PDF文件
        pdf_files = self.load_pdf_files()

        for pdf_path in pdf_files:
            # 读取PDF文件内容
            documents = self.load_pdf_content(pdf_path)

            # 将文本切分成小段
            docs = self.split_text(documents)

            # 将文档插入到ChromaDB
            self.insert_docs_chromadb(docs)

        print("PDFs processed successfully!")


if __name__ == "__main__":

    pdf_processor = PDFProcessor(directory="./app/data/pdf", host="localhost", port=8000)
    pdf_processor.process_pdfs()
    # 如果需要清空数据库，可以调用下面的方法
    # pdf_processor.clear_database()
