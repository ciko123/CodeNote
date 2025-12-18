# 导入JSON模块，用于处理JSON格式的数据
import json
# 导入LangChain核心的工具类
# Tool: 用于创建工具的类，可以将函数包装为可调用的工具对象
from langchain_core.tools import Tool 

# 定义加法函数
def add(params: str) -> int:
    """执行两个数字的加法运算
    
    Args:
        params (str): JSON格式的参数字符串，包含a和b两个数字
        
    Returns:
        int: 两个数字的和
    """
    # 将JSON字符串解析为Python字典
    params = json.loads(params)
    # 从字典中获取参数a，默认值为0
    a = params.get("a",0)
    # 从字典中获取参数b，默认值为0
    b = params.get("b",0)
    
    # 返回两个数字的和
    return a + b
    
    
# 使用Tool类创建工具实例
# name: 工具名称，用于标识工具
# description: 工具描述，用于LLM理解工具的用途
# func: 工具对应的函数
add_tool = Tool(name="add", description="add two numbers", func=add)

# 调用工具并传入JSON格式的参数
# invoke(): 调用工具的方法，参数为JSON字符串
result = add_tool.invoke(json.dumps({"a":1,"b":2}))

# 打印工具执行结果
print(result)