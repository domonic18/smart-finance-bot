import os
import logging
import time
from tqdm import tqdm
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from rag.vector_db import VectorDB


class PDFProcessor:
    def __init__(self,
                 directory,  
                 vector_db: VectorDB,  # 向量数据库实例
                 file_group_num=20,  
                 batch_num=6,  
                 chunksize=500,  
                 overlap=100,  
                 embed=None):  

        self.directory = directory              # PDF文件所在目录
        self.file_group_num = file_group_num    # 每组处理的文件数
        self.batch_num = batch_num              # 每次插入的批次数量
        self.chunksize = chunksize              # 切分文本的大小
        self.overlap = overlap                  # 切分文本的重叠大小
        self.vector_db = vector_db              # 使用多态向量数据库实例

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
                self.vector_db.add_with_langchain(batch)

                # 更新已插入的文档数量
                total_docs_inserted += len(batch)

                # 计算并显示当前的TPM
                elapsed_time = time.time() - start_time  # 计算已用时间（秒）
                if elapsed_time > 0:  # 防止除以零
                    tpm = (total_docs_inserted / elapsed_time) * 60  # 转换为每分钟插入的文档数
                    pbar.set_postfix({"TPM": f"{tpm:.2f}"})  # 更新进度条的后缀信息

                # 更新进度条
                pbar.update(1)

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

        # 将文档插入到ChromaDB
        self.insert_docs_chromadb(docs, self.batch_num)

    def process_pdfs(self):
        # 获取目录下所有的PDF文件
        pdf_files = self.load_pdf_files()

        group_num = self.file_group_num

        # group_num 个PDF文件为一组，分批处理
        for i in range(0, len(pdf_files), group_num):
            pdf_files_group = pdf_files[i:i + group_num]
            self.process_pdfs_group(pdf_files_group)

        print("PDFs processed successfully!")
