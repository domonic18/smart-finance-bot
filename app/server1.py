from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from rag import My_Chroma_RAG
from fastapi.middleware.cors import CORSMiddleware
from utils import recognition
from utils import classify

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
)

# 定义请求模型
class Query(BaseModel):
    input: str  # 假设输入数据是一个字符串

# 定义响应模型
class Response(BaseModel):
    output: str  # 假设输出数据是一个字符串

def model(input):
    recognition_result = recognition(input)
    return classify(recognition_result)

# 创建API路由
@app.post("/query", response_model=Response)
async def query(query: Query):  # 使用模型类名Query而不是变量名query
    try:
        result = model(query.input)  # 确保query.input是Query模型的属性
        return Response(output=result)  # 返回Response模型的实例
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 运行Uvicorn服务器
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)