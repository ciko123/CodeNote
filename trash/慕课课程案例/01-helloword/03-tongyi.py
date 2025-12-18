# 导入操作系统模块，用于访问环境变量
import os
# 导入LangChain的通义千问聊天模型
from langchain_community.chat_models.tongyi import ChatTongyi
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()

# 创建通义千问聊天模型实例
# model: 使用的模型名称 (qwen-max是通义千问最强模型)
# api_key: 从环境变量中获取通义千问API密钥
# base_url: 注释掉了自定义base_url，使用默认的DashScope端点
tongyi_chat = ChatTongyi(
    model="qwen-max",
    api_key=os.environ.get("TONGYI_API_KEY"),
    # base_url=os.environ.get("TONGYI_BASE_URL"),
)
# 调用模型，发送问题
response = tongyi_chat.invoke("你是谁")
# 打印模型的回复内容
print(response.content)
