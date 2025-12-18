# 导入LangChain核心的可运行Lambda类
from langchain_core.runnables import RunnableLambda

# 定义带类型注解的函数：输入整数，返回字符串
def add_one_with_types(x: int) -> str:
    # 将输入的整数加1，然后转换为字符串返回
    return str(x + 1)

# 创建 RunnableLambda 并使用 with_types 显式声明输入输出类型
# with_types: 显式指定可运行对象的输入和输出类型
# input_type=int: 声明输入类型为整数
# output_type=str: 声明输出类型为字符串
runnable = RunnableLambda(add_one_with_types).with_types(input_type=int, output_type=str)


# 打印输入类型的JSON Schema
# input_schema: 自动推断的输入类型模式
# model_json_schema(): 将模式转换为JSON格式
print(runnable.input_schema.model_json_schema()) # Show inferred input schema
# 打印输出类型的JSON Schema
# output_schema: 自动推断的输出类型模式
print(runnable.output_schema.model_json_schema()) # Show inferred output schema

# 调用可运行对象，传入整数4
# 执行流程: 4 + 1 = 5, 然后转换为字符串"5"
result = runnable.invoke(4)
print("\nResult:", result)