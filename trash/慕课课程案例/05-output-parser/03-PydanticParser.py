# 导入类型提示模块
from typing import List, Optional
# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI
# 导入LangChain核心的工具模块（虽然未使用但保留）
from langchain_core.tools import tool
# 导入LangChain核心的Pydantic输出解析器
from langchain_core.output_parsers import PydanticOutputParser
# 导入LangChain核心的提示词模板类
from langchain_core.prompts import PromptTemplate
# 导入Pydantic的数据模型和字段类
from pydantic import BaseModel, Field
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()

# 创建OpenAI聊天模型实例
# model: 使用的模型名称 (gpt-4o)
# temperature: 控制输出随机性，0.6表示中等随机性
model = ChatOpenAI(model="gpt-4o", temperature=0.6)

# 定义电影数据模型
# 使用Pydantic进行数据验证和类型检查
class Movie(BaseModel):
    title: str = Field(description="电影标题")
    director: str = Field(description="导演姓名")
    year: int = Field(description="上映年份", ge=1900, le=2023)  # 限制年份范围
    genres: List[str] = Field(description="电影类型列表")
    rating: Optional[float] = Field(description="电影评分，0-10之间", ge=0, le=10)  # 可选字段，限制评分范围

# 创建提示模板，包含输出格式说明
template = """
你是一个电影信息提取助手。请从以下文本中提取电影信息，并以JSON格式返回。

文本: {text}

{format_instructions}
"""

# 创建Pydantic输出解析器实例
# pydantic_object: 指定要解析的目标数据模型
parser = PydanticOutputParser(pydantic_object=Movie)

# 创建提示词模板
# template: 提示词模板字符串
# input_variables: 动态输入变量
# partial_variables: 预填充变量（格式说明）
prompt_template = PromptTemplate(
    template=template,
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# 定义电影信息文本
movie_text = """
《泰坦尼克号》是一部由詹姆斯·卡梅隆执导的史诗级浪漫灾难电影。
这部电影于1997年上映，讲述了穷画家杰克和贵族女露丝之间的爱情故事。
它被归类为爱情、灾难和剧情片，获得了评论界和观众的广泛好评，IMDb评分为8.8分。
"""

# 格式化提示
formatted_prompt = prompt_template.format_prompt(text=movie_text)
print("Formatted Prompt:",formatted_prompt)
print("==" * 20)

# 调用模型生成回复
response = model.invoke(formatted_prompt)
print("模型输出类型:", type(response))  # 打印模型的原始输出
print("模型输出:", response)  # 打印模型的原始输出

print("==" * 20)
# 使用Pydantic解析器处理回复，生成结构化对象
output = parser.invoke(response)
print(type(output))  # 打印解析后的对象类型
print(output)  # 打印解析后的对象内容