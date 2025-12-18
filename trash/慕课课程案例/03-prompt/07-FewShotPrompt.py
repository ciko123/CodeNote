# 导入LangChain核心的聊天提示词模板类和少样本聊天消息提示词模板类
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
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

# 定义少样本示例（用于数学运算）
# 🦜 符号代表加法运算
examples = [
    {"input": "2 🦜 2", "output": "4"},
    {"input": "2 🦜 3", "output": "5"},
    {"input": "4 🦜 5", "output": "9"},
]

# 创建示例聊天提示词模板
# 使用消息格式：用户输入和AI回复
example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{input}"),
        ("ai", "{output}"),
    ]
)
# 创建少样本聊天消息提示词模板
# example_prompt: 示例格式化模板
# examples: 示例列表
few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=examples,
)

# 打印少样本提示词的字符串表示
print(few_shot_prompt.invoke({}).to_string())

print("-" * 20)

# 创建最终的聊天提示词模板
# 包含系统消息、少样本示例和用户输入
final_prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "你是个数学奇才。"),  
        few_shot_prompt,  # 插入少样本示例
        ("human", "{input}"),
    ]
)

# 使用最终模板生成具体提示词
s = final_prompt_template.invoke({"input": "2 🦜 9"}).to_string()

# 打印完整的提示词
print(s)

print("-" * 20)

# 调用模型生成回复
response = model.invoke(s)
# 打印模型回复
print(response)