# 导入操作系统模块
import os
# 导入LangChain的提示词模板类
from langchain.prompts import PromptTemplate
# 导入LangChain核心的可配置字段类
from langchain_core.runnables import ConfigurableField
# 导入DeepSeek聊天模型
from langchain_deepseek import ChatDeepSeek
# 导入OpenAI聊天模型
from langchain_openai import ChatOpenAI
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()

# 创建可配置的模型实例
# ChatOpenAI: 创建OpenAI GPT-3.5-turbo模型作为默认选项
# configurable_alternatives: 设置可选择的模型替代方案
# ConfigurableField(id="llm"): 定义可配置字段标识符
# default_key="openai": 设置默认选项的键名
# deepseek_chat: 定义DeepSeek模型作为替代选项
model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1).configurable_alternatives(
    ConfigurableField(id="llm"),
    default_key="openai",
    deepseek_chat=ChatDeepSeek(model="deepseek-chat", api_key=os.environ.get("DEEPSEEK_API_KEY"))
)

# 创建可配置的提示词模板实例
# PromptTemplate.from_template: 创建默认的笑话提示词模板
# configurable_alternatives: 设置可选择的提示词替代方案
# default_key="joke": 设置默认选项的键名
# shi: 定义诗歌提示词模板作为替代选项
prompt = PromptTemplate.from_template("给我说一下关于{topic}的笑话").configurable_alternatives(
    ConfigurableField(id="prompt"),
    default_key="joke",
    shi = PromptTemplate.from_template("写一首诗关于：{topic}")
)

# 创建处理链：提示词模板 -> 模型
chain = prompt | model

# 调用链并动态配置模型和提示词模板
# with_config: 在运行时动态配置参数
# configurable: 指定要配置的可配置字段及其值
# "prompt": "shi": 使用诗歌提示词模板
# "llm": "deepseek_chat": 使用DeepSeek模型
print(chain.with_config(configurable={"prompt": "shi", "llm": "deepseek_chat"}).invoke({"topic": "熊"}))