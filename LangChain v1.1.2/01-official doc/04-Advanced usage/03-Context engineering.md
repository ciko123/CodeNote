# Agent中的上下文工程 (Context engineering in agents)

## 概述 (Overview)

构建agent（或任何LLM应用程序）的难点在于使它们足够可靠。虽然它们可能适用于原型，但在实际用例中经常失败。

### 为什么agent会失败？ (Why do agents fail?)

当agent失败时，通常是因为agent内部的LLM调用执行了错误的操作/没有按预期执行。LLM失败的原因有两个之一：

1. 底层LLM能力不足
2. 没有向LLM传递"正确"的上下文

更多时候，实际上是第二个原因导致agent不可靠。

**上下文工程 (Context engineering)** 是以正确的格式提供正确的信息和工具，以便LLM能够完成任务。这是AI工程师的首要工作。缺乏"正确"的上下文是更可靠agent的首要障碍，而LangChain的agent抽象是专门设计来促进上下文工程的。

上下文工程新手？从[概念概述](/oss/python/concepts/context)开始，了解不同类型的上下文以及何时使用它们。

### Agent循环 (The agent loop)

典型的agent循环包含两个主要步骤：

1. **模型调用 (Model call)** - 使用提示词和可用工具调用LLM，返回响应或执行工具的请求
2. **工具执行 (Tool execution)** - 执行LLM请求的工具，返回工具结果


此循环持续进行，直到LLM决定完成。

### 您可以控制的内容 (What you can control)

要构建可靠的agent，您需要控制agent循环中每个步骤发生的事情，以及步骤之间发生的事情。

