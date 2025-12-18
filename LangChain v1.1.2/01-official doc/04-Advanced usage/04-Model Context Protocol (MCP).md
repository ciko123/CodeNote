# 模型上下文协议 (Model Context Protocol, MCP)

[模型上下文协议 (MCP)](https://modelcontextprotocol.io/introduction)是一个开放协议，用于标准化应用程序向LLM提供工具和上下文的方式。LangChain代理可以使用[`langchain-mcp-adapters`](https://github.com/langchain-ai/langchain-mcp-adapters)库来使用在MCP服务器上定义的工具。

## 快速开始 (Quickstart)

安装`langchain-mcp-adapters`库：

  ```bash
  pip install langchain-mcp-adapters
  ```

  ```bash
  uv add langchain-mcp-adapters
  ```

`langchain-mcp-adapters`使代理能够使用跨一个或多个MCP服务器定义的工具。

  `MultiServerMCPClient`默认是**无状态的**。每次工具调用都会创建一个新的MCP `ClientSession`，执行工具，然后清理。有关更多详细信息，请参阅[有状态会话](#stateful-sessions)部分。

```python
from langchain_mcp_adapters.client import MultiServerMCPClient  # [!code highlight]
from langchain.agents import create_agent


client = MultiServerMCPClient(  # [!code highlight]
    {
        "math": {
            "transport": "stdio",  # 本地子进程通信
            "command": "python",
            # math_server.py文件的绝对路径
            "args": ["/path/to/math_server.py"],
        },
        "weather": {
            "transport": "http",  # 基于HTTP的远程服务器
            # 确保在端口8000启动天气服务器
            "url": "http://localhost:8000/mcp",
        }
    }
)

tools = await client.get_tools()  # [!code highlight]
agent = create_agent(
    "claude-sonnet-4-5-20250929",
    tools  # [!code highlight]
)
math_response = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
)
weather_response = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "what is the weather in nyc?"}]}
)

## 自定义服务器 (Custom servers)

要创建自定义MCP服务器，请使用[FastMCP](https://gofastmcp.com/getting-started/welcome)库：


```

  ```bash
  pip install fastmcp
  uv add fastmcp
  ```

要使用MCP工具服务器测试您的代理，请使用以下示例：

  ```python
from fastmcp import FastMCP

  mcp = FastMCP("Math")

  @mcp.tool()
  def add(a: int, b: int) -> int:
      """添加两个数字"""
      return a + b

  @mcp.tool()
  def multiply(a: int, b: int) -> int:
      """乘以两个数字"""
      return a * b

  if __name__ == "__main__":
      mcp.run(transport="stdio")
  ```

  ```python
from fastmcp import FastMCP

  mcp = FastMCP("Weather")

  @mcp.tool()
  async def get_weather(location: str) -> str:
      """获取位置的天气。"""
      return "It's always sunny in New York"

  if __name__ == "__main__":
      mcp.run(transport="streamable-http")
  ```

## 传输方式 (Transports)

MCP支持不同的传输机制用于客户端-服务器通信。

### HTTP

`http`传输（也称为`streamable-http`）使用HTTP请求进行客户端-服务器通信。有关更多详细信息，请参阅[MCP HTTP传输规范](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports#streamable-http)。

```python
client = MultiServerMCPClient(
    {
        "weather": {
            "transport": "http",
            "url": "http://localhost:8000/mcp",
        }
    }
)
```

#### 传递标头 (Passing headers)

通过HTTP连接到MCP服务器时，您可以使用连接配置中的`headers`字段包含自定义标头（例如用于身份验证或追踪）。这支持`sse`（已被MCP规范弃用）和`streamable_http`传输。

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

client = MultiServerMCPClient(
    {
        "weather": {
            "transport": "http",
            "url": "http://localhost:8000/mcp",
            "headers": {  # [!code highlight]
                "Authorization": "Bearer YOUR_TOKEN",  # [!code highlight]
                "X-Custom-Header": "custom-value"  # [!code highlight]
            },  # [!code highlight]
        }
    }
)
tools = await client.get_tools()
agent = create_agent("openai:gpt-4.1", tools)
response = await agent.ainvoke({"messages": "what is the weather in nyc?"})
```

#### 身份验证 (Authentication)

`langchain-mcp-adapters`库在底层使用官方的[MCP SDK](https://github.com/modelcontextprotocol/python-sdk)，这允许您通过实现`httpx.Auth`接口提供自定义身份验证机制。

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "weather": {
            "transport": "http",
            "url": "http://localhost:8000/mcp",
            "auth": auth, # [!code highlight]
        }
    }
)
```

* [Example custom auth implementation](https://github.com/modelcontextprotocol/python-sdk/blob/main/examples/clients/simple-auth-client/mcp_simple_auth_client/main.py)
* [Built-in OAuth flow](https://github.com/modelcontextprotocol/python-sdk/blob/main/src/mcp/client/auth.py#L179)

### stdio

客户端将服务器作为子进程启动并通过标准输入/输出通信。最适合本地工具和简单设置。

  与HTTP传输不同，`stdio`连接本质上是**有状态的**——子进程在客户端连接的生命周期内持续存在。但是，当使用`MultiServerMCPClient`而没有显式会话管理时，每个工具调用仍然会创建新会话。有关管理持久连接，请参阅[有状态会话](#stateful-sessions)。

```python
client = MultiServerMCPClient(
    {
        "math": {
            "transport": "stdio",
            "command": "python",
            "args": ["/path/to/math_server.py"],
        }
    }
)
```

## 有状态会话 (Stateful sessions)

默认情况下，`MultiServerMCPClient`是**无状态的**——每个工具调用都会创建一个新的MCP会话，执行工具，然后清理。

如果您需要控制MCP会话的[生命周期](https://modelcontextprotocol.io/specification/2025-03-26/basic/lifecycle)（例如，当使用跨工具调用维护上下文的有状态服务器时），您可以使用`client.session()`创建持久的`ClientSession`。

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import create_agent

client = MultiServerMCPClient({...})

# 显式创建会话
async with client.session("server_name") as session:  # [!code highlight]
    # 将会话传递给加载工具、资源或提示词
    tools = await load_mcp_tools(session)  # [!code highlight]
    agent = create_agent(
        "anthropic:claude-3-7-sonnet-latest",
        tools
    )
```

## 核心功能 (Core features)

### 工具 (Tools)

[工具](https://modelcontextprotocol.io/docs/concepts/tools)允许MCP服务器暴露可执行函数，LLM可以调用这些函数来执行操作——如查询数据库、调用API或与外部系统交互。LangChain将MCP工具转换为LangChain[工具](/oss/python/langchain/tools)，使它们可以直接在任何LangChain代理或工作流中使用。

#### 加载工具 (Loading tools)

使用`client.get_tools()`从MCP服务器检索工具并将它们传递给您的代理：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

client = MultiServerMCPClient({...})
tools = await client.get_tools()  # [!code highlight]
agent = create_agent("claude-sonnet-4-5-20250929", tools)
```

#### 结构化内容 (Structured content)

MCP工具可以返回[结构化内容](https://modelcontextprotocol.io/specification/2025-03-26/server/tools#structured-content)以及人类可读的文本响应。当工具需要返回机器可解析的数据（如JSON）以及显示给模型的文本时，这很有用。

当MCP工具返回`structuredContent`时，适配器将其包装在[`MCPToolArtifact`](/docs/reference/langchain-mcp-adapters#MCPToolArtifact)中，并将其作为工具的工件返回。您可以使用`ToolMessage`上的`artifact`字段访问它。

**从工件中提取结构化内容**

调用代理后，您可以访问响应中工具消息的结构化内容：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain.messages import ToolMessage

client = MultiServerMCPClient({...})
tools = await client.get_tools()
agent = create_agent("claude-sonnet-4-5-20250929", tools)

result = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "Get data from the server"}]}
)

# 从工具消息中提取结构化内容
for message in result["messages"]:
    if isinstance(message, ToolMessage) and message.artifact:
        structured_content = message.artifact["structured_content"]
```

#### 多模态工具内容 (Multimodal tool content)

MCP工具可以在其响应中返回[多模态内容](https://modelcontextprotocol.io/specification/2025-03-26/server/tools#tool-result)（图像、文本等）。当MCP服务器返回包含多个部分的内容（例如，文本和图像）时，适配器将它们转换为LangChain的[标准内容块](/oss/python/langchain/messages#standard-content-blocks)。您可以通过`ToolMessage`上的`content_blocks`属性访问标准化表示：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent

client = MultiServerMCPClient({...})
tools = await client.get_tools()
agent = create_agent("claude-sonnet-4-5-20250929", tools)

result = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "Take a screenshot of the current page"}]}
)

# 从工具消息中访问多模态内容
for message in result["messages"]:
    if message.type == "tool":
        # 提供商原生格式的原始内容
        print(f"Raw content: {message.content}")

        # 标准化内容块  # [!code highlight]
        for block in message.content_blocks:  # [!code highlight]
            if block["type"] == "text":  # [!code highlight]
                print(f"Text: {block['text']}")  # [!code highlight]
            elif block["type"] == "image":  # [!code highlight]
                print(f"Image URL: {block.get('url')}")  # [!code highlight]
                print(f"Image base64: {block.get('base64', '')[:50]}...")  # [!code highlight]
```

这使您能够以提供商无关的方式处理多模态工具响应，无论底层MCP服务器如何格式化其内容。

### 资源 (Resources)

[资源](https://modelcontextprotocol.io/docs/concepts/resources)允许MCP服务器暴露数据——如文件、数据库记录或API响应——这些数据可以被客户端读取。LangChain将MCP资源转换为[Blob](/docs/reference/langchain-core/documents#Blob)对象，这些对象提供了处理文本和二进制内容的统一接口。

#### 加载资源 (Loading resources)

使用`client.get_resources()`从MCP服务器加载资源：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({...})

# 从服务器加载所有资源
blobs = await client.get_resources("server_name")  # [!code highlight]

# 或者按URI加载特定资源
blobs = await client.get_resources("server_name", uris=["file:///path/to/file.txt"])  # [!code highlight]

for blob in blobs:
    print(f"URI: {blob.metadata['uri']}, MIME type: {blob.mimetype}")
    print(blob.as_string())  # 对于文本内容
```

您也可以直接与会话一起使用[`load_mcp_resources`](/docs/reference/langchain-mcp-adapters#load_mcp_resources)以获得更多控制：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.resources import load_mcp_resources

client = MultiServerMCPClient({...})

async with client.session("server_name") as session:
    # Load all resources
    blobs = await load_mcp_resources(session)

    # Or load specific resources by URI
    blobs = await load_mcp_resources(session, uris=["file:///path/to/file.txt"])
```

### 提示词 (Prompts)

[提示词](https://modelcontextprotocol.io/docs/concepts/prompts)允许MCP服务器暴露可重用的提示词模板，这些模板可以被客户端检索和使用。LangChain将MCP提示词转换为[消息](/docs/concepts/messages)，使其易于集成到基于聊天的工作流中。

#### 加载提示词 (Loading prompts)

使用`client.get_prompt()`从MCP服务器加载提示词：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({...})

# Load a prompt by name
messages = await client.get_prompt("server_name", "summarize")  # [!code highlight]

# Load a prompt with arguments
messages = await client.get_prompt(  # [!code highlight]
    "server_name",  # [!code highlight]
    "code_review",  # [!code highlight]
    arguments={"language": "python", "focus": "security"}  # [!code highlight]
)  # [!code highlight]

# Use the messages in your workflow
for message in messages:
    print(f"{message.type}: {message.content}")
```

您也可以直接与会话一起使用[`load_mcp_prompt`](/docs/reference/langchain-mcp-adapters#load_mcp_prompt)以获得更多控制：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.prompts import load_mcp_prompt

client = MultiServerMCPClient({...})

async with client.session("server_name") as session:
    # Load a prompt by name
    messages = await load_mcp_prompt(session, "summarize")

    # Load a prompt with arguments
    messages = await load_mcp_prompt(
        session,
        "code_review",
        arguments={"language": "python", "focus": "security"}
    )
```

## 高级功能 (Advanced features)

### 工具拦截器 (Tool Interceptors)

MCP服务器作为独立进程运行——它们无法访问LangGraph运行时信息，如[存储](/oss/python/langgraph/persistence#memory-store)、[上下文](/oss/python/langchain/context-engineering)或代理状态。**拦截器通过在MCP工具执行期间让您访问此运行时上下文来弥合这一差距**。

拦截器还提供类似中间件的工具调用控制：您可以修改请求、实现重试、动态添加标头或完全短路执行。

| 章节                                                     | 描述                                                                       |
| --------------------------------------------------------- | --------------------------------------------------------------------------- |
| [访问运行时上下文](#accessing-runtime-context)           | 读取用户ID、API密钥、存储数据和代理状态                                     |
| [状态更新和命令](#state-updates-and-commands)             | 使用`Command`更新代理状态或控制图流程                                       |
| [编写拦截器](#writing-interceptors)                       | 修改请求、组合拦截器和错误处理的模式                                         |

#### 访问运行时上下文 (Accessing runtime context)

当MCP工具在LangChain代理中使用时（通过`create_agent`），拦截器获得对`ToolRuntime`上下文的访问权限。这提供了对工具调用ID、状态、配置和存储的访问——实现了访问用户数据、持久化信息和控制代理行为的强大模式。

  **Runtime context**:
    Access user-specific configuration like user IDs, API keys, or permissions that are passed at invocation time：

```python
from dataclasses import dataclass
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langchain_mcp_adapters.interceptors import MCPToolCallRequest
    from langchain.agents import create_agent

    @dataclass
    class Context:
        user_id: str
        api_key: str
    
    async def inject_user_context(
        request: MCPToolCallRequest,
        handler,
    ):
        """Inject user credentials into MCP tool calls."""
        runtime = request.runtime
        user_id = runtime.context.user_id  # [!code highlight]
        api_key = runtime.context.api_key  # [!code highlight]
    
        # Add user context to tool arguments
        modified_request = request.override(
            args={**request.args, "user_id": user_id}
        )
        return await handler(modified_request)
    
    client = MultiServerMCPClient(
        {...},
        tool_interceptors=[inject_user_context],
    )
    tools = await client.get_tools()
    agent = create_agent("gpt-4o", tools, context_schema=Context)
    
    # Invoke with user context
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "Search my orders"}]},
        context={"user_id": "user_123", "api_key": "sk-..."}
    )
```

  **Store**:
    Access long-term memory to retrieve user preferences or persist data across conversations：

```python
from dataclasses import dataclass
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langchain_mcp_adapters.interceptors import MCPToolCallRequest
    from langchain.agents import create_agent
    from langgraph.store.memory import InMemoryStore

    @dataclass
    class Context:
        user_id: str
    
    async def personalize_search(
        request: MCPToolCallRequest,
        handler,
    ):
        """Personalize MCP tool calls using stored preferences."""
        runtime = request.runtime
        user_id = runtime.context.user_id
        store = runtime.store  # [!code highlight]
    
        # Read user preferences from store
        prefs = store.get(("preferences",), user_id)  # [!code highlight]
    
        if prefs and request.name == "search":
            # Apply user's preferred language and result limit
            modified_args = {
                **request.args,
                "language": prefs.value.get("language", "en"),
                "limit": prefs.value.get("result_limit", 10),
            }
            request = request.override(args=modified_args)
    
        return await handler(request)
    
    client = MultiServerMCPClient(
        {...},
        tool_interceptors=[personalize_search],
    )
    tools = await client.get_tools()
    agent = create_agent(
        "gpt-4o",
        tools,
        context_schema=Context,
        store=InMemoryStore()
    )
```

  **State**:
    Access conversation state to make decisions based on the current session：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
    from langchain_mcp_adapters.interceptors import MCPToolCallRequest
    from langchain.messages import ToolMessage

    async def require_authentication(
        request: MCPToolCallRequest,
        handler,
    ):
        """Block sensitive MCP tools if user is not authenticated."""
        runtime = request.runtime
        state = runtime.state  # [!code highlight]
        is_authenticated = state.get("authenticated", False)  # [!code highlight]
    
        sensitive_tools = ["delete_file", "update_settings", "export_data"]
    
        if request.name in sensitive_tools and not is_authenticated:
            # Return error instead of calling tool
            return ToolMessage(
                content="Authentication required. Please log in first.",
                tool_call_id=runtime.tool_call_id,
            )
    
        return await handler(request)
    
    client = MultiServerMCPClient(
        {...},
        tool_interceptors=[require_authentication],
    )
```

  **工具调用 ID (Tool call ID)**:
    访问工具调用ID以返回格式正确的响应或跟踪工具执行：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
    from langchain_mcp_adapters.interceptors import MCPToolCallRequest
    from langchain.messages import ToolMessage

    async def rate_limit_interceptor(
        request: MCPToolCallRequest,
        handler,
    ):
        """限制昂贵的MCP工具调用的频率。"""
        runtime = request.runtime
        tool_call_id = runtime.tool_call_id  # [!code highlight]
    
        # 检查频率限制（简化示例）
        if is_rate_limited(request.name):
            return ToolMessage(
                content="Rate limit exceeded. Please try again later.",
                tool_call_id=tool_call_id,  # [!code highlight]
            )
    
        result = await handler(request)
    
        # 记录成功的工具调用
        log_tool_execution(tool_call_id, request.name, success=True)
    
        return result
    
    client = MultiServerMCPClient(
        {...},
        tool_interceptors=[rate_limit_interceptor],
    )
```

有关更多上下文工程模式，请参阅[上下文工程](/oss/python/langchain/context-engineering)和[工具](/oss/python/langchain/tools)。

#### 状态更新和命令 (State updates and commands)

拦截器可以返回`Command`对象来更新代理状态或控制图执行流。这对于跟踪任务进度、在代理之间切换或提前结束执行很有用。

```python
from langchain.agents import AgentState, create_agent
from langchain_mcp_adapters.interceptors import MCPToolCallRequest
from langchain.messages import ToolMessage
from langgraph.types import Command

async def handle_task_completion(
    request: MCPToolCallRequest,
    handler,
):
    """标记任务完成并移交给摘要代理。"""
    result = await handler(request)

    if request.name == "submit_order":
        return Command(
            update={
                "messages": [result] if isinstance(result, ToolMessage) else [],
                "task_status": "completed",  # [!code highlight]
            },
            goto="summary_agent",  # [!code highlight]
        )

    return result
```

使用带有`goto="__end__"`的`Command`来提前结束执行：

```python
async def end_on_success(
    request: MCPToolCallRequest,
    handler,
):
    """当任务标记为完成时结束代理运行。"""
    result = await handler(request)

    if request.name == "mark_complete":
        return Command(
            update={"messages": [result], "status": "done"},
            goto="__end__",  # [!code highlight]
        )

    return result
```

#### 自定义拦截器 (Custom interceptors)

拦截器是包装工具执行的异步函数，支持请求/响应修改、重试逻辑和其他横切关注点。它们遵循“洋葱”模式，其中列表中的第一个拦截器是最外层。

**基本模式**

拦截器是接收请求和处理器的异步函数。您可以在调用处理器之前修改请求，在之后修改响应，或完全跳过处理器。

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.interceptors import MCPToolCallRequest

async def logging_interceptor(
    request: MCPToolCallRequest,
    handler,
):
    """在执行前后记录工具调用。"""
    print(f"Calling tool: {request.name} with args: {request.args}")
    result = await handler(request)
    print(f"Tool {request.name} returned: {result}")
    return result

client = MultiServerMCPClient(
    {"math": {"transport": "stdio", "command": "python", "args": ["/path/to/server.py"]}},
    tool_interceptors=[logging_interceptor],  # [!code highlight]
)
```

**修改请求**

使用`request.override()`创建修改后的请求。这遵循不可变模式，保持原始请求不变。

```python
async def double_args_interceptor(
    request: MCPToolCallRequest,
    handler,
):
    """在执行前将所有数字参数加倍。"""
    modified_args = {k: v * 2 for k, v in request.args.items()}
    modified_request = request.override(args=modified_args)  # [!code highlight]
    return await handler(modified_request)

# 原始调用：add(a=2, b=3) 变为 add(a=4, b=6)
```

**运行时修改标头**

拦截器可以基于请求上下文动态修改HTTP标头：

```python
async def auth_header_interceptor(
    request: MCPToolCallRequest,
    handler,
):
    """根据被调用的工具添加身份验证标头。"""
    token = get_token_for_tool(request.name)
    modified_request = request.override(
        headers={"Authorization": f"Bearer {token}"}  # [!code highlight]
    )
    return await handler(modified_request)
```

**组合拦截器**

多个拦截器以“洋葱”顺序组合——列表中的第一个拦截器是最外层：

```python
async def outer_interceptor(request, handler):
    print("outer: before")
    result = await handler(request)
    print("outer: after")
    return result

async def inner_interceptor(request, handler):
    print("inner: before")
    result = await handler(request)
    print("inner: after")
    return result

client = MultiServerMCPClient(
    {...},
    tool_interceptors=[outer_interceptor, inner_interceptor],  # [!code highlight]
)

# 执行顺序：
# outer: before -> inner: before -> tool execution -> inner: after -> outer: after
```

**错误处理**

使用拦截器捕获工具执行错误并实现重试逻辑：

```python
import asyncio

async def retry_interceptor(
    request: MCPToolCallRequest,
    handler,
    max_retries: int = 3,
    delay: float = 1.0,
):
    """使用指数退避重试失败的工具调用。"""
    last_error = None
    for attempt in range(max_retries):
        try:
            return await handler(request)
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                wait_time = delay * (2 ** attempt)  # 指数退避
                await asyncio.sleep(wait_time)
                print(f"工具 {request.name} 失败（尝试 {attempt + 1}），{wait_time}秒后重试...")
    raise last_error

client = MultiServerMCPClient(
    {...},
    tool_interceptors=[retry_interceptor],
)

您还可以捕获特定的错误类型并返回回退值：

```python
async def fallback_interceptor(
    request: MCPToolCallRequest,
    handler,
):
    """如果工具执行失败，则返回回退值。"""
    try:
        return await handler(request)
    except TimeoutError:
        return f"工具 {request.name} 超时。请稍后重试。"
    except ConnectionError:
        return f"无法连接到 {request.name} 服务。使用缓存数据。"
```

### 进度通知 (Progress notifications)

订阅长时间运行的工具执行的进度更新：

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.callbacks import Callbacks, CallbackContext

async def on_progress(
    progress: float,
    total: float | None,
    message: str | None,
    context: CallbackContext,
):
    """处理来自MCP服务器的进度更新。"""
    percent = (progress / total * 100) if total else progress
    tool_info = f" ({context.tool_name})" if context.tool_name else ""
    print(f"[{context.server_name}{tool_info}] 进度: {percent:.1f}% - {message}")

client = MultiServerMCPClient(
    {...},
    callbacks=Callbacks(on_progress=on_progress),  # [!code highlight]
)
```

`CallbackContext`提供：

* `server_name`：MCP服务器的名称
* `tool_name`：正在执行的工具的名称（在工具调用期间可用）

### 日志记录 (Logging)

MCP协议支持来自服务器的[日志记录](https://modelcontextprotocol.io/specification/2025-03-26/server/utilities/logging#log-levels)通知。使用`Callbacks`类订阅这些事件。

```python
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.callbacks import Callbacks, CallbackContext
from mcp.types import LoggingMessageNotificationParams

async def on_logging_message(
    params: LoggingMessageNotificationParams,
    context: CallbackContext,
):
    """处理来自MCP服务器的日志消息。"""
    print(f"[{context.server_name}] {params.level}: {params.data}")

client = MultiServerMCPClient(
    {...},
    callbacks=Callbacks(on_logging_message=on_logging_message),  # [!code highlight]
)
```

## 其他资源 (Additional resources)

* [MCP文档](https://modelcontextprotocol.io/introduction)
* [MCP传输文档](https://modelcontextprotocol.io/docs/concepts/transports)
* [`langchain-mcp-adapters`](https://github.com/langchain-ai/langchain-mcp-adapters)

***

  [在GitHub上编辑此页面的源代码。](https://github.com/langchain-ai/docs/edit/main/src/oss/langchain/mcp.mdx)

  [通过MCP以编程方式连接这些文档](/use-these-docs)到Claude、VSCode等，以获得实时答案。

---