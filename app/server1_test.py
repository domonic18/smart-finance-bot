import requests

# 定义API的URL
url = "http://localhost:8082/query"

# 定义要发送的数据
data = {
    "input": "中国铁路通信信号股份有限公司的主要经营模式是怎样的？"
}
response = requests.post(url, json=data)

print(response.json()["output"])