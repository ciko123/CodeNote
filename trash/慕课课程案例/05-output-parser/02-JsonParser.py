# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI
# 导入LangChain核心的工具模块（虽然未使用但保留）
from langchain_core.tools import tool
# 导入LangChain核心的JSON输出解析器
from langchain_core.output_parsers import JsonOutputParser
# 导入LangChain核心的提示词模板类
from langchain_core.prompts import PromptTemplate
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()

# 创建OpenAI聊天模型实例
# model: 使用的模型名称 (gpt-4o)
# temperature: 控制输出随机性，0.6表示中等随机性
model = ChatOpenAI(model="gpt-4o", temperature=0.6)

# 定义提示词模板
# 包含格式说明和用户信息提取要求
template = """
你是一个助手，需要返回用户信息的JSON格式数据。

{format_instructions}

请返回一个包含以下字段的JSON对象：
- name: 用户的姓名
- age: 用户的年龄
- hobbies: 用户的爱好列表
- favorite_color: 用户最喜欢的颜色

用户信息：{text}
"""

# 创建JSON输出解析器实例
# JsonOutputParser: 将模型输出解析为Python字典对象
parser = JsonOutputParser()

# 创建提示词模板
# template: 提示词模板字符串
# input_variables: 动态输入变量
# partial_variables: 预填充变量（格式说明）
prompt_template = PromptTemplate(
    template=template,
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# 使用提示词模板生成具体提示词
prompt = prompt_template.format_prompt(text="用户叫张三，今年25岁，喜欢阅读、游泳和编程，最喜欢的颜色是蓝色。")
print("prompt:", prompt)

# 调用模型生成回复
response = model.invoke(prompt)
print(type(response))  # 打印模型的原始输出类型
print("response:", response)
print("==" * 20)
# 使用JSON解析器处理回复，提取字典内容
output = parser.invoke(response)
print(type(output))  # 打印解析后的对象类型
print(output)  # 打印解析后的对象内容