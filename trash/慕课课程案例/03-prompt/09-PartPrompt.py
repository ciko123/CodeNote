# 导入LangChain核心的提示词模板类
from langchain_core.prompts import PromptTemplate

# 从字符串创建提示词模板
# 包含三个变量占位符：{first}, {second}, {third}
prompt_template = PromptTemplate.from_template("把大象放冰箱需要三步，第一步:{first}, 第二步:{second}, 第三步:{third}")

# //业务处理

# 使用partial方法部分填充模板
# 只填充第一个变量{first}，其他变量保持不变
first_prompt_template = prompt_template.partial(first="打开冰箱门")

# 业务处理todo

# 继续部分填充模板
# 填充第二个变量{second}
second_prompt_template = first_prompt_template.partial(second="把大象放进去")

# 业务处理todo
# 使用invoke方法填充最后一个变量并生成最终提示词
final_prompt = second_prompt_template.invoke({"third": "关上冰箱门"})

# 打印完整的提示词
print(final_prompt)


