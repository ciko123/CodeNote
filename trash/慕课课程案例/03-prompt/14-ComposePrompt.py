# 导入LangChain核心的提示词模板类和管道提示词模板类
from langchain_core.prompts import PromptTemplate
from langchain_core.prompts.pipeline import PipelinePromptTemplate

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
# 将各个子模板组合成一个列表，用于管道处理

input_prompts = [
    ("introduction", introduction_prompt_template),
    ("example", example_prompt_template),
    ("start", start_prompt_template),
]

# -----------------

# 创建管道提示词模板
# final_prompt: 最终的完整模板
# pipeline_prompts: 子模板列表，按顺序处理
pipeline_prompt_template = PipelinePromptTemplate(
    final_prompt=full_prompt_template, pipeline_prompts=input_prompts
)

# 打印管道模板所需的输入变量
print(pipeline_prompt_template.input_variables)
print("=========================="*3)
# 使用管道模板生成完整的提示词
# 自动处理所有子模板的变量填充
print(
    pipeline_prompt_template.format(
        person="埃隆·马斯克",
        example_q="你最喜欢的车是什么？",
        example_a="Tesla",
        input="你最喜欢的社交媒体网站是什么？",
    )
)