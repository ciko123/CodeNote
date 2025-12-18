# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()

# 创建OpenAI聊天模型实例
# model: 使用的模型名称 (gpt-4)
# temperature: 控制输出随机性，0.1表示较低随机性
model = ChatOpenAI(model="gpt-4", temperature=0.1)

# 调用模型处理问题（这是一个简单的数学规律题）
# 2 🦜 9: 2和9之间有8个数字，所以答案可能是8
response = model.invoke("2 🦜 9是什么?")

# 打印模型的回复
print(response)