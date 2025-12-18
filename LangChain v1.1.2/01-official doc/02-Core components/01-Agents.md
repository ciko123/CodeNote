# 核心部件
## 代理 (Agents)

代理 (Agents) 结合语言模型和工具来创建能够推理任务、决定使用哪些工具并迭代地朝着解决方案努力的系统。

`create_agent` 提供了生产就绪的代理实现，基于 LangGraph 构建图结构运行时。

![image-20251206145533950](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20251206145533950.png)

## 核心组件

### 模型 (Model)

#### 静态模型
创建时配置一次，保持不变：

```python
from langchain.agents import create_agent


# 方式1：通过 模型型号 创建
agent = create_agent(
    "gpt-5",  # 支持自动推断，存在映射配置
    tools=tools
)


# 方式2：通过 模型对象
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

model = ChatOpenAI(
    model="gpt-5", 
    temperature=0.1,
    max_tokens=1000,嗯
    timeout=30
    # ... (other params)
)

agent = create_agent(model, tools=tools)
```

#### 动态模型
运行时根据状态选择模型：

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse

# 基础模型
basic_model = ChatOpenAI(model="gpt-4o-mini")
# 高级模型
advanced_model = ChatOpenAI(model="gpt-4o")

@wrap_model_call
def dynamic_model_selection(request: ModelRequest, handler) -> ModelResponse:
    """根据对话复杂度选择模型。"""
    message_count = len(request.state["messages"])

    if message_count > 10:
        # 对于较长的对话使用高级模型
        model = advanced_model
    else:
        model = basic_model

    return handler(request.override(model=model))

agent = create_agent(
    model=basic_model,  # 默认模型
    tools=tools,
    middleware=[dynamic_model_selection]
)
```

### 工具 (Tools)

工具赋予代理行动能力，支持：
- 序列中的多个工具调用
- 并行工具调用
- 动态工具选择
- 错误处理和重试

#### 定义工具
```python
from langchain.tools import tool

@tool
def search(query: str) -> str:
    """搜索信息。"""
    return f"搜索结果: {query}"

@tool
def get_weather(location: str) -> str:
    """获取位置的天气信息。"""
    return f"{location} 的天气: 晴天，72°F"

agent = create_agent(model, tools=[search, get_weather])
```

#### 工具错误处理
```python
from langchain.agents.middleware import wrap_tool_call
from langchain.messages import ToolMessage

@wrap_tool_call
def handle_tool_errors(request, handler):
    try:
        return handler(request)
    except Exception as e:
        return ToolMessage(
            content=f"工具错误: 请检查您的输入并重试。({str(e)})",
            tool_call_id=request.tool_call["id"]
        )

agent = create_agent(
    model="gpt-4o",
    tools=[search, get_weather],
    middleware=[handle_tool_errors]
)
```

### 系统提示 (System prompt)

#### 基本用法
```python
agent = create_agent(
    model,
    tools,
    system_prompt="您是一个有用的助手。请简洁准确。"
)
```

#### 高级用法（支持缓存）
```python
# SystemMessage 的形式 

from langchain.agents import create_agent
from langchain.messages import SystemMessage, HumanMessage

# 文学分析代理
literary_agent = create_agent(
    model="anthropic:claude-sonnet-4-5",
    system_prompt=SystemMessage(
        content=[
            {
                "type": "text",
                "text": "您是一个负责分析文学作品的 AI 助手。",
            },
            {
                "type": "text",
                "text": "<《傲慢与偏见》的全部内容>",
                "cache_control": {"type": "ephemeral"}
            }
        ]
    )
)

result = literary_agent.invoke(
    {"messages": [HumanMessage("分析《傲慢与偏见》的主要主题。")]}
)
```

#### 动态系统提示
```python
@dynamic_prompt
def user_role_prompt(request: ModelRequest) -> str:
    """根据用户角色生成系统提示。"""
    user_role = request.runtime.context.get("user_role", "user")
    base_prompt = "您是一个有用的助手。"

    if user_role == "expert":
        return f"{base_prompt} 提供详细的技术响应。"
    elif user_role == "beginner":
        return f"{base_prompt} 简单解释概念，避免术语。"

    return base_prompt

agent = create_agent(
    model="gpt-4o",
    tools=[web_search],
    middleware=[user_role_prompt],
    context_schema=Context
)

