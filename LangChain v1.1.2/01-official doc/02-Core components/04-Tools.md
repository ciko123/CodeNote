# 工具（Tools）

## Create tools

### 基础使用

```py
from langchain.tools import tool

@tool
def search_database(query: str, limit: int = 10) -> str:
    """搜索客户数据库中匹配查询的记录。

    Args:
        query: 要搜索的搜索词
        limit: 返回的最大结果数
    """
    return f"为 '{query}' 找到了 {limit} 个结果"
```

### 自定义工具名和描述

```python
@tool("calculator", description="执行算术计算。对任何数学问题使用此工具。")
def calc(expression: str) -> str:
    """计算数学表达式。"""
    return str(eval(expression))
```

### 高级模式定义

#### JSON 参数

```py
weather_schema = {
    "type": "object",
    "properties": {
        "location": {"type": "string"},
        "units": {"type": "string"},
        "include_forecast": {"type": "boolean"}
    },
    "required": ["location", "units", "include_forecast"]
}

@tool(args_schema=weather_schema)
def get_weather(location: str, units: str = "celsius", include_forecast: bool = False) -> str:
    """获取当前天气和可选预报。"""
    temp = 22 if units == "celsius" else 72
    result = f"{location}的当前天气：{temp}度{units[0].upper()}"
    if include_forecast:
        result += "\n未来5天：晴天"
    return result
```

#### Pydantic 参数
```python
from pydantic import BaseModel, Field
from typing import Literal

class WeatherInput(BaseModel):
    """天气查询的输入。"""
    location: str = Field(description="城市名称或坐标")
    units: Literal["celsius", "fahrenheit"] = Field(
        default="celsius",
        description="温度单位偏好"
    )
    include_forecast: bool = Field(
        default=False,
        description="包含5天预报"
    )

@tool(args_schema=WeatherInput)
def get_weather(location: str, units: str = "celsius", include_forecast: bool = False) -> str:
    """获取当前天气和可选预报。"""
    temp = 22 if units == "celsius" else 72
    result = f"{location}的当前天气：{temp}度{units[0].upper()}"
    if include_forecast:
        result += "\n未来5天：晴天"
    return result
```
## Accessing Context

- **上下文感知决策** - 基于状态和用户信息做出智能响应
- **个性化体验** - 根据用户配置和会话信息定制功能
- **跨对话记忆** - 维护长期信息，提供连续性服务

![image-20251206162030815](C:\Users\Administrator\Desktop\LangChainDemo\LangChain v1.1\md\02-Core components\assets\image-20251206162030815.png)

### ToolRuntime

#### Accessing state
```python
from langchain.tools import tool, ToolRuntime

# 访问对话状态
@tool
def summarize_conversation(
    runtime: ToolRuntime
) -> str:
    """总结到目前为止的对话。"""
    messages = runtime.state["messages"]

    human_msgs = sum(1 for m in messages if m.__class__.__name__ == "HumanMessage")
    ai_msgs = sum(1 for m in messages if m.__class__.__name__ == "AIMessage")
    tool_msgs = sum(1 for m in messages if m.__class__.__name__ == "ToolMessage")

    return f"对话包含 {human_msgs} 条用户消息，{ai_msgs} 条 AI 响应，和 {tool_msgs} 条工具结果"

# 访问自定义状态字段
@tool
def get_user_preference(
    pref_name: str,
    runtime: ToolRuntime  # 对模型不可见
) -> str:
    """获取用户偏好值。"""
    preferences = runtime.state.get("user_preferences", {})
    return preferences.get(pref_name, "未设置")
```

#### Updating state
```python
from langgraph.types import Command
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langchain.tools import tool, ToolRuntime

# 清空对话历史
@tool
def clear_conversation() -> Command:
    """清空对话历史。"""
    return Command(
        update={
            "messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)],
        }
    )

# 更新用户名
@tool
def update_user_name(
    new_name: str,
    runtime: ToolRuntime
) -> Command:
    """更新用户名。"""
    return Command(update={"user_name": new_name})
```

#### Context

```python
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime

USER_DATABASE = {
    "user123": {
        "name": "Alice Johnson",
        "account_type": "Premium",
        "balance": 5000,
        "email": "alice@example.com"
    },
    "user456": {
        "name": "Bob Smith",
        "account_type": "Standard",
        "balance": 1200,
        "email": "bob@example.com"
    }
}

@dataclass
class UserContext:
    user_id: str

@tool
def get_account_info(runtime: ToolRuntime[UserContext]) -> str:
    """获取当前用户的账户信息。"""
    user_id = runtime.context.user_id

    if user_id in USER_DATABASE:
        user = USER_DATABASE[user_id]
        return f"账户持有人：{user['name']}\n类型：{user['account_type']}\n余额：${user['balance']}"
    return "未找到用户"

model = ChatOpenAI(model="gpt-4o")
agent = create_agent(
    model,
    tools=[get_account_info],
    context_schema=UserContext,
    system_prompt="您是一个金融助手。"
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "我当前的余额是多少？"}]},
    context=UserContext(user_id="user123")
)
```

### Memory (Store) 

```python
from typing import Any
from langgraph.store.memory import InMemoryStore
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime

# 访问记忆
@tool
def get_user_info(user_id: str, runtime: ToolRuntime) -> str:
    """查找用户信息。"""
    store = runtime.store
    user_info = store.get(("users",), user_id)
    return str(user_info.value) if user_info else "未知用户"

# 更新记忆
@tool
def save_user_info(user_id: str, user_info: dict[str, Any], runtime: ToolRuntime) -> str:
    """保存用户信息。"""
    store = runtime.store
    store.put(("users",), user_id, user_info)
    return "成功保存用户信息。"

store = InMemoryStore()
agent = create_agent(
    model,
    tools=[get_user_info, save_user_info],
    store=store
)

# 第一会话：保存用户信息
agent.invoke({
    "messages": [{"role": "user", "content": "保存以下用户：用户ID：abc123，姓名：Foo，年龄：25，邮箱：foo@langchain.dev"}]
})

# 第二会话：获取用户信息
agent.invoke({
    "messages": [{"role": "user", "content": "获取ID为'abc123'的用户信息"}]
})

```
### Stream Writer


```python
from langchain.tools import tool, ToolRuntime

@tool
def get_weather(city: str, runtime: ToolRuntime) -> str:
    """获取给定城市的天气。"""
    writer = runtime.stream_writer

    # 工具执行时流式更新
    writer(f"正在查找城市数据: {city}")
    writer(f"已获取城市数据: {city}")

    return f"{city} 总是晴天！"
```