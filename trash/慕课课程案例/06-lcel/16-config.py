# 导入操作系统模块
import os
# 导入LangChain核心的可运行Lambda类
from langchain_core.runnables import RunnableLambda
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()

# 定义加1函数，接受配置参数
def add_one(x:int,config:dict)->int:
    
    # 打印配置信息，展示config参数的传递
    print(f"add_one:{config}")
    
    return x+1

# 定义乘2函数，接受配置参数
def double(x:int,config:dict)->int:
    
    # 打印配置信息，展示config参数的传递
    print(f"double:{config}")
    
    return x * 2

# 创建处理流水线：先执行加1，然后执行乘2
pipline = RunnableLambda(add_one) | RunnableLambda(double)

# 调用流水线并传入配置信息
# config参数可以包含各种配置信息，如用户ID、状态、标签、元数据等
# 这些配置信息会在流水线的每个阶段传递给对应的函数
print(
    
    pipline.invoke(1,
    config={
      # 可配置参数：可以动态修改的配置
      'configurable': {
          'userId': 'id-1212', 
          'status': ['up'], 
      },
      # 标签：用于标识和追踪
      'tags': ['tag11', 'tag2'], 
      # 元数据：额外的描述信息
      'metadata': {'key1': 'value1', 'key2': 'value2'}
      
   })
    
)