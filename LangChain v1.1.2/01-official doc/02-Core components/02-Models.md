# 🤖 模型 (Models)




#### 📋 **核心能力**

- **文本生成** 
- **工具调用** - 外部工具集成（数据库、API）
- **结构化输出** - 响应格式约束
- **多模态** - 图像、音频、视频处理
- **推理** - 多步逻辑推理

#### 🧠 **代理引擎**

- 驱动决策过程
- 决定工具选择、结果解释、答案输出时机

#### 📊 **性能关键**

- 模型质量 = 代理可靠性
- 不同专长：复杂指令、结构化推理、大上下文

#### 🔧 **技术优势**

- 统一接口
- 多提供商支持
- 灵活切换试验



## 初始化模型

**支持的提供商：**

- OpenAI
- Anthropic
- Azure
- Google Gemini
- AWS Bedrock

OpenAI举例，需要安装对应的大模型提供商的包

```bash
pip install -U "langchain[openai]"
```

```python
import os
from langchain.chat_models import init_chat_model

os.environ["OPENAI_API_KEY"] = "sk-..."

model = init_chat_model("gpt-4.1")
response = model.invoke("Why do parrots talk?")
```

## 关键方法

- **Invoke (调用)** - 模型接收消息作为输入，在生成完整响应后输出消息。
- **Stream (流式传输)** - 调用模型，但在生成时实时流式传输输出。
- **Batch (批处理)** - 以批处理方式向模型发送多个请求以实现更高效的处理。

## 参数

- **标准参数**

- **模型供应商特有参数**

  ChatOpenAI` 有 `use_responses_api` 来指定是使用 OpenAI Responses 还是 Completions API。

#### 标准参数

| 参数 | 类型 | 说明 |
|------|------|------|
| **model** | `string` (必需) | 模型名称或标识符，支持 `provider:model` 格式（如 `openai:o1`） |
| **api_key** | `string` | 提供商身份验证密钥，通常通过环境变量设置 |
| **temperature** | `number` | 控制输出随机性：高值更创造性，低值更确定性 |
| **max_tokens** | `number` | 限制响应长度（token 数量） |
| **timeout** | `number` | 请求超时时间（秒） |
| **max_retries** | `number` | 失败重试次数 |

```python
# 使用模型参数初始化
model = init_chat_model(
    "claude-sonnet-4-5-20250929",
    # 传递给模型的 kwargs：
    temperature=0.7,
    timeout=30,
    max_tokens=1000,
)
```

## **Invocation **调用

### Invoke (调用)

调用模型最直接的方法是使用 `invoke()` 传入单个消息或消息列表。

**单个消息：**

```python
response = model.invoke("Why do parrots have colorful feathers?")
print(response)
```

**字典格式：**
```python
conversation = [
    {"role": "system", "content": "您是一个有用的助手，负责将英语翻译成法语。"},
    {"role": "user", "content": "翻译：我喜欢编程。"},
    {"role": "assistant", "content": "J'adore la programmation."},
    {"role": "user", "content": "翻译：我喜欢构建应用程序。"}
]

response = model.invoke(conversation)
print(response)  # AIMessage("J'adore créer des applications.")
```

**消息对象（Chat模型才能使用）**

```python
from langchain.messages import HumanMessage, AIMessage, SystemMessage

conversation = [
    SystemMessage("您是一个有用的助手，负责将英语翻译成法语。"),
    HumanMessage("翻译：我喜欢编程。"),
    AIMessage("J'adore la programmation."),
    HumanMessage("翻译：我喜欢构建应用程序。")
]

response = model.invoke(conversation)
print(response)  # AIMessage("J'adore créer des applications.")
```

### Stream (流式传输)

大多数模型可以在生成输出时流式传输其输出内容。通过渐进式显示输出，流式传输显著改善了用户体验，特别是对于较长的响应。

调用 `stream()` 返回一个迭代器，在输出块产生时生成它们。您可以使用循环实时处理每个块：

**基本文本流式传输：**
```python
for chunk in model.stream("为什么鹦鹉有彩色的羽毛？"):
    print(chunk.text, end="|", flush=True)
```

```py
# 流式传输工具调用、推理和其他内容

for chunk in model.stream("天空是什么颜色？"):
    for block in chunk.content_blocks:
        if block["type"] == "reasoning" and (reasoning := block.get("reasoning")):
            print(f"推理: {reasoning}")
        elif block["type"] == "tool_call_chunk":
            print(f"工具调用块: {block}")
        elif block["type"] == "text":
            print(block["text"])
        else:
            ...
