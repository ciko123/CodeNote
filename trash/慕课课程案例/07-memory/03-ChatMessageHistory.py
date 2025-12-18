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
        # 系统消息：定义AI助手的角色和行为
        (
            "system",
            "你是一个乐于助人的助手。尽你所能回答所有问题。简洁回复，20个字左右",
        ),
        # 消息占位符：用于插入对话历史
        MessagesPlaceholder(variable_name="messages"),
        # 用户消息：当前的问题
        (
            "user",
            "{question}",
        ),
    ]
)

# 创建处理链：提示词模板 -> 模型
chain = prompt_template | model

# 创建聊天消息历史实例
# ChatMessageHistory: 用于存储和管理对话历史
chat_message_history = ChatMessageHistory()

# 添加用户消息到历史记录
# add_user_message: 添加人类消息到历史记录
chat_message_history.add_user_message("你好，我是老顾，请将这句话从汉语翻译成英语:我喜欢编程。")
# 添加AI消息到历史记录
# add_ai_message: 添加AI回复到历史记录
chat_message_history.add_ai_message("I love programming")

# 打印消息历史，展示存储的对话内容
print(chat_message_history.messages)

print("===="*20)

# 调用链并传入当前问题和消息历史
# question: 当前的问题
# messages: 从ChatMessageHistory获取的消息历史
response = chain.invoke(
    {
        "question": "你好，你知道我是谁吗？",
        "messages": chat_message_history.messages,
    }
)

# 打印AI回复，展示基于ChatMessageHistory的记忆功能
print(response)

