import json
import sys
import os
import datetime

# 获取当前目录
sys.path.append(os.path.join(os.getcwd(), "app"))
from FinanceBot import FinanceBot

# llm大模型
# chat大模型
# embedding大模型

class TestQuestion():
    """
    测试：
        下一步优化计划：多线程
        注意：比赛要求的是jsonl格式的文件，每一行都是一个独立的json
    """
    def __init__(self, input_question_all_path , out_answer_path):
        self.input_question_path = input_question_all_path
        self.out_answer_path = out_answer_path
        self.data = []
        # 一次性把数据存到内存中
        with open(self.input_question_path, mode='r', encoding='utf-8') as f:
            for line in f:
                # 解析每一行的 JSON 数据
                record = json.loads(line)
                self.data.append(record)
        
        self.model = FinanceBot()

    def question_inference(self, start=0, end=5):
        """start: 起始id，end：结束id+1"""

        file_name = f"answer_id_{start}_{end-1}.json"
        file_path = os.path.join(self.out_answer_path, file_name)

        # 收集所有需要写入的数据
        data_to_write = []

        try:
            for item in self.data[start:end]:
                print(f"ID: {item['id']}, Question: {item['question']}")
                result = self.model.recognize_intent(item['question'])
                answer = self.model.do_action(result)
                
                data_out = {"id": item['id'], "question": item['question'], "answer": answer}
                data_to_write.append(data_out)

            # 一次性写入所有数据
            with open(file=file_path, mode='a', encoding='utf-8') as f:
                for data in data_to_write:
                    json_line = json.dumps(data, ensure_ascii=False)
                    f.write(json_line + "\n")

        except Exception as e:
            print(f"Error writing to file: {e}")


if __name__ == "__main__":
    current_path = os.getcwd()
    # 获取当前时间，以便生成以时间命名的文件夹
    current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

    input_question_all_path = os.path.join(current_path, "app/dataset/question.json")
    out_answer_path = os.path.join(current_path, "app/test/test_result", current_time)
    
    if out_answer_path and not os.path.exists(out_answer_path):
        os.makedirs(out_answer_path)

    test_question = TestQuestion(input_question_all_path, out_answer_path)
    test_question.question_inference(start=0, end=1)