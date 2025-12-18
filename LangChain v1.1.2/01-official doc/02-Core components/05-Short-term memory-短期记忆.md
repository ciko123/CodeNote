# Short-term memory（短期记忆）

## 概述
记忆是让AI代理记住之前交互信息的系统，对学习反馈、适应用户偏好、效率和用户体验至关重要。

- **短期记忆**：在单个线程（对话会话）中记住之前的交互
- **上下文窗口挑战**：长对话可能超出LLM的上下文限制，导致信息丢失或性能下降
- **消息管理**：消息历史不断增长，需要修剪、删除或总结等技术来保持在上下文窗口内


## 使用方法
为代理添加短期记忆，需要在创建代理时指定检查点（checkpointer）：

- **检查点**：提供线程级持久性，将状态保存到数据库或内存
- **状态管理**：短期记忆作为代理状态的一部分进行管理
- **线程隔离**：每个线程保持独立的对话上下文
- **自动更新**：在代理调用或工具执行时自动读写状态
```python
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver  

agent = create_agent(
    "gpt-5",
    tools=[get_user_info],
    checkpointer=InMemorySaver(),  
)

agent.invoke(
    {"messages": [{"role": "user", "content": "你好！我的名字是鲍勃。"}]},
    {"configurable": {"thread_id": "1"}},  
)
```

## 生产环境
在生产环境中，使用由数据库支持的检查点：
```bash
pip install langgraph-checkpoint-postgres
```
```python
from langchain.agents import create_agent
from langgraph.checkpoint.postgres import PostgresSaver  

DB_URI = "postgresql://postgres:postgres@localhost:5442/postgres?sslmode=disable"

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup() # 在PostgreSQL中自动创建表
    agent = create_agent(
        "gpt-5",
        tools=[get_user_info],
        checkpointer=checkpointer,  
    )
```

## 自定义代理记忆
```python
from langchain.agents import create_agent, AgentState
from langgraph.checkpoint.memory import InMemorySaver

class CustomAgentState(AgentState):  
    user_id: str
    preferences: dict

agent = create_agent(
    "gpt-5",
    tools=[get_user_info],
    state_schema=CustomAgentState,  
    checkpointer=InMemorySaver(),
)

# 自定义状态可以在 invoke 中传递
result = agent.invoke(
    {
        "messages": [{"role": "user", "content": "你好"}],
        "user_id": "user_123",  
        "preferences": {"theme": "dark"}  
    },
    {"configurable": {"thread_id": "1"}})
```

## 常见模式
启用短期记忆后，长对话可能会超出LLM的上下文窗口。常见的解决方案包括：

- **修剪消息**：移除前N条或后N条消息（在调用LLM之前）
- **删除消息**：从LangGraph状态中永久删除消息
- **总结消息**：总结历史中的早期消息并用摘要替换它们
- **自定义策略**：自定义策略（例如，消息过滤等）

这使得代理能够在不超出LLM上下文窗口的情况下跟踪对话。


### Trim messages 修剪消息
大多数LLM都有一个最大支持的上下文窗口（以token为单位）。
决定何时截断消息的一种方法是计算消息历史中的token数量，并在接近该限制时进行截断。如果您使用LangChain，可以使用修剪消息工具，并指定要从列表中保留的token数量，以及处理边界的策略（例如，保留最后max_tokens个token）。
要在代理中修剪消息历史，使用 @before_model 中间件装饰器：
```python
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import before_model
from langgraph.runtime import Runtime
from langchain_core.runnables import RunnableConfig
from typing import Any


@before_model
def trim_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """仅保留最后几条消息以适应上下文窗口。"""
    messages = state["messages"]

    if len(messages) <= 3:
        return None  # 无需更改

    first_msg = messages[0]
    recent_messages = messages[-3:] if len(messages) % 2 == 0 else messages[-4:]
    new_messages = [first_msg] + recent_messages

    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),
            *new_messages
        ]
    }

agent = create_agent(
    your_model_here,
    tools=your_tools_here,
    middleware=[trim_messages],
    checkpointer=InMemorySaver(),
)

config: RunnableConfig = {"configurable": {"thread_id": "1"}}

agent.invoke({"messages": "你好，我的名字是鲍勃"}, config)
agent.invoke({"messages": "写一首关于猫的短诗"}, config)
agent.invoke({"messages": "现在为狗写一首"}, config)
final_response = agent.invoke({"messages": "我的名字是什么？"}, config)

final_response["messages"][-1].pretty_print()
```
```
================================== Ai Message ==================================

Your name is Bob. You told me that earlier.
If you'd like me to call you a nickname or use a different name, just say the word.
```

### 删除消息
```python
from langchain.messages import RemoveMessage  

def delete_messages(state):
    messages = state["messages"]
    if len(messages) > 2:
        # 删除最早的两条消息
        return {"messages": [RemoveMessage(id=m.id) for m in messages[:2]]}  
```
要删除所有消息：
```python
from langgraph.graph.message import REMOVE_ALL_MESSAGES

def delete_messages(state):
    return {"messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES)]}
```

