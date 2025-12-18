# 导入LangChain核心的可运行基类和序列类
from langchain_core.runnables import Runnable,RunnableSequence
# 导入类型提示模块
from typing import Any, Dict, List

# 自定义数据验证器类，继承自Runnable基类
class DataValidator(Runnable):
    def invoke(self, input: Dict[str, Any], config: Any = None, **kwargs) -> Dict[str, Any]:
        # 验证输入数据是否包含必要字段
        if "name" not in input or "age" not in input:
            raise ValueError("输入数据缺少必要字段")
        return input

# 自定义年龄转换器类，继承自Runnable基类
class AgeTransformer(Runnable):
    def invoke(self, input: Dict[str, Any], config: Any = None, **kwargs) -> Dict[str, Any]:
        # 根据年龄添加年龄组字段
        # **input: 展开原始字典，保留原有字段
        # age_group: 新增字段，根据年龄判断年龄组
        return {
            **input,
            "age_group": "青年" if input["age"] < 35 else "中年"
        }
        
# 使用管道操作符创建数据处理流水线
# DataValidator(): 验证输入数据
# AgeTransformer(): 转换年龄数据
age_pipeline = DataValidator() | AgeTransformer()

# 打印流水线的图形化表示（ASCII图）
print(age_pipeline.get_graph().draw_ascii())

# 调用流水线，传入缺少age字段的数据，将抛出异常
print(age_pipeline.invoke({"name": "Alice"}))