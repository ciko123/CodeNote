# 内置中间件 (Built-in middleware)

> 常见agent (代理)用例的预构建中间件

LangChain为常见用例提供预构建中间件。每个中间件都是生产就绪的，可根据特定需求配置。

## 提供者无关中间件

以下中间件适用于任何LLM提供者：

| 中间件 | 描述 |
| --- | --- |
| [总结 (Summarization)](#summarization) | 接近token限制时自动总结对话历史 |
| [人在回路 (Human-in-the-loop)](#human-in-the-loop) | 暂停执行以供人工批准工具调用 |
| [模型调用限制 (Model call limit)](#model-call-limit) | 限制模型调用次数以防止过度成本 |
| [工具调用限制 (Tool call limit)](#tool-call-limit) | 通过限制调用次数控制工具执行 |
| [模型降级 (Model fallback)](#model-fallback) | 主模型失败时自动降级到备用模型 |
| [PII检测 (PII detection)](#pii-detection) | 检测和处理个人身份信息 (PII) |
| [待办事项 (To-do list)](#to-do-list) | 为agent配备任务规划和跟踪能力 |
| [LLM工具选择器 (LLM tool selector)](#llm-tool-selector) | 使用LLM在调用主模型前选择相关工具 |
| [工具重试 (Tool retry)](#tool-retry) | 使用指数退避自动重试失败的工具调用 |
| [模型重试 (Model retry)](#model-retry) | 使用指数退避自动重试失败的模型调用 |
| [LLM工具模拟器 (LLM tool emulator)](#llm-tool-emulator) | 使用LLM模拟工具执行用于测试 |
| [上下文编辑 (Context editing)](#context-editing) | 通过修剪或清除工具使用管理对话上下文 |
| [Shell工具 (Shell tool)](#shell-tool) | 向agent暴露持久shell会话用于命令执行 |
| [文件搜索 (File search)](#file-search) | 提供文件系统文件的Glob和Grep搜索工具 |

### 总结 (Summarization)

接近token限制时自动总结对话历史，保留近期消息的同时压缩旧上下文。总结功能适用于以下情况：

* 超出上下文窗口的长时间运行对话
* 具有大量历史记录的多轮对话
* 需要保留完整对话上下文的应用

**API参考：**[`SummarizationMiddleware`](https://reference.langchain.com/python/langchain/middleware/#langchain.agents.middleware.SummarizationMiddleware)

```python
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

agent = create_agent(
    model="gpt-4o",
    tools=[your_weather_tool, your_calculator_tool],
    middleware=[
        SummarizationMiddleware(
            model="gpt-4o-mini",
            trigger=("tokens", 4000),
            keep=("messages", 20),
        ),
    ],
)
```

### 人在回路 (Human-in-the-loop)

在工具调用执行前暂停agent执行，以供人工批准、编辑或拒绝工具调用。人在回路功能适用于以下情况：

* 需要人工批准的高风险操作（如数据库写入、金融交易）
* 人工监督必需的合规工作流
* 人工反馈指导agent的长时间运行对话

**API参考：**`HumanInTheLoopMiddleware`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver

def read_email_tool(email_id: str) -> str:
    """根据ID读取邮件的模拟函数。"""
    return f"ID为 {email_id} 的邮件内容"

def send_email_tool(recipient: str, subject: str, body: str) -> str:
    """发送邮件的模拟函数。"""
    return f"邮件已发送至 {recipient}，主题为 '{subject}'”

agent = create_agent(
    model="gpt-4o",
    tools=[read_email_tool, send_email_tool],
    checkpointer=InMemorySaver(),
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "your_send_email_tool": {
                    "allowed_decisions": ["approve", "edit", "reject"],
                },
                "your_read_email_tool": False,
            }
        ),
    ],
)
```

### 模型调用限制 (Model call limit)

限制模型调用次数以防止无限循环或过度成本。模型调用限制适用于以下情况：

* 防止失控agent进行过多API调用
* 在生产部署中强制成本控制
* 在特定调用预算内测试agent行为

**API参考：**`ModelCallLimitMiddleware`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ModelCallLimitMiddleware

agent = create_agent(
    model="gpt-4o",
    tools=[],
    middleware=[
        ModelCallLimitMiddleware(
            thread_limit=10,
            run_limit=5,
            exit_behavior="end",
        ),
    ],
)
```

### 工具调用限制 (Tool call limit)

通过限制工具调用次数控制agent执行，可以全局限制所有工具或为特定工具设置限制。工具调用限制适用于以下情况：

* 防止对昂贵外部API的过度调用
* 限制网络搜索或数据库查询
* 强制特定工具使用的频率限制
* 防止失控agent循环

**API参考：**`ToolCallLimitMiddleware`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware

agent = create_agent(
    model="gpt-4o",
    tools=[search_tool, database_tool],
    middleware=[
        # 全局限制
        ToolCallLimitMiddleware(thread_limit=20, run_limit=10),
        # 特定工具限制
        ToolCallLimitMiddleware(
            tool_name="search",
            thread_limit=5,
            run_limit=3,
        ),
    ],
)
```

### 模型降级 (Model fallback)

主模型失败时自动降级到备用模型。模型降级适用于以下情况：

* 构建处理模型中断的弹性agent
* 通过降级到更便宜的模型优化成本
* 跨OpenAI、Anthropic等的提供者冗余

**API参考：**`ModelFallbackMiddleware`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ModelFallbackMiddleware

agent = create_agent(
    model="gpt-4o",
    tools=[],
    middleware=[
        ModelFallbackMiddleware(
            "gpt-4o-mini",
            "claude-3-5-sonnet-20241022",
        ),
    ],
)
```

### PII检测 (PII detection)

使用可配置策略检测和处理对话中的个人身份信息 (PII)。PII检测适用于以下情况：

* 具有合规要求的医疗和金融应用
* 需要清理日志的客户服务agent
* 处理敏感用户数据的任何应用

**API参考：**`PIIMiddleware`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware

agent = create_agent(
    model="gpt-4o",
    tools=[],
    middleware=[
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        PIIMiddleware("credit_card", strategy="mask", apply_to_input=True),
    ],
)
```

### 待办事项 (To-do list)

为agent配备复杂多步骤任务的任务规划和跟踪能力。待办事项列表适用于以下情况：

* 需要跨多个工具协调的复杂多步骤任务
* 进度可见性重要的长时间运行操作

**API参考：**`TodoListMiddleware`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware

agent = create_agent(
    model="gpt-4o",
    tools=[read_file, write_file, run_tests],
    middleware=[TodoListMiddleware()],
)
```

### LLM工具选择器 (LLM tool selector)

使用LLM在调用主模型前智能选择相关工具。LLM工具选择器适用于以下情况：

* 具有许多工具（10+）的agent，其中大多数与查询无关
* 通过过滤不相关工具减少token使用
* 提高模型焦点和准确性

**API参考：**`LLMToolSelectorMiddleware`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolSelectorMiddleware

agent = create_agent(
    model="gpt-4o",
    tools=[tool1, tool2, tool3, tool4, tool5, ...],
    middleware=[
        LLMToolSelectorMiddleware(
            model="gpt-4o-mini",
            max_tools=3,
            always_include=["search"],
        ),
    ],
)
```

### 工具重试 (Tool retry)

使用可配置的指数退避自动重试失败的工具调用。工具重试适用于以下情况：

* 处理外部API调用中的瞬态故障
* 提高网络依赖工具的可靠性
* 构建优雅处理临时错误的弹性agent

**API参考：**`ToolRetryMiddleware`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ToolRetryMiddleware

agent = create_agent(
    model="gpt-4o",
    tools=[search_tool, database_tool],
    middleware=[
        ToolRetryMiddleware(
            max_retries=3,
            backoff_factor=2.0,
            initial_delay=1.0,
        ),
    ],
)
```

### 模型重试 (Model retry)

使用可配置的指数退避自动重试失败的模型调用。模型重试适用于以下情况：

* 处理模型API调用中的瞬态故障
* 提高网络依赖模型请求的可靠性
* 构建优雅处理临时模型错误的弹性agent

**API参考：**`ModelRetryMiddleware`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ModelRetryMiddleware

agent = create_agent(
    model="gpt-4o",
    tools=[search_tool, database_tool],
    middleware=[
        ModelRetryMiddleware(
            max_retries=3,
            backoff_factor=2.0,
            initial_delay=1.0,
        ),
    ],
)
```

### LLM工具模拟器 (LLM tool emulator)

使用LLM模拟工具执行用于测试目的，用AI生成的响应替换实际工具调用。LLM工具模拟器适用于以下情况：

* 不执行真实工具的情况下测试agent行为
* 外部工具不可用或昂贵时开发agent
* 实现实际工具前原型化agent工作流

**API参考：**`LLMToolEmulator`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import LLMToolEmulator

agent = create_agent(
    model="gpt-4o",
    tools=[get_weather, search_database, send_email],
    middleware=[
        LLMToolEmulator(),  # 模拟所有工具
    ],
)
```

### 上下文编辑 (Context editing)

在达到token限制时通过清除旧工具调用输出来管理对话上下文，同时保留近期结果。这有助于在具有许多工具调用的长对话中保持上下文窗口可管理。上下文编辑适用于以下情况：

* 具有许多工具调用且超出token限制的长对话
* 通过移除不再相关的旧工具输出来减少token成本
* 在上下文中只保留最近的N个工具结果

**API参考：**`ContextEditingMiddleware`、`ClearToolUsesEdit`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import ContextEditingMiddleware, ClearToolUsesEdit

agent = create_agent(
    model="gpt-4o",
    tools=[],
    middleware=[
        ContextEditingMiddleware(
            edits=[
                ClearToolUsesEdit(
                    trigger=100000,
                    keep=3,
                ),
            ],
        ),
    ],
)
```

### Shell工具 (Shell tool)

向agent暴露持久shell会话用于命令执行。Shell工具中间件适用于以下情况：

* 需要执行系统命令的agent
* 开发和部署自动化任务
* 测试和验证工作流
* 文件系统操作和脚本执行

**API参考：**`ShellToolMiddleware`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import (
    ShellToolMiddleware,
    HostExecutionPolicy,
)

agent = create_agent(
    model="gpt-4o",
    tools=[search_tool],
    middleware=[
        ShellToolMiddleware(
            workspace_root="/workspace",
            execution_policy=HostExecutionPolicy(),
        ),
    ],
)
```

### 文件搜索 (File search)

提供文件系统文件的Glob和Grep搜索工具。文件搜索中间件适用于以下情况：

* 代码探索和分析
* 按名称模式查找文件
* 使用正则表达式搜索代码内容
* 需要文件发现的大型代码库

**API参考：**`FilesystemFileSearchMiddleware`

```python
from langchain.agents import create_agent
from langchain.agents.middleware import FilesystemFileSearchMiddleware

agent = create_agent(
    model="gpt-4o",
    tools=[],
    middleware=[
        FilesystemFileSearchMiddleware(
            root_path="/workspace",
            use_ripgrep=True,
        ),
    ],
)
```

## 提供者特定中间件

这些中间件针对特定LLM提供者进行了优化。请参阅每个提供者的文档以获取完整详细信息和示例。

### Anthropic

为Claude模型提供提示词缓存、bash工具、文本编辑器、记忆和文件搜索中间件。

### OpenAI

为OpenAI模型提供内容审核中间件。