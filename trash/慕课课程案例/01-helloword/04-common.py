# 导入LangChain的OpenAI兼容聊天模型
from langchain_openai import ChatOpenAI

# 导入操作系统模块，用于访问环境变量
import os

# 导入dotenv用于加载环境变量
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()

# 创建通义千问聊天模型实例（使用OpenAI兼容接口）
# model: 使用的模型名称 (qwen-max是通义千问最强模型)
# base_url: 通义千问API的兼容模式端点地址
# api_key: 从环境变量中获取通义千问API密钥
# temperature: 控制输出随机性，0表示最确定性的输出
llm = ChatOpenAI(
    model="qwen-max",
    base_url=os.environ.get("TONGYI_BASE_URL"),
    api_key=os.environ.get("TONGYI_API_KEY"),
    temperature=0,
)

# 调用模型，发送问题
response = llm.invoke("你是谁")

# 打印模型的回复内容
print(response.content)
