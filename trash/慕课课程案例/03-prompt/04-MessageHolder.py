# 导入LangChain核心的提示词模板类和消息占位符
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder

# 导入LangChain核心的消息类型
from langchain_core.messages import HumanMessage, AIMessage

# 创建聊天提示词模板
# 使用MessagesPlaceholder来动态插入消息列表
prompt_template = ChatPromptTemplate([
    ("system", "你是个乐于助人的助手,在回答用户问题时，需要带上用户的名字"),
    ("user", "我是{name}"),
    # MessagesPlaceholder: 动态消息占位符，用于插入历史对话
    MessagesPlaceholder("msgs")
])

# 使用提示词模板生成具体提示词
# msgs参数传入消息列表，包含历史对话
s = prompt_template.invoke({"msgs": [
                                    AIMessage(content="你好，有什么需要咨询的？"),
                                    HumanMessage(content="三国志作者是谁？")
                                    ], 
                            "name": "张三"})

# 打印格式化的提示词字符串
print(s.to_string())

# 导入OpenAI聊天模型
from langchain_openai import ChatOpenAI
# 创建模型实例
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
# 调用模型生成回复
response = llm.invoke(s)
# 打印回复内容
print(response.content)