# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()
# 导入LangChain的消息类型
from langchain.schema import SystemMessage, HumanMessage, AIMessage


# 创建OpenAI聊天模型实例
# model: 使用的模型名称 (gpt-3.5-turbo)
# temperature: 控制输出随机性，0.1表示较低随机性
model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
# 构建聊天消息列表
messages = [
    # 系统消息：设定AI角色和回答风格
    SystemMessage(content="你是一个知识渊博的助手，擅长回答各种问题。请简洁的回答，字数控制在20个字内"),
    # 用户消息：询问量子力学解释
    HumanMessage(content="请用一句话解释量子力学"),
    
]
# 调用模型处理消息列表
response = model.invoke(messages)
# 打印回复对象的类型（通常是AIMessage）
print(type(response))
# 打印回复内容
print(response)