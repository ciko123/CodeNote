# 导入操作系统模块
import os
# 导入LangChain核心的可运行Lambda类
from langchain_core.runnables import RunnableLambda
# 导入LangChain核心的回调处理器基类
from langchain_core.callbacks import BaseCallbackHandler


# 自定义回调处理器类，继承自BaseCallbackHandler
class MyCallbackHandler(BaseCallbackHandler):
    # 链开始执行时的回调方法
    def on_chain_start(self, serialized, inputs, **kwargs):
        print("Chain started with run_id:", kwargs.get("run_id"))
        print("Chain started with run_name:", kwargs.get("name"))
    
    # 链结束执行时的回调方法
    def on_chain_end(self, outputs, **kwargs):
        print("Chain ended with run_id:", kwargs.get("run_id"))


# 定义加1函数，接受配置参数
def add_one(x:int,config:dict)->int:
    
    # 打印配置信息，展示config参数的传递
    print(f"add_one:{config}")
    
    return x+1

# 创建可运行对象并设置运行名称
# with_config(run_name="AddOneRunnable"): 为可运行对象设置一个可识别的名称
runnable = RunnableLambda(add_one).with_config(run_name="AddOneRunnable")
# 创建回调处理器实例
callbacks=[MyCallbackHandler()]

# 调用可运行对象并传入完整的配置信息
# config包含多种配置选项：
# - configurable: 可配置参数
# - tags: 标签用于分类和追踪
# - metadata: 元数据信息
# - callbacks: 回调处理器列表，用于监控和记录执行过程
print(runnable.invoke(1,config={
      'configurable': {
          'userId': 'id-1212', 
          'status': ['up'], 
      },
      'tags': ['tag11', 'tag2'], 
      'metadata': {'key1': 'value1', 'key2': 'value2'},
      'callbacks': callbacks
   }))