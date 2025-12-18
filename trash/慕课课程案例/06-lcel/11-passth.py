# 导入LangChain核心的传递类和可运行Lambda类
# RunnablePassthrough: 将输入直接传递给下一个组件，不进行修改
from langchain_core.runnables import RunnablePassthrough, RunnableLambda


# 创建传递对象实例
passthrough = RunnablePassthrough()

# 定义添加额外信息的函数
def add_extra(input_text):
    # 返回包含原有字段和新增字段的数据
    return {"name": input_text["name"], "geeting": input_text["geeting"], "extra": "附加信息"}

# 将普通函数包装为可运行对象
add_extra_runnable = RunnableLambda(func=add_extra)

# 可以创建简单的传递链
# chain = passthrough | add_extra_runnable

# print(chain.invoke({"name": "张三","age": 18}))

print("===" * 20)

# 使用assign方法创建新的传递对象
# assign: 在传递原始输入的同时，添加或修改特定字段
# geeting: 新增字段，使用lambda函数根据name生成问候语
runnable_1 = passthrough.assign(geeting=lambda x: f"hello,{x['name']}!")

# 创建处理链：先添加geeting字段，然后添加extra字段
chain1 = runnable_1 | add_extra_runnable
# 调用链并传入测试数据
print(chain1.invoke({"name": "张三","age": 18}))