# 导入异步编程模块
import asyncio
# 导入LangChain核心的可运行Lambda类
from langchain_core.runnables import RunnableLambda

# 定义同步函数：将输入值加1
def add_one(x:int) -> int:
    return x + 1

# 定义异步函数：将输入值加2
async def add_one_async(x:int) -> int:
    return x + 2

# 创建RunnableLambda实例
# func: 同步函数实现
# afunc: 异步函数实现
runnable_add_one = RunnableLambda(
                    func=add_one,
                    afunc=add_one_async
                )

# 同步调用可运行对象，传入值1，结果为2
print(runnable_add_one.invoke(1))

# 批量处理，传入列表[1,2,3]，结果为[2,3,4]
print(runnable_add_one.batch([1,2,3]))

# 定义异步主函数
async def main():
    # 异步调用可运行对象，传入值4，结果为6（使用异步函数实现）
    print(await runnable_add_one.ainvoke(4))
    
# 运行异步主函数
asyncio.run(main())