删除消息时，请确保生成的消息历史是有效的。检查您正在使用的LLM提供商的限制。例如：

*   某些提供商期望消息历史以用户消息开头
*   大多数提供商要求带有工具调用的助手消息后跟相应的工具结果消息

```python
from langchain.messages import RemoveMessage
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import after_model
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.runtime import Runtime
from langchain_core.runnables import RunnableConfig

@after_model
def delete_old_messages(state: AgentState, runtime: Runtime) -> dict | None:
    """删除旧消息以保持对话可管理。"""
    messages = state["messages"]
    if len(messages) > 2:
        # 删除最早的两条消息
        return {"messages": [RemoveMessage(id=m.id) for m in messages[:2]]}
    return None

agent = create_agent(
    "gpt-5-nano",
    tools=[],
    system_prompt="请简洁明了，直奔主题。",
    middleware=[delete_old_messages],
    checkpointer=InMemorySaver(),
)

config: RunnableConfig = {"configurable": {"thread_id": "1"}}

for event in agent.stream(
    {"messages": [{"role": "user", "content": "你好！我是鲍勃"}]},
    config,
    stream_mode="values",
):
    print([(message.type, message.content) for message in event["messages"]])

for event in agent.stream(
    {"messages": [{"role": "user", "content": "我的名字是什么？"}]},
    config,
    stream_mode="values",
):
    print([(message.type, message.content) for message in event["messages"]])
```

```
[('human', "你好！我是鲍勃")]
[('human', "你好！我是鲍勃"), ('ai', '你好鲍勃！很高兴认识你。今天我能为你做些什么？我可以回答问题、头脑风暴、起草文本、解释事物或帮助编写代码。')]
[('human', "你好！我是鲍勃"), ('ai', '你好鲍勃！很高兴认识你。今天我能为你做些什么？我可以回答问题、头脑风暴、起草文本、解释事物或帮助编写代码。'), ('human', '我的名字是什么？')]
[('human', "你好！我是鲍勃"), ('ai', '你好鲍勃！很高兴认识你。今天我能为你做些什么？我可以回答问题、头脑风暴、起草文本、解释事物或帮助编写代码。'), ('human', '我的名字是什么？'), ('ai', '你的名字是鲍勃。今天我能为你做些什么，鲍勃？')]
[('human', '我的名字是什么？'), ('ai', '你的名字是鲍勃。今天我能为你做些什么，鲍勃？')]
```


### Summarize messages 总结消息
```python
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig

checkpointer = InMemorySaver()

agent = create_agent(
    model="gpt-4o",
    tools=[],
    middleware=[
        SummarizationMiddleware(
            model="gpt-4o-mini",
            trigger=("tokens", 4000),
            keep=("messages", 20)
        )
    ],
    checkpointer=checkpointer,
)

config: RunnableConfig = {"configurable": {"thread_id": "1"}}
agent.invoke({"messages": "你好，我的名字是鲍勃"}, config)
agent.invoke({"messages": "写一首关于猫的短诗"}, config)
agent.invoke({"messages": "现在为狗写一首"}, config)
final_response = agent.invoke({"messages": "我的名字是什么？"}, config)

final_response["messages"][-1].pretty_print()

# > Your name is Bob!
```
## 访问记忆
您可以通过几种方式访问和修改代理的短期记忆（状态）：

### 工具

#### 在工具中读取短期记忆
使用 ToolRuntime 参数在工具中访问短期记忆（状态）。
tool_runtime 参数对工具签名是隐藏的（因此模型看不到它），但工具可以通过它访问状态。

```python
from langchain.agents import create_agent, AgentState
from langchain.tools import tool, ToolRuntime

class CustomState(AgentState):
    user_id: str

@tool
def get_user_info(
    runtime: ToolRuntime
) -> str:
    """查找用户信息。"""
    user_id = runtime.state["user_id"]
    return "User is John Smith" if user_id == "user_123" else "Unknown user"

agent = create_agent(
    model="gpt-5-nano",
    tools=[get_user_info],
    state_schema=CustomState,
)

result = agent.invoke({
    "messages": "查找用户信息",
    "user_id": "user_123"
})
print(result["messages"][-1].content)
# > User is John Smith.
```

#### 从工具写入短期记忆
要在执行期间修改代理的短期记忆（状态），您可以直接从工具返回状态更新。
这对于持久化中间结果或使信息对后续工具或提示可访问很有用。

