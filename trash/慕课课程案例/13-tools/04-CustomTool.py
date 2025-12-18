# 导入异步IO模块，用于异步操作
import asyncio
# 导入类型提示模块的可选类型、任意类型和协程类型
from typing import Optional, Any, Coroutine

# 导入LangChain核心的回调管理器类
# AsyncCallbackManagerForToolRun: 异步工具运行的回调管理器
# CallbackManagerForToolRun: 同步工具运行的回调管理器
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
# 导入LangChain核心的基础工具类
# BaseTool: 用于创建自定义工具的基类
from langchain_core.tools import BaseTool
# 导入LangChain核心工具基类的参数模式类型
from langchain_core.tools.base import ArgsSchema
# 导入Pydantic的基础模型和字段类
from pydantic import BaseModel, Field


# 定义计算器输入的参数模型
class CalculatorInput(BaseModel):
    """计算器工具的输入参数模型"""
    # 第一个数字：整数类型，必填
    a: int = Field(description="first number")
    # 第二个数字：整数类型，必填
    b: int = Field(description="second number")

# 自定义计算器工具类，继承自BaseTool
class CustomCalculatorTool(BaseTool):
    # 工具名称，用于标识工具
    name: str = "Calculator"
    # 工具描述，用于LLM理解工具的用途
    description: str = "useful for when you need to answer questions about math"
    # 参数模式，使用Pydantic模型进行参数验证
    args_schema: Optional[ArgsSchema] = CalculatorInput

    # 重写同步运行方法
    def _run(
        self, a: int, b: int, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> int:
        """同步使用工具进行计算
        
        Args:
            a (int): 第一个数字
            b (int): 第二个数字
            run_manager: 运行管理器，用于处理回调
            
        Returns:
            int: 两个数字的乘积
        """
        # 执行乘法运算
        return a * b
    
    # 重写异步运行方法
    async def _arun(
        self,
        a: int,
        b: int,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> int:
        """异步使用工具进行计算
        
        Args:
            a (int): 第一个数字
            b (int): 第二个数字
            run_manager: 异步运行管理器，用于处理回调
            
        Returns:
            int: 两个数字的乘积
        """
        # 调用同步方法，传入同步的运行管理器
        return self._run(a, b, run_manager=run_manager.get_sync())
    
# 创建自定义计算器工具实例
multiply = CustomCalculatorTool()

# 打印工具参数的JSON Schema，用于LLM理解参数结构
print(multiply.args_schema.model_json_schema()) 

# 使用字典格式调用工具（自定义工具支持字典参数）
print(multiply.invoke({"a":2,"b":3}))