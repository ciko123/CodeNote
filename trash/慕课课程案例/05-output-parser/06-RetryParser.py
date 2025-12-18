# 导入类型提示模块
from typing import Dict, List
# 导入LangChain的输出修复解析器和重试解析器
from langchain.output_parsers import OutputFixingParser,RetryWithErrorOutputParser
# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI
# 导入LangChain核心的工具模块（虽然未使用但保留）
from langchain_core.tools import tool
# 导入LangChain核心的Pydantic输出解析器
from langchain_core.output_parsers import PydanticOutputParser
# 导入LangChain核心的提示词模板类
from langchain_core.prompts import PromptTemplate
# 导入Pydantic的数据模型、字段类和字段验证器
from pydantic import BaseModel, Field, field_validator
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()

# 创建OpenAI聊天模型实例
# model: 使用的模型名称 (gpt-4o)
# temperature: 控制输出随机性，0.9表示较高随机性，有助于创造性修复
model = ChatOpenAI(model="gpt-4o", temperature=0.9)

# 定义电影推荐数据模型
class MovieRecommendation(BaseModel):
    movies: List[Dict] = Field(description="推荐的电影列表")
    
    @field_validator('movies')
    def check_movies(cls, field):
        # 定义每个电影对象必须包含的字段
        required_fields = ["title", "year", "genre", "rating", "description"]
        # 验证每个电影记录是否包含所有必要字段
        for movie in field:
            for field_name in required_fields:
                if field_name not in movie:
                    raise ValueError(f"电影记录缺少必要字段: {field_name}")
        return field


# 创建Pydantic输出解析器实例
parser = PydanticOutputParser(pydantic_object=MovieRecommendation)

# 创建修复解析器
# OutputFixingParser: 当解析失败时，使用LLM尝试修复输出格式
fixing_parser = OutputFixingParser.from_llm(
    parser=parser,
    llm=model
)

# 创建重试解析器
# RetryWithErrorOutputParser: 当解析失败时，使用LLM重新生成整个输出
retry_parser = RetryWithErrorOutputParser.from_llm(
    parser=parser,
    llm=model,
    max_retries=3  # 设置最大重试次数
)

# 定义提示模板
template = """
推荐一些{genre}类型的电影，格式如下：
{{
    "movies": [
        {{
            "title": "电影名称",
            "year": 发行年份,
            "genre": "电影类型",
            "rating": 评分,
            "description": "简短描述"
        }},
        {{
            "title": "电影名称2",
            "year": 发行年份2,
            "genre": "电影类型2",
            "rating": 评分2,
            "description": "简短描述2"
        }}
    ]
}}

请确保每个电影对象包含所有必要的字段: title, year, genre, rating, description。

{format_instructions}
"""

# 创建提示词模板
prompt_template = PromptTemplate(
    template=template,
    input_variables=["genre"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# 生成格式化的提示词
prompt_value = prompt_template.format_prompt(genre="科幻")
print("Formatted Prompt:", prompt_value)
print("==" * 20)

# 格式错误的输出：缺少字段和格式问题
# 输出缺少genre字段，且格式不符合要求
model_output = """
[
    {
        "title": "星际穿越",
        "year": 2014,
        "rating": 8.6,
        "description": "一部关于时空旅行和黑洞的科幻电影"
    },
    {
        "title": "盗梦空间",
        "year": 2010,
        "rating": 8.8,
        "description": "一部关于梦境和潜意识的电影"
    }
]
"""

# 使用 OutputFixingParser
try:
    print("=== 使用 OutputFixingParser ===")
    fixed_output = fixing_parser.parse(model_output)
    print("成功修复输出:", fixed_output)
    for movie in fixed_output.movies:
        print(f"电影: {movie['title']}")
except Exception as e:
    print(f"OutputFixingParser 修复失败: {e}")

print("==" * 20)

# 使用 RetryWithErrorOutputParser
try:
    print("\n=== 使用 RetryWithErrorOutputParser ===")
    # parse_with_prompt: 结合原始提示词进行重试
    retried_output = retry_parser.parse_with_prompt(model_output, prompt_value)
    print("成功重试输出:",retried_output)
    for movie in retried_output.movies:
        print(f"电影: {movie['title']}")
except Exception as e:
    print(f"RetryWithErrorOutputParser 重试失败: {e}")