import sys
import argparse
import subprocess
from utils.util import get_huggingface_embeddings, get_qwen_models
from rag.pdf_processor import PDFProcessor

def import_pdf(directory):
    # 假设 get_huggingface_embeddings 和 PDFProcessor 已经实现
    embed = get_huggingface_embeddings()

    persist_path = "chroma_db"
    server_type = "local"

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
    else:
        print("未知的任务类型。请使用: importpdf, startchroma, 或 testapik")

if __name__ == "__main__":
    main()
