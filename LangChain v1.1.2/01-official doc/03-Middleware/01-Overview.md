# 概述 (Overview)

在每个步骤控制和定制 agent (代理) 执行

Middleware (中间件) 提供了一种更严格控制 agent 内部行为的方式。Middleware 在以下方面很有用：

- **跟踪 agent 行为**：使用 logging (日志记录)、analytics (分析) 和 debugging (调试)
- **转换数据**：prompts (提示词)、[tool selection](https://docs.langchain.com/oss/python/langchain/middleware/built-in#llm-tool-selector) (工具选择) 和 output formatting (输出格式化)
- **执行控制**：添加 [retries](https://docs.langchain.com/oss/python/langchain/middleware/built-in#tool-retry) (重试)、[fallbacks](https://docs.langchain.com/oss/python/langchain/middleware/built-in#model-fallback) (降级) 和 early termination (早期终止) 逻辑
- **安全防护**：应用 [rate limits](https://docs.langchain.com/oss/python/langchain/middleware/built-in#model-call-limit) (频率限制)、guardrails (防护机制) 和 [PII detection](https://docs.langchain.com/oss/python/langchain/middleware/built-in#pii-detection) (PII 检测)

通过将 middleware 传递给 [`create_agent`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.create_agent) 来添加：

```py
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware, HumanInTheLoopMiddleware

agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[
        SummarizationMiddleware(...),
        HumanInTheLoopMiddleware(...)
    ],
)
```

## Agent 循环 (The agent loop)

核心 agent 循环包括调用模型、让模型选择要执行的工具，然后在不再调用工具时结束：

![Core agent loop diagram](C:\Users\Administrator\Desktop\LangChainDemo\LangChain v1.1\md\03-Middleware\assets\core_agent_loop.png)

Middleware 在每个步骤的前后暴露钩子：

![Middleware flow diagram](C:\Users\Administrator\Desktop\LangChainDemo\LangChain v1.1\md\03-Middleware\assets\middleware_final.png)

## 附加资源 (Additional resources)

## 内置 Middleware (Built-in middleware)

浏览常见用例的内置 middleware。

## 自定义 Middleware (Custom middleware)

使用钩子和装饰器构建您自己的 middleware。

## Middleware API 参考 (Middleware API reference)

完整的 middleware API 参考。

## 测试 Agent (Testing agents)

使用 LangSmith 测试您的 agent.
