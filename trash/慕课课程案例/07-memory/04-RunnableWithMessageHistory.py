# 导入操作系统模块
import os
# 导入LangChain核心的消息类：AI消息和人类消息
from langchain_core.messages import AIMessage, HumanMessage
# 导入LangChain核心的提示词模板类和消息占位符类
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI
# 导入LangChain社区的聊天消息历史类
from langchain_community.chat_message_histories import ChatMessageHistory
# 导入LangChain核心的带消息历史的可运行类
from langchain_core.runnables import RunnableWithMessageHistory

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
prompt_template = ChatPromptTemplate.from_messages(
    [
        # 系统消息：定义AI助手的角色和能力
        (
            "system",
            "你是一个助手，擅长能力{ability}。用20个字以内回答，如果不知道的话，请回答“不知道”。",
        ),
        # 消息占位符：用于插入对话历史
        MessagesPlaceholder(variable_name="chat_history"),
        # 人类消息：当前的问题
        ("human", "{input}")
    ]
)

# 创建会话存储字典
# store: 用于存储不同会话的消息历史
store = {}

# 定义获取会话历史的函数
def get_session_history(session_id: str):
    # 如果会话ID不存在，创建新的消息历史
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    # 返回对应会话的消息历史
    return store[session_id]

# 创建处理链：提示词模板 -> 模型
chain = prompt_template | model

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

# 第一次调用：询问余弦定理
# session_id: "a1" - 创建或获取会话a1的历史
r1 = chain_with_history.invoke(
    {"ability":"数学","input": "请问什么是余弦定理？"},
    config={"configurable":{"session_id": "a1"}}
)

# 打印第一次回复
print(r1)

print("============================================================")

# 第二次调用：询问之前的问题
# 使用相同的session_id "a1"，AI能够记住之前的对话
r2 = chain_with_history.invoke(
    {"ability":"数学","input": "我刚才问题是什么？"},
    config={"configurable":{"session_id": "a1"}}
)

# 打印第二次回复，展示记忆功能
print(r2)

print("=======================B2=====================================")

# 第三次调用：询问之前的问题
# 使用不同的session_id "b2"，AI无法记住会话a1的对话
r3 = chain_with_history.invoke(
    {"ability":"数学","input": "我刚才问题是什么？"},
    config={"configurable":{"session_id": "b2"}}
)
# 打印第三次回复，展示不同会话的隔离性
print(r3)