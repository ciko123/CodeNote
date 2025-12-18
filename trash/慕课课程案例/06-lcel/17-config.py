# 导入LangChain核心的可运行Lambda类
from langchain_core.runnables import RunnableLambda


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


# 创建处理流水线，使用with_config方法为特定组件添加配置
# RunnableLambda(add_one).with_config(): 为add_one组件添加特定配置
# "timeout": 5: 设置超时时间为5秒
# "userId": "user-123": 设置用户ID
# "tags": ["math", "demo"]: 设置标签用于分类和追踪
# "metadata": {"source": "user_input"}: 设置元数据信息
# RunnableLambda(double): double组件不添加特定配置，将使用默认配置
pipline = (RunnableLambda(add_one).with_config({
            "timeout": 5,
            "userId": "user-123",
            "tags": ["math", "demo"],
            "metadata": {"source": "user_input"}
        })
    | RunnableLambda(double)
)

# 调用流水线，传入初始值1
# add_one函数将收到with_config中设置的配置
# double函数将收到默认配置或空配置
print(pipline.invoke(1))