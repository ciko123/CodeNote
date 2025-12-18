# 导入操作系统模块
import os
# 导入LangChain核心的聊天提示词模板类
from langchain_core.prompts import ChatPromptTemplate
# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()

# 创建OpenAI聊天模型实例
# model: 使用的模型名称 (gpt-4o)
# temperature: 控制输出随机性，0.6表示中等随机性
model = ChatOpenAI(model="gpt-4o", temperature=0.6)

# 创建聊天提示词模板
# from_template: 从字符串模板创建提示词
# {topic}: 动态变量，将被替换为具体主题
prompt_template = ChatPromptTemplate.from_template("给我讲一个关于{topic}的笑话")

# 使用LCEL管道操作符创建链
# |: 管道操作符，将左侧组件的输出作为右侧组件的输入
# prompt_template | model: 将提示词模板的输出传递给模型
chain = prompt_template | model

# 调用链并传入变量
# invoke: 调用链，自动将变量传递给提示词模板，然后将结果传递给模型
response = chain.invoke({"topic": "冰淇淋"})

# 打印模型回复
print(response)