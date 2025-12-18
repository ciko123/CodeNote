# 导入LangChain核心的提示词模板类
from langchain_core.prompts import PromptTemplate

# 导入datetime模块用于获取当前日期
from datetime import datetime


# 定义获取当前日期的函数
# 返回格式化的日期字符串 (YYYY/MM/DD)
def _get_datetime():
    now = datetime.now()
    return now.strftime("%Y/%m/%d")


# 创建提示词模板
# template: 提示词模板字符串，包含两个变量占位符
# input_variables: 需要动态填充的变量列表
prompt_template = PromptTemplate(
    template="给我讲一下发生在：{date}，有关{who}新闻",
    input_variables=["who", "date"],
)

# 使用partial方法预填充date变量，传入函数
# 每次调用时会动态执行函数获取当前日期
partial_prompt_template1 = prompt_template.partial(date=_get_datetime)

# 使用partial方法预填充date变量，传入固定字符串
partial_prompt_template2 = prompt_template.partial(date="2021/04/22")

# todo

# 使用format方法填充who变量并打印提示词
# 第一个模板使用动态日期，第二个使用固定日期
print(partial_prompt_template1.format(who="张三"))
print(partial_prompt_template2.format(who="张三"))
