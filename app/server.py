from fastapi import FastAPI, HTTPException
from langserve import add_routes
from fastapi.middleware.cors import CORSMiddleware
from finance_bot import FinanceBot
from finance_bot_ex import FinanceBotEx

finance_bot = FinanceBot()
finance_bot_ex = FinanceBotEx()


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


# 创建API路由
@app.post("/query", response_model=dict)
async def query(query: dict):  # 使用字典类型代替Query模型
    try:
        # 从字典中获取input
        input_data = query.get("input")
        result = finance_bot.handle_query(input_data)

        # 返回字典格式的响应
        return {"output": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/queryex", response_model=dict)
async def query(query: dict):  # 使用字典类型代替Query模型
    try:
        # 从字典中获取input
        input_data = query.get("input")
        result = finance_bot_ex.handle_query(input_data)

        # 返回字典格式的响应
        return {"output": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 添加路由
add_routes(
    app,
    finance_bot_ex.init_agent() | chat ,
    path="/chat",
)

# 运行Uvicorn服务器
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8082)