# 系统提示将根据上下文动态设置
result = agent.invoke(
    {"messages": [{"role": "user", "content": "解释机器学习"}]},
    context={"user_role": "expert"}
)
```

### 调用 (Invocation)

```python
result = agent.invoke({
    "messages": [{"role": "user", "content": "旧金山的天气怎么样？"}]
})
```

## 高级概念

### 结构化输出 (Structured output)

#### ToolStrategy（通用）
```python
from pydantic import BaseModel
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

# 联系信息模型
class ContactInfo(BaseModel):
    name: str
    email: str
    phone: str

agent = create_agent(
    model="gpt-4o-mini",
    tools=[search_tool],
    response_format=ToolStrategy(ContactInfo)
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "从以下信息中提取联系信息：John Doe, john@example.com, (555) 123-4567"}]
})

result["structured_response"]
# ContactInfo(name='John Doe', email='john@example.com', phone='(555) 123-4567')
```

#### ProviderStrategy（模型供应商支持）
```python
from langchain.agents.structured_output import ProviderStrategy

agent = create_agent(
    model="gpt-4o",
    response_format=ProviderStrategy(ContactInfo)
)
```

### 记忆 (Memory)

代理通过消息状态维护对话历史，支持自定义状态架构。

#### 通过中间件定义状态（推荐）
```python
from langchain.agents import AgentState
from langchain.agents.middleware import AgentMiddleware
from typing import Any

# 自定义状态类
class CustomState(AgentState):
    user_preferences: dict

# 自定义中间件类
class CustomMiddleware(AgentMiddleware):
    state_schema = CustomState
    tools = [tool1, tool2]

    def before_model(self, state: CustomState, runtime) -> dict[str, Any] | None:
        ...

agent = create_agent(
    model,
    tools=tools,
    middleware=[CustomMiddleware()]
)

# 代理现在可以跟踪除消息之外的额外状态
result = agent.invoke({
    "messages": [{"role": "user", "content": "我更喜欢技术解释"}],
    "user_preferences": {"style": "technical", "verbosity": "detailed"},
})
```

#### 通过 state_schema 定义状态
```python
from langchain.agents import AgentState

# 自定义状态类
class CustomState(AgentState):
    user_preferences: dict

agent = create_agent(
    model,
    tools=[tool1, tool2],
    state_schema=CustomState
)
# 代理现在可以跟踪除消息之外的额外状态
result = agent.invoke({
    "messages": [{"role": "user", "content": "我更喜欢技术解释"}],
    "user_preferences": {"style": "technical", "verbosity": "detailed"},
})
```

### 流式传输 (Streaming)

```python
for chunk in agent.stream({
    "messages": [{"role": "user", "content": "搜索 AI 新闻并总结发现"}]
}, stream_mode="values"):
    # 每个 chunk 包含该时间点的完整状态
    latest_message = chunk["messages"][-1]
    if latest_message.content:
        print(f"代理: {latest_message.content}")
    elif latest_message.tool_calls:
        print(f"调用工具: {[tc['name'] for tc in latest_message.tool_calls]}")
```

### 中间件 (Middleware)

中间件提供强大的可扩展性，用于：
- 调用模型前处理状态（消息修剪、上下文注入）
- 修改或验证模型响应（防护机制、内容过滤）
- 自定义工具执行错误处理
- 动态模型选择
- 添加日志记录、监控或分析

主要装饰器：`@before_model`、`@after_model`、`@wrap_tool_call`、`@dynamic_prompt`

```py
print("🔧 中间件功能概览：")
print("中间件提供强大的可扩展性，用于：")

middleware_features = [
    "调用模型前处理状态（消息修剪、上下文注入）",
    "修改或验证模型响应（防护机制、内容过滤）",
    "自定义工具执行错误处理",
    "动态模型选择",
    "添加日志记录、监控或分析"
]

for i, feature in enumerate(middleware_features, 1):
    print(f"{i}. {feature}")

print("\n🎯 主要装饰器：")
decorators = [
    "@before_model - 在模型调用前处理",
    "@after_model - 在模型调用后处理",
    "@wrap_tool_call - 包装工具调用",
    "@dynamic_prompt - 动态生成提示"
]

for decorator in decorators:
    print(f"  • {decorator}")

print("\n✅ 中间件概念介绍完成")
print("💡 提示: 中间件是扩展代理功能的核心机制，允许在不修改核心逻辑的情况下添加复杂行为")
```

