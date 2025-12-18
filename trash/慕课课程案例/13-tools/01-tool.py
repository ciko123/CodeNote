# 导入LangChain核心的工具装饰器
# tool: 用于将函数转换为LangChain工具的装饰器
from langchain_core.tools import tool
# 导入Pydantic的基础模型和字段类
# BaseModel: 用于创建数据模型的基类
# Field: 用于定义模型字段的属性和描述
from pydantic import BaseModel, Field

# 注释掉的代码：使用Pydantic模型定义工具参数的另一种方式
# class CityModel(BaseModel):
#     city: str = Field(..., description="城市名称")


# 使用@tool装饰器创建工具函数
# parse_docstring=True: 表示解析函数的文档字符串来自动生成工具的参数模式
@tool(parse_docstring=True)
def get_weather(city: str)-> str:
    """获取天气信息

    Args:
        city (str): 城市名称

    Returns:
        str: 城市的天气信息
    """
    
    # 返回模拟的天气信息
    return "It's sunny in " + city



# 打印工具的属性信息
print(get_weather.name)        # 打印工具名称（函数名）
print(get_weather.description) # 打印工具描述（文档字符串的第一行）
print(get_weather.args)        # 打印工具参数信息
# 打印工具参数的JSON Schema格式，用于LLM理解参数结构
print(get_weather.args_schema.model_json_schema())


