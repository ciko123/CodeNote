# 导入LangChain核心的提示词模板类
from langchain_core.prompts import PromptTemplate

# 定义完整的提示词模板，包含三个占位符
# {introduction}: 角色介绍部分
# {example}: 互动示例部分  
# {start}: 真实互动开始部分
full_template = """{introduction}

{example}

{start}"""

# 从完整模板创建提示词模板对象
full_prompt_template = PromptTemplate.from_template(full_template)

# 创建角色介绍提示词模板
# {introduction}: 定义AI扮演的角色
introduction_prompt_template = PromptTemplate.from_template("""你扮演 {person}.""")
# s = introduction_prompt_template.invoke({"person": "张三"})
# full_prompt_template.partial(introduction=s)

# 创建示例提示词模板
# {example}: 展示问答示例
example_template = """以下是一个互动示例:

Q: {example_q}
A: {example_a}"""
example_prompt_template = PromptTemplate.from_template(example_template)

# 创建开始提示词模板
# {start}: 真实互动的开始
start_template = """下面是真实的互动！

Q: {input}
A:"""
start_prompt_template = PromptTemplate.from_template(start_template)

# 组合提示词
# 将各个子模板组合成一个列表，便于批量处理

input_prompts = [
    ("introduction", introduction_prompt_template),
    ("example", example_prompt_template),
    ("start", start_prompt_template),
]

# -----------------

# 定义输入数据，包含所有需要的变量
my_input = {
    "person": "埃隆·马斯克",
    "example_q": "你最喜欢的车是什么？",
    "example_a": "Tesla",
    "input": "你最喜欢的社交媒体网站是什么？",
}
# 循环处理每个子模板
for name, prompt_template in input_prompts:
    # 调用子模板并转换为字符串，存入输入字典
    my_input[name] = prompt_template.invoke(my_input).to_string()
    # 打印中间结果
    print(my_input)
    print("-------------------------")

# 使用完整模板生成最终提示词
my_output = full_prompt_template.invoke(my_input)

# 打印最终生成的提示词文本
print(my_output.text)