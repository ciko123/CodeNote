# 导入LangChain核心的提示词模板类和少样本提示词模板类
from langchain_core.prompts import PromptTemplate, FewShotPromptTemplate
# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()

# 创建OpenAI聊天模型实例
# model: 使用的模型名称 (gpt-4o)
# temperature: 控制输出随机性，0表示最确定性的输出
model = ChatOpenAI(model="gpt-4o", temperature=0)

# 定义少样本示例（用于提取城市名）
# 每个示例包含输入和对应的输出
examples = [
    {"input": "北京天气怎么样", "output": "北京市"},
    {"input": "南京属于江苏省", "output": "南京市"},
    {"input": "武汉有什么好玩地方？", "output": "武汉市"}
]

# 创建示例提示词模板
# 用于格式化每个示例的显示方式
example_prompt = PromptTemplate(
    input_variables=["input", "output"],
    template="输入: {input}\n输出: {output}"
)

# 创建少样本提示词模板
# examples: 示例列表
# example_prompt: 示例格式化模板
# prefix: 提示词前缀
# suffix: 提示词后缀（包含最终输入）
# input_variables: 输入变量列表
few_shot_prompt = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
    prefix="请回答以下问题：",
    suffix="input: {input}\noutput:",
    input_variables=["input"]
)

# 使用少样本提示词模板生成具体提示词
prompt = few_shot_prompt.format(input="烟花三月下扬州")

# 打印生成的提示词（包含示例和问题）
print(prompt)

print("" + "-" * 20)


# 调用模型生成回复
response = model.invoke(prompt)
# 打印模型回复
print(response)