import sys
import argparse
import subprocess
from utils.util import get_huggingface_embeddings, get_qwen_models
from rag.pdf_processor import PDFProcessor
import settings
import sqlite3
import re

def import_pdf(directory):
    # 使用 HuggingFace 的模型
    embed = settings.EMBED

    persist_path = settings.CHROMA_PERSIST_DB_PATH
    server_type = settings.CHROMA_SERVER_TYPE_IMPORT

    # 创建 PDFProcessor 实例
    pdf_processor = PDFProcessor(directory=directory,
                                 chroma_server_type=server_type,
                                 persist_path=persist_path,
                                 embed=embed)

    # 处理 PDF 文件
    pdf_processor.process_pdfs()


def start_chroma(path, port, host):
    # 启动 chroma 的命令
    command = f"chroma run --path {path} --port {port} --host {host}"
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"启动 Chroma 时出错: {e}")


def test_apik():
    # 假设 get_qwen_models 已经实现
    llm, chat, embed = get_qwen_models()
    print(llm.invoke(input="你好"))
    print(chat.invoke(input="你好"))
    print(embed.embed_query(text="你好"))


def add_indexes_to_all_tables(db_path):
    # 连接到 SQLite 数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        print(f"Processing table: {table_name}")

        # 获取表的所有字段
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()

        for column in columns:
            column_name = column[1]
            index_name = f"idx_{table_name}_{column_name}".replace(' ', '_')  # 替换空格以避免问题

            # 使用双引号转义表名和列名
            try:
                print(f"Creating index: {index_name} on column: {column_name}")
                cursor.execute(f"CREATE INDEX IF NOT EXISTS \"{index_name}\" ON \"{table_name}\" (\"{column_name}\");")
            except sqlite3.OperationalError as e:
                print(f"Error creating index for {column_name} in table {table_name}: {e}")

    # 提交更改并关闭连接
    conn.commit()
    conn.close()
    print("All indexes created successfully.")


def sanitize_name(name):
    """替换不安全字符为安全字符"""
    # 定义要替换的字符和替换后的字符
    replacements = {
        '(': '_lparen_',
        ')': '_rparen_',
        ' ': '_',  # 替换空格为下划线
        '-': '_dash_',  # 替换连字符为下划线
        # 可以根据需要添加更多替换规则
    }
    
    for unsafe_char, safe_char in replacements.items():
        name = name.replace(unsafe_char, safe_char)
    
    return name

def rename_tables_and_columns(db_path):
    # 连接到 SQLite 数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        sanitized_table_name = sanitize_name(table_name)

        # 如果表名需要更改，重命名表
        if sanitized_table_name != table_name:
            print(f"Renaming table: {table_name} to {sanitized_table_name}")
            cursor.execute(f"ALTER TABLE \"{table_name}\" RENAME TO \"{sanitized_table_name}\";")
            table_name = sanitized_table_name  # 更新当前表名

        # 获取表的所有字段
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()

        for column in columns:
            column_name = column[1]
            sanitized_column_name = sanitize_name(column_name)

            # 如果字段名需要更改，重命名字段
            if sanitized_column_name != column_name:
                print(f"Renaming column: {column_name} to {sanitized_column_name} in table {table_name}")
                cursor.execute(f"ALTER TABLE \"{table_name}\" RENAME COLUMN \"{column_name}\" TO \"{sanitized_column_name}\";")

    # 提交更改并关闭连接
    conn.commit()
    conn.close()
    print("All names sanitized successfully.")


def main():
    parser = argparse.ArgumentParser(description="Entroy script for executing jobs.")
    parser.add_argument('--job', type=str, required=True, help='Job to execute: importpdf, startchroma, testapik')

    # 添加 importpdf 任务的参数
    parser.add_argument('--dir', type=str, help='Directory for PDF files')

    # 添加 startchroma 任务的参数
    parser.add_argument('--path', type=str, default='chroma_db', help='Path for Chroma DB')
    parser.add_argument('--port', type=int, default=8000, help='Port to run Chroma on')
    parser.add_argument('--host', type=str, default='localhost', help='Host address for Chroma server')

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    if args.job == 'importpdf':
        if not args.dir:
            print("请提供 --dir 参数以指定 PDF 文件目录")
        else:
            import_pdf(args.dir)
    elif args.job == 'startchroma':
        start_chroma(args.path, args.port, args.host)
    elif args.job == 'testapik':
        test_apik()
    elif args.job == 'addindexes':
        add_indexes_to_all_tables(settings.SQLDATABASE_URI)
    elif args.job == 'renametables':
        rename_tables_and_columns(settings.SQLDATABASE_URI)
    else:
        print("未知的任务类型。请使用: importpdf, startchroma, 或 testapik")


if __name__ == "__main__":
    main()
