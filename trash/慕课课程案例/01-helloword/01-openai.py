# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()

# 创建OpenAI聊天模型实例
# model: 使用的模型名称
# temperature: 控制输出随机性，0表示最确定性的输出
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 调用模型，发送问题
response = llm.invoke("你是谁？")

# 打印模型的回复内容
print(response.content)
