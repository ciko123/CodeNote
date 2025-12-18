# 自定义中间件 (Custom middleware)

通过在agent (代理)执行流程的特定点实现钩子 (hooks) 来构建自定义中间件。

## 钩子 (Hooks)

中间件提供两种风格的钩子来拦截agent执行：

**节点式钩子 (Node-style hooks)**
在特定执行点顺序运行。用于日志记录、验证和状态更新。

**包装式钩子 (Wrap-style hooks)**
围绕每个模型或工具调用运行。

### 节点式钩子 (Node-style hooks)

在特定执行点顺序运行。用于日志记录、验证和状态更新。

**可用钩子：**

* `before_agent` - agent启动前（每次调用一次）
* `before_model` - 每次模型调用前
* `after_model` - 每次模型响应后
* `after_agent` - agent完成后（每次调用一次）

**示例：**

**装饰器示例：**
```python
from langchain.agents.middleware import before_model, after_model, AgentState
from langchain.messages import AIMessage
from langgraph.runtime import Runtime
from typing import Any


@before_model(can_jump_to=["end"])
def check_message_limit(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    if len(state["messages"]) >= 50:
        return {
            "messages": [AIMessage("对话限制已到达。")],
            "jump_to": "end"
        }
    return None

@after_model
def log_response(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    print(f"模型返回: {state['messages'][-1].content}")
    return None
```

**类示例：**
```python
from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langchain.messages import AIMessage
from langgraph.runtime import Runtime
from typing import Any

class MessageLimitMiddleware(AgentMiddleware):
    def __init__(self, max_messages: int = 50):
        super().__init__()
        self.max_messages = max_messages

    @hook_config(can_jump_to=["end"])
    def before_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        if len(state["messages"]) == self.max_messages:
            return {
                "messages": [AIMessage("对话限制已到达。")],
                "jump_to": "end"
            }
        return None

    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"模型返回: {state['messages'][-1].content}")
        return None
```

### 包装式钩子 (Wrap-style hooks)

拦截执行并控制处理程序的调用时机。用于重试、缓存和转换。

您可以决定处理程序被调用零次（短路）、一次（正常流程）或多次（重试逻辑）。

**可用钩子：**

* `wrap_model_call` - 围绕每次模型调用
* `wrap_tool_call` - 围绕每次工具调用

**示例：**

```python
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from typing import Callable


@wrap_model_call
def retry_model(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    for attempt in range(3):
        try:
            return handler(request)
        except Exception as e:
            if attempt == 2:
                raise
            print(f"错误后重试 {attempt + 1}/3: {e}")
```


```python
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from typing import Callable

class RetryMiddleware(AgentMiddleware):
    def __init__(self, max_retries: int = 3):
        super().__init__()
        self.max_retries = max_retries

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        for attempt in range(self.max_retries):
            try:
                return handler(request)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                print(f"错误后重试 {attempt + 1}/{self.max_retries}: {e}")
```

## 创建中间件 (Create middleware)

您可以通过两种方式创建中间件：
简单快速地为单个钩子创建中间件。使用装饰器来包装单个函数。
更强大的复杂中间件，支持多个钩子或配置。

### Decorator-based middleware

快速简单地为单个钩子创建中间件。使用装饰器来包装单个函数。

**可用装饰器：**

**节点式：**

* [`@before_agent`](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.before_agent) - Runs before agent starts (once per invocation)
* [`@before_model`](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.before_model) - Runs before each model call
* [`@after_model`](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.after_model) - Runs after each model response
* [`@after_agent`](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.after_agent) - Runs after agent completes (once per invocation)

**包装式：**

* [`@wrap_model_call`](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.wrap_model_call) - Wraps each model call with custom logic
* [`@wrap_tool_call`](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.wrap_tool_call) - Wraps each tool call with custom logic

**便捷装饰器：**

* [`@dynamic_prompt`](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.dynamic_prompt) - Generates dynamic system prompts

**Example:**

```python
from langchain.agents.middleware import (
    before_model,
    wrap_model_call,
    AgentState,
    ModelRequest,
    ModelResponse,
)
from langchain.agents import create_agent
from langgraph.runtime import Runtime
from typing import Any, Callable

@before_model
def log_before_model(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    print(f"即将调用模型，包含 {len(state['messages'])} 条消息")
    return None

@wrap_model_call
def retry_model(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    for attempt in range(3):
        try:
            return handler(request)
        except Exception as e:
            if attempt == 2:
                raise
            print(f"错误后重试 {attempt + 1}/3: {e}")

agent = create_agent(
    model="gpt-4o",
    middleware=[log_before_model, retry_model],
    tools=[],
)

# 使用自定义状态调用
result = agent.invoke({
    "messages": [HumanMessage("你好")],
    "model_call_count": 0,
    "user_id": "user-123",
})
```