```python
from langchain.tools import tool, ToolRuntime
from langchain_core.runnables import RunnableConfig
from langchain.messages import ToolMessage
from langchain.agents import create_agent, AgentState
from langgraph.types import Command
from pydantic import BaseModel

class CustomState(AgentState):  
    user_name: str

class CustomContext(BaseModel):
    user_id: str

@tool
def update_user_info(
    runtime: ToolRuntime[CustomContext, CustomState],
) -> Command:
    """查找并更新用户信息。"""
    user_id = runtime.context.user_id
    name = "John Smith" if user_id == "user_123" else "Unknown user"
    return Command(update={  
        "user_name": name,
        # 更新消息历史
        "messages": [
            ToolMessage(
                "成功查找用户信息",
                tool_call_id=runtime.tool_call_id
            )
        ]
    })

@tool
def greet(
    runtime: ToolRuntime[CustomContext, CustomState]
) -> str | Command:
    """一旦找到用户信息，使用此功能向用户问好。"""
    user_name = runtime.state.get("user_name", None)
    if user_name is None:
       return Command(update={
            "messages": [
                ToolMessage(
                    "请调用'update_user_info'工具，它将获取并更新用户姓名。",
                    tool_call_id=runtime.tool_call_id
                )
            ]
        })
    return f"Hello {user_name}!"

agent = create_agent(
    model="gpt-5-nano",
    tools=[update_user_info, greet],
    state_schema=CustomState, 
    context_schema=CustomContext,
)

agent.invoke(
    {"messages": [{"role": "user", "content": "向用户问好"}]},
    context=CustomContext(user_id="user_123"),
)
```

### 提示词
在中间件中访问短期记忆（状态），以基于对话历史或自定义状态字段创建动态提示词。
```python
from langchain.agents import create_agent
from typing import TypedDict
from langchain.agents.middleware import dynamic_prompt, ModelRequest

class CustomContext(TypedDict):
    user_name: str

def get_weather(city: str) -> str:
    """获取城市天气。"""
    return f"{city}的天气总是晴朗的！"

@dynamic_prompt
def dynamic_system_prompt(request: ModelRequest) -> str:
    user_name = request.runtime.context["user_name"]
    system_prompt = f"您是一个有用的助手。请称呼用户为{user_name}。"
    return system_prompt

agent = create_agent(
    model="gpt-5-nano",
    tools=[get_weather],
    middleware=[dynamic_system_prompt],
    context_schema=CustomContext,
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "旧金山的天气怎么样？"}]},
    context=CustomContext(user_name="John Smith"),
)
for msg in result["messages"]:
    msg.pretty_print()
```

```
================================ Human Message =================================

旧金山的天气怎么样？
================================== Ai Message =================================
Tool Calls:
  get_weather (call_WFQlOGn4b2yoJrv7cih342FG)
 Call ID: call_WFQlOGn4b2yoJrv7cih342FG
  Args:
    city: San Francisco
================================= Tool Message =================================
Name: get_weather

旧金山的天气总是晴朗的！
================================== Ai Message =================================

你好 John Smith，旧金山的天气总是晴朗的！
```

### 模型调用前
在 @before_model 中间件中访问短期记忆（状态），在模型调用之前处理消息。
```python
from langchain.messages import RemoveMessage
from langgraph.graph.message import REMOVE_ALL_MESSAGES
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import before_model
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from typing import Any

@before_model
def trim_messages(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    """仅保留最后几条消息以适应上下文窗口。"""
    messages = state["messages"]

    # 如果消息数量不超过3条，无需修剪
    if len(messages) <= 3:
        return None  # 无需更改

    # 保留第一条消息（通常是系统提示或初始上下文）
    first_msg = messages[0]
    
    # 根据消息总数的奇偶性决定保留的消息数量
    # 偶数条消息时保留最后3条，奇数条时保留最后4条
    recent_messages = messages[-3:] if len(messages) % 2 == 0 else messages[-4:]
    
    # 组合保留的消息
    new_messages = [first_msg] + recent_messages

    # 返回操作：先删除所有消息，然后添加保留的消息
    return {
        "messages": [
            RemoveMessage(id=REMOVE_ALL_MESSAGES),  # 删除所有现有消息
            *new_messages  # 添加新组合的消息
        ]
    }

agent = create_agent(
    "gpt-5-nano",
    tools=[],
    middleware=[trim_messages],
    checkpointer=InMemorySaver()
)

config: RunnableConfig = {"configurable": {"thread_id": "1"}}

agent.invoke({"messages": "你好，我的名字是鲍勃"}, config)
agent.invoke({"messages": "写一首关于猫的短诗"}, config)
agent.invoke({"messages": "现在为狗写一首"}, config)
final_response = agent.invoke({"messages": "我的名字是什么？"}, config)

final_response["messages"][-1].pretty_print()
```

```
================================== Ai Message ==================================

你的名字是鲍勃。你之前告诉过我。
如果你希望我用昵称称呼你或使用不同的名字，尽管说。
```

### 模型调用后
在 @after_model 中间件中访问短期记忆（状态），在模型调用之后处理消息。
```python
from langchain.messages import RemoveMessage
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import after_model
from langgraph.runtime import Runtime

@after_model
def validate_response(state: AgentState, runtime: Runtime) -> dict | None:
    """删除包含敏感词的消息。"""
    STOP_WORDS = ["password", "secret"]
    last_message = state["messages"][-1]
    if any(word in last_message.content for word in STOP_WORDS):
        return {"messages": [RemoveMessage(id=last_message.id)]}
    return None

agent = create_agent(
    model="gpt-5-nano",
    tools=[],
    middleware=[validate_response],
    checkpointer=InMemorySaver(),
)
```
