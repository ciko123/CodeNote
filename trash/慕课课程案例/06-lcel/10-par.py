# 导入LangChain核心的可运行Lambda类和并行执行类
from langchain_core.runnables import RunnableLambda,RunnableParallel

# 定义加1函数
def add_one(x: int) -> int:
    return x + 1

# 定义乘2函数
def mul_two(x: int) -> int:
    return x * 2

# 定义乘3函数
def mul_three(x: int) -> int:
    return x * 3

# 定义加法函数，将并行执行的结果相加
def add_two(input: dict)-> int:
    # 从字典中提取mul_two和mul_three的结果并相加
    return input["mul_two"] + input["mul_three"]

# 将普通函数包装为可运行对象
runnable_1 = RunnableLambda(add_one)
runnable_2 = RunnableLambda(mul_two)
runnable_3 = RunnableLambda(mul_three)

# 将结果合并函数包装为可运行对象
runnable_4 = RunnableLambda(add_two)

# 创建并行处理流水线
# runnable_1: 先执行加1操作
# {"mul_two": runnable_2, "mul_three": runnable_3}: 并行执行乘2和乘3操作
# runnable_4: 最后将并行结果相加
pipeline = runnable_1 | {
    "mul_two": runnable_2,
    "mul_three": runnable_3
} | runnable_4

# 打印流水线的图形化表示（ASCII图）
print(pipeline.get_graph().draw_ascii())

# 调用流水线，传入初始值1
# 执行流程: 
# 1. 1 + 1 = 2
# 2. 并行执行: 2 * 2 = 4, 2 * 3 = 6
# 3. 合并结果: 4 + 6 = 10
print(pipeline.invoke(1))