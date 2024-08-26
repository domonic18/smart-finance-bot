from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langserve import add_routes
from utils.util import get_qwen_models
from utils.util import get_ernie_models

from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_core.prompts import HumanMessagePromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from fastapi.middleware.cors import CORSMiddleware

# llm, chat, embed = get_qwen_models()
llm, chat, embed = get_ernie_models()

# 创建 FastAPI 应用
app = FastAPI(
    title="Qwen API",
    version="0.1",
    description="Qwen API",
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有的来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许的HTTP方法
    allow_headers=["*"],  # 允许的请求头
)

# 构建Prompt模板
sys_msg = SystemMessagePromptTemplate.from_template(template="这是一个创意文案生成专家。")
user_msg = HumanMessagePromptTemplate.from_template(template="""
    用户将输入几个产品的关键字，请根据关键词生成一段适合老年市场的文案，要求：成熟，稳重，符合老年市场的风格。
    用户输入为：{ad_words}。
    营销文案为：
""")
messages = [sys_msg, user_msg]
prompt = ChatPromptTemplate.from_messages(messages=messages)                

# 添加路由
add_routes(
    app, 
    prompt | llm | StrOutputParser(),
    path="/gen",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8082)