| 上下文类型 (Context Type) | 您控制的内容 (What You Control) | 瞬时或持久 (Transient or Persistent) |
| --------------------------------------------- | ------------------------------------------------------------------------------------ | ----------------------- |
| **[模型上下文](#model-context) (Model Context)** | 进入模型调用的内容（指令、消息历史、工具、响应格式） | 瞬时 (Transient) |
| **[工具上下文](#tool-context) (Tool Context)** | 工具可以访问和产生的内容（对状态、存储、运行时上下文的读/写） | 持久 (Persistent) |
| **[生命周期上下文](#life-cycle-context) (Life-cycle Context)** | 模型和工具调用之间发生的事情（摘要、防护机制、日志记录等） | 持久 (Persistent) |

  - **瞬时上下文**:
    LLM在单次调用中看到的内容。您可以修改消息、工具或提示词，而不会改变保存在状态中的内容。
  
  - **持久上下文**:
    在轮次之间保存在状态中的内容。生命周期钩子和工具写入会永久修改此内容。

### 数据源 (Data sources)

在此过程中，您的agent访问（读/写）不同的数据源：

| 数据源 (Data Source) | 又称为 (Also Known As) | 范围 (Scope) | 示例 (Examples) |
| ------------------- | -------------------- | ------------------- | -------------------------------------------------------------------------- |
| **运行时上下文 (Runtime Context)** | 静态配置 (Static configuration) | 对话范围 (Conversation-scoped) | 用户ID、API密钥、数据库连接、权限、环境设置 |
| **状态 (State)** | 短期记忆 (Short-term memory) | 对话范围 (Conversation-scoped) | 当前消息、上传的文件、身份验证状态、工具结果 |
| **存储 (Store)** | 长期记忆 (Long-term memory) | 跨对话 (Cross-conversation) | 用户偏好、提取的洞察、记忆、历史数据 |

### 工作原理 (How it works)

LangChain[中间件](/oss/python/langchain/middleware)是底层机制，使上下文工程对使用LangChain的开发者变得实用。

中间件允许您钩入agent生命周期中的任何步骤并：

* 更新上下文
* 跳转到agent生命周期中的不同步骤

在本指南中，您将看到频繁使用中间件API作为实现上下文工程目标的手段。

## 模型上下文 (Model Context)

控制进入每个模型调用的内容 - 指令、可用工具、使用哪个模型以及输出格式。这些决策直接影响可靠性和成本。

  - **系统提示词**:
    开发者给LLM的基本指令。
  
  - **消息**:
    发送给LLM的完整消息列表（对话历史）。
  
  - **工具**:
    agent可以访问以采取操作的实用程序。
  
  - **模型**:
    要调用的实际模型（包括配置）。
  
  - **响应格式**:
    模型最终响应的模式规范。

所有这些类型的模型上下文都可以从**状态**（短期记忆）、**存储**（长期记忆）或**运行时上下文**（静态配置）中获取。

### 系统提示词 (System Prompt)

系统提示词设置LLM的行为和能力。不同的用户、上下文或对话阶段需要不同的指令。成功的agent利用记忆、偏好和配置为对话的当前状态提供正确的指令。

  **状态 (State)**:
    从状态访问消息数量或对话上下文：

```python
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest

@dynamic_prompt
def state_aware_prompt(request: ModelRequest) -> str:
    # request.messages is a shortcut for request.state["messages"]
    message_count = len(request.messages)

    base = "您是帮助助手。"

    if message_count > 10:
        base += "\n这是一个长对话 - 请尽量简洁。"

    return base

agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[state_aware_prompt]
)
```

  **存储 (Store)**:
    从长期记忆访问用户偏好：

```python
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest
from langgraph.store.memory import InMemoryStore

@dataclass
class Context:
    user_id: str

@dynamic_prompt
def store_aware_prompt(request: ModelRequest) -> str:
    user_id = request.runtime.context.user_id

    # Read from Store: get user preferences
    store = request.runtime.store
    user_prefs = store.get(("preferences",), user_id)

    base = "您是帮助助手。"

    if user_prefs:
        style = user_prefs.value.get("communication_style", "balanced")
        base += f"\n用户偏好 {style} 响应。"

    return base

agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[store_aware_prompt],
    context_schema=Context,
    store=InMemoryStore()
)
```

  **运行时上下文 (Runtime Context)**:
    从运行时上下文访问用户ID或配置：

```python
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.agents.middleware import dynamic_prompt, ModelRequest

@dataclass
class Context:
user_role: str
deployment_env: str

@dynamic_prompt
def context_aware_prompt(request: ModelRequest) -> str:
# Read from Runtime Context: user role and environment
user_role = request.runtime.context.user_role
env = request.runtime.context.deployment_env

base = "您是帮助助手。"

if user_role == "admin":
    base += "\n您有管理员访问权限。您可以执行所有操作。"
elif user_role == "viewer":
    base += "\n您有只读访问权限。请指导用户执行只读操作。"

if env == "production":
    base += "\n请小心处理任何数据修改。"

return base

agent = create_agent(
model="gpt-4o",
tools=[...],
middleware=[context_aware_prompt],
context_schema=Context
)
```
### 消息 (Messages)

消息构成发送给LLM的提示词。
管理消息内容以确保LLM有正确的信息来良好响应至关重要。

  **状态 (State)**:
    当与当前查询相关时，从状态注入上传的文件上下文：

```python
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from typing import Callable

@wrap_model_call
def inject_file_context(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """注入关于用户本次会话上传的文件的上下文。"""
    # 从状态读取：获取上传文件的元数据
    uploaded_files = request.state.get("uploaded_files", [])  # [!code highlight]

    if uploaded_files:
        # 构建关于可用文件的上下文
        file_descriptions = []
        for file in uploaded_files:
            file_descriptions.append(
                f"- {file['name']} ({file['type']}): {file['summary']}"
            )

        file_context = f"""您在此对话中可以访问的文件：
{chr(10).join(file_descriptions)}

回答问题时请参考这些文件。"""

        # 在最近的消息之前注入文件上下文
        messages = [  # [!code highlight]
            *request.messages,
            {"role": "user", "content": file_context},
        ]
        request = request.override(messages=messages)  # [!code highlight]

    return handler(request)

agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[inject_file_context]
)
```

  **存储 (Store)**:
    从存储注入用户的电子邮件写作风格以指导起草：

```python
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from typing import Callable
from langgraph.store.memory import InMemoryStore

@dataclass
class Context:
    user_id: str

@wrap_model_call
def inject_writing_style(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """从存储注入用户的电子邮件写作风格。"""
    user_id = request.runtime.context.user_id

    # Read from Store: get user's writing style examples
    store = request.runtime.store
    writing_style = store.get(("writing_style",), user_id)

    if writing_style:
        style = writing_style.value
        # 从存储的示例构建风格指南
        style_context = f"""您的写作风格：
- 语气：{style.get('tone', 'professional')}
- 典型问候语："{style.get('greeting', 'Hi')}"
- 典型结束语："{style.get('sign_off', 'Best')}"
- 您编写的电子邮件示例：
{style.get('example_email', '')}"""

        # Append at end - models pay more attention to final messages
        messages = [
            *request.messages,
            {"role": "user", "content": style_context}
        ]
        request = request.override(messages=messages)  # [!code highlight]

    return handler(request)

agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[inject_writing_style],
    context_schema=Context,
    user_jurisdiction: str
    industry: str
    compliance_frameworks: list[str]

@wrap_model_call
def inject_compliance_rules(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """从运行时上下文注入合规约束。"""
    # 从运行时上下文读取：获取合规要求
    jurisdiction = request.runtime.context.user_jurisdiction  # [!code highlight]
    industry = request.runtime.context.industry  # [!code highlight]
    frameworks = request.runtime.context.compliance_frameworks  # [!code highlight]

    # 构建合规约束
    rules = []
    if "GDPR" in frameworks:
        rules.append("- 必须在处理个人数据之前获得明确同意")
        rules.append("- 用户有权删除数据")
    if "HIPAA" in frameworks:
        rules.append("- 未经授权不得共享患者健康信息")
        rules.append("- 必须使用安全的加密通信")
    if industry == "finance":
        rules.append("- 不能在没有适当免责声明的情况下提供财务建议")

    if rules:
        compliance_context = f"""{jurisdiction}的合规要求:
{chr(10).join(rules)}"""

        # Append at end - models pay more attention to final messages
        messages = [
            *request.messages,
            {"role": "user", "content": compliance_context}
        ]
        request = request.override(messages=messages)  # [!code highlight]

    return handler(request)

agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[inject_compliance_rules],
    context_schema=Context
)
```

  **瞬时 vs 持久消息更新：**

  上面的示例使用`wrap_model_call`进行**瞬时**更新 - 修改发送给模型的消息以进行单次调用，而不改变保存在状态中的内容。

  对于修改状态的**持久**更新（如[生命周期上下文](#summarization)中的摘要示例），使用生命周期钩子如`before_model`或`after_model`来永久更新对话历史。有关更多详情，请参阅[中间件文档](/oss/python/langchain/middleware)。

### 工具 (Tools)

工具让模型能够与数据库、API和外部系统交互。您定义和选择工具的方式直接影响模型是否能够有效完成任务。

#### 定义工具 (Defining tools)

每个工具都需要清晰的名称、描述、参数名称和参数描述。这些不仅仅是元数据 - 它们指导模型关于何时以及如何使用工具的推理。

```python
from langchain.tools import tool

@tool(parse_docstring=True)
def search_orders(
user_id: str,
status: str,
limit: int = 10
) -> str:
"""按状态搜索用户订单。

当用户询问订单历史或想要检查
订单状态时使用此工具。始终按提供的状态过滤。

参数：
    user_id: 用户的唯一标识符
    status: 订单状态：'pending'、'shipped'或'delivered'
    limit: 要返回的最大结果数
"""
# 实现在这里
pass
```


#### 选择工具 (Selecting tools)

并非每个工具都适用于每种情况。太多工具可能会压垮模型（过载上下文）并增加错误；太少工具会限制能力。动态工具选择根据身份验证状态、用户权限、功能标志或对话阶段调整可用工具集。

  **状态 (State)**:
    仅在达到特定对话里程碑后启用高级工具：

```python
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from typing import Callable

@wrap_model_call
def state_based_tools(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """根据对话状态过滤工具。"""
    # 从状态读取：检查用户是否已通过身份验证
    state = request.state  # [!code highlight]
    is_authenticated = state.get("authenticated", False)  # [!code highlight]
    message_count = len(state["messages"])

    # 仅在身份验证后启用敏感工具
    if not is_authenticated:
        tools = [t for t in request.tools if t.name.startswith("public_")]
        request = request.override(tools=tools)  # [!code highlight]
    elif message_count < 5:
        # 在对话早期限制工具
        tools = [t for t in request.tools if t.name != "advanced_search"]
        request = request.override(tools=tools)  # [!code highlight]

    return handler(request)

agent = create_agent(
    model="gpt-4o",
    tools=[public_search, private_search, advanced_search],
    middleware=[state_based_tools]
)
```

  **存储 (Store)**:
    根据存储中的用户偏好或功能标志过滤工具：

```python
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from typing import Callable
from langgraph.store.memory import InMemoryStore

@dataclass
class Context:
    user_id: str

@wrap_model_call
def store_based_tools(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """根据存储偏好过滤工具。"""
    user_id = request.runtime.context.user_id

    # Read from Store: get user's enabled features
    store = request.runtime.store
    feature_flags = store.get(("features",), user_id)

    if feature_flags:
        enabled_features = feature_flags.value.get("enabled_tools", [])
        # 仅包含为此用户启用的工具
        tools = [t for t in request.tools if t.name in enabled_features]
        request = request.override(tools=tools)

    return handler(request)

agent = create_agent(
    model="gpt-4o",
    tools=[search_tool, analysis_tool, export_tool],
    middleware=[store_based_tools],
    context_schema=Context,
    store=InMemoryStore()
)
```

  **运行时上下文 (Runtime Context)**:
    根据运行时上下文的用户权限过滤工具：

```python
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from typing import Callable

@dataclass
class Context:
    user_role: str

@wrap_model_call
def context_based_tools(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """根据运行时上下文权限过滤工具。"""
    # 从运行时上下文读取：获取用户角色
    user_role = request.runtime.context.user_role

    if user_role == "admin":
        # 管理员获得所有工具
        pass
    elif user_role == "editor":
        # 编辑者不能删除
        tools = [t for t in request.tools if t.name != "delete_data"]
        request = request.override(tools=tools)
    else:
        # 查看者获得只读工具
        tools = [t for t in request.tools if t.name.startswith("read_")]
        request = request.override(tools=tools)

    return handler(request)

agent = create_agent(
    model="gpt-4o",
    tools=[read_data, write_data, delete_data],
    middleware=[context_based_tools],
    context_schema=Context
)
```

参见[动态选择工具](/oss/python/langchain/middleware#dynamically-selecting-tools)获取更多示例。

### 模型 (Model)

不同的模型有不同的优势、成本和上下文窗口。为当前任务选择合适的模型，这在agent运行过程中可能会发生变化。

  **状态 (State)**:
    根据状态的对话长度使用不同模型：

```python
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain.chat_models import init_chat_model
from typing import Callable

# Initialize models once outside the middleware
large_model = init_chat_model("claude-sonnet-4-5-20250929")
standard_model = init_chat_model("gpt-4o")
efficient_model = init_chat_model("gpt-4o-mini")

@wrap_model_call
def state_based_model(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """根据状态对话长度选择模型。"""
    # request.messages 是 request.state["messages"] 的快捷方式
    message_count = len(request.messages)  # [!code highlight]

    if message_count > 20:
        # 长对话 - 使用具有更大上下文窗口的模型
        model = large_model
    elif message_count > 10:
        # 中等对话
        model = standard_model
    else:
        # 短对话 - 使用高效模型
        model = efficient_model

    request = request.override(model=model)  # [!code highlight]

    return handler(request)

agent = create_agent(
    model="gpt-4o-mini",
    tools=[...],
    middleware=[state_based_model]
)
```

  **存储 (Store)**:
    使用存储中用户偏好的模型：

```python
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain.chat_models import init_chat_model
from typing import Callable
from langgraph.store.memory import InMemoryStore

@dataclass
class Context:
    user_id: str

# 初始化可用模型一次
MODEL_MAP = {
    "gpt-4o": init_chat_model("gpt-4o"),
    "gpt-4o-mini": init_chat_model("gpt-4o-mini"),
    "claude-sonnet": init_chat_model("claude-sonnet-4-5-20250929"),
}

@wrap_model_call
def store_based_model(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """Select model based on Store preferences."""
    user_id = request.runtime.context.user_id

    # Read from Store: get user's preferred model
    store = request.runtime.store
    user_prefs = store.get(("preferences",), user_id)

    if user_prefs:
        preferred_model = user_prefs.value.get("preferred_model")
        if preferred_model and preferred_model in MODEL_MAP:
            request = request.override(model=MODEL_MAP[preferred_model])

    return handler(request)

agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[store_based_model],
    context_schema=Context,
    store=InMemoryStore()
)
```

  **Runtime Context**:
    Select model based on cost limits or environment from Runtime Context:

```python
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from langchain.chat_models import init_chat_model
from typing import Callable

@dataclass
class Context:
    cost_tier: str
    environment: str

# Initialize models once outside the middleware
premium_model = init_chat_model("claude-sonnet-4-5-20250929")
standard_model = init_chat_model("gpt-4o")
budget_model = init_chat_model("gpt-4o-mini")

@wrap_model_call
def context_based_model(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """Select model based on Runtime Context."""
    # Read from Runtime Context: cost tier and environment
    cost_tier = request.runtime.context.cost_tier
    environment = request.runtime.context.environment

    if environment == "production" and cost_tier == "premium":
        # 生产环境高级用户获得最佳模型
        model = premium_model
    elif cost_tier == "budget":
        # 预算层级获得高效模型
        model = budget_model
    else:
        # 标准层级
        model = standard_model

    request = request.override(model=model)

    return handler(request)

agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[context_based_model],
    context_schema=Context
)
```

参见[动态模型](/oss/python/langchain/agents#dynamic-model)获取更多示例。

### 响应格式 (Response Format)

结构化输出将非结构化文本转换为经过验证的结构化数据。当提取特定字段或为下游系统返回数据时，自由格式文本是不够的。
**工作原理：** 当您提供模式作为响应格式时，模型的最终响应保证符合该模式。agent运行模型/工具调用循环直到模型完成调用工具，然后将最终响应强制转换为提供的格式。
#### 定义格式 (Defining formats)

模式定义指导模型。字段名称、类型和描述指定输出应该遵循的确切格式。

```python
from pydantic import BaseModel, Field

class CustomerSupportTicket(BaseModel):
"""从客户消息中提取的结构化票证信息。"""

category: str = Field(
    description="问题类别：'billing'、'technical'、'account'或'product'"
)
priority: str = Field(
    description="紧急程度：'low'、'medium'、'high'或'critical'"
)
summary: str = Field(
    description="客户问题的单句摘要"
)
customer_sentiment: str = Field(
    description="客户的情感语调：'frustrated'、'neutral'或'satisfied'"
)
```

#### 选择格式 (Selecting formats)

动态响应格式选择根据用户偏好、对话阶段或角色调整模式 - 早期返回简单格式，随着复杂性增加返回详细格式。

  **状态 (State)**:
    根据对话状态配置结构化输出：

```python
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from pydantic import BaseModel, Field
from typing import Callable

class SimpleResponse(BaseModel):
    """早期对话的简单响应。"""
    answer: str = Field(description="简要回答")

class DetailedResponse(BaseModel):
    """已建立对话的详细响应。"""
    answer: str = Field(description="详细回答")
    reasoning: str = Field(description="推理说明")
    confidence: float = Field(description="置信度分数 0-1")

@wrap_model_call
def state_based_output(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """根据状态选择输出格式。"""
    # request.messages 是 request.state["messages"] 的快捷方式
    message_count = len(request.messages)  # [!code highlight]

    if message_count < 3:
        # 早期对话 - 使用简单格式
        request = request.override(response_format=SimpleResponse)  # [!code highlight]
    else:
        # 已建立对话 - 使用详细格式
        request = request.override(response_format=DetailedResponse)  # [!code highlight]

    return handler(request)

agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[state_based_output]
)
```

  **存储 (Store)**:
    根据存储中的用户偏好配置输出格式：

```python
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from pydantic import BaseModel, Field
from typing import Callable
from langgraph.store.memory import InMemoryStore

@dataclass
class Context:
    user_id: str

class VerboseResponse(BaseModel):
    """带详细信息的详细响应。"""
    answer: str = Field(description="详细回答")
    sources: list[str] = Field(description="使用的来源")

class ConciseResponse(BaseModel):
    """简洁响应。"""
    answer: str = Field(description="简要回答")

@wrap_model_call
def store_based_output(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """根据存储偏好选择输出格式。"""
    user_id = request.runtime.context.user_id

    # 从存储读取：获取用户偏好的响应风格
    store = request.runtime.store
    user_prefs = store.get(("preferences",), user_id)

    if user_prefs:
        style = user_prefs.value.get("response_style", "concise")
        if style == "verbose":
            request = request.override(response_format=VerboseResponse)
        else:
            request = request.override(response_format=ConciseResponse)

    return handler(request)

agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[store_based_output],
    context_schema=Context,
    store=InMemoryStore()
)
```

  **运行时上下文 (Runtime Context)**:
    根据运行时上下文（如用户角色或环境）配置输出格式：

```python
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from pydantic import BaseModel, Field
from typing import Callable

@dataclass
class Context:
    user_role: str
    environment: str

class AdminResponse(BaseModel):
    """管理员用的带技术细节的响应。"""
    answer: str = Field(description="答案")
    debug_info: dict = Field(description="调试信息")
    system_status: str = Field(description="系统状态")

class UserResponse(BaseModel):
    """普通用户用的简单响应。"""
    answer: str = Field(description="答案")

@wrap_model_call
def context_based_output(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse]
) -> ModelResponse:
    """根据运行时上下文选择输出格式。"""
    # 从运行时上下文读取：用户角色和环境
    user_role = request.runtime.context.user_role
    environment = request.runtime.context.environment

    if user_role == "admin" and environment == "production":
        # 生产环境管理员获得详细输出
        request = request.override(response_format=AdminResponse)
    else:
        # 普通用户获得简单输出
        request = request.override(response_format=UserResponse)

    return handler(request)

agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[context_based_output],
    context_schema=Context
)
```

## 工具上下文 (Tool Context)

工具的特殊之处在于它们既读取又写入上下文。

在最基本的情况下，当工具执行时，它接收LLM的请求参数并返回一个工具消息。工具完成其工作并产生结果。

工具还可以为模型获取重要信息，使其能够执行和完成任务。

### 读取 (Reads)

大多数真实世界的工具需要的不仅仅是LLM的参数。它们需要用户ID进行数据库查询，API密钥访问外部服务，或当前会话状态来做决策。工具从状态、存储和运行时上下文读取以访问这些信息。

  **状态 (State)**:
    从状态读取以检查当前会话信息：

```python
from langchain.tools import tool, ToolRuntime
from langchain.agents import create_agent

@tool
def check_authentication(
    runtime: ToolRuntime
) -> str:
    """检查用户是否已通过身份验证。"""
    # 从状态读取：检查当前身份验证状态
    current_state = runtime.state
    is_authenticated = current_state.get("authenticated", False)

    if is_authenticated:
        return "User is authenticated"
    else:
        return "User is not authenticated"

agent = create_agent(
    model="gpt-4o",
    tools=[check_authentication]
)
```

  **存储 (Store)**:
    从存储读取以访问持久化的用户偏好：

```python
from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime
from langchain.agents import create_agent
from langgraph.store.memory import InMemoryStore

@dataclass
class Context:
    user_id: str

@tool
def get_preference(
    preference_key: str,
    runtime: ToolRuntime[Context]
) -> str:
    """从存储获取用户偏好。"""
    user_id = runtime.context.user_id

    # 从存储读取：获取现有偏好
    store = runtime.store
    existing_prefs = store.get(("preferences",), user_id)

    if existing_prefs:
        value = existing_prefs.value.get(preference_key)
        return f"{preference_key}: {value}" if value else f"No preference set for {preference_key}"
    else:
        return "No preferences found"

agent = create_agent(
    model="gpt-4o",
    tools=[get_preference],
    context_schema=Context,
from dataclasses import dataclass
from langchain.tools import tool, ToolRuntime
from langchain.agents import create_agent
from langgraph.store.memory import InMemoryStore

@dataclass
class Context:
    user_id: str

@tool
def save_preference(
    preference_key: str,
    preference_value: str,
    runtime: ToolRuntime[Context]
) -> str:
    """将用户偏好保存到存储。"""
    user_id = runtime.context.user_id

    # 读取现有偏好
    store = runtime.store
    existing_prefs = store.get(("preferences",), user_id)

    # 与新偏好合并
    prefs = existing_prefs.value if existing_prefs else {}
    prefs[preference_key] = preference_value

    # 写入存储：保存更新的偏好
    store.put(("preferences",), user_id, prefs)

    return f"Saved preference: {preference_key} = {preference_value}"

agent = create_agent(
    model="gpt-4o",
    tools=[save_preference],
    context_schema=Context,
    store=InMemoryStore()
)
```

参见[工具](/oss/python/langchain/tools)获取在工具中访问状态、存储和运行时上下文的全面示例。

## 生命周期上下文 (Life-cycle Context)

控制核心agent步骤**之间**发生的事情 - 拦截数据流以实现横切关注点，如摘要、防护机制和日志记录。

正如您在[模型上下文](#model-context)和[工具上下文](#tool-context)中看到的，[中间件](/oss/python/langchain/middleware)是使上下文工程变得实用的机制。中间件允许您挂钩到agent生命周期中的任何步骤，并且可以：

1. **更新上下文** - 修改状态和存储以持久化更改，更新对话历史，或保存洞察
2. **在生命周期中跳转** - 基于上下文移动到agent周期中的不同步骤（例如，如果满足条件则跳过工具执行，使用修改的上下文重复模型调用）

### 示例：摘要 (Example: Summarization)

最常见的生命周期模式之一是在对话历史变得过长时自动压缩它。与[模型上下文](#messages)中显示的瞬时消息修剪不同，摘要**持久化更新状态** - 永久地用摘要替换旧消息，该摘要为所有未来的轮次保存。

LangChain为此提供了内置中间件：

```python
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[
        SummarizationMiddleware(
            model="gpt-4o-mini",
            trigger={"tokens": 4000},
            keep={"messages": 20},
        ),
    ],
)
```

当对话超过令牌限制时，`SummarizationMiddleware`自动：

1. 使用单独的LLM调用摘要较旧的消息
2. 在状态中用摘要消息替换它们（永久地）
3. 保持最近的消息完整以提供上下文

摘要化的对话历史被永久更新 - 未来的轮次将看到摘要而不是原始消息。

有关内置中间件的完整列表、可用挂钩以及如何创建自定义中间件，请参阅[中间件文档](/oss/python/langchain/middleware)。

## 最佳实践 (Best practices)

1. **从简单开始** - 从静态提示词和工具开始，仅在需要时添加动态功能
2. **增量测试** - 一次添加一个上下文工程功能
3. **监控性能** - 跟踪模型调用、令牌使用和延迟
4. **使用内置中间件** - 利用[`SummarizationMiddleware`](/oss/python/langchain/middleware#summarization)、[`LLMToolSelectorMiddleware`](/oss/python/langchain/middleware#llm-tool-selector)等
5. **记录您的上下文策略** - 明确说明传递了什么上下文以及为什么
6. **理解瞬时与持久化**：模型上下文更改是瞬时的（每次调用），而生命周期上下文更改持久化到状态

## 相关资源 (Related resources)

* [Context conceptual overview](/oss/python/concepts/context) - Understand context types and when to use them
* [Middleware](/oss/python/langchain/middleware) - Complete middleware guide
* [Tools](/oss/python/langchain/tools) - Tool creation and context access
* [Memory](/oss/python/concepts/memory) - Short-term and long-term memory patterns
* [Agents](/oss/python/langchain/agents) - Core agent concepts

***

  [Edit the source of this page on GitHub.](https://github.com/langchain-ai/docs/edit/main/src/oss/langchain/context-engineering.mdx)

  [Connect these docs programmatically](/use-these-docs) to Claude, VSCode, and more via MCP for real-time answers.


---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.langchain.com/llms.txt