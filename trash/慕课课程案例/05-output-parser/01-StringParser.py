# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI
# 导入LangChain核心的字符串输出解析器
from langchain_core.output_parsers import StrOutputParser
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()

# 创建OpenAI聊天模型实例
# model: 使用的模型名称 (gpt-4)
# temperature: 控制输出随机性，0.6表示中等随机性
model = ChatOpenAI(model="gpt-4", temperature=0.6)

# 创建字符串输出解析器实例
# StrOutputParser: 将模型输出解析为纯字符串
parser = StrOutputParser()

# 定义提示词
prompt = "请用一句话解释量子力学"
# 调用模型生成回复
response = model.invoke(prompt)
# 打印原始回复的类型和内容
print(type(response))
print(response)
print("============================================")
# 使用解析器处理回复，提取字符串内容
parsed_response = parser.invoke(response)
# 打印解析后回复的类型和内容
print(type(parsed_response))
print(parsed_response)