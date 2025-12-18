# 导入异步编程模块
import asyncio
# 导入操作系统模块
import os

# 导入LangChain社区的聊天消息历史类和SQL聊天消息历史类
# ChatMessageHistory: 内存中的消息历史存储
# SQLChatMessageHistory: 基于SQLite数据库的消息历史存储
from langchain_community.chat_message_histories import ChatMessageHistory, SQLChatMessageHistory
# 导入LangChain核心的人类消息类
from langchain_core.messages import HumanMessage
# 导入LangChain核心的提示词模板类和消息占位符类
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# 导入LangChain核心的带消息历史的可运行类
from langchain_core.runnables import RunnableWithMessageHistory
# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI

# 导入dotenv用于加载环境变量
from dotenv import load_dotenv
# 从.env文件加载环境变量
load_dotenv()

# 创建DeepSeek聊天模型实例
# model: 使用的模型名称 (deepseek-chat)
# base_url: DeepSeek API的基础URL
# api_key: 从环境变量获取DeepSeek API密钥
# temperature: 控制输出随机性，0表示确定性输出
model = ChatOpenAI(
    model="deepseek-chat",
    base_url="https://api.deepseek.com/v1",
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    temperature=0,
)

# 创建带消息历史的聊天提示词模板
# from_messages: 从消息列表创建提示词模板
# MessagesPlaceholder: 用于插入历史消息的占位符
prompt = ChatPromptTemplate.from_messages(
    [
        # 系统消息：定义AI助手的角色和回答方式
        (
            "system",
            "你是一个助手,用20个字以内回答",
        ),
        # 消息占位符：用于插入对话历史
        MessagesPlaceholder(variable_name="chat_history"),
        # 人类消息：当前的问题
        ("human", "{input}")
    ]
)

# 创建处理链：提示词模板 -> 模型
chain = prompt | model


# 定义获取会话历史的函数
def get_session_history(session_id: str):
    # 返回基于SQLite的消息历史实例
    # session_id: 会话标识符，用于区分不同的会话
    # connection: SQLite数据库连接字符串，数据将保存在history.db文件中
    return SQLChatMessageHistory(session_id=session_id,connection="sqlite:///history.db")
    
    

# 创建带消息历史的可运行链
# RunnableWithMessageHistory: 自动管理消息历史的包装器
# chain: 原始的处理链
# get_session_history: 获取会话历史的函数
# input_messages_key: 输入消息的键名
# history_messages_key: 历史消息的键名
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)

# 创建配置对象，指定会话ID
# session_id: "a2" - 使用会话ID a2
config = {"configurable":{"session_id": "a2"}}

# 注释掉的代码：第一次调用，介绍自己并询问中国大小
# r1 = chain_with_history.invoke(
#     {"input": "我是张三,请问中国有多大？"},
#     config=config
# )


# 调用链并询问AI是否知道用户名字
# 由于使用了SQLite数据库存储，即使程序重启，消息历史也会被保留
r1 = chain_with_history.invoke(
    {"input": "你知道我的名字叫什么吗？"},
    config=config
)

# 打印AI回复，展示基于SQLite数据库的持久化记忆功能
print(r1)