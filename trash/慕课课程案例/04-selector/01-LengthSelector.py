# 导入LangChain核心的示例选择器类
from langchain_core.example_selectors import LengthBasedExampleSelector
# 导入LangChain核心的提示词模板类
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI

# 示例数据 ,模拟数据库存放的数据
# 定义用于生成反义词的例子
examples = [
    {"input": "快乐", "output": "悲伤"},
    {"input": "高", "output": "矮"},
    {"input": "精力充沛", "output": "昏昏欲睡"},
    {"input": "阳光", "output": "阴暗"},
    {"input": "喧哗", "output": "安静"},
]

# 创建示例格式化模板
example_prompt = PromptTemplate(
    input_variables=["input", "output"],
    template="input: {input}\noutput: {output}",
)

# 使用长度选择器来选择示例
# LengthBasedExampleSelector: 根据文本长度动态选择示例数量
example_selector = LengthBasedExampleSelector(
    # 这些是可供选择的示例。
    examples=examples,
    # 这是用于格式化示例的PromptTemplate。
    example_prompt=example_prompt,
    # 提示的最大长度，超过此长度将剪切示例。
    # 可以帮助控制所选择的示例的规模
    max_length=50,
    get_text_length=lambda x: len(x)  # 计算文本长度的函数
)

# 使用少样本prompt模板
dynamic_prompt = FewShotPromptTemplate(
    # 我们提供一个ExampleSelector而不是示例。
    example_selector=example_selector,
    example_prompt=example_prompt,
    suffix="Input: {input}\nOutput:", # adjective为形容词
    input_variables=["input"],
)

# 测试短问题（会选择更多示例）
short_question = "大"
prompt1 = dynamic_prompt.format(input=short_question)
print(prompt1)

# model = ChatOpenAI(model="gpt-4o", temperature=0)
# res = model.invoke(prompt1)
# print(res.content)

print("===============")
# 测试长问题（会选择更少示例）
long_question = "又大又大,又大又高,高大无比,高耸入云"
prompt2 = dynamic_prompt.format(input=long_question)
print(prompt2)  
# model = ChatOpenAI(model="gpt-4o", temperature=0)
# res = model.invoke(prompt2)
# print(res.content)
print("===============")
# 打印每个示例的文本长度
print("example_selector.example_text_lengths:", example_selector.example_text_lengths)

# 打印不同问题选择的示例数量
print("short_question使用的示例数量:", len(example_selector.select_examples({"input": short_question})))
print("long_question使用的示例数量:", len(example_selector.select_examples({"input": long_question})))
