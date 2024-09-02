
from FinanceBot import FinanceBot
import json
# llm大模型
# chat大模型
# embedding大模型

class TestQuestion():
    """
    测试：
        下一步优化计划：多线程
        注意：比赛要求的是jsonl格式的文件，每一行都是一个独立的json
    """
    def __init__(self,input_question_all_path= '/gemini/code/smart-finance-bot/app/dataset/question.json',out_answer_path = "/gemini/code/smart-finance-bot/app/dataset/"):
        self.input_question_path = input_question_all_path
        self.out_answer_path = out_answer_path
        self.data = []
        # 一次性把数据存到内存中
        with open(self.input_question_path, mode='r', encoding='utf-8') as f:
            for line in f:
                # 解析每一行的 JSON 数据
                record = json.loads(line)
                self.data.append(record)
        
        self.model = FinanceBot(start_chromdb_server=False,llm=llm, chat=chat, embed=embed)

    def question_inference(self,start = 0,end=5):
        """start:起始id，end：结束id+1"""
        file_name = f"answer_id_{start}_{end-1}.json"
        for item in self.data[start:end]:
            print(f"ID: {item['id']}, Question: {item['question']}")
            result = self.model.recognize_intent(item['question'])
            answer = self.model.do_action(result)
           
            data1 = {"id": item['id'], "question": item['question'], "answer": answer}
            with open(file =self.out_answer_path+file_name, mode='a', encoding='utf-8') as f:
                json_line = json.dumps(data1, ensure_ascii=False)
                f.write(json_line + "\n")
                