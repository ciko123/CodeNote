# 导入LangChain核心的可运行Lambda类和序列类
from langchain_core.runnables import RunnableLambda,RunnableSequence

# 定义加1函数
def add_one(x:int) -> int:
    return x + 1

# 定义乘2函数
def mul_two(x:int) -> int:
    return x * 2

# 将普通函数包装为可运行对象
add_one_runnable = RunnableLambda(func=add_one)
mul_two_runnable = RunnableLambda(func=mul_two)

# 可以使用RunnableSequence显式创建序列
# sequence = RunnableSequence(first=add_one_runnable, last=mul_two_runnable)

# 使用管道操作符创建序列（更简洁的方式）
# |: 管道操作符，自动创建RunnableSequence
sequence = add_one_runnable | mul_two_runnable

# 打印序列的图形化表示（ASCII图）
print(sequence.get_graph().draw_ascii())

# 调用序列，传入初始值1
# 执行流程: 1 + 1 = 2, 然后 2 * 2 = 4
print(sequence.invoke(1))