# 结构化输出 (Structured output)

LangChain 的 [`create_agent`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.create_agent) 自动处理结构化输出，在代理状态的 `'structured_response'` 键中返回验证后的数据。

## 核心功能
- **自动验证**：确保输出符合指定模式
- **多策略支持**：ProviderStrategy、ToolStrategy 和自动选择
- **错误处理**：智能重试机制
- **多种模式**：支持 Pydantic、Dataclass、TypedDict 和 JSON Schema

```python  theme={null}
def create_agent(
    ...
    response_format: Union[
        ToolStrategy[StructuredResponseT],
        ProviderStrategy[StructuredResponseT],
        type[StructuredResponseT],
    ]
```

## 响应格式 (Response Format)

* **`ToolStrategy[StructuredResponseT]`**：使用工具调用
* **`ProviderStrategy[StructuredResponseT]`**：使用提供商原生结构化输出
* **`type[StructuredResponseT]`**：自动选择最佳策略
* **`None`**：无结构化输出

## 提供商策略 (Provider Strategy)

某些模型提供商通过其 API 原生支持结构化输出（如 OpenAI、Grok、Gemini）。这是最可靠的方法。

### 使用方法
```python
class ProviderStrategy(Generic[SchemaT]):
    schema: type[SchemaT]
```

### 支持的模式类型
- **Pydantic 模型**：带有字段验证的 `BaseModel` 子类
- **Dataclasses**：带有类型注解的 Python 数据类
- **TypedDict**：类型化字典类
- **JSON Schema**：符合 JSON 模式规范的字典

### 自动选择策略
当直接传递模式类型给 [`create_agent.response_format`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.create_agent(response_format)) 且模型支持原生结构化输出时，LangChain 自动使用 `ProviderStrategy`。

### Pydantic 模型

```py
from pydantic import BaseModel, Field
from langchain.agents import create_agent

class ContactInfo(BaseModel):
    """人员联系信息。"""
    name: str = Field(description="人员姓名")
    email: str = Field(description="电子邮件地址")
    phone: str = Field(description="电话号码")

agent = create_agent(
    model="gpt-5",
    response_format=ContactInfo  
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "从以下信息提取联系人信息：John Doe, john@example.com, (555) 123-4567"}]
})

print(result["structured_response"])
# ContactInfo(name='John Doe', email='john@example.com', phone='(555) 123-4567')
```

### Dataclasses

```py
from dataclasses import dataclass
from langchain.agents import create_agent

@dataclass
class ContactInfo:
    """联系人信息。"""
    name: str  # 联系人姓名
    email: str  # 联系人电子邮件地址
    phone: str  # 联系人电话号码

agent = create_agent(
    model="gpt-5",
    response_format=ContactInfo  # Auto-selects ProviderStrategy
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "从以下信息提取联系人信息：John Doe, john@example.com, (555) 123-4567"}]
})

result["structured_response"]
# ContactInfo(name='John Doe', email='john@example.com', phone='(555) 123-4567')
```

### TypedDict

```py
from typing_extensions import TypedDict
from langchain.agents import create_agent

class ContactInfo(TypedDict):
    """联系人信息。"""
    name: str  # 联系人姓名
    email: str  # 联系人电子邮件地址
    phone: str  # 联系人电话号码

agent = create_agent(
    model="gpt-5",
    response_format=ContactInfo
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "从以下信息提取联系人信息：John Doe, john@example.com, (555) 123-4567"}]
})

result["structured_response"]
# {'name': 'John Doe', 'email': 'john@example.com', 'phone': '(555) 123-4567'}
```

### JSON Schema

```py
from langchain.agents import create_agent

contact_info_schema = {
    "type": "object",
    "description": "人员联系信息。",
    "properties": {
        "name": {"type": "string", "description": "人员姓名"},
        "email": {"type": "string", "description": "电子邮件地址"},
        "phone": {"type": "string", "description": "电话号码"}
    },
    "required": ["name", "email", "phone"]
}

agent = create_agent(
    model="gpt-5",
    response_format=ProviderStrategy(contact_info_schema)
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "从以下信息提取联系人信息：John Doe, john@example.com, (555) 123-4567"}]
})

result["structured_response"]
# {'name': 'John Doe', 'email': 'john@example.com', 'phone': '(555) 123-4567'}
```

提供商原生结构化输出提供高可靠性和严格验证，因为模型提供商强制执行模式。在可用时使用它。

