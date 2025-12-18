# 导入LangChain核心的消息类：AI消息和人类消息
from langchain_core.messages import AIMessage, HumanMessage
# 导入LangChain核心的提示词模板类和消息占位符类
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI

# 导入dotenv用于加载环境变量
from dotenv import load_dotenv
# 从.env文件加载环境变量
load_dotenv()

# 创建OpenAI聊天模型实例
# model: 使用的模型名称 (gpt-4)
# temperature: 控制输出随机性，0.6表示中等随机性
model = ChatOpenAI(model="gpt-4", temperature=0.6)

# 创建聊天提示词模板
# from_messages: 从消息列表创建提示词模板
# [ ("system", "..."), ("user", "...") ]: 定义系统提示和用户提示的格式
prompt_template = ChatPromptTemplate.from_messages(
    [
        
        # 系统消息：定义AI助手的角色和行为
        ("system","你是一个乐于助人的助手。尽你所能回答所有问题。回答方式简洁，20个字左右"),
        # 用户消息：使用变量占位符，将被实际问题替换
        ("user","{question}")
    ]
)

# 创建处理链：提示词模板 -> 模型
chain = prompt_template | model

# 第一次调用：询问金庸是谁
response = chain.invoke({"question":"你好，我叫老顾，请问金庸是谁"})

# 打印第一次回复
print(response.content)

# 第二次调用：询问AI是否记得用户名字
# 由于没有记忆功能，AI无法记住之前对话中的用户名字
response1 = chain.invoke({"question":"你好，你知道我叫什么名字吗？"})

# 打印第二次回复，展示无记忆功能的效果
print(response1.content)