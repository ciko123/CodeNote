# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI
# 导入LangChain的消息类型
from langchain.schema import (
    AIMessage,  # 代表AI生成的消息
    HumanMessage,  # 代表用户输入的消息
    SystemMessage  # 代表系统生成的消息或指令，用于指导AI的行为
)
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()

# 创建OpenAI聊天模型实例
# model: 使用的模型名称 (gpt-4o)
# temperature: 控制输出随机性，0表示最确定性的输出
model = ChatOpenAI(model="gpt-4o", temperature=0)

# 构建多轮对话的消息列表
messages = [
    # 系统消息：设定AI角色和行为模式
    SystemMessage(content="你是知识渊博的专家，知道很多著名书籍相关知识，请简洁的用20个字回答问题"),
    # 用户消息：自我介绍
    HumanMessage(content="我的身份是学员，名字叫小顾"),
    # AI消息：回应问候
    AIMessage(content="欢迎，有什么需要咨询的?"),
    # 用户消息：询问三国志作者
    HumanMessage(content="三国志作者的是谁？"),
    # AI消息：回答三国志作者
    AIMessage(content="《三国志》的作者是三国时期的历史学家陈寿。"),
    # 用户消息：询问红楼梦作者
    HumanMessage(content="红楼梦呢？"),
]

# 调用模型处理多轮对话并获取回复
response = model.invoke(messages)
print(response.content)