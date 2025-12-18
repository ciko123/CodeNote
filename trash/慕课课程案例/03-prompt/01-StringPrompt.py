# 导入LangChain的提示词模板类
from langchain.prompts import PromptTemplate
# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI

# 从字符串创建提示词模板
# {topic}是变量占位符，可以在运行时替换
prompt_template = PromptTemplate.from_template("给我们讲一个关于{topic}笑话。")

# 创建OpenAI聊天模型实例
# model_name: 使用的模型名称 (gpt-3.5-turbo)
# temperature: 控制输出随机性，0.7表示较高随机性，适合创意内容
model = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)

# 使用提示词模板生成具体提示词
# 将{topic}替换为"python"
prompt = prompt_template.invoke({"topic": "python"})

# 调用模型生成回复
response = model.invoke(prompt)

# 打印模型生成的内容
print(response.content)
