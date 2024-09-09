import json
import os
from finance_bot import FinanceBot
from finance_bot_ex import FinanceBotEx
from utils.logger_config import LoggerManager
import datetime


logger_manager = LoggerManager(name="TestQuestion", log_file="test_question.log")
logger = logger_manager.logger

class TestQuestion():
    def __init__(self, 
                 input_question_path,                               # 测试用例文件的读取路径
                 output_answer_root_dic="test_result",              # 测试结果输出的保存目录
                 test_plan_name="TestPlan",                         # 测试计划名称
                 test_case_start=0,                                 # 测试用例的起始ID
                 test_case_end=5                                    # 测试用例的结束ID
                 ):
        self.input_question_path = input_question_path
        self.output_answer_root_dic = output_answer_root_dic
        self.test_case_data = []
        self.test_plan_name = test_plan_name.replace(" ", "_")
        self.test_case_start = test_case_start
        self.test_case_end = test_case_end

        self.__init_dirs()
        self.__load_data()
        self.__init_model()
        # 检查进度文件是否存在
        self.check_progress_file()
        logger.info(f"""
                    测试参数：
                    测试用例读取路径：{self.input_question_path}
                    测试结果输出路径：{self.output_answer_root_dic}
                    测试用例Start：{self.test_case_start}
                    测试用例End：{self.test_case_end}
        """)

    def __init_dirs(self):
        """初始化目录"""
        # 创建测试结果的根目录
        if not os.path.exists(self.output_answer_root_dic):
            os.makedirs(self.output_answer_root_dic)
        logger.info(f"Output root directory: {self.output_answer_root_dic}")

        # 创建测试计划的目录
        self.test_plan_dic = os.path.join(self.output_answer_root_dic, self.test_plan_name)
        if not os.path.exists(self.test_plan_dic):
            os.makedirs(self.test_plan_dic)
        logger.info(f"Test plan directory: {self.test_plan_dic}")

        # 创建用当前时间命名的详细结果目录
        current_time = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        self.test_result_dic = os.path.join(self.test_plan_dic, current_time)
        if not os.path.exists(self.test_result_dic):
            os.makedirs(self.test_result_dic)
        logger.info(f"Test result directory: {self.test_result_dic}")

        # 初始化测试进度文件路径    
        self.progress_file_path = os.path.join(self.test_plan_dic, "test_progress.json")

        # 初始化测试结果输出文件路径
        log_path = os.path.join(self.test_result_dic, "test_question.log")
        logger_manager.set_log_file(log_path)
    def __load_data(self):
        # 一次性把数据存到内存中
        with open(self.input_question_path, mode='r', encoding='utf-8') as f:
            for line in f:
                # 解析每一行的 JSON 数据
                record = json.loads(line)
                self.test_case_data.append(record)
    def __init_model(self):
        # self.model = FinanceBot()
        self.model = FinanceBotEx()
        logger.info(f'测试所使用的框架：FinanceBotEx')

    def check_progress_file(self):
        """检查进度文件是否存在，如果存在则读取进度信息"""
        if os.path.exists(self.progress_file_path):
            with open(self.progress_file_path, mode='r', encoding='utf-8') as f:
                progress_info = json.load(f)
                current_id = progress_info.get("current_progress", 0)
                case_end_id = progress_info.get("end_case_id", 0)

                if current_id < case_end_id:
                    logger.info(f"上次执行未完成，当前进度为: {current_id}")

                    # 提示用户是否继续执行
                    user_input = input("检测到上次未执行的结果，是否继续执行？(y/n): ")
                    if user_input.lower() == 'y':
                        self.test_case_start = current_id


    def update_progress(self, current):
        """更新进度信息"""
        progress_info = {
            "test_plan_name": self.test_plan_name,
            "start_case_id": self.test_case_start,
            "end_case_id": self.test_case_end,
            "current_progress": current
        }
        with open(self.progress_file_path, mode='w', encoding='utf-8') as f:
            json.dump(progress_info, f, ensure_ascii=False)

    def run_cases(self):
        """运行测试用例"""
        file_name = f"answer_id_{self.test_case_start}_{self.test_case_end - 1}.json"
        file_path = os.path.join(self.test_result_dic, file_name)

        # 收集所有需要写入的数据
        data_to_write = []

        for i in range(self.test_case_start, self.test_case_end):
            # 加异常保护，避免end大于文件中实际个数
            if i < 0 or i >= len(self.test_case_data):
                logger.error(f"无效的索引: {i}.")
                continue  # 跳过无效索引

            item = self.test_case_data[i]
            logger.info(f"ID: {item['id']}, Question: {item['question']}")

            try:
                answer = self.model.handle_query(item['question'])
            except Exception as e:
                # 如果发生了异常，那么后续继续跑case就没有意义了，应该抛出异常停止
                logger.error(f"Error processing question: {e}")
                raise

            data_out = {"id": item['id'], "question": item['question'], "answer": answer}
            data_to_write.append(data_out)

            # 更新进度
            self.update_progress(i + 1)
            try:
                with open(file=file_path, mode='a', encoding='utf-8') as f:
                    json_line = json.dumps(data_out, ensure_ascii=False)
                    f.write(json_line + "\n")

            except Exception as e:
                logger.error(f"Error writing to file: {e}")

        logger.info(f"测试用例 从起始 {self.test_case_start} 到 {self.test_case_end - 1} 执行完毕.")
