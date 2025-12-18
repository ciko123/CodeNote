# 导入类型提示模块
from typing import Any, Dict, List

# 导入LangChain核心的基础示例选择器类
from langchain_core.example_selectors import BaseExampleSelector
# 导入LangChain核心的提示词模板类
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv
# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI

# 从.env文件加载环境变量
load_dotenv()

class CustomExampleSelector(BaseExampleSelector):
    """医疗示例选择器"""

    def __init__(self, examples: List[dict[str, str]]):
        """
        初始化医疗示例选择器

        :param examples: 医疗相关的示例列表，每个示例是一个字典，包含输入和输出
        """
        self.examples = examples

    def add_example(self, example: dict[str, str]) -> Any:
        """将新示例添加到存储中的键。"""
        self.examples.append(example)

    def select_examples(self, input_variables: dict[str, str]) -> list[dict[str, str]]:
        """
        根据输入变量选择医疗示例

        :param input_variables: 包含选择条件（如疾病名称、症状等）的字典
        :return: 符合条件的示例列表
        """
        # 假设我们根据疾病名称来选择示例
        disease_name = input_variables.get("disease_name", None)
        if disease_name is None:
            return []  # 如果没有提供疾病名称，则返回空列表

        # 根据疾病名称匹配相关示例（不区分大小写）
        selected_examples = [
            example for example in self.examples
            if disease_name.lower() in example["input"].lower()
        ]

        return selected_examples
    
# 示例数据 ,模拟数据库存放的数据
examples = [
    {"input": "流感症状", "output": "发烧、咳嗽、喉咙痛、身体酸痛。"},
    {"input": "糖尿病治疗", "output": "饮食控制、运动、药物"},
    {"input": "新冠肺炎症状", "output": "发烧、咳嗽、疲劳、味觉或嗅觉丧失。"},
    {"input": "糖尿病症状", "output": "口渴、尿频、体重减轻。"},
]

# 创建医疗示例选择器实例
custom_example_selector = CustomExampleSelector(examples)

# 选择与疾病名称 "diabetes" 相关的示例
# selected_examples = custom_example_selector.select_examples({"disease_name": "糖尿病"})

# 打印选择的示例
# print(selected_examples)
print("==========================")

# 添加示例
# custom_example_selector.add_example({"input": "头晕症状", "output": "头晕、眼睛模糊。"})

# # 选择与疾病名称 "diabetes" 相关的示例
# selected_examples = custom_example_selector.select_examples({"disease_name": "头晕症状"})

# # 打印选择的示例
# print(selected_examples)
print("==========================")


# 创建示例格式化模板
example_prompt = PromptTemplate(
    input_variables=["input", "output"],
    template="输入: {input}\n输出: {output}",
)

# 使用少样本prompt模板
dynamic_prompt = FewShotPromptTemplate(
    # 我们提供一个ExampleSelector而不是示例。
    example_selector=custom_example_selector,
    example_prompt=example_prompt,
    prefix="根据描述确定病情",
    suffix="输入: {disease_name}\n输出:",
    input_variables=["disease_name"],
)

# 一个输入较小的示例，因此它选择所有示例。
prompt = dynamic_prompt.format(disease_name="糖尿病")

# 打印生成的提示词
print(prompt)


# 创建模型实例并生成回复
model = ChatOpenAI(model="gpt-4o", temperature=0)
res = model.invoke(prompt)
# 打印模型回复
print(res)