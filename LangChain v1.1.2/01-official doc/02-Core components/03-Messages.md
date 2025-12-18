# Messages

消息是LangChain中模型的基本上下文单元。它们表示模型的输入和输出，携带在与LLM交互时表示对话状态所需的内容和元数据。

- Role 角色 - 标识消息类型（例如system，user）
- Content - 表示消息的实际内容（如文本、图像、音频、文档等）
- 元数据-可选字段，例如响应信息、消息ID和令牌使用情况



## Basic usage 基本用法

```python
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, AIMessage, SystemMessage

model = init_chat_model("gpt-5-nano")

system_msg = SystemMessage("您是一个有用的助手。")
human_msg = HumanMessage("您好，您好吗？")

# 与聊天模型一起使用
messages = [system_msg, human_msg]
response = model.invoke(messages)  # 返回 AIMessage
```

### Text prompts

- 您有一个单独的请求
- 你不需要对话记录
- 您想要最小的代码复杂性

```python  theme={null}
response = model.invoke("Write a haiku about spring")
```



### Message prompts

* 管理多轮对话
* 处理多模态内容（图像、音频、文件）
* 包含系统指令

```python  theme={null}
from langchain.messages import SystemMessage, HumanMessage, AIMessage

messages = [
    SystemMessage("您是一位诗歌专家"),
    HumanMessage("写一首关于春天的俳句"),
    AIMessage("樱花盛开...")
]
response = model.invoke(messages)
```

### Dictionary format

您也可以直接以 OpenAI 聊天完成格式指定消息。

```python  theme={null}
messages = [
    {"role": "system", "content": "您是一位诗歌专家"},
    {"role": "user", "content": "写一首关于春天的俳句"},
    {"role": "assistant", "content": "樱花盛开..."}
]
response = model.invoke(messages)
```

## Message types

###  System message

告诉模型如何表现并为交互提供上下文

```python
system_msg = SystemMessage("您是一个有用的编程助手。")

messages = [
    system_msg,
    HumanMessage("我如何创建一个 REST API？")
]
response = model.invoke(messages)
```

```python
from langchain.messages import SystemMessage, HumanMessage

system_msg = SystemMessage("""
您是一位具有 Web 框架专业知识的资深 Python 开发者。
始终提供代码示例并解释您的推理过程。
在解释中要简洁但全面。
""")

messages = [
    system_msg,
    HumanMessage("我如何创建一个 REST API？")
]
response = model.invoke(messages)
```

***

### Human Message

代表用户输入和交互。包含文本、图像、音频、文件以及任何其他数量的多模态内容

  ```python
  # 使用字符串是单个 HumanMessage 的快捷方式
  response = model.invoke("什么是机器学习？")
  
  # 使用 HumanMessage
  response = model.invoke([
    HumanMessage("什么是机器学习？")
  ])
  ```

```python
human_msg = HumanMessage(
    content="你好！",
    name="alice",  # 可选：标识不同用户，name字段行为因提供者而异-有些将其用于用户标识，有些则忽略它。要检查，请参阅模型提供者的参考。
    id="msg_123",  # 可选：用于跟踪的唯一标识符
)
```

***

### AI Message

代表模型调用的输出

包括多模态数据、工具调用和提供商特定的元数据，供后续访问。

```python  theme={null}
response = model.invoke("解释 AI")
print(type(response))  # <class 'langchain.messages.AIMessage'>
```

提供商对消息类型的权衡/上下文化不同，这意味着有时手动创建一个新的 [`AIMessage`](https://reference.langchain.com/python/langchain/messages/#langchain.messages.AIMessage) 对象并将其插入到消息历史中会很有帮助，就好像它来自模型一样。

```python  theme={null}
from langchain.messages import AIMessage, SystemMessage, HumanMessage

# 手动创建 AI 消息（例如，用于对话历史）
ai_msg = AIMessage("我很乐意帮助您解决那个问题！")

# 添加到对话历史
messages = [
    SystemMessage("您是一个有用的助手"),
    HumanMessage("您能帮助我吗？"),
    ai_msg,  # 插入，就好像它来自模型
    HumanMessage("太好了！2+2 是多少？")
]

response = model.invoke(messages)
```

#### 工具调用

当模型进行 [工具调用](/oss/python/langchain/models#工具调用) 时，它们会包含在 [`AIMessage`](https://reference.langchain.com/python/langchain/messages/#langchain.messages.AIMessage) 中：

```python  theme={null}
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-5-nano")

def get_weather(location: str) -> str:
    """获取某个位置的天气。"""
    ...

model_with_tools = model.bind_tools([get_weather])
response = model_with_tools.invoke("巴黎的天气怎么样？")

for tool_call in response.tool_calls:
    print(f"工具: {tool_call['name']}")
    print(f"参数: {tool_call['args']}")
    print(f"ID: {tool_call['id']}")
```

#### 令牌使用

```python  theme={null}
from langchain.chat_models import init_chat_model

model = init_chat_model("gpt-5-nano")

response = model.invoke("Hello!")
response.usage_metadata
```

```
# AIMessage可以在其usage_metadata字段中保存令牌计数和其他使用元数据：
# {'input_tokens': 8,
#  'output_tokens': 304,
#  'total_tokens': 312,
#  'input_token_details': {'audio': 0, 'cache_read': 0},
#  'output_token_details': {'audio': 0, 'reasoning': 256}}
```

#### Streaming and chunks

```python  theme={null}
# 在流式传输期间，您将收到可以组合成完整消息对象的AIMessageChunk对象：
chunks = []
full_message = None
for chunk in model.stream("Hi"):
    chunks.append(chunk)
    print(chunk.text)
    full_message = chunk if full_message is None else full_message + chunk
```

***

### Tool Message

对于支持工具调用的模型，AI消息可以包含工具调用。工具消息用于将单个工具执行的结果传递回模型。

```python  theme={null}
from langchain.messages import AIMessage
from langchain.messages import ToolMessage

# 在模型进行工具调用后
# （这里，我们为简洁起见手动创建消息）
ai_message = AIMessage(
    content=[],
    tool_calls=[{
        "name": "get_weather",
        "args": {"location": "San Francisco"},
        "id": "call_123"
    }]
)

# 执行工具并创建结果消息
weather_result = "晴天，72°F"
tool_message = ToolMessage(
    content=weather_result,
    tool_call_id="call_123"  # 必须与调用 ID 匹配
)

# 继续对话
messages = [
    HumanMessage("旧金山的天气怎么样？"),
    ai_message,  # 模型的工具调用
    tool_message,  # 工具执行结果
]
response = model.invoke(messages)  # 模型处理结果
```

    from langchain.messages import ToolMessage
    
    # 发送给模型
    message_content = "那是最美好的时代，那是最糟糕的时代。"
    
    # 下游可用的工件
    artifact = {"document_id": "doc_123", "page": 0}
    
    tool_message = ToolMessage(
        content=message_content, # 工具调用的字符串化输出。
        tool_call_id="call_123", # 此消息响应的工具调用的ID。必须与AIMessage中的工具调用ID匹配。
        name="search_books", # 被调用的工具的名称。
        artifact=artifact, # artifact字段存储补充数据，这些数据不会发送到模型，但可以通过编程方式访问。这对于存储原始结果、调试信息或用于下游处理的数据非常有用，而不会弄乱模型的上下文。
    )
## Message content（待办）
