# 导入LangChain的聊天提示词模板类
from langchain.prompts import ChatPromptTemplate
# 导入LangChain的可运行分支类
from langchain.schema.runnable import RunnableBranch

# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI

# 导入dotenv用于加载环境变量
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()

# 创建中文提示词模板
# from_template: 从字符串模板创建提示词
# {concept}: 动态变量，将被替换为具体概念
chinese_prompt = ChatPromptTemplate.from_template("解释一下概念：{concept}")

# 创建英文提示词模板
# 要求用英文回复，且字符串长度不超过20个字
english_prompt = ChatPromptTemplate.from_template("解释一下概念：: {concept},用英文回复，字符串长度不超过20个字")

# 创建条件分支
# RunnableBranch: 根据输入中的language字段选择不同的提示词模板
# (lambda x: x["language"] == "zh", chinese_prompt): 如果language为zh，使用中文模板
# (lambda x: x["language"] == "en", english_prompt): 如果language为en，使用英文模板
# lambda x: "没有语言，抱歉，我无法解释。": 默认情况返回错误信息
branch = RunnableBranch(
    (lambda x: x["language"] == "zh", chinese_prompt),
    (lambda x: x["language"] == "en", english_prompt),
    lambda x: "没有语言，抱歉，我无法解释。"
)

# 创建处理链：先根据语言选择提示词模板，然后调用模型生成回复
chain = branch | ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)

# 调用链并传入测试数据
# concept: "机器学习", language: "en"
# 将使用英文提示词模板，要求用英文解释机器学习概念
print(chain.invoke({"concept": "机器学习", "language": "en"}))