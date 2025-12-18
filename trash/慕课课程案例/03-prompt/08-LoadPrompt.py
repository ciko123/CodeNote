# 导入LangChain核心的提示词加载函数
from langchain_core.prompts import load_prompt

# 从JSON文件加载提示词模板
# 文件路径: 03-prompt/08-prompt.json
# encoding: 指定文件编码为utf-8，防止中文乱码
prompt_template = load_prompt("03-prompt/08-prompt.json",encoding="utf-8")

# 使用加载的提示词模板生成具体提示词
# 传入变量值：name="小明", who="猫"
prompt = prompt_template.invoke({"name": "小明", "who": "猫"})
# 打印生成的提示词
print(prompt)