```

**构建 AIMessage：**

```python
full = None  # None | AIMessageChunk
for chunk in model.stream("天空是什么颜色？"):
    full = chunk if full is None else full + chunk
    print(full.text)

# 天空
# 天空是
# 天空通常是
# 天空通常是蓝色
# 天空通常是蓝色的
# ...

print(full.content_blocks)
# [{"type": "text", "text": "天空通常是蓝色的..."}]
```

#### Streaming events 流式事件

```py
async for event in model.astream_events("Hello"):

    if event["event"] == "on_chat_model_start":
        print(f"Input: {event['data']['input']}")

    elif event["event"] == "on_chat_model_stream":
        print(f"Token: {event['data']['chunk'].text}")

    elif event["event"] == "on_chat_model_end":
        print(f"Full message: {event['data']['output'].text}")

    else:
        pass


# Input: Hello
# Token: Hi
# Token:  there
# Token: !
# Token:  How
# Token:  can
# Token:  I
# ...
# Full message: Hi there! How can I help today?
```

### Batch (批处理)

**核心优势：**

- 批处理独立请求 → **提升性能，降低成本**
- 支持并行处理

**方法对比：**

- `batch()` - 客户端并行化调用，返回最终结果
- `batch_as_completed()` - 流式传输，实时接收各输入输出

**重要区别：**

- 这是客户端并行化，非提供商批处理 API
- 与 OpenAI/Anthropic 的批处理 API 不同

**结果顺序：**

- `batch_as_completed()` - **无序到达**
- 每个结果包含输入索引，支持重构原始顺序

**并发控制：**

- 大量输入时控制并行调用数量
- 通过 `RunnableConfig` 设置 `max_concurrency` 属性
- 适用于 `batch()` 和 `batch_as_completed()`



```python
responses = model.batch([
    "为什么鹦鹉有彩色的羽毛？",
    "飞机是如何飞行的？",
    "什么是量子计算？"
])
for response in responses:
    print(response)


# 独立输出结果
for response in model.batch_as_completed([
    "Why do parrots have colorful feathers?",
    "How do airplanes fly?",
    "What is quantum computing?"
]):
    print(response)
```

**带最大并发数的批处理：**
```python
model.batch(
    list_of_inputs,
    config={
        'max_concurrency': 5,  # 限制为 5 个并行调用
    }
)
```


## 工具调用

模型可以请求调用执行任务的工具，例如从数据库获取数据、搜索网页或运行代码。工具是以下内容的配对：
- 一个模式，包括工具的名称、描述和/或参数定义（通常是 JSON 模式）
- 要执行的函数或协程。

您可能听说过术语“函数调用”。我们将其与“工具调用”互换使用。



### 工具调用流程

![image-20251206152913546](C:\Users\Administrator\AppData\Roaming\Typora\typora-user-images\image-20251206152913546.png)

### **绑定用户工具**

```python
from langchain.tools import tool

@tool
def get_weather(location: str) -> str:
    """获取位置的天气。"""
    return f"{location} 天气晴朗。"

model_with_tools = model.bind_tools([get_weather])  

response = model_with_tools.invoke("波士顿的天气怎么样？")
for tool_call in response.tool_calls:
    # 查看模型进行的工具调用
    print(f"工具: {tool_call['name']}")
    print(f"参数: {tool_call['args']}")
```



### Tool execution loop 工具执行循环

```py
from langchain.tools import tool

@tool
def get_weather(location: str) -> str:
    """获取位置的天气信息。"""
    return f"{location} 天气晴朗。"

# 绑定（可能是多个）工具到模型
model_with_tools = model.bind_tools([get_weather])

# 步骤 1：模型生成工具调用
messages = [{"role": "user", "content": "波士顿的天气怎么样？"}]
ai_msg = model_with_tools.invoke(messages)
messages.append(ai_msg)

# 步骤 2：执行工具并收集结果
for tool_call in ai_msg.tool_calls:
    # 使用生成的参数执行工具
    tool_result = get_weather.invoke(tool_call)
    messages.append(tool_result)

# 步骤 3：将结果传回模型获取最终响应
final_response = model_with_tools.invoke(messages)
print(final_response.text)
# "波士顿当前天气 72°F，晴朗。"
```



### Forcing tool calls 强制工具调用

```py
# 强制使用所有工具
model_with_tools = model.bind_tools([tool_1], tool_choice="any")

