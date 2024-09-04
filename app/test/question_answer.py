import json
import os
from finance_bot import FinanceBot
from finance_bot_ex import FinanceBotEx
from utils.logger_config import LoggerManager

logger_manager = LoggerManager(name="TestQuestion", log_file="test_question.log")
logger = logger_manager.logger

class TestQuestion():
    """
    测试：
        下一步优化计划：多线程
        注意：比赛要求的是jsonl格式的文件，每一行都是一个独立的json
    """

    def __init__(self, input_question_all_path, out_answer_path):
        self.input_question_path = input_question_all_path
        self.out_answer_path = out_answer_path
        self.data = []

        log_path = os.path.join(self.out_answer_path, "test_question.log")
        logger_manager.set_log_file(log_path)

        # 一次性把数据存到内存中
        with open(self.input_question_path, mode='r', encoding='utf-8') as f:
            for line in f:
                # 解析每一行的 JSON 数据
                record = json.loads(line)
                self.data.append(record)

        # self.model = FinanceBot()
        self.model = FinanceBotEx()


    def question_inference(self, start=0, end=5):
        """start: 起始id，end：结束id+1"""

        file_name = f"answer_id_{start}_{end - 1}.json"
        file_path = os.path.join(self.out_answer_path, file_name)

        # 收集所有需要写入的数据
        data_to_write = []

        try:
            for item in self.data[start:end]:
                logger.info(f"ID: {item['id']}, Question: {item['question']}")
                answer = self.model.handle_query(item['question'])

                data_out = {"id": item['id'], "question": item['question'], "answer": answer}
                data_to_write.append(data_out)

            # 一次性写入所有数据
            with open(file=file_path, mode='a', encoding='utf-8') as f:
                for data in data_to_write:
                    json_line = json.dumps(data, ensure_ascii=False)
                    f.write(json_line + "\n")

        except Exception as e:
            logger.info(f"Error writing to file: {e}")
