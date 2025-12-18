# 导入LangChain的提示词模板类
from langchain.prompts import PromptTemplate
# 导入LangChain核心的可配置字段类
from langchain_core.runnables import ConfigurableField
# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv

# 从.env文件加载环境变量
load_dotenv()


# 创建OpenAI模型实例并配置可配置字段
# ChatOpenAI: 创建GPT-3.5-turbo模型，初始temperature为0
# configurable_fields: 将模型的某些参数设置为可配置
# ConfigurableField: 定义可配置字段的属性
model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0).configurable_fields(
    temperature=ConfigurableField(
        id="llm_temperature" ,  # 配置字段的唯一标识符
        name="llm 温度",        # 配置字段的显示名称
        description="llm 温度",  # 配置字段的描述信息
    )
)

# 创建提示词模板
# from_template: 从字符串模板创建提示词
# {x}: 动态变量，将被替换为具体数值
prompt = PromptTemplate.from_template("给一个大于 {x} 的随机数")

# 创建处理链：提示词模板 -> 模型
chain = prompt | model

# 调用链并动态配置temperature参数
# with_config: 在运行时动态配置参数
# configurable: 指定要配置的可配置字段及其值
# "llm_temperature": 0.9: 将模型的temperature设置为0.9，增加输出随机性
print(chain.with_config(configurable={"llm_temperature": 0.9}).invoke({"x": 5}))