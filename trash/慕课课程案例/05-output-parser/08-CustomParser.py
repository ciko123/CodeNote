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


class TaskListOutputParser(BaseOutputParser[List[Dict[str, Any]]]):
    """自定义输出解析器，用于将 LLM 生成的文本解析为任务列表。
    
    该解析器期望输入文本格式为：
    1. [任务名称1] - [截止日期1] - [优先级1]
    2. [任务名称2] - [截止日期2] - [优先级2]
    ...
    """
    
    def parse(self, text: str) -> List[Dict[str, Any]]:
        """解析文本输出为任务列表。
        
        Args:
            text: LLM 生成的原始文本输出。
            
        Returns:
            结构化的任务列表，每个任务包含名称、截止日期和优先级。
        """
        tasks = []
        
        # 使用正则表达式匹配任务项
        # \d+\. 匹配数字加点的格式（如"1."）
        # \[(.*?)\] 匹配方括号内的内容
        # \s*-\s* 匹配破折号分隔符，允许前后有空格
        task_pattern = r"^\s*\d+\.\s*\[(.*?)\]\s*-\s*\[(.*?)\]\s*-\s*\[(.*?)\]"
        
        # 逐行处理文本
        for line in text.split('\n'):
            match = re.match(task_pattern, line)
            if match:
                # 提取匹配的三个组：任务名称、截止日期、优先级
                name, deadline, priority = match.groups()
                tasks.append({
                    'name': name.strip(),
                    'deadline': deadline.strip(),
                    'priority': priority.strip()
                })
        
        return tasks
    
    def get_format_instructions(self) -> str:
        """返回格式说明，指导 LLM 如何格式化输出。"""
        return """
        请按照以下格式输出任务列表：
        
        1. [任务名称] - [截止日期] - [优先级]
        2. [任务名称] - [截止日期] - [优先级]
        3. [任务名称] - [截止日期] - [优先级]
        
        例如：
        1. [完成项目报告] - [2023-12-31] - [高]
        2. [准备演示文稿] - [2023-12-25] - [中]
        3. [回复邮件] - [2023-12-20] - [低]
        """


# 创建OpenAI聊天模型实例
# model: 使用的模型名称 (gpt-4o)
# temperature: 控制输出随机性，0.6表示中等随机性
model = ChatOpenAI(model="gpt-4o", temperature=0.6)

# 创建自定义任务列表解析器实例
parser = TaskListOutputParser()

# 定义提示词模板
template = """
你是一个任务管理助手。请列出用户做下面事项时，需要计划3个任务。

事项: {text}

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

# 定义输入文本
text = """
去北京旅游
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
# 使用自定义解析器处理回复，生成结构化任务列表
output = parser.invoke(response)
print(type(output))  # 打印解析后的对象类型
print(output)  # 打印解析后的对象内容
