import os
import logging
import time
from tqdm import tqdm
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag.vector_db import VectorDB
from rag.elasticsearch_db import TraditionDB
from utils.logger_config import LoggerManager

logger = LoggerManager().logger

class PDFProcessor:
    def __init__(self, directory, db_type='vector', **kwargs):
        """
        初始化 PDF 处理器
        :param directory: PDF 文件所在目录
        :param db_type: 数据库类型 ('vector' 或 'es')
        :param kwargs: 其他参数
        """
        self.directory = directory  # PDF 文件所在目录
        self.db_type = db_type  # 数据库类型
        self.file_group_num = kwargs.get('file_group_num', 20)  # 每组处理的文件数
        self.batch_num = kwargs.get('batch_num', 6)  # 每次插入的批次数量
        self.chunksize = kwargs.get('chunksize', 500)  # 切分文本的大小
        self.overlap = kwargs.get('overlap', 100)  # 切分文本的重叠大小
        logger.info(f"""
                    初始化PDF文件导入器:
                    配置参数：
                    - 导入的文件路径：{self.directory}
                    - 每次处理文件数：{self.file_group_num}
                    - 每批次处理样本数：{self.batch_num}
                    - 切分文本的大小：{self.chunksize}
                    - 切分文本重叠大小：{self.overlap}
                    """)

        # 根据数据库类型初始化相应的客户端
        if db_type == 'vector':
            self.vector_db = kwargs.get('vector_db')  # 向量数据库实例
            self.es_client = None

            logger.info(f'导入的目标数据库为：向量数据库')
        elif db_type == 'es':
            self.vector_db = None
            self.es_client = kwargs.get('es_client')  # Elasticsearch 客户端
            
            logger.info(f'导入的目标数据库为：ES数据库')
        else:
            raise ValueError("db_type must be either 'vector' or 'es'.")
    def load_pdf_files(self):
        """
        加载目录下的所有PDF文件
        """
        pdf_files = []
        for file in os.listdir(self.directory):
            if file.lower().endswith('.pdf'):
                pdf_files.append(os.path.join(self.directory, file))

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
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunksize,
            chunk_overlap=self.overlap,
            length_function=len,
            add_start_index=True,
        )
        docs = text_splitter.split_documents(documents)

        logging.info("Split text into smaller chunks with RecursiveCharacterTextSplitter.")
        return docs

    def insert_docs(self, docs, insert_function, batch_size=None):
        """
        将文档插入到指定的数据库，并显示进度
        :param docs: 要插入的文档列表
        :param insert_function: 插入函数
        :param batch_size: 批次大小
        """
        if batch_size is None:
            batch_size = self.batch_num

        logging.info(f"Inserting {len(docs)} documents.")
        start_time = time.time()
        total_docs_inserted = 0

        total_batches = (len(docs) + batch_size - 1) // batch_size

        with tqdm(total=total_batches, desc="Inserting batches", unit="batch") as pbar:
            for i in range(0, len(docs), batch_size):
                batch = docs[i:i + batch_size]
                insert_function(batch)  # 调用传入的插入函数

                total_docs_inserted += len(batch)

                # 计算并显示当前的TPM
                elapsed_time = time.time() - start_time
                if elapsed_time > 0:
                    tpm = (total_docs_inserted / elapsed_time) * 60
                    pbar.set_postfix({"TPM": f"{tpm:.2f}"})

                pbar.update(1)

    def insert_to_vector_db(self, docs):
        """
        将文档插入到 VectorDB
        """
        self.vector_db.add_with_langchain(docs)

    def insert_to_elasticsearch(self, docs):
        """
        将文档插入到 Elasticsearch
        """
        self.es_client.add_documents(docs)

    def process_pdfs_group(self, pdf_files_group):
        # 读取PDF文件内容
        pdf_contents = []

        for pdf_path in pdf_files_group:
            # 读取PDF文件内容
            documents = self.load_pdf_content(pdf_path)

            # 将documents 逐一添加到pdf_contents
            pdf_contents.extend(documents)

        # 将文本切分成小段
        docs = self.split_text(pdf_contents)

        if self.db_type == 'vector':
            # 将文档插入到 VectorDB
            self.insert_docs(docs, self.insert_to_vector_db)
        elif self.db_type == 'es':
            # 将文档插入到 Elasticsearch
            self.insert_docs(docs, self.insert_to_elasticsearch)
        else:
            raise ValueError("db_type must be either 'vector' or 'es'.")

    def process_pdfs(self):
        # 获取目录下所有的PDF文件
        pdf_files = self.load_pdf_files()

        group_num = self.file_group_num

        # group_num 个PDF文件为一组，分批处理
        for i in range(0, len(pdf_files), group_num):
            pdf_files_group = pdf_files[i:i + group_num]
            self.process_pdfs_group(pdf_files_group)

        print("PDFs processed successfully!")
