# 导入操作系统模块，用于访问环境变量
import os
# 导入LangChain的DeepSeek聊天模型
from langchain_deepseek import ChatDeepSeek
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()

# 创建DeepSeek聊天模型实例
# model: 使用的模型名称
# api_key: 从环境变量中获取DeepSeek API密钥
deepseek_chat = ChatDeepSeek(
    model="deepseek-chat", api_key=os.environ.get("DEEPSEEK_API_KEY")
)

# 调用模型，发送问题
response = deepseek_chat.invoke("你是谁")
# 打印模型的回复内容
print(response.content)
