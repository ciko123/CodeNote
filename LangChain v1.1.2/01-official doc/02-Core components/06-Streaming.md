# 流式传输 (Streaming)

## 概述

- **流式传输代理进度**：在每个代理步骤后获取状态更新
- **流式传输 LLM 令牌**：流式传输语言模型生成的令牌
- **流式传输自定义更新**：发送用户定义的信号（例如"已获取 10/100 条记录"）
- **流式传输多种模式**：选择"更新"、"消息"或"自定义"模式

##  Agent progress

要流式传输代理进度，请使用带有 `stream_mode="updates"` 的 `stream` 或 `astream` 方法。这将在每个代理步骤后发出事件。

LLM 节点：AIMessage with tool call requests
Tool 节点：ToolMessage with execution result
LLM 节点：Final AI response

```python
from langchain.agents import create_agent

def get_weather(city: str) -> str:
    """获取指定城市的天气。"""
    
    return f"{city} 的天气总是晴朗的！"

agent = create_agent(
    model="gpt-5-nano",
    tools=[get_weather],
)

# 使用流式输出
for chunk in agent.stream(   
    {"messages": [{"role": "user", "content": "旧金山的天气怎么样？"}]},
    stream_mode="updates",
):
    for step, data in chunk.items():
        print(f"步骤: {step}")
        print(f"内容: {data['messages'][-1].content_blocks}")
```
```
步骤: model
内容: [{'type': 'tool_call', 'name': 'get_weather', 'args': {'city': '旧金山'}, 'id': 'call_6CH1EspN9ceIQfjM4EAoesRJ'}]
步骤: tools
内容: [{'type': 'text', 'text': '旧金山 的天气总是晴朗的！'}]
步骤: model
内容: [{'type': 'text', 'text': '旧金山的天气总是晴朗的！'}]
```

## LLM tokens

要流式传输 LLM 生成的令牌，请使用 `stream_mode="messages"`。下面您可以看到代理流式传输工具调用和最终响应的输出。
```python
from langchain.agents import create_agent

def get_weather(city: str) -> str:
    """获取指定城市的天气。"""
    return f"{city} 的天气总是晴朗的！"

agent = create_agent(
    OPENAI_MODEL,
    tools=[get_weather],
)

# 使用消息流式输出
for token, metadata in agent.stream(   
    {"messages": [{"role": "user", "content": "旧金山的天气怎么样？"}]},
    stream_mode="messages",
):
    print(f"节点: {metadata['langgraph_node']}")
    print(f"内容: {token.content_blocks}")
```

```
节点: model
内容: []
节点: model
内容: [{'type': 'tool_call_chunk', 'id': 'call_rNT76jkAqCiQXlyh8pYfYgq6', 'name': 'get_weather', 'args': None, 'index': 0}]
节点: model
内容: [{'type': 'tool_call_chunk', 'id': None, 'name': None, 'args': '{"', 'index': 0}]
节点: model
内容: [{'type': 'tool_call_chunk', 'id': None, 'name': None, 'args': 'city', 'index': 0}]
节点: model
内容: [{'type': 'tool_call_chunk', 'id': None, 'name': None, 'args': '":"', 'index': 0}]
节点: model
内容: [{'type': 'tool_call_chunk', 'id': None, 'name': None, 'args': '旧', 'index': 0}]
节点: model
内容: [{'type': 'tool_call_chunk', 'id': None, 'name': None, 'args': '金', 'index': 0}]
节点: model
内容: [{'type': 'tool_call_chunk', 'id': None, 'name': None, 'args': '山', 'index': 0}]
节点: model
内容: [{'type': 'tool_call_chunk', 'id': None, 'name': None, 'args': '"}', 'index': 0}]
节点: model
内容: []
节点: model
内容: []
节点: model
内容: []
节点: tools
内容: [{'type': 'text', 'text': '旧金山 的天气总是晴朗的！'}]
节点: model
内容: []
节点: model
内容: []
节点: model
内容: [{'type': 'text', 'text': '旧'}]
节点: model
内容: [{'type': 'text', 'text': '金'}]
节点: model
内容: [{'type': 'text', 'text': '山'}]
节点: model
内容: [{'type': 'text', 'text': '的'}]
节点: model
内容: [{'type': 'text', 'text': '天气'}]
节点: model
内容: [{'type': 'text', 'text': '一直'}]
节点: model
内容: [{'type': 'text', 'text': '晴'}]
节点: model
内容: [{'type': 'text', 'text': '朗'}]
节点: model
内容: [{'type': 'text', 'text': '。'}]
节点: model
内容: []
节点: model
内容: []
节点: model
内容: []
```

