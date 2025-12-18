# 组合提示词
# 导入LangChain核心的提示词模板类
from langchain_core.prompts import PromptTemplate

# 使用+运算符组合多个提示词模板和字符串
# 这种方式可以将多个提示词部分合并成一个完整的模板
prompt_template = (
    PromptTemplate.from_template("给我讲一个笑话，关于 {topic}")
    + ", 要非常简洁，10个字以内"
    + "\n\n用 {language} 讲述"
)

# 使用组合后的提示词模板生成具体提示词
# 传入变量值：topic="猫", language="英语"
print(prompt_template.format(topic="猫", language="英语"))