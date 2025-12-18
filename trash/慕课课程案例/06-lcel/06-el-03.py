# 导入LangChain核心的可运行Lambda类
from langchain_core.runnables import RunnableLambda

# 定义乘法函数，接受两个整数参数
def multiply(a: int, b: int) -> int:
    return a * b

# 定义字典包装函数，从字典中提取参数
def multiply_dict_warper(inputs: dict):
    # 从字典中提取键"a"和"b"的值，传递给multiply函数
    return multiply(inputs["a"], inputs["b"])

# 创建RunnableLambda实例，使用字典包装函数
runnable_multiply = RunnableLambda(multiply_dict_warper)
# 传入字典参数，计算2*3=6
print(runnable_multiply.invoke({"a": 2, "b": 3}))


# 定义元组包装函数，从元组中提取参数
def multiply_tuple_warper(inputs: tuple) -> int:
    # 从元组中提取索引0和1的值，传递给multiply函数
    return multiply(inputs[0], inputs[1])

# 创建RunnableLambda实例，使用元组包装函数
runnable_tuply_multiply = RunnableLambda(multiply_tuple_warper)
# 传入元组参数，计算3*3=9
print(runnable_tuply_multiply.invoke((3,3)))


# 定义参数类，用于封装乘法参数
class MultiplyParameters:
    def __init__(self, a: int, b: int):
        self.a = a
        self.b = b
        
# 定义对象包装函数，从对象中提取参数
def multiply_parameters_warper(inputs: MultiplyParameters) -> int:
    # 从MultiplyParameters对象中提取属性a和b，传递给multiply函数
    return multiply(inputs.a, inputs.b)

# 创建RunnableLambda实例，使用对象包装函数
runnable_param_multiply = RunnableLambda(multiply_parameters_warper)
# 传入MultiplyParameters对象，计算4*4=16
print(runnable_param_multiply.invoke(MultiplyParameters(4,4)))