如果提供商原生支持您的模型选择的结构化输出，那么写 `response_format=ProductReview` 与写 `response_format=ProviderStrategy(ProductReview)` 在功能上是等效的。无论哪种情况，如果不支持结构化输出，代理将回退到工具调用策略。

## 工具调用策略 (Tool calling strategy)

对于不支持原生结构化输出的模型，LangChain 使用工具调用来实现相同的结果。

要使用此策略，请配置 `ToolStrategy`：

```python  theme={null}
class ToolStrategy(Generic[SchemaT]):
    schema: type[SchemaT]
    tool_message_content: str | None
    handle_errors: Union[
        bool,
        str,
        type[Exception],
        tuple[type[Exception], ...],
        Callable[[Exception], str],
    ]
```

  定义结构化输出格式的模式。支持：

  * **Pydantic 模型**：具有字段验证的 `BaseModel` 子类
  * **Dataclasses**：带有类型注解的 Python 数据类
  * **TypedDict**：类型化字典类
  * **JSON Schema**：具有 JSON 模式规范的字典
  * **Union types**：多个模式选项。模型将根据上下文选择最合适的模式。

    生成结构化输出时返回的工具消息的自定义内容。
    如果未提供，默认为显示结构化响应数据的消息。
    结构化输出验证失败的错误处理策略。默认为 `True`。

  * **`True`**：使用默认错误模板捕获所有错误
  * **`str`**：使用此自定义消息捕获所有错误
  * **`type[Exception]`**：仅使用默认消息捕获此异常类型
  * **`tuple[type[Exception], ...]`**：仅使用默认消息捕获这些异常类型
  * **`Callable[[Exception], str]`**：返回错误消息的自定义函数
  * **`False`**：不重试，让异常传播

#### Pydantic 

  ```python Pydantic Model theme={null}
from pydantic import BaseModel, Field
from typing import Literal
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

class ProductReview(BaseModel):
  """产品评论分析。"""
  rating: int | None = Field(description="产品评分", ge=1, le=5)
  sentiment: Literal["positive", "negative"] = Field(description="评论情感")
  key_points: list[str] = Field(description="评论要点")

agent = create_agent(
  model="gpt-5",
  tools=tools,
  response_format=ToolStrategy(ProductReview)
)

result = agent.invoke({
  "messages": [{"role": "user", "content": "分析评论：'产品很棒：5星。快递很快，但价格有点贵'"}]
})
result["structured_response"]
  # ProductReview(rating=5, sentiment='positive', key_points=['快递很快', '价格有点贵'])
  ```

#### Dataclasses

  ```python Union Types theme={null}
from dataclasses import dataclass
from typing import Literal
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy


@dataclass
class ProductReview:
    "产品评论分析。"
    rating: int | None  # 产品评分（1-5）
    sentiment: Literal["positive", "negative"]  # 评论情感倾向
    key_points: list[str]  # 评论要点

agent = create_agent(
    model="gpt-5",
    tools=tools,
    response_format=ToolStrategy(ProductReview)
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "分析这个评论：'很棒的产品：5星满分。快递很快，但价格有点贵'"}]
})
result["structured_response"]
# ProductReview(rating=5, sentiment='positive', key_points=['fast shipping', 'expensive'])
  ```
#### TypedDict

```py
from typing import Literal
from typing_extensions import TypedDict
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

class ProductReview(TypedDict):
    "产品评论分析。"
    rating: int | None  # 产品评分（1-5）
    sentiment: Literal["positive", "negative"]  # 评论情感倾向
    key_points: list[str]  # 评论要点

agent = create_agent(
    model="gpt-5",
    tools=tools,
    response_format=ToolStrategy(ProductReview)
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "分析这个评论：'很棒的产品：5星满分。快递很快，但价格有点贵'"}]
})
result["structured_response"]
# {'rating': 5, 'sentiment': 'positive', 'key_points': ['fast shipping', 'expensive']}
```

#### JSON Schema

```py
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

product_review_schema = {
    "type": "object",
    "description": "产品评论分析。",
    "properties": {
        "rating": {
            "type": ["integer", "null"],
            "description": "产品评分（1-5）",
            "minimum": 1,
            "maximum": 5
        },
        "sentiment": {
            "type": "string",
            "enum": ["positive", "negative"],
            "description": "评论情感倾向"
        },
        "key_points": {
            "type": "array",
            "items": {"type": "string"},
            "description": "评论要点"
        }
    },
    "required": ["sentiment", "key_points"]
}

agent = create_agent(
    model="gpt-5",
    tools=tools,
    response_format=ToolStrategy(product_review_schema)
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "分析这个评论：'很棒的产品：5星满分。快递很快，但价格有点贵'"}]
})
result["structured_response"]
# {'rating': 5, 'sentiment': 'positive', 'key_points': ['fast shipping', 'expensive']}
```

