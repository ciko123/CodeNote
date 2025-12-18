# 长期记忆 (Long-term memory)

## 概述 (Overview)

LangChain 代理使用 [LangGraph 持久化](/oss/python/langgraph/persistence#memory-store) 来启用长期记忆。这是一个更高级的主题，需要 LangGraph 的知识才能使用。

## 内存存储 (Memory storage)

LangGraph 将长期记忆存储为 JSON 文档，在一个 [存储](/oss/python/langgraph/persistence#memory-store) 中。
每个记忆都组织在一个自定义的 `命名空间` (类似于文件夹) 和一个独特的 `键` (类似于文件名) 下。命名空间通常包括用户或组织 ID 或其他标签，使得信息更容易组织。
这种结构支持记忆的层次化组织。然后通过内容过滤器支持跨命名空间搜索。

```python
from langgraph.store.memory import InMemoryStore


def embed(texts: list[str]) -> list[list[float]]:
    # Replace with an actual embedding function or LangChain embeddings object
    return [[1.0, 2.0] * len(texts)]


# InMemoryStore 将数据保存到内存字典中。在生产环境中使用 DB 支持的存储。
store = InMemoryStore(index={"embed": embed, "dims": 2}) # [!code highlight]
user_id = "my-user"
application_context = "chitchat"
namespace = (user_id, application_context) # [!code highlight]
store.put( # [!code highlight]
    namespace,
    "a-memory",
    {
        "rules": [
            "User likes short, direct language",
            "User only speaks English & python",
        ],
        "my-key": "my-value",
    },
)
# 按 ID 获取“记忆”
item = store.get(namespace, "a-memory") # [!code highlight]
# 在此命名空间内搜索“记忆”，按内容等价性过滤，按向量相似性排序
items = store.search( # [!code highlight]
    namespace, filter={"my-key": "my-value"}, query="language preferences"
)
```

有关内存存储的更多信息，请参阅 [持久化](/oss/python/langgraph/persistence#memory-store) 指南。

## 在工具中读取长期记忆 (Read long-term memory in tools)

```python
from dataclasses import dataclass

from langchain_core.runnables import RunnableConfig
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langgraph.store.memory import InMemoryStore


@dataclass
class Context:
    user_id: str

# InMemoryStore 将数据保存到内存字典中。在生产环境中使用 DB 支持的存储。
store = InMemoryStore() # [!code highlight]

# Write sample data to the store using the put method
store.put( # [!code highlight]
    ("users",),  # 命名空间用于将相关数据分组（用户命名空间用于用户数据）
    "user_123",  # 命名空间内的键（用户 ID 作为键）
    {
        "name": "John Smith",
        "language": "English",
    }  # 为给定用户存储的数据
)

@tool
def get_user_info(runtime: ToolRuntime[Context]) -> str:
    """查找用户信息。"""
    # 访问存储 - 与提供给 `create_agent` 的相同
    store = runtime.store # [!code highlight]
    user_id = runtime.context.user_id
    # 从存储中检索数据 - 返回带有值和元数据的 StoreValue 对象
    user_info = store.get(("users",), user_id) # [!code highlight]
    return str(user_info.value) if user_info else "未知用户"

agent = create_agent(
    model="claude-sonnet-4-5-20250929",
    tools=[get_user_info],
    # 将存储传递给代理 - 使代理能够在运行工具时访问存储
    store=store, # [!code highlight]
    context_schema=Context
)

# 运行代理
agent.invoke(
    {"messages": [{"role": "user", "content": "查找用户信息"}]},
    context=Context(user_id="user_123") # [!code highlight]
)
```


## 从工具中写入长期记忆 (Write long-term memory from tools)

```python
from dataclasses import dataclass
from typing_extensions import TypedDict

from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime
from langgraph.store.memory import InMemoryStore


# InMemoryStore 将数据保存到内存字典中。在生产环境中使用 DB 支持的存储。
store = InMemoryStore() # [!code highlight]

@dataclass
class Context:
    user_id: str

# TypedDict 为 LLM 定义用户信息的结构
class UserInfo(TypedDict):
    name: str

# 允许代理更新用户信息的工具（对聊天应用程序有用）
@tool
def save_user_info(user_info: UserInfo, runtime: ToolRuntime[Context]) -> str:
    """保存用户信息。"""
    # Access the store - same as that provided to `create_agent`
    store = runtime.store # [!code highlight]
    user_id = runtime.context.user_id # [!code highlight]
    # 在存储中存储数据（命名空间、键、数据）
    store.put(("users",), user_id, user_info) # [!code highlight]
    return "成功保存用户信息。"

agent = create_agent(
    model="claude-sonnet-4-5-20250929",
    tools=[save_user_info],
    store=store, # [!code highlight]
    context_schema=Context
)

# 运行代理
agent.invoke(
    {"messages": [{"role": "user", "content": "我的名字是 John Smith"}]},,
    # 在上下文中传递 user_id 以标识正在更新谁的信息
    context=Context(user_id="user_123") # [!code highlight]
)

# 您可以直接访问存储来获取值
store.get(("users",), "user_123").value
```

***

  [在 GitHub 上编辑此页面的源代码。](https://github.com/langchain-ai/docs/edit/main/src/oss/langchain/long-term-memory.mdx)

  [通过 MCP 以编程方式连接这些文档](/use-these-docs)到 Claude、VSCode 等，以获得实时答案。


---

> 要在此文档中查找导航和其他页面，请在以下位置获取 llms.txt 文件：https://docs.langchain.com/llms.txt