##  Custom updates

要从工具执行时流式传输更新，您可以使用 `get_stream_writer`。

```python
from langchain.agents import create_agent
from langgraph.config import get_stream_writer  

def get_weather(city: str) -> str:
    """获取给定城市的天气。"""
    writer = get_stream_writer()  
    # 流式传输任意数据
    writer(f"正在获取 {city} 的数据。")
    writer(f"已获取 {city} 的数据。")
    return f"{city} 的天气总是晴朗的！"

agent = create_agent(
    model="claude-sonnet-4-5-20250929",
    tools=[get_weather],
)
for chunk in agent.stream(
    {"messages": [{"role": "user", "content": "旧金山的天气怎么样？"}]},
    stream_mode="custom"
):
    print(chunk)
    
# 正在获取 San Francisco 的数据。
# 已获取 San Francisco 的数据。
```

##  流式传输多种模式

您可以通过将流式模式作为列表传递来指定多种流式模式：`stream_mode=["updates", "custom"]`：

#### 流式传输多种模式
```python
from langchain.agents import create_agent
from langgraph.config import get_stream_writer
def get_weather(city: str) -> str:
    """获取给定城市的天气。"""
    writer = get_stream_writer()
    writer(f"正在获取 {city} 的数据。")
    writer(f"已获取 {city} 的数据。")
    return f"{city} 的天气总是晴朗的！"

agent = create_agent(
    model="gpt-5-nano",
    tools=[get_weather],
)

for stream_mode, chunk in agent.stream(  
    {"messages": [{"role": "user", "content": "旧金山的天气怎么样？"}]},
    stream_mode=["updates", "custom"]
):
    print(f"stream_mode: {stream_mode}")
    print(f"content: {chunk}")
    print("\n")
```

输出
```
stream_mode: updates
content: {'model': {'messages': [AIMessage(content='', response_metadata={'token_usage': {'completion_tokens': 280, 'prompt_tokens': 132, 'total_tokens': 412, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 256, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'gpt-5-nano-2025-08-07', 'system_fingerprint': None, 'id': 'chatcmpl-C9tlgBzGEbedGYxZ0rTCz5F7OXpL7', 'service_tier': 'default', 'finish_reason': 'tool_calls', 'logprobs': None}, id='lc_run--480c07cb-e405-4411-aa7f-0520fddeed66-0', tool_calls=[{'name': 'get_weather', 'args': {'city': 'San Francisco'}, 'id': 'call_KTNQIftMrl9vgNwEfAJMVu7r', 'type': 'tool_call'}], usage_metadata={'input_tokens': 132, 'output_tokens': 280, 'total_tokens': 412, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 256}})]}}

stream_mode: custom
content: 正在获取 San Francisco 的数据。

stream_mode: custom
content: Acquired data for city: San Francisco

stream_mode: updates
content: {'tools': {'messages': [ToolMessage(content="It's always sunny in San Francisco!", name='get_weather', tool_call_id='call_KTNQIftMrl9vgNwEfAJMVu7r')]}}

stream_mode: updates
content: {'model': {'messages': [AIMessage(content='San Francisco weather: It's always sunny in San Francisco!\n\n', response_metadata={'token_usage': {'completion_tokens': 764, 'prompt_tokens': 168, 'total_tokens': 932, 'completion_tokens_details': {'accepted_prediction_tokens': 0, 'audio_tokens': 0, 'reasoning_tokens': 704, 'rejected_prediction_tokens': 0}, 'prompt_tokens_details': {'audio_tokens': 0, 'cached_tokens': 0}}, 'model_provider': 'openai', 'model_name': 'gpt-5-nano-2025-08-07', 'system_fingerprint': None, 'id': 'chatcmpl-C9tljDFVki1e1haCyikBptAuXuHYG', 'service_tier': 'default', 'finish_reason': 'stop', 'logprobs': None}, id='lc_run--acbc740a-18fe-4a14-8619-da92a0d0ee90-0', usage_metadata={'input_tokens': 168, 'output_tokens': 764, 'total_tokens': 932, 'input_token_details': {'audio': 0, 'cache_read': 0}, 'output_token_details': {'audio': 0, 'reasoning': 704}})]}}
```

## Disable streaming 禁用流式传输

在某些应用程序中，您可能需要为特定模型禁用单个令牌的流式传输。

这在多代理系统中很有用，可以控制哪些代理流式传输其输出。
