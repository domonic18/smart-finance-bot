import requests

# 注意请求路径：常规路径后面添加一个 invoke
url = " http://localhost:8082/gen/invoke"

data = {"ad_words": "助听器"}

# 注意传参格式：外面包一层 input
response = requests.post(url=url, json={"input": data})

print(response.json()["output"])