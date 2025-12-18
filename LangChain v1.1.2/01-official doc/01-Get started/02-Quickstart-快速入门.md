# 快速入门

本快速入门将在几分钟内带您从设置到运行功能完整的 AI 代理。

## 环境要求

- 安装 LangChain 包
- 设置 OpenAI API 密钥：`export OPENAI_API_KEY=your_key`
- 可通过更改模型名称使用其他支持的模型

## 基础代理

创建一个可以回答问题和调用工具的简单代理：

```python
from langchain.agents import create_agent

def get_weather(city: str) -> str:
    """获取给定城市的天气。"""
    return f"{city} 总是晴天！"

agent = create_agent(
    model="gpt-4o",
    tools=[get_weather],
    system_prompt="您是一个有用的助手",
)

# 运行代理
agent.invoke(
    {"messages": [{"role": "user", "content": "旧金山的天气怎么样"}]}
)
```

## 实际应用代理

构建一个展示关键生产概念的天气预报代理：结构化输出、工具集成和对话记忆。

### 系统提示和工具

```python
from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime
from langchain.chat_models import init_chat_model

# 系统提示
SYSTEM_PROMPT = """您是一个会说双关语的专家天气预报员。

您可以访问两个工具：
- get_weather_for_location: 获取特定位置的天气
- get_user_location: 获取用户的位置

如果用户询问天气，请确保您知道位置。"""

# 工具定义
@tool
def get_weather_for_location(city: str) -> str:
    """获取给定城市的天气。"""
    return f"{city} 总是晴天！"

@dataclass
class Context:
    """运行时上下文架构。"""
    user_id: str

@tool
def get_user_location(runtime: ToolRuntime[Context]) -> str:
    """根据用户 ID 检索用户信息。"""
    user_id = runtime.context.user_id
    return "Florida" if user_id == "1" else "SF"

# 模型配置
model = init_chat_model(
    "gpt-4o",
    temperature=0.5,
    timeout=10,
    max_tokens=1000
)
```

### 运行代理

```python
from langchain.agents.structured_output import ToolStrategy
from langgraph.checkpoint.memory import InMemorySaver

# 响应格式
@dataclass
class ResponseFormat:
    """代理的响应架构。"""
    punny_response: str
    weather_conditions: str | None = None

# 记忆
checkpointer = InMemorySaver()

# 创建代理
agent = create_agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[get_user_location, get_weather_for_location],
    context_schema=Context,
    response_format=ToolStrategy(ResponseFormat),
    checkpointer=checkpointer
)

# 运行代理
config = {"configurable": {"thread_id": "1"}}

response = agent.invoke(
    {"messages": [{"role": "user", "content": "外面的天气怎么样？"}]},
    config=config,
    context=Context(user_id="1")
)

print(response['structured_response'])
# ResponseFormat(punny_response="Florida 今天仍然是个'阳光灿烂'的日子！", weather_conditions="Florida 总是晴天！")
```

## 总结

恭喜！您现在拥有一个可以：
- 理解上下文并记住对话
- 智能使用多个工具  
- 提供结构化响应
- 处理用户特定信息
- 维护对话状态

的 AI 代理。