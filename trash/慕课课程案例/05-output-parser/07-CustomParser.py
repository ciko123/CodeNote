# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI
# 导入LangChain核心的消息类型
from langchain_core.messages import AIMessage, AIMessageChunk

# 导入dotenv用于加载环境变量
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()

# 创建OpenAI聊天模型实例
# model: 使用的模型名称 (gpt-4o)
# temperature: 控制输出随机性，0.6表示中等随机性
model = ChatOpenAI(model="gpt-4o", temperature=0.6)

# 定义自定义解析函数
def parse(ai_message: AIMessage) -> str:
    """Parse the AI message."""
    # swapcase(): 将字符串中的大写字母转换为小写，小写字母转换为大写
    return ai_message.content.swapcase()

# 调用模型生成回复
response = model.invoke("hello")
# 打印原始回复
print(response)

print("=================")

# 使用自定义解析函数处理回复
print("parse:", parse(response))