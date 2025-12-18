# 导入LangChain核心的提示词模板类
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, \
    AIMessagePromptTemplate

# 从消息列表创建聊天提示词模板
# 使用不同类型的消息模板：
# SystemMessagePromptTemplate: 系统消息模板
# HumanMessagePromptTemplate: 用户消息模板  
# AIMessagePromptTemplate: AI消息模板
prompt_template = ChatPromptTemplate.from_messages([
    # 系统消息：设定AI角色和回答风格
    SystemMessagePromptTemplate.from_template("你是{product}的客服助手，你的名字叫{name}，请简洁的用20个字回答问题"),
    # 用户消息：问候和自我介绍
    HumanMessagePromptTemplate.from_template("hello 你好,我的名字叫{human_name}"),
    # AI消息：预设的回应
    AIMessagePromptTemplate.from_template("你好，有什么需要咨询的"),
    # 用户消息：具体问题
    HumanMessagePromptTemplate.from_template("{query}")
])

# 使用invoke方法生成提示词（返回PromptValue对象）
prompt = prompt_template.invoke({
    "product": "langchain",
    "name": "老顾",
    "human_name": "张三",
    "query": "langchain是什么，用来做什么的？"
})
print(prompt)

print("-" * 20)

# 使用format_messages方法生成消息列表（返回消息对象列表）
prompt1 = prompt_template.format_messages(product="langchain", name="老顾", human_name="张三", query="langchain是什么，用来做什么的？")

print("prompt1:",prompt1)

print("-" * 20)


# 导入OpenAI聊天模型
from langchain_openai import ChatOpenAI

# 创建模型实例
model = ChatOpenAI(model="gpt-4o", temperature=0)
# 调用模型生成回复
response = model.invoke(prompt)

# 打印回复内容
print(response.content)