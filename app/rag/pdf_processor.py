import os
import chromadb
import datetime
import logging
import uuid
import time
import argparse
from tqdm import tqdm 
from chromadb import Client
from chromadb import Settings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from langchain_chroma import Chroma
import sys

# 获取当前目录
current_directory = os.getcwd()
sys.path.append(os.path.join(current_directory, "app"))
from utils.util import get_qwen_models

llm , chat, embed = get_qwen_models()

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

        # 使用qwen模型的embeddings
        self.embedding_function = embed

        # 使用HuggingFaceEmbeddings
        # self.embedding_function = HuggingFaceEmbeddings(model_name="bert-base-chinese")
        
        self.chroma_db = self.__connect_with_langchain__()

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

    def __connect_with_langchain__(self):
        """
        连接到 Chroma 数据库
        """
        client = chromadb.HttpClient(host=self.host, port=self.port)

        chroma_db = Chroma(
                embedding_function=self.embedding_function,
                client=client
            )

        return chroma_db


    def add_with_langchain(self, docs):
        """
        将文档添加到数据库
        """
        self.chroma_db.add_documents(documents=docs)
            

class PDFProcessor:
    def __init__(self, directory, host, port):
        self.directory = directory
        self.chroma_db = ChromaDB(host=host, port=port)
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

        # 记录开始时间
        start_time = time.time()  
        total_docs_inserted = 0

        # 计算总批次
        total_batches = (len(docs) + batch_size - 1) // batch_size  

        with tqdm(total=total_batches, desc="Inserting batches", unit="batch") as pbar:
            for i in range(0, len(docs), batch_size):
                # 获取当前批次的样本
                batch = docs[i:i + batch_size]  

                # 将样本入库
                # 方式一：使用chromadb 的add方法
                # self.chroma_db.add(batch)

                # 方式二：使用chromadb 的add_with_langchain方法
                self.chroma_db.add_with_langchain(batch)

                # 更新已插入的文档数量
                total_docs_inserted += len(batch)  
            
                # 计算并显示当前的TPM
                elapsed_time = time.time() - start_time  # 计算已用时间（秒）
                if elapsed_time > 0:  # 防止除以零
                    tpm = (total_docs_inserted / elapsed_time) * 60  # 转换为每分钟插入的文档数
                    pbar.set_postfix({"TPM": f"{tpm:.2f}"})  # 更新进度条的后缀信息
                
                # 更新进度条
                pbar.update(1)  

    def process_pdfs(self):
        # 获取目录下所有的PDF文件
        pdf_files = self.load_pdf_files()

        for pdf_path in tqdm(pdf_files, desc="Processing PDFs"):
            # 读取PDF文件内容
            documents = self.load_pdf_content(pdf_path)

            # 将文本切分成小段
            docs = self.split_text(documents)

            # 将文档插入到ChromaDB
            self.insert_docs_chromadb(docs)

        print("PDFs processed successfully!")



if __name__ == "__main__":
    # 创建解析器
    parser = argparse.ArgumentParser(description="Process PDFs and interact with ChromaDB.")
    
    # 添加参数
    parser.add_argument('--directory', type=str, default="./app/dataset/pdf", help='Directory containing PDF files.')
    parser.add_argument('--host', type=str, default="localhost", help='ChromaDB host address.')
    parser.add_argument('--port', type=int, default=8000, help='ChromaDB port.')

    # 解析参数
    args = parser.parse_args()

    # 创建 PDFProcessor 实例
    pdf_processor = PDFProcessor(directory=args.directory, host=args.host, port=args.port)
    
    # 处理 PDF 文件
    pdf_processor.process_pdfs()
    
    # 如果需要清空数据库，可以调用下面的方法
    # pdf_processor.clear_database()