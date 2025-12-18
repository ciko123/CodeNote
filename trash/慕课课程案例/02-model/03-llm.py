# 导入LangChain的OpenAI模型（用于文本补全）
from langchain_openai import OpenAI

# 导入dotenv用于加载环境变量
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()

# 创建OpenAI LLM实例（用于文本生成，非聊天格式）
# model: 使用的模型名称 (gpt-3.5-turbo-instruct是文本补全模型)
# temperature: 控制输出随机性，0.1表示较低随机性
llm = OpenAI(model="gpt-3.5-turbo-instruct", temperature=0.1)

# 定义提示词
prompt = "请用一句话解释量子力学"
# 调用LLM生成文本
response = llm.invoke(prompt)
# 打印生成的文本内容
print(response)