**何时使用装饰器：**

* 需要单个钩子
* 无复杂配置
* 快速原型开发

### 基于类的中间件 (Class-based middleware)

更强大的复杂中间件，支持多个钩子或配置。当您需要为同一钩子定义同步和异步实现，或者想在单个中间件中组合多个钩子时，使用类。

**示例：**

```python
from langchain.agents.middleware import (
    AgentMiddleware,
    AgentState,
    ModelRequest,
    ModelResponse,
)
from langgraph.runtime import Runtime
from typing import Any, Callable

class LoggingMiddleware(AgentMiddleware):
    def before_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"即将调用模型，包含 {len(state['messages'])} 条消息")
        return None

    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        print(f"模型返回: {state['messages'][-1].content}")
        return None

agent = create_agent(
    model="gpt-4o",
    middleware=[LoggingMiddleware()],
    tools=[...],
)
```

**何时使用类：**

* 为同一钩子定义同步和异步实现
* 在单个中间件中需要多个钩子
* 需要复杂配置（例如可配置阈值、自定义模型）
* 跨项目重用，具有初始化时配置

## 自定义状态模式 (Custom state schema)

中间件可以用自定义属性扩展agent的状态。这使得中间件能够：

* **跨执行跟踪状态**：维护计数器、标志或在agent执行生命周期中持续存在的其他值

* **在钩子间共享数据**：将信息从`before_model`传递到`after_model`或在不同中间件实例之间传递

* **实现横切关注点**：添加如频率限制、使用跟踪、用户上下文或审计日志等功能，而无需修改核心agent逻辑

* **做出条件决策**：使用累积状态来决定是否继续执行、跳转到不同节点或动态修改行为


```python
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.agents.middleware import AgentState, before_model, after_model
from typing_extensions import NotRequired
from typing import Any
from langgraph.runtime import Runtime


class CustomState(AgentState):
    model_call_count: NotRequired[int]
    user_id: NotRequired[str]


@before_model(state_schema=CustomState, can_jump_to=["end"])
def check_call_limit(state: CustomState, runtime: Runtime) -> dict[str, Any] | None:
    count = state.get("model_call_count", 0)
    if count > 10:
        return {"jump_to": "end"}
    return None


@after_model(state_schema=CustomState)
def increment_counter(state: CustomState, runtime: Runtime) -> dict[str, Any] | None:
    return {"model_call_count": state.get("model_call_count", 0) + 1}


agent = create_agent(
    model="gpt-4o",
    middleware=[check_call_limit, increment_counter],
    tools=[],
)

# 使用自定义状态调用
result = agent.invoke({
    "messages": [HumanMessage("你好")],
    "model_call_count": 0,
    "user_id": "user-123",
})
```

```python
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.agents.middleware import AgentState, AgentMiddleware
from typing_extensions import NotRequired
from typing import Any

class CustomState(AgentState):
    model_call_count: NotRequired[int]
    user_id: NotRequired[str]


class CallCounterMiddleware(AgentMiddleware[CustomState]):
    state_schema = CustomState

    def before_model(self, state: CustomState, runtime) -> dict[str, Any] | None:
        count = state.get("model_call_count", 0)
        if count > 10:
            return {"jump_to": "end"}
        return None

    def after_model(self, state: CustomState, runtime) -> dict[str, Any] | None:
        return {"model_call_count": state.get("model_call_count", 0) + 1}


agent = create_agent(
    model="gpt-4o",
    middleware=[CallCounterMiddleware()],
    tools=[],
)

# 使用自定义状态调用
result = agent.invoke({
    "messages": [HumanMessage("你好")],
    "model_call_count": 0,
    "user_id": "user-123",
})
```
## 执行顺序 (Execution order)

使用多个中间件时，了解它们的执行方式：

```python
agent = create_agent(
    model="gpt-4o",
    middleware=[middleware1, middleware2, middleware3],
    tools=[...],
)
```


  **Before hooks run in order:**

  1. `middleware1.before_agent()`
  2. `middleware2.before_agent()`
  3. `middleware3.before_agent()`

  **Agent loop starts**

  4. `middleware1.before_model()`
  5. `middleware2.before_model()`
  6. `middleware3.before_model()`

  **Wrap hooks nest like function calls:**

  7. `middleware1.wrap_model_call()` → `middleware2.wrap_model_call()` → `middleware3.wrap_model_call()` → model

  **After hooks run in reverse order:**

  8. `middleware3.after_model()`
  9. `middleware2.after_model()`
  10. `middleware1.after_model()`

  **Agent loop ends**

  11. `middleware3.after_agent()`
  12. `middleware2.after_agent()`
    13. `middleware1.after_agent()`

