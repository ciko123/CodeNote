# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()

# 创建OpenAI聊天模型实例
# model: 使用的模型名称 (gpt-4)
# temperature: 控制输出随机性，0.1表示较低随机性，输出更稳定
model = ChatOpenAI(model="gpt-4",
                   temperature=0.1)

# 调用模型发送问题并打印回复内容
print(model.invoke("三国志的作者是谁？").content)