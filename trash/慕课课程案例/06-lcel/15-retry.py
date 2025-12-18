# 导入LangChain核心的可运行Lambda类
from langchain_core.runnables import RunnableLambda
# 导入随机数模块
import random
# 导入时间模块
import time
# 导入日期时间模块
from datetime import datetime

# 定义加1函数
def add_one(x:int)->int:
    return x + 1

# 定义乘2函数，包含随机异常逻辑
def double(x:int)->int:
    
    # 记录开始执行时间
    start_time = time.time()
    # 格式化时间输出
    format_time = datetime.fromtimestamp(start_time).strftime("%Y-%m-%d %H:%M:%S")
    print(f"开始执行时间：{format_time}")
    
    # 生成0-1之间的随机数
    r = random.random()
    
    print(f"随机数：{r}")
    
    # 如果随机数大于0，抛出异常（实际上总是抛出异常）
    if r > 0:
        print("此代码有异常")
        raise ValueError(f"触发了异常，随机数为{r}")
    
    return x * 2

# 创建带重试机制的流水线
# RunnableLambda(add_one): 先执行加1操作
# RunnableLambda(double).with_retry(): 对乘2操作添加重试机制
# stop_after_attempt=5: 最多重试5次
# retry_if_exception_type=(ValueError,): 只对ValueError异常进行重试
pipline = (RunnableLambda(add_one) | 
            RunnableLambda(double).with_retry(
                stop_after_attempt=5,
                retry_if_exception_type=(ValueError,),
            )
)

# 使用try-catch捕获可能的异常
try:
    # 调用流水线，传入初始值2
    # 由于double函数总是抛出异常，重试5次后仍然失败
    print(pipline.invoke(2))
except Exception as e:
    # 打印最终的异常信息
    print(e)