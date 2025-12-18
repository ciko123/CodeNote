# 防护机制 (Guardrails)

> 为您的agent (代理)实现安全检查和内容过滤

防护机制通过在agent执行的关键点验证和过滤内容，帮助您构建安全、合规的AI应用程序。它们可以检测敏感信息、执行内容策略、验证输出，并在问题发生前阻止不安全行为。

常见用例包括：

* 防止PII (个人身份信息) 泄露
* 检测和阻止提示词注入攻击
* 阻止不当或有害内容
* 执行业务规则和合规要求
* 验证输出质量和准确性
* 执行数据保护和隐私合规

您可以使用[中间件 (middleware)](/oss/python/langchain/middleware)来实现防护机制，在战略点拦截执行 - 在agent启动前、完成后，或围绕模型和工具调用。

  防护机制可以使用两种互补的方法来实现：
使用基于规则的逻辑，如正则表达式模式、关键词匹配或显式检查。快速、可预测且成本效益高，但可能错过细微的违规行为。
使用LLM (大型语言模型) 或分类器通过语义理解来评估内容。捕获规则遗漏的细微问题，但速度较慢且成本更高。

LangChain提供内置防护机制（例如[PII检测](#pii-detection)、[人在回路 (human-in-the-loop)](#human-in-the-loop)）和灵活的中间件系统，用于使用任一方法构建自定义防护机制。

## 内置防护机制

### PII检测 (PII detection)

LangChain提供内置中间件用于检测和处理个人身份信息 (PII)。此中间件可以检测常见的PII类型，如电子邮件、信用卡号码、IP地址等。

PII检测中间件适用于具有合规要求的医疗和金融应用程序、需要清理日志的客户服务代理，以及任何处理敏感用户数据的应用程序。

PII中间件支持多种处理检测到的PII的策略：

| 策略 | 描述 | 示例 |
| -------- | --------------------------------------- | --------------------- |
| `redact` | 替换为`[REDACTED_TYPE]` | `[REDACTED_EMAIL]` |
| `mask` | 部分遮蔽（例如最后4位数字） | `****-****-****-1234` |
| `hash` | 替换为确定性哈希 | `a8f5f167...` |
| `block` | 检测到时抛出异常 | 抛出错误 |

```python
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware


agent = create_agent(
    model="gpt-4o",
    tools=[customer_service_tool, email_tool],
    middleware=[
        # 在发送到模型之前编辑用户输入中的电子邮件
        PIIMiddleware(
            "email",
            strategy="redact",
            apply_to_input=True,
        ),
        # 遮蔽用户输入中的信用卡
        PIIMiddleware(
            "credit_card",
            strategy="mask",
            apply_to_input=True,
        ),
        # 阻止API密钥 - 如果检测到则抛出错误
        PIIMiddleware(
            "api_key",
            detector=r"sk-[a-zA-Z0-9]{32}",
            strategy="block",
            apply_to_input=True,
        ),
    ],
)

# 当用户提供PII时，将根据策略进行处理
result = agent.invoke({
    "messages": [{"role": "user", "content": "My email is john.doe@example.com and card is 5105-1051-0510-5100"}]
})
```


  **内置PII类型：**

  * `email` - 电子邮件地址
  * `credit_card` - 信用卡号码（Luhn验证）
  * `ip` - IP地址
  * `mac_address` - MAC地址
  * `url` - URL

  **配置选项：**

  | 参数 | 描述 | 默认值 |
  | ----------------------- | ---------------------------------------------------------------------- | ---------------------- |
  | `pii_type` | 要检测的PII类型（内置或自定义） | 必需 |
  | `strategy` | 如何处理检测到的PII (`"block"`, `"redact"`, `"mask"`, `"hash"`) | `"redact"` |
  | `detector` | 自定义检测器函数或正则表达式模式 | `None`（使用内置） |
  | `apply_to_input` | 在模型调用前检查用户消息 | `True` |
  | `apply_to_tool_results` | 在执行后检查工具结果消息 | `False` |

请参阅[中间件文档](/oss/python/langchain/middleware#pii-detection)以了解PII检测功能的完整详情。

### 人在回路 (Human-in-the-loop)

LangChain提供内置中间件，用于在执行敏感操作之前要求人工批准。这是高风险决策最有效的防护机制之一。

人在回路中间件适用于金融交易和转账、删除或修改生产数据、向外部发送通信以及任何具有重大业务影响的操作。

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command


agent = create_agent(
    model="gpt-4o",
    tools=[search_tool, send_email_tool, delete_database_tool],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                # 需要敏感操作的批准
                "send_email": True,
                "delete_database": True,
                # 自动批准安全操作
                "search": False,
            }
        ),
    ],
    # 在中断之间保持状态
    checkpointer=InMemorySaver(),
)

