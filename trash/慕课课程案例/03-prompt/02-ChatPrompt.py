# 导入LangChain的聊天提示词模板类
from langchain.prompts import ChatPromptTemplate

# 创建聊天提示词模板
# 使用元组列表格式：(角色, 内容模板)
# system: 系统消息，设定AI角色
# user: 用户消息，包含变量占位符{topic}
prompt_template = ChatPromptTemplate([
    ("system", "你是个乐于助人的助手"),
    ("user", "给我们讲一个有关{topic}的笑话")
])

# 使用提示词模板生成具体提示词
# 将{topic}替换为"猫"
prompt = prompt_template.invoke({"topic": "猫"})

# 打印提示词对象的字符串表示
print(prompt)
print("" + "-" * 20)
# 打印格式化的提示词字符串
print(prompt.to_string())
print("" + "-" * 20)
# 打印消息列表格式（用于模型调用）
print(prompt.to_messages())
print("" + "-" * 20)
# 打印JSON格式的提示词
print(prompt.to_json())