#### Union types

```py
from pydantic import BaseModel, Field
from typing import Literal, Union
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

class ProductReview(BaseModel):
    "产品评论分析。"
    rating: int | None = Field(description="产品评分", ge=1, le=5)
    sentiment: Literal["positive", "negative"] = Field(description="评论情感倾向")
    key_points: list[str] = Field(description="评论要点。小写，每个1-3个词。")

class CustomerComplaint(BaseModel):
    """关于产品或服务的客户投诉。"""
    issue_type: Literal["product", "service", "shipping", "billing"] = Field(description="问题类型")
    severity: Literal["low", "medium", "high"] = Field(description="投诉严重程度")
    description: str = Field(description="投诉简要描述")

agent = create_agent(
    model="gpt-5",
    tools=tools,
    response_format=ToolStrategy(Union[ProductReview, CustomerComplaint])
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "分析这个评论：'很棒的产品：5星满分。快递很快，但价格有点贵'"}]
})
result["structured_response"]
# ProductReview(rating=5, sentiment='positive', key_points=['fast shipping', 'expensive'])
```

### 自定义工具消息内容 (Custom tool message content)

`tool_message_content` 参数允许您自定义生成结构化输出时出现在对话历史中的消息：

```python  theme={null}
from pydantic import BaseModel, Field
from typing import Literal
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy

class MeetingAction(BaseModel):
    """从会议记录中提取的行动项目。"""
    task: str = Field(description="要完成的具体任务")
    assignee: str = Field(description="负责任务的人员")
    priority: Literal["low", "medium", "high"] = Field(description="优先级")

agent = create_agent(
    model="gpt-5",
    tools=[],
    response_format=ToolStrategy(
        schema=MeetingAction,
        tool_message_content="行动项目已捕获并添加到会议记录中！"
    )
)

agent.invoke({
    "messages": [{"role": "user", "content": "从我们的会议中：Sarah 需要尽快更新项目时间表"}]
})
```

```
================================ Human Message =================================

从我们的会议中：Sarah 需要尽快更新项目时间表
================================== Ai Message ==================================
Tool Calls:
  MeetingAction (call_1)
 Call ID: call_1
  Args:
    task: 更新项目时间表
    assignee: Sarah
    priority: high
================================= Tool Message =================================
Name: MeetingAction

行动项目已捕获并添加到会议记录中！
```

