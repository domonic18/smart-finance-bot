import os
import nltk
from nltk.corpus import stopwords
from utils.logger_config import LoggerManager

logger = LoggerManager().logger


class UtilNltk:
    def __init__(self):
        """
        加载停用词
        """
        # 获取当前路径
        # current_dir = os.getcwd()
        # nltk_data_path = os.path.join(current_dir, '..', 'nltk_data')
        # nltk.data.path.append(nltk_data_path)

        current_file_path = os.path.abspath(__file__)
        root_directory = os.path.dirname(current_file_path)
        nltk.data.path.append(os.path.join(root_directory, "nltk_data"))

        try:
            chinese_stopwords = stopwords.words('chinese')
            logger.info(f'加载停用词：{len(chinese_stopwords)} 个')
        except Exception as e:
            logger.error(f"加载停用词异常: {e}")