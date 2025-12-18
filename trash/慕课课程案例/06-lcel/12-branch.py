# 导入LangChain的可运行分支类
# RunnableBranch: 根据条件选择不同的执行路径
from langchain.schema.runnable import RunnableBranch
# 导入LangChain的提示词模板类
from langchain.prompts import PromptTemplate
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()

# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI

# 创建GPT-3.5模型实例，用于处理较短输入
# model: 使用的模型名称 (gpt-3.5-turbo)
# temperature: 控制输出随机性，0.1表示较低随机性，适合简单回复
gpt35_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)

# 创建GPT-4模型实例，用于处理较长输入
# model: 使用的模型名称 (gpt-4)
# temperature: 控制输出随机性，0.1表示较低随机性
gpt4_model = ChatOpenAI(model="gpt-4", temperature=0.1)

# 创建条件分支
# RunnableBranch: 根据条件选择不同的模型
# (lambda x: len(x) < 10, gpt35_model): 如果输入长度小于10，使用GPT-3.5模型
# gpt4_model: 默认情况使用GPT-4模型
branch = RunnableBranch(
    (lambda x: len(x) < 10, gpt35_model),
    gpt4_model
)

# 调用分支并传入测试文本
# 文本长度为16，大于10，因此使用GPT-4模型处理
print(branch.invoke("你是谁？请用比较简单的回复语言进行回答"))