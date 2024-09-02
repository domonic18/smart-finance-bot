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

import sys
# 获取当前目录
sys.path.append(os.path.join(os.getcwd(), "app"))
from utils.chroma_util import ChromaDB

 

class PDFProcessor:
    def __init__(self, directory, chroma_server_type, persist_path):
        self.directory = directory
        self.chroma_db = ChromaDB(chroma_server_type=chroma_server_type, persist_path=persist_path)
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
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100, 
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
    parser.add_argument('--persist_path', type=str, default="chroma_db", help='ChromaDB local file path.')

    # 解析参数
    args = parser.parse_args()

    # 创建 PDFProcessor 实例
    pdf_processor = PDFProcessor(directory=args.directory, chroma_server_type="local", persist_path=args.persist_path)
    
    # 处理 PDF 文件
    pdf_processor.process_pdfs()
    