**关键规则：**

* `before_*` 钩子：从第一个到最后一个
* `after_*` 钩子：从最后一个到第一个（反向）
* `wrap_*` 钩子：嵌套（第一个中间件包装所有其他）

## Agent跳转 (Agent jumps)

要从中间件提前退出，返回包含`jump_to`的字典：

**可用跳转目标：**

* `'end'`: 跳转到agent执行的末尾（或第一个`after_agent`钩子）
* `'tools'`: 跳转到工具节点
* `'model'`: 跳转到模型节点（或第一个`before_model`钩子）


```py
from langchain.agents.middleware import after_model, hook_config, AgentState
from langchain.messages import AIMessage
from langgraph.runtime import Runtime
from typing import Any
```


```python
@after_model
@hook_config(can_jump_to=["end"])
def check_for_blocked(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
    last_message = state["messages"][-1]
    if "BLOCKED" in last_message.content:
        return {
            "messages": [AIMessage("我无法回应该请求。")],
            "jump_to": "end"
        }
    return None

```

```python
from langchain.agents.middleware import AgentMiddleware, hook_config, AgentState
from langchain.messages import AIMessage
from langgraph.runtime import Runtime
from typing import Any

class BlockedContentMiddleware(AgentMiddleware):
    @hook_config(can_jump_to=["end"])
    def after_model(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
        last_message = state["messages"][-1]
        if "BLOCKED" in last_message.content:
            return {
                "messages": [AIMessage("我无法回应该请求。")],
                "jump_to": "end"
            }
        return None
```

## 最佳实践 (Best practices)

1. 保持中间件专注 - 每个应该做好一件事
2. 优雅地处理错误 - 不要让中间件错误导致agent崩溃
3. **使用适当的钩子类型**：
   * 节点式用于顺序逻辑（日志记录、验证）
   * 包装式用于控制流（重试、降级、缓存）
4. 清晰地记录任何自定义状态属性
5. 在集成前独立单元测试中间件
6. 考虑执行顺序 - 将关键中间件放在列表中的第一位
7. 尽可能使用内置中间件

## 示例 (Examples)

### 动态模型选择 (Dynamic model selection)


```py
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain.chat_models import init_chat_model
from typing import Callable

complex_model = init_chat_model("gpt-4o")
simple_model = init_chat_model("gpt-4o-mini")

@wrap_model_call
def dynamic_model(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    # 根据对话长度使用不同的模型
    if len(request.messages) > 10:
        model = complex_model
    else:
        model = simple_model
    return handler(request.override(model=model))

```

```python
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain.chat_models import init_chat_model
from typing import Callable

complex_model = init_chat_model("gpt-4o")
simple_model = init_chat_model("gpt-4o-mini")

class DynamicModelMiddleware(AgentMiddleware):
    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        # 根据对话长度使用不同的模型
        if len(request.messages) > 10:
            model = complex_model
        else:
            model = simple_model
        return handler(request.override(model=model))
```

### 工具调用监控 (Tool call monitoring)


```python
from langchain.agents.middleware import wrap_tool_call
from langchain.tools.tool_node import ToolCallRequest
from langchain.messages import ToolMessage
from langgraph.types import Command
from typing import Callable

@wrap_tool_call
def monitor_tool(
    request: ToolCallRequest,
    handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    print(f"Executing tool: {request.tool_call['name']}")
    print(f"Arguments: {request.tool_call['args']}")
    try:
        result = handler(request)
        print(f"工具成功完成")
        return result
    except Exception as e:
        print(f"工具失败: {e}")
        raise
```

```python
from langchain.tools.tool_node import ToolCallRequest
from langchain.agents.middleware import AgentMiddleware
from langchain.messages import ToolMessage
from langgraph.types import Command
from typing import Callable

class ToolMonitoringMiddleware(AgentMiddleware):
    def wrap_tool_call(
        self,
        request: ToolCallRequest,
        handler: Callable[[ToolCallRequest], ToolMessage | Command],
    ) -> ToolMessage | Command:
        print(f"Executing tool: {request.tool_call['name']}")
        print(f"Arguments: {request.tool_call['args']}")
        try:
            result = handler(request)
            print(f"工具成功完成")
            return result
        except Exception as e:
            print(f"工具失败: {e}")
            raise
```