没有 `tool_message_content`，我们最终的 [`ToolMessage`](https://reference.langchain.com/python/langchain/messages/#langchain.messages.ToolMessage) 将是：

```
================================= Tool Message =================================
Name: MeetingAction
返回结构化响应：{'task': 'update the project timeline', 'assignee': 'Sarah', 'priority': 'high'}
```

### 错误处理 (Error handling)

模型通过工具调用生成结构化输出时可能出错。LangChain 提供智能重试机制来自动处理这些错误。
#### 多个结构化输出错误

当模型错误调用多个结构化输出工具时，代理在 [`ToolMessage`](https://reference.langchain.com/python/langchain/messages/#langchain.messages.ToolMessage) 中提供错误反馈并提示模型重试：

```python
from pydantic import BaseModel, Field
from typing import Union
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy


class ContactInfo(BaseModel):
    """联系人信息"""
    name: str = Field(description="人员姓名")
    email: str = Field(description="电子邮件地址")

class EventDetails(BaseModel):
    """活动详情"""
    event_name: str = Field(description="活动名称")
    date: str = Field(description="活动日期")

agent = create_agent(
    model="gpt-5",
    tools=[],
    response_format=ToolStrategy(Union[ContactInfo, EventDetails])  # 默认：handle_errors=True
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "提取信息：John Doe (john@email.com) 正在组织 3 月 15 日的技术会议"}]
})

```
```
================================ Human Message =================================

提取信息：John Doe (john@email.com) 正在组织 3 月 15 日的技术会议
================================== Ai Message ==================================
Tool Calls:
  ContactInfo (call_1)
 Call ID: call_1
  Args:
    name: John Doe
    email: john@email.com
  EventDetails (call_2)
 Call ID: call_2
  Args:
    event_name: 技术会议
    date: 3月15日
================================= Tool Message =================================
Name: ContactInfo

错误：模型错误地返回了多个结构化响应（ContactInfo, EventDetails），但期望只有一个。
 请修正您的错误。
================================= Tool Message =================================
Name: EventDetails

错误：模型错误地返回了多个结构化响应（ContactInfo, EventDetails），但期望只有一个。
 请修正您的错误。
================================== Ai Message ==================================
Tool Calls:
  ContactInfo (call_3)
 Call ID: call_3
  Args:
    name: John Doe
    email: john@email.com
================================= Tool Message =================================
Name: ContactInfo

返回结构化响应：{'name': 'John Doe', 'email': 'john@email.com'}

================================ Human Message =================================

解析这个：'Amazing product, 10/10!'
================================== Ai Message ==================================
Tool Calls:
  ProductRating (call_1)
 Call ID: call_1
  Args:
    rating: 10
    comment: Amazing product
================================= Tool Message =================================
Name: ProductRating

错误：无法解析工具 'ProductRating' 的结构化输出：ProductRating.rating 的 1 个验证错误
  输入应小于或等于 5 [type=less_than_equal, input_value=10, input_type=int]。
 请修正您的错误。
================================== Ai Message ==================================
Tool Calls:
  ProductRating (call_2)
 Call ID: call_2
  Args:
    rating: 5
    comment: Amazing product
================================= Tool Message =================================
Name: ProductRating

返回结构化响应：{'rating': 5, 'comment': 'Amazing product'}
**自定义错误消息：**

```
```
ToolStrategy(
    schema=ProductRating,
    handle_errors="请提供有效的评分（1-5）和评论。"
)
```

如果 `handle_errors` 是字符串，代理将*始终*使用固定的工具消息提示模型重试：

```
================================= Tool Message =================================
Name: ProductRating

请提供有效的评分（1-5）和评论。
```

**仅处理特定异常：**

```py
ToolStrategy(
    schema=ProductRating,
    handle_errors=ValueError  # 仅在 ValueError 时重试，其他异常直接抛出
)
```

如果 `handle_errors` 是异常类型，仅当抛出的异常是指定类型时，代理才会重试（使用默认错误消息）。在所有其他情况下，异常将被抛出。

**处理多个异常类型：**

```py
ToolStrategy(
    schema=ProductRating,
    handle_errors=(ValueError, TypeError)  # 在 ValueError 和 TypeError 时重试
)
```

如果 `handle_errors` 是异常元组，仅当抛出的异常是指定类型之一时，代理才会重试（使用默认错误消息）。在所有其他情况下，异常将被抛出。

**自定义错误处理函数：**
```python
def custom_error_handler(error: Exception) -> str:
    if isinstance(error, StructuredOutputValidationError):
        return "格式有问题，请重试。"
    elif isinstance(error, MultipleStructuredOutputsError):
        return "返回了多个结构化输出，请选择最相关的一个。"
    else:
        return f"错误: {str(error)}"

agent = create_agent(
    model="gpt-5",
    tools=[],
    response_format=ToolStrategy(
                        schema=Union[ContactInfo, EventDetails],
                        handle_errors=custom_error_handler
                    )  # 默认：handle_errors=True
)

result = agent.invoke({
    "messages": [{"role": "user", "content": "提取信息：John Doe (john@email.com) 正在组织 3 月 15 日的技术会议"}]
})

for msg in result['messages']:
    # 如果消息实际上是 ToolMessage 对象（不是字典），检查其类名
    if type(msg).__name__ == "ToolMessage":
        print(msg.content)
    # 如果消息是字典或者您需要备用方案
    elif isinstance(msg, dict) and msg.get('tool_call_id'):
        print(msg['content'])
```

在 `StructuredOutputValidationError` 时：

```
================================= Tool Message =================================
Name: ToolStrategy

格式有问题，请重试。
```

在 `MultipleStructuredOutputsError` 时：

```
================================= Tool Message =================================
Name: ToolStrategy

返回了多个结构化输出，请选择最相关的一个。
```

在其他错误时：

```
================================= Tool Message =================================
Name: ToolStrategy

错误：<错误消息>
```

**不进行错误处理：**

```py
response_format = ToolStrategy(
    schema=ProductRating,
    handle_errors=False  # 所有错误都被抛出
)