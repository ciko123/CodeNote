# 导入正则表达式模块
import re
# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI
# 导入类型提示模块
from typing import Any, Dict, Iterable, List
# 导入LangChain核心的基础输出解析器类
from langchain_core.output_parsers import BaseOutputParser
# 导入LangChain核心的提示词模板类
from langchain_core.prompts import PromptTemplate

# 导入dotenv用于加载环境变量
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()


class EntityExtractionParser(BaseOutputParser[Dict[str, List[str]]]):
    """自定义输出解析器，用于从文本中提取并分类实体。
    
    该解析器能够识别并分类以下实体类型：
    - 人物 (PERSON)
    - 地点 (LOCATION)
    - 事件 (EVENT)
    """
    
    def parse(self, text: str) -> Dict[str, List[str]]:
        """解析文本并提取分类实体。
        
        Args:
            text: LLM 生成的原始文本输出。
            
        Returns:
            结构化的实体字典，按类型分类。
        """
        # 初始化实体字典，包含三种实体类型
        entities = {
            "PERSON": [],
            "LOCATION": [],
            "EVENT": []
        }
        
        # 提取人物（支持逗号、顿号、空格分隔）
        # (?:人物|姓名|人): 非捕获组，匹配人物、姓名或人
        # \s*: 匹配零个或多个空白字符
        # ([^\n]+): 捕获组，匹配除换行符外的所有字符
        person_pattern = r"(?:人物|姓名|人):\s*([^\n]+)"
        for match in re.finditer(person_pattern, text):
            # 使用正则表达式分割多个实体（支持中文和英文分隔符）
            persons = [p.strip() for p in re.split(r"[,，\s]+", match.group(1)) if p.strip()]
            entities["PERSON"].extend(persons)

        # 提取地点（支持逗号、顿号、空格分隔）
        # (?:地点|位置|城市): 非捕获组，匹配地点、位置或城市
        location_pattern = r"(?:地点|位置|城市):\s*([^\n]+)"
        for match in re.finditer(location_pattern, text):
            locations = [l.strip() for l in re.split(r"[,，\s]+", match.group(1)) if l.strip()]
            entities["LOCATION"].extend(locations)

        # 提取事件（支持逗号、顿号、空格分隔）
        # (?:事件|活动|发生): 非捕获组，匹配事件、活动或发生
        event_pattern = r"(?:事件|活动|发生):\s*([^\n]+)"
        for match in re.finditer(event_pattern, text):
            events = [e.strip() for e in re.split(r"[,，\s]+", match.group(1)) if e.strip()]
            entities["EVENT"].extend(events)
        return entities
    
    def get_format_instructions(self) -> str:
        """返回格式说明，指导 LLM 如何格式化输出。"""
        return """
        请按照以下格式输出信息：
        
        人物: [姓名1], [姓名2], [姓名3]
        地点: [位置1], [位置2], [位置3]
        事件: [事件1], [事件2], [事件3]
        
        例如：
        人物: 张三, 李四, 王五
        地点: 北京, 上海, 广州
        事件: 会议, 展览, 讲座
        """

# 创建OpenAI聊天模型实例
# model: 使用的模型名称 (gpt-4o)
# temperature: 控制输出随机性，0.6表示中等随机性
model = ChatOpenAI(model="gpt-4o", temperature=0.6)

# 创建实体提取解析器实例
parser = EntityExtractionParser()

# 定义提示词模板
template = """
你是一个信息提取助手。请从以下文本中提取人物、地点和事件：

文本: {text}

{format_instructions}
"""

# 创建提示词模板
# template: 提示词模板字符串
# input_variables: 动态输入变量
# partial_variables: 预填充变量（格式说明）
prompt_template = PromptTemplate(
    template=template,
    input_variables=["text"],
    partial_variables={"format_instructions": parser.get_format_instructions()},
)

# 定义输入文本（包含人物、地点、事件信息）
text = """
2023年，特斯拉CEO埃隆·马斯克访问了中国上海的特斯拉超级工厂。
在那里，他参加了一个关于可持续能源的论坛，并宣布了新的投资计划。
同时，苹果公司CEO蒂姆·库克也在旧金山参加了全球开发者大会。
"""

# 格式化提示
formatted_prompt = prompt_template.format_prompt(text=text)

# 打印生成的提示模板内容
print(formatted_prompt)

print("==" * 20)

# 调用模型生成回复
response = model.invoke(formatted_prompt)
print("模型输出类型:", type(response))  # 打印模型的原始输出
print("模型输出:", response)  # 打印模型的原始输出
print("==" * 20)
# 使用实体提取解析器处理回复，生成结构化实体字典
output = parser.invoke(response)
print(type(output))  # 打印解析后的对象类型
print(output)  # 打印解析后的对象内容