### 动态选择工具 (Dynamically selecting tools)

在运行时选择相关工具以提高性能和准确性。

**优势：**

* **更短的提示词** - 通过仅暴露相关工具来降低复杂性
* **更好的准确性** - 模型从更少选项中正确选择
* **权限控制** - 基于用户访问权限动态过滤工具


```python
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from typing import Callable


@wrap_model_call
def select_tools(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    """根据状态/上下文选择相关工具的中间件。"""
    # 根据状态/上下文选择一个小的、相关的工具子集
    relevant_tools = select_relevant_tools(request.state, request.runtime)
    return handler(request.override(tools=relevant_tools))

agent = create_agent(
    model="gpt-4o",
    tools=all_tools,  # 所有可用工具都需要预先注册
    middleware=[select_tools],
)
```

```python
from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from typing import Callable

class ToolSelectorMiddleware(AgentMiddleware):
    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """根据状态/上下文选择相关工具的中间件。"""
        # 根据状态/上下文选择一个小的、相关的工具子集
        relevant_tools = select_relevant_tools(request.state, request.runtime)
        return handler(request.override(tools=relevant_tools))

agent = create_agent(
    model="gpt-4o",
    tools=all_tools,  # 所有可用工具都需要预先注册
    middleware=[ToolSelectorMiddleware()],
)
```


### 处理系统消息 (Working with system messages)

使用`ModelRequest`上的`system_message`字段在中间件中修改系统消息。`system_message`字段包含一个[`SystemMessage`](https://reference.langchain.com/python/langchain/messages/#langchain.messages.SystemMessage)对象（即使agent是用字符串`system_prompt`创建的）。

**示例：向系统消息添加上下文**


```python
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain.messages import SystemMessage
from typing import Callable

@wrap_model_call
def add_context(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    # 始终使用内容块工作
    new_content = list(request.system_message.content_blocks) + [
        {"type": "text", "text": "附加上下文。"}
    ]
    new_system_message = SystemMessage(content=new_content)
    return handler(request.override(system_message=new_system_message))
```

```python
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain.messages import SystemMessage
from typing import Callable

class ContextMiddleware(AgentMiddleware):
    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        # 始终使用内容块工作
        new_content = list(request.system_message.content_blocks) + [
            {"type": "text", "text": "附加上下文。"}
        ]
        new_system_message = SystemMessage(content=new_content)
        return handler(request.override(system_message=new_system_message))
```


**示例：使用缓存控制 (Anthropic)**

当使用Anthropic模型时，您可以使用带有缓存控制指令的结构化内容块来缓存大型系统提示词：

```python
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain.messages import SystemMessage
from typing import Callable

@wrap_model_call
def add_cached_context(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    # 始终使用内容块工作
    new_content = list(request.system_message.content_blocks) + [
        {
            "type": "text",
            "text": "这里是一个大型文档需要分析：\n\n<document>...</document>",
            # 内容直到这一点是缓存的
            "cache_control": {"type": "ephemeral"}
        }
    ]

    new_system_message = SystemMessage(content=new_content)
    return handler(request.override(system_message=new_system_message))
```

```python
from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain.messages import SystemMessage
from typing import Callable

class CachedContextMiddleware(AgentMiddleware):
    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        # 始终使用内容块工作
        new_content = list(request.system_message.content_blocks) + [
            {
                "type": "text",
                "text": "这里是一个大型文档需要分析：\n\n<document>...</document>",
                "cache_control": {"type": "ephemeral"}  # 这个内容将被缓存
            }
        ]

        new_system_message = SystemMessage(content=new_content)
        return handler(request.override(system_message=new_system_message))
```


**注意事项：**

* `ModelRequest.system_message` 总是一个[`SystemMessage`](https://reference.langchain.com/python/langchain/messages/#langchain.messages.SystemMessage)对象，即使agent是用`system_prompt="string"`创建的
* 使用`SystemMessage.content_blocks`以块列表的形式访问内容，无论原始内容是字符串还是列表
* 修改系统消息时，使用`content_blocks`并追加新块以保留现有结构
* 您可以将[`SystemMessage`](https://reference.langchain.com/python/langchain/messages/#langchain.messages.SystemMessage)对象直接传递给`create_agent`的`system_prompt`参数，用于缓存控制等高级用例

## 其他资源 (Additional resources)

* [中间件API参考](https://reference.langchain.com/python/langchain/middleware/)
* [内置中间件](/oss/python/langchain/middleware/built-in)
* [测试代理](/oss/python/langchain/test)

***

