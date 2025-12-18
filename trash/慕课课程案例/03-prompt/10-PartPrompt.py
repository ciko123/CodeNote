# 导入LangChain核心的提示词模板类
from langchain_core.prompts import PromptTemplate

# 创建提示词模板，使用partial_variables预填充部分变量
# template: 提示词模板字符串，包含三个变量占位符
# input_variables: 需要动态填充的变量列表（不包括已预填充的变量）
# partial_variables: 预填充的变量字典
prompt = PromptTemplate(
    template="把大象放冰箱分三步:\n第一步:{first}\n第二步:{second}\n第三步:{third}",
    input_variables=["second", "third"], 
    partial_variables={"first": "打开冰箱门"}
)

# 使用partial方法对second变量赋值
partial_prompt = prompt.partial(second="把大象塞到冰箱里")
# 使用format方法对third变量赋值并生成最终提示词
print(partial_prompt.format(third="关闭冰箱门"))