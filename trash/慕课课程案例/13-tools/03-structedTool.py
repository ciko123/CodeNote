# 导入LangChain核心的结构化工具类
# StructuredTool: 用于创建具有结构化参数的工具，支持Pydantic模型验证
from langchain_core.tools import StructuredTool
# 导入Pydantic的基础模型和字段类
from pydantic import BaseModel, Field
# 导入类型提示模块的可选类型
from typing import Optional


# 定义银行账户查询的参数模型
class BankAccountQuery(BaseModel):
    """银行账户查询的参数模型"""
    # 账户ID：必填字段，用户银行账号
    account_id: str = Field(description="用户的银行账号")
    # 开始日期：可选字段，查询的开始日期，格式为YYYY-MM-DD
    start_date: Optional[str] = Field(default=None,description="查询开始日期，格式YYYY-MM-DD")
    # 结束日期：可选字段，查询的结束日期，格式为YYYY-MM-DD
    end_date: Optional[str] = Field(default=None,description="查询结束日期，格式YYYY-MM-DD")
    # 查询类型：字符串字段，有默认值和枚举限制
    query_type: str = Field(
        default="balance", 
        enum=["balance", "transactions", "interest_rate"],  # 限制只能选择这三个值
        description="查询类型：余额查询、交易记录或利率查询"
    )

# 定义银行账户查询函数
def query_bank_account(
    account_id: str, 
    start_date: Optional[str]=None, 
    end_date: Optional[str]=None,
    query_type: str = "balance"
) -> str:
    """查询银行账户信息
    
    Args:
        account_id (str): 银行账号
        start_date (Optional[str]): 查询开始日期
        end_date (Optional[str]): 查询结束日期
        query_type (str): 查询类型
        
    Returns:
        str: 查询结果
    """
    # 这里通常会调用实际的银行API
    # 为了示例，我们只返回模拟数据
    
    # 根据查询类型返回不同的模拟数据
    if query_type == "balance":
        return f"账户 {account_id} 当前余额为: ¥10,000.00"
    elif query_type == "transactions":
        # 如果提供了日期范围，返回带日期的交易记录
        if start_date and end_date:
            return f"账户 {account_id} 在 {start_date} 到 {end_date} 之间有5笔交易"
        else:
            return f"账户 {account_id} 最近有9笔交易"
    elif query_type == "interest_rate":
        return f"账户 {account_id} 的当前利率为 1.5%"
    else:
        return "不支持的查询类型"
    
# 使用StructuredTool.from_function创建结构化工具
# func: 工具对应的函数
# name: 工具名称
# description: 工具描述，用于LLM理解工具用途
# args_schema: 参数模式，使用Pydantic模型进行参数验证
bank_tool = StructuredTool.from_function(
    func=query_bank_account,
    name="query_bank_account",
    description="查询银行账户信息的工具，可以查询余额、交易记录或利率",
    args_schema=BankAccountQuery
)

# 打印工具参数的JSON Schema，用于LLM理解参数结构
print(bank_tool.args_schema.model_json_schema())

# 使用字典格式调用工具（结构化工具支持字典参数）
result = bank_tool.invoke(
    {
        "account_id": "123456",
        # "start_date": "2023-01-01",  # 可选参数可以省略
        # "end_date": "2023-01-31",    # 可选参数可以省略
        "query_type": "balance"       # 使用默认值也可以省略
    }
)

# 打印工具执行结果
print(result)