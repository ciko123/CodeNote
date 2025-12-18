# 导入LangChain核心的可运行Lambda类
# RunnableLambda: 将普通函数包装为可运行对象，支持LCEL管道操作
from langchain_core.runnables import RunnableLambda


# 使用RunnableLambda创建可运行对象并使用管道操作符组合
# 第一个RunnableLambda: 将输入值加1
# 第二个RunnableLambda: 将结果乘以2
# |: 管道操作符，将第一个函数的输出传递给第二个函数
result = RunnableLambda(lambda x: x + 1) | RunnableLambda(lambda x: x * 2)

# 调用组合后的可运行对象并传入初始值2
# 执行流程: 2 + 1 = 3, 然后 3 * 2 = 6
print(result.invoke(2))