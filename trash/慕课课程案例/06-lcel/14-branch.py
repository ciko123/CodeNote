# 导入LangChain的可运行分支类
from langchain.schema.runnable import RunnableBranch
# 导入LangChain核心的工具装饰器
from langchain_core.tools import tool

# 使用@tool装饰器创建搜索工具
@tool
def search(question: str):
    """使用搜索引擎回答问题"""
    return f"{question}->搜索结果..."

# 使用@tool装饰器创建维基百科工具
@tool
def wiki(question: str):
    """从维基百科获取相关信息"""
    return f"{question}->获取wiki结果..."
    

# 创建条件分支，根据问题类型选择不同的工具
# RunnableBranch: 根据问题内容选择合适的工具
# (lambda x: "搜索" in x["question"].lower(), search): 如果问题包含"搜索"，使用搜索工具
# (lambda x: "获取" in x["question"].lower(), wiki): 如果问题包含"获取"，使用维基百科工具
# lambda x: "我不知道该怎么回答。": 默认情况返回错误信息
branch = RunnableBranch(
    (lambda x: "搜索" in x["question"].lower(), search),
    (lambda x: "获取" in x["question"].lower(), wiki),
    lambda x: "我不知道该怎么回答。"  # 默认回复
)

# 使用示例：调用分支并传入测试问题
# 问题"法国首都"不包含"搜索"或"获取"，因此返回默认回复
result = branch.invoke({"question": "法国首都"})
print(result)