# 人在回路需要线程ID进行持久化
config = {"configurable": {"thread_id": "some_id"}}

# Agent将在执行敏感工具之前暂停并等待批准
result = agent.invoke(
    {"messages": [{"role": "user", "content": "Send an email to the team"}]},
    config=config
)

result = agent.invoke(
    Command(resume={"decisions": [{"type": "approve"}]}),
    config=config  # 相同的线程ID以恢复暂停的对话
)
```

## 自定义防护机制 (Custom guardrails)

对于更复杂的防护机制，您可以创建在agent执行之前或之后运行的自定义中间件。这使您完全控制验证逻辑、内容过滤和安全检查。

### Agent前防护机制 (Before agent guardrails)

使用"agent前"钩子在每次调用开始时验证请求一次。这对于会话级检查（如身份验证、频率限制或在任何处理开始之前阻止不当请求）很有用。

  ```python
  from typing import Any

  from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
  from langgraph.runtime import Runtime

  class ContentFilterMiddleware(AgentMiddleware):
      """Deterministic guardrail: Block requests containing banned keywords."""

      def __init__(self, banned_keywords: list[str]):
          super().__init__()
          self.banned_keywords = [kw.lower() for kw in banned_keywords]

      @hook_config(can_jump_to=["end"])
      def before_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
          # 获取第一条用户消息
          if not state["messages"]:
              return None

          first_message = state["messages"][0]
          if first_message.type != "human":
              return None

          content = first_message.content.lower()

          # 检查被禁止的关键词
          for keyword in self.banned_keywords:
              if keyword in content:
                  # 在任何处理之前阻止执行
                  return {
                      "messages": [{
                          "role": "assistant",
                          "content": "I cannot process requests containing inappropriate content. Please rephrase your request."
                      }],
                      "jump_to": "end"
                  }

          return None

  # 使用自定义防护机制
  from langchain.agents import create_agent

  agent = create_agent(
      model="gpt-4o",
      tools=[search_tool, calculator_tool],
      middleware=[
          ContentFilterMiddleware(
              banned_keywords=["hack", "exploit", "malware"]
          ),
      ],
  )

  # 此请求将在任何处理之前被阻止
  result = agent.invoke({
      "messages": [{"role": "user", "content": "How do I hack into a database?"}]
  })
  ```

  ```python
  from typing import Any

  from langchain.agents.middleware import before_agent, AgentState, hook_config
  from langgraph.runtime import Runtime

  banned_keywords = ["hack", "exploit", "malware"]

  @before_agent(can_jump_to=["end"])
  def content_filter(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
      """确定性防护机制：阻止包含被禁止关键词的请求。"""
      # 获取第一条用户消息
      if not state["messages"]:
          return None

      first_message = state["messages"][0]
      if first_message.type != "human":
          return None

      content = first_message.content.lower()

      # 检查被禁止的关键词
      for keyword in banned_keywords:
          if keyword in content:
              # 在任何处理之前阻止执行
              return {
                  "messages": [{
                      "role": "assistant",
                      "content": "I cannot process requests containing inappropriate content. Please rephrase your request."
                  }],
                  "jump_to": "end"
              }

      return None

  # 使用自定义防护机制
  from langchain.agents import create_agent

  agent = create_agent(
      model="gpt-4o",
      tools=[search_tool, calculator_tool],
      middleware=[content_filter],
  )

  # 此请求将在任何处理之前被阻止
  result = agent.invoke({
      "messages": [{"role": "user", "content": "How do I hack into a database?"}]
  })
  ```
### Agent后防护机制 (After agent guardrails)

使用"agent后"钩子在返回给用户之前验证最终输出一次。这对于基于模型的安全检查、质量验证或对完整agent响应的最终合规扫描很有用。

  ```python
  from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
  from langgraph.runtime import Runtime
  from langchain.messages import AIMessage
  from langchain.chat_models import init_chat_model
  from typing import Any

  class SafetyGuardrailMiddleware(AgentMiddleware):
      """基于模型的防护机制：使用LLM评估响应安全性。"""

      def __init__(self):
          super().__init__()
          self.safety_model = init_chat_model("gpt-4o-mini")

      @hook_config(can_jump_to=["end"])
      def after_agent(self, state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
          # 获取最终的AI响应
          if not state["messages"]:
              return None

          last_message = state["messages"][-1]
          if not isinstance(last_message, AIMessage):
              return None

          # 使用模型评估安全性
          safety_prompt = f"""评估此响应是否安全且适当。
          仅回复'SAFE'或'UNSAFE'。

          响应：{last_message.content}"""

          result = self.safety_model.invoke([{"role": "user", "content": safety_prompt}])

          if "UNSAFE" in result.content:
              last_message.content = "I cannot provide that response. Please rephrase your request."

          return None

  # 使用安全防护机制
  from langchain.agents import create_agent

  agent = create_agent(
      model="gpt-4o",
      tools=[search_tool, calculator_tool],
      middleware=[SafetyGuardrailMiddleware()],
  )

  result = agent.invoke({
      "messages": [{"role": "user", "content": "How do I make explosives?"}]
  })
  ```

  ```python
  from langchain.agents.middleware import after_agent, AgentState, hook_config
  from langgraph.runtime import Runtime
  from langchain.messages import AIMessage
  from langchain.chat_models import init_chat_model
  from typing import Any

  safety_model = init_chat_model("gpt-4o-mini")

  @after_agent(can_jump_to=["end"])
  def safety_guardrail(state: AgentState, runtime: Runtime) -> dict[str, Any] | None:
      """基于模型的防护机制：使用LLM评估响应安全性。"""
      # 获取最终的AI响应
      if not state["messages"]:
          return None

      last_message = state["messages"][-1]
      if not isinstance(last_message, AIMessage):
          return None

      # 使用模型评估安全性
      safety_prompt = f"""评估此响应是否安全且适当。
      仅回复'SAFE'或'UNSAFE'。

      响应：{last_message.content}"""

      result = safety_model.invoke([{"role": "user", "content": safety_prompt}])

      if "UNSAFE" in result.content:
          last_message.content = "I cannot provide that response. Please rephrase your request."

      return None

  # 使用安全防护机制
  from langchain.agents import create_agent

  agent = create_agent(
      model="gpt-4o",
      tools=[search_tool, calculator_tool],
      middleware=[safety_guardrail],
  )

  result = agent.invoke({
      "messages": [{"role": "user", "content": "How do I make explosives?"}]
  })
  ```

### 组合多个防护机制 (Combine multiple guardrails)

您可以通过将多个防护机制添加到中间件数组中来堆叠它们。它们按顺序执行，允许您构建分层保护：

```python
from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware, HumanInTheLoopMiddleware

agent = create_agent(
    model="gpt-4o",
    tools=[search_tool, send_email_tool],
    middleware=[
        # 第1层：确定性输入过滤器（agent前）
        ContentFilterMiddleware(banned_keywords=["hack", "exploit"]),

        # 第2层：PII保护（模型前后）
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        PIIMiddleware("email", strategy="redact", apply_to_output=True),

        # 第3层：敏感工具的人工批准
        HumanInTheLoopMiddleware(interrupt_on={"send_email": True}),

        # 第4层：基于模型的安全检查（agent后）
        SafetyGuardrailMiddleware(),
    ],
)
```

## 其他资源 (Additional resources)

* [中间件文档](/oss/python/langchain/middleware) - 自定义中间件的完整指南
* [中间件API参考](https://reference.langchain.com/python/langchain/middleware/) - 自定义中间件的完整指南
* [人在回路](/oss/python/langchain/human-in-the-loop) - 为敏感操作添加人工审查
* [测试代理](/oss/python/langchain/test) - 测试安全机制的策


---

> To find navigation and other pages in this documentation, fetch the llms.txt file at: https://docs.langchain.com/llms.txt