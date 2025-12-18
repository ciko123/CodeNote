# 导入类型提示模块：异步迭代器和迭代器
from typing import AsyncIterator, Iterator
# 导入LangChain核心的可运行基类
from langchain_core.runnables import Runnable

# 自定义文本转换器类，继承自Runnable基类
class TextTranformer(Runnable):
    
    def __init__(self, prefix: str = "处理后的文本: "):
        # 初始化前缀文本
        self.prefix = prefix
        
    def invoke(self, input: str) -> str:
        # 自定义文本处理逻辑
        processed_text = input.upper()  # 转换为大写
        return f"{self.prefix}{processed_text}"
    async def ainvoke(self, input: str) -> str:
        # 异步处理实现
        return self.invoke(input)
    
    def stream(self, input: str) -> Iterator[str]:
        # 流式处理，逐个字符生成结果
        processed_text = input.upper()
        for char in processed_text:
            yield f"{self.prefix}{char}"
            
    async def astream(self, input: str) -> AsyncIterator[str]:
        # 异步流式处理
        processed_text = input.upper()
        for char in processed_text:
            yield f"{self.prefix}{char}"
    
    def batch(self, inputs: list[str]) -> list[str]:
        # 批量处理多个输入
        return [self.invoke(input) for input in inputs]
    
    async def abatch(self, inputs: list[str]) -> list[str]:
        # 异步批量处理
        return [await self.ainvoke(input) for input in inputs]


# 创建文本转换器实例，设置自定义前缀
transformer = TextTranformer(prefix="结果：")
# 同步调用，将"hello world"转换为大写并添加前缀
result = transformer.invoke("hello world")
print(result)

print("stream:")

# 流式处理，逐个字符输出
for chunk in transformer.stream("hello world"):
    print(chunk)
    
print("batch:")

# 批量处理多个字符串
results = transformer.batch(["hello", "world"])
print(results)

print("\n异步 调用:")

# 导入异步编程模块
import asyncio

# 定义异步测试函数
async def async_test():
    # 异步调用
    result = await transformer.ainvoke("hello world")
    print(f"ainvoke: {result}")
    
    # 异步流式处理
    async for chunk in transformer.astream("hello world"):
        print(chunk)  # 每次输出一个字符前缀化内容
    
    # 异步批量处理
    abatch_results = await transformer.abatch(["hello", "world"])
    print("\naBatch 结果:")
    print(abatch_results)

# 运行异步测试
asyncio.run(async_test())