# 导入类型提示模块
from typing import List
# 导入LangChain核心的输出解析器异常类
from langchain_core.exceptions import OutputParserException
# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI
# 导入LangChain核心的工具模块（虽然未使用但保留）
from langchain_core.tools import tool
# 导入LangChain核心的Pydantic输出解析器
from langchain_core.output_parsers import PydanticOutputParser
# 导入LangChain的输出修复解析器
from langchain.output_parsers import OutputFixingParser
# 导入LangChain核心的提示词模板类
from langchain_core.prompts import PromptTemplate
# 导入Pydantic的数据模型、字段类和模型验证器
from pydantic import BaseModel, Field, model_validator
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()

# 创建OpenAI聊天模型实例
# model: 使用的模型名称 (gpt-4o)
# temperature: 控制输出随机性，0.9表示较高随机性，有助于创造性修复
model = ChatOpenAI(model="gpt-4o", temperature=0.9)

# 定义电影数据模型
class Movie(BaseModel):
    name: str = Field(description="电影名称")
    director: str = Field(description="导演姓名")
    year: int = Field(description="上映年份")

# 创建Pydantic输出解析器实例
parser = PydanticOutputParser(pydantic_object=Movie)

# 定义有问题的输出（缺少必要字段）
# bad_output = '{"name": "卧虎藏龙", "director": "李安"}'  # 缺少year字段
# bad_output = "{'name': '卧虎藏龙', 'fare': 89.00}"  # 格式错误，字段不匹配
bad_output = '{"director": "冯小刚"}'  # 缺少name和year字段

# 尝试直接解析有问题的输出
try:
    parser.parse(bad_output)
except OutputParserException as e:
    print("错误:", e)   

print("======开始修复====")
# 创建输出修复解析器
# OutputFixingParser: 当解析失败时，使用LLM尝试修复输出格式
# parser: 基础解析器
# llm: 用于修复的模型
fix_parser = OutputFixingParser.from_llm(parser=parser, llm=model)
# 使用修复解析器处理有问题的输出
output = fix_parser.parse(bad_output)
print("修复后的输出类型:", type(output))
print("修复后的输出内容:", output)