# 强制使用指定工具
model_with_tools = model.bind_tools([tool_1], tool_choice="tool_1")
```

### 并行工具调用

- **默认启用**：多数支持工具调用的模型默认启用并行工具调用

- **选择性禁用**：部分模型允许禁用并行功能（包括OpenAI和Anthropic）

- **设置方法**：通过设置 `parallel_tool_calls=False` 禁用并行工具调用

```py
model_with_tools = model.bind_tools([get_weather])

response = model_with_tools.invoke(
    "波士顿和东京的天气怎么样？"
)

# 模型可能生成多个工具调用
print(response.tool_calls)
# [
#   {'name': 'get_weather', 'args': {'location': 'Boston'}, 'id': 'call_1'},
#   {'name': 'get_weather', 'args': {'location': 'Tokyo'}, 'id': 'call_2'},
# ]

# 执行所有工具（可以使用异步并行执行）
results = []
for tool_call in response.tool_calls:
    if tool_call['name'] == 'get_weather':
        result = get_weather.invoke(tool_call)
    ...
    results.append(result)
```



### Streaming tool calls 流式工具调用

```py
for chunk in model_with_tools.stream(
    "波士顿和东京的天气怎么样？"
):
    # 工具调用块逐步到达
    for tool_chunk in chunk.tool_call_chunks:
        if name := tool_chunk.get("name"):
            print(f"工具: {name}")
        if id_ := tool_chunk.get("id"):
            print(f"ID: {id_}")
        if args := tool_chunk.get("args"):
            print(f"参数: {args}")

# 输出:
# 工具: get_weather
# ID: call_SvMlU1TVIZugrFLckFE2ceRE
# 参数: {"lo
# 参数: catio
# 参数: n": "B
# 参数: osto
# 参数: n"}
# 工具: get_weather
# ID: call_QMZdy6qInx13oWKE7KhuhOLR
# 参数: {"lo
# 参数: catio
# 参数: n": "T
# 参数: okyo
# 参数: "}
```



## Structured output 结构化输出

### Pydantic 

```python
from pydantic import BaseModel, Field

class Movie(BaseModel):
    """带有详细信息的电影。"""
    title: str = Field(..., description="电影的标题")
    year: int = Field(..., description="电影发布的年份")
    director: str = Field(..., description="电影的导演")
    rating: float = Field(..., description="电影评分（满分10分）")

model_with_structure = model.with_structured_output(Movie)
response = model_with_structure.invoke("提供电影《盗梦空间》的详细信息")
print(response)  # Movie(title="盗梦空间", year=2010, director="Christopher Nolan", rating=8.8)
```

#### 方法参数

| 方法                 | 特点                              |
| :------------------- | :-------------------------------- |
| **json_schema**      | 专用结构化输出功能                |
| **function_calling** | 通过工具调用实现结构化输出        |
| **json_mode**        | 早期版本，JSON 模式需在提示中描述 |

### TypedDict

- Python 内置类型

- 适合无需运行时验证的场景

```py
from typing_extensions import TypedDict, Annotated

class MovieDict(TypedDict):
    """包含详细信息的电影。"""
    title: Annotated[str, ..., "电影标题"]
    year: Annotated[int, ..., "电影上映年份"]
    director: Annotated[str, ..., "电影导演"]
    rating: Annotated[float, ..., "电影评分（满分10分）"]

model_with_structure = model.with_structured_output(MovieDict)
response = model_with_structure.invoke("提供电影《盗梦空间》的详细信息")
print(response)  # {'title': 'Inception', 'year': 2010, 'director': 'Christopher Nolan', 'rating': 8.8}
```

### JSON Schema

为了获得最大的控制或互操作性，您可以提供原始JSON模式。

```py
import json

json_schema = {
    "title": "Movie",
    "description": "包含详细信息的电影",
    "type": "object",
    "properties": {
        "title": {
            "type": "string",
            "description": "电影标题"
        },
        "year": {
            "type": "integer",
            "description": "电影上映年份"
        },
        "director": {
            "type": "string",
            "description": "电影导演"
        },
        "rating": {
            "type": "number",
            "description": "电影评分（满分10分）"
        }
    },
    "required": ["title", "year", "director", "rating"]
}

model_with_structure = model.with_structured_output(
    json_schema,
    method="json_schema",
)
response = model_with_structure.invoke("提供电影《盗梦空间》的详细信息")
print(response)  # {'title': 'Inception', 'year': 2010, ...}
```
