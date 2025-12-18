# 测试 (Test)

代理应用程序让 LLM 决定自己的下一步来解决问题。这种灵活性很强大，但模型的黑盒性质使得很难预测代理某一部分的调整如何影响其余部分。要构建生产就绪的代理，彻底的测试是必不可少的。

有几种测试代理的方法：

* [单元测试](#unit-testing) 使用内存模拟独立地测试代理的小型、确定性部分，以便您可以快速且确定性地断言确切行为。

* [集成测试](#integration-testing) 使用真实的网络调用来测试代理，以确认组件协同工作、凭据和模式对齐，以及延迟可接受。

代理应用程序往往更依赖集成测试，因为它们将多个组件链接在一起，并且必须处理由于 LLM 的非确定性性质而导致的不稳定性。

## 单元测试 (Unit Testing)

### 模拟聊天模型 (Mocking Chat Model)

对于不需要 API 调用的逻辑，您可以使用内存存根来模拟响应。

LangChain 提供了 [`GenericFakeChatModel`](https://python.langchain.com/api_reference/core/language_models/langchain_core.language_models.fake_chat_models.GenericFakeChatModel.html) 来模拟文本响应。它接受一个响应迭代器（AIMessages 或字符串）并返回每次调用一个。它支持常规和流式使用。

```python  theme={null}
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel

model = GenericFakeChatModel(messages=iter([
    AIMessage(content="", tool_calls=[ToolCall(name="foo", args={"bar": "baz"}, id="call_1")]),
    "bar"
]))

model.invoke("hello")
# AIMessage(content='', ..., tool_calls=[{'name': 'foo', 'args': {'bar': 'baz'}, 'id': 'call_1', 'type': 'tool_call'}])
```

如果我们再次调用模型，它将返回迭代器中的下一个项目：

```python  theme={null}
model.invoke("hello, again!")
# AIMessage(content='bar', ...)
```

### InMemorySaver 检查点 (InMemorySaver Checkpointer)

要在测试期间启用持久化，您可以使用 [`InMemorySaver`](https://reference.langchain.com/python/langgraph/checkpoints/#langgraph.checkpoint.memory.InMemorySaver) 检查点。这允许您模拟多个回合来测试状态依赖行为：

```python  theme={null}
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model,
    tools=[],
    checkpointer=InMemorySaver()
)

# 第一次调用
agent.invoke(HumanMessage(content="我住在澳大利亚悉尼。"))

# 第二次调用：第一条消息被持久化（悉尼位置），所以模型返回 GMT+10 时间
agent.invoke(HumanMessage(content="我的本地时间是什么？"))
```

## 集成测试 (Integration Testing)

许多代理行为只有在使用真实 LLM 时才会出现，例如代理决定调用哪个工具、如何格式化响应，或者提示修改是否影响整个执行轨迹。LangChain 的 [`agentevals`](https://github.com/langchain-ai/agentevals) 包提供了专门设计用于使用实时模型测试代理轨迹的评估器。

AgentEvals 让您通过执行**轨迹匹配**或使用**LLM 评判器**来轻松评估代理的轨迹（消息的确切序列，包括工具调用）：

<Card title="轨迹匹配" icon="equals" arrow="true" href="#trajectory-match-evaluator">
  为给定输入硬编码参考轨迹并通过逐步比较验证运行。

  适用于测试您知道预期行为的明确定义工作流程。当您对应该调用哪些工具以及调用顺序有特定期望时使用。这种方法是确定性的、快速且经济高效的，因为它不需要额外的 LLM 调用。
</Card>

<Card title="LLM 评判器" icon="gavel" arrow="true" href="#llm-as-judge-evaluator">
  使用 LLM 定性验证代理的执行轨迹。“评判器”LLM 根据提示评分标准（可以包括参考轨迹）审查代理的决策。

  更灵活且可以评估效率和适当性等细微方面，但需要 LLM 调用且确定性较低。当您想要评估代理轨迹的整体质量和合理性，而没有严格的工具调用或顺序要求时使用。
</Card>

### 安装 AgentEvals (Installing AgentEvals)

```bash  theme={null}
pip install agentevals
```

或者，直接克隆 [AgentEvals 仓库](https://github.com/langchain-ai/agentevals)。

### 轨迹匹配评估器 (Trajectory Match Evaluator)

AgentEvals 提供 `create_trajectory_match_evaluator` 函数来将您的代理轨迹与参考轨迹进行匹配。有四种模式可供选择：

| 模式        | 描述                                               | 使用场景                                                              |
| ----------- | --------------------------------------------------------- | --------------------------------------------------------------------- |
| `strict`    | 相同顺序中的消息和工具调用的精确匹配  | 测试特定序列（例如，授权前的策略查找） |
| `unordered` | 允许任何顺序中的相同工具调用                      | 当顺序不重要时验证信息检索             |
| `subset`    | 代理只调用参考中的工具（无额外）         | 确保代理不超过预期范围                          |
| `superset`  | 代理至少调用参考工具（允许额外） | 验证执行了最低要求的操作                          |

<Accordion title="严格匹配">
  `strict` 模式确保轨迹包含相同顺序中的相同消息和相同工具调用，尽管它允许消息内容存在差异。当您需要强制执行特定操作序列时，这很有用，例如在授权操作之前要求策略查找。

  ```python  theme={null}
  from langchain.agents import create_agent
  from langchain.tools import tool
  from langchain.messages import HumanMessage, AIMessage, ToolMessage
  from agentevals.trajectory.match import create_trajectory_match_evaluator


  @tool
  def get_weather(city: str):
      """Get weather information for a city."""
      return f"It's 75 degrees and sunny in {city}."

  agent = create_agent("gpt-4o", tools=[get_weather])

  evaluator = create_trajectory_match_evaluator(  # [!code highlight]
      trajectory_match_mode="strict",  # [!code highlight]
  )  # [!code highlight]

  def test_weather_tool_called_strict():
      result = agent.invoke({
          "messages": [HumanMessage(content="What's the weather in San Francisco?")]
      })

      reference_trajectory = [
          HumanMessage(content="What's the weather in San Francisco?"),
          AIMessage(content="", tool_calls=[
              {"id": "call_1", "name": "get_weather", "args": {"city": "San Francisco"}}
          ]),
          ToolMessage(content="It's 75 degrees and sunny in San Francisco.", tool_call_id="call_1"),
          AIMessage(content="The weather in San Francisco is 75 degrees and sunny."),
      ]

      evaluation = evaluator(
          outputs=result["messages"],
          reference_outputs=reference_trajectory
      )
      # {
      #     'key': 'trajectory_strict_match',
      #     'score': True,
      #     'comment': None,
      # }
      assert evaluation["score"] is True
  ```
</Accordion>

<Accordion title="无序匹配">
  `unordered` 模式允许任何顺序中的相同工具调用，当您想要验证特定信息已被检索但不关心顺序时，这很有帮助。例如，代理可能需要检查城市的天气和事件，但顺序无关紧要。

  ```python  theme={null}
  from langchain.agents import create_agent
  from langchain.tools import tool
  from langchain.messages import HumanMessage, AIMessage, ToolMessage
  from agentevals.trajectory.match import create_trajectory_match_evaluator


  @tool
  def get_weather(city: str):
      """Get weather information for a city."""
      return f"It's 75 degrees and sunny in {city}."

  @tool
  def get_events(city: str):
      """Get events happening in a city."""
      return f"Concert at the park in {city} tonight."

  agent = create_agent("gpt-4o", tools=[get_weather, get_events])

  evaluator = create_trajectory_match_evaluator(  # [!code highlight]
      trajectory_match_mode="unordered",  # [!code highlight]
  )  # [!code highlight]

  def test_multiple_tools_any_order():
      result = agent.invoke({
          "messages": [HumanMessage(content="What's happening in SF today?")]
      })

      # Reference shows tools called in different order than actual execution
      reference_trajectory = [
          HumanMessage(content="What's happening in SF today?"),
          AIMessage(content="", tool_calls=[
              {"id": "call_1", "name": "get_events", "args": {"city": "SF"}},
              {"id": "call_2", "name": "get_weather", "args": {"city": "SF"}},
          ]),
          ToolMessage(content="Concert at the park in SF tonight.", tool_call_id="call_1"),
          ToolMessage(content="It's 75 degrees and sunny in SF.", tool_call_id="call_2"),
          AIMessage(content="Today in SF: 75 degrees and sunny with a concert at the park tonight."),
      ]

      evaluation = evaluator(
          outputs=result["messages"],
          reference_outputs=reference_trajectory,
      )
      # {
      #     'key': 'trajectory_unordered_match',
      #     'score': True,
      # }
      assert evaluation["score"] is True
  ```
</Accordion>

<Accordion title="子集和超集匹配">
  `superset` 和 `subset` 模式匹配部分轨迹。`superset` 模式验证代理至少调用了参考轨迹中的工具，允许额外的工具调用。`subset` 模式确保代理没有调用参考中之外的任何工具。

  ```python  theme={null}
  from langchain.agents import create_agent
  from langchain.tools import tool
  from langchain.messages import HumanMessage, AIMessage, ToolMessage
  from agentevals.trajectory.match import create_trajectory_match_evaluator


  @tool
  def get_weather(city: str):
      """Get weather information for a city."""
      return f"It's 75 degrees and sunny in {city}."

  @tool
  def get_detailed_forecast(city: str):
      """Get detailed weather forecast for a city."""
      return f"Detailed forecast for {city}: sunny all week."

  agent = create_agent("gpt-4o", tools=[get_weather, get_detailed_forecast])

  evaluator = create_trajectory_match_evaluator(  # [!code highlight]
      trajectory_match_mode="superset",  # [!code highlight]
  )  # [!code highlight]

  def test_agent_calls_required_tools_plus_extra():
      result = agent.invoke({
          "messages": [HumanMessage(content="What's the weather in Boston?")]
      })

      # Reference only requires get_weather, but agent may call additional tools
      reference_trajectory = [
          HumanMessage(content="What's the weather in Boston?"),
          AIMessage(content="", tool_calls=[
              {"id": "call_1", "name": "get_weather", "args": {"city": "Boston"}},
          ]),
          ToolMessage(content="It's 75 degrees and sunny in Boston.", tool_call_id="call_1"),
          AIMessage(content="The weather in Boston is 75 degrees and sunny."),
      ]

      evaluation = evaluator(
          outputs=result["messages"],
          reference_outputs=reference_trajectory,
      )
      # {
      #     'key': 'trajectory_superset_match',
      #     'score': True,
      #     'comment': None,
      # }
      assert evaluation["score"] is True
  ```
</Accordion>

<Info>
  您还可以设置 `tool_args_match_mode` 属性和/或 `tool_args_match_overrides` 来自定义评估器如何考虑实际轨迹与参考轨迹中工具调用之间的相等性。默认情况下，只有对相同工具具有相同参数的工具调用才被视为相等。访问[仓库](https://github.com/langchain-ai/agentevals?tab=readme-ov-file#tool-args-match-modes)了解更多详细信息。
</Info>

### LLM 评判器评估器 (LLM-as-Judge Evaluator)

您也可以使用 LLM 通过 `create_trajectory_llm_as_judge` 函数评估代理的执行路径。与轨迹匹配评估器不同，它不需要参考轨迹，但如果有的话可以提供一个。

<Accordion title="无参考轨迹">
  ```python  theme={null}
  from langchain.agents import create_agent
  from langchain.tools import tool
  from langchain.messages import HumanMessage, AIMessage, ToolMessage
  from agentevals.trajectory.llm import create_trajectory_llm_as_judge, TRAJECTORY_ACCURACY_PROMPT


  @tool
  def get_weather(city: str):
      """获取城市的天气信息。"""
      return f"{city} 的天气是 75 度，晴朗。"

  agent = create_agent("gpt-4o", tools=[get_weather])

  evaluator = create_trajectory_llm_as_judge(  # [!code highlight]
      model="openai:o3-mini",  # [!code highlight]
      prompt=TRAJECTORY_ACCURACY_PROMPT,  # [!code highlight]
  )  # [!code highlight]

  def test_trajectory_quality():
      result = agent.invoke({
          "messages": [HumanMessage(content="西雅图的天气怎么样？")]
      })

      evaluation = evaluator(
          outputs=result["messages"],
      )
      # {
      #     'key': 'trajectory_accuracy',
      #     'score': True,
      #     'comment': 'The provided agent trajectory is reasonable...'
      # }
      assert evaluation["score"] is True
  ```
</Accordion>

<Accordion title="有参考轨迹">
  如果您有参考轨迹，可以向提示添加一个额外变量并传入参考轨迹。下面，我们使用预构建的 `TRAJECTORY_ACCURACY_PROMPT_WITH_REFERENCE` 提示并配置 `reference_outputs` 变量：

  ```python  theme={null}
  evaluator = create_trajectory_llm_as_judge(
      model="openai:o3-mini",
      prompt=TRAJECTORY_ACCURACY_PROMPT_WITH_REFERENCE,
  )
  evaluation = judge_with_reference(
      outputs=result["messages"],
      reference_outputs=reference_trajectory,
  )
  ```
</Accordion>

<Info>
  有关 LLM 如何评估轨迹的更多可配置性，请访问[仓库](https://github.com/langchain-ai/agentevals?tab=readme-ov-file#trajectory-llm-as-judge)。
</Info>

### 异步支持 (Async Support)

所有 `agentevals` 评估器都支持 Python asyncio。对于使用工厂函数的评估器，通过在函数名中的 `create_` 后添加 `async` 来提供异步版本。

<Accordion title="异步评判器和评估器示例">
  ```python  theme={null}
  from agentevals.trajectory.llm import create_async_trajectory_llm_as_judge, TRAJECTORY_ACCURACY_PROMPT
  from agentevals.trajectory.match import create_async_trajectory_match_evaluator

  async_judge = create_async_trajectory_llm_as_judge(
      model="openai:o3-mini",
      prompt=TRAJECTORY_ACCURACY_PROMPT,
  )

  async_evaluator = create_async_trajectory_match_evaluator(
      trajectory_match_mode="strict",
  )

  async def test_async_evaluation():
      result = await agent.ainvoke({
          "messages": [HumanMessage(content="天气怎么样？")]
      })

      evaluation = await async_judge(outputs=result["messages"])
      assert evaluation["score"] is True
  ```
</Accordion>

## LangSmith 集成 (LangSmith Integration)

为了长期跟踪实验，您可以将评估器结果记录到 [LangSmith](https://smith.langchain.com/)，这是一个构建生产级 LLM 应用程序的平台，包括跟踪、评估和实验工具。

首先，通过设置所需的环境变量来设置 LangSmith：

```bash  theme={null}
export LANGSMITH_API_KEY="your_langsmith_api_key"
export LANGSMITH_TRACING="true"
```

LangSmith 提供两种主要运行评估的方法：[pytest](/langsmith/pytest) 集成和 `evaluate` 函数。

<Accordion title="使用 pytest 集成">
  ```python  theme={null}
  import pytest
  from langsmith import testing as t
  from agentevals.trajectory.llm import create_trajectory_llm_as_judge, TRAJECTORY_ACCURACY_PROMPT

  trajectory_evaluator = create_trajectory_llm_as_judge(
      model="openai:o3-mini",
      prompt=TRAJECTORY_ACCURACY_PROMPT,
  )

  @pytest.mark.langsmith
  def test_trajectory_accuracy():
      result = agent.invoke({
          "messages": [HumanMessage(content="旧金山的天气怎么样？")]
      })

      reference_trajectory = [
          HumanMessage(content="旧金山的天气怎么样？"),
          AIMessage(content="", tool_calls=[
              {"id": "call_1", "name": "get_weather", "args": {"city": "旧金山"}}
          ]),
          ToolMessage(content="旧金山的天气是 75 度，晴朗。", tool_call_id="call_1"),
          AIMessage(content="旧金山的天气是 75 度，晴朗。"),
      ]

      # 将输入、输出和参考输出记录到 LangSmith
      t.log_inputs({})
      t.log_outputs({"messages": result["messages"]})
      t.log_reference_outputs({"messages": reference_trajectory})

      trajectory_evaluator(
          outputs=result["messages"],
          reference_outputs=reference_trajectory
      )
  ```

  使用 pytest 运行评估：

  ```bash  theme={null}
  pytest test_trajectory.py --langsmith-output
  ```

  结果将自动记录到 LangSmith。
</Accordion>

<Accordion title="使用 evaluate 函数">
  或者，您可以在 LangSmith 中创建数据集并使用 `evaluate` 函数：

  ```python  theme={null}
  from langsmith import Client
  from agentevals.trajectory.llm import create_trajectory_llm_as_judge, TRAJECTORY_ACCURACY_PROMPT

  client = Client()

  trajectory_evaluator = create_trajectory_llm_as_judge(
      model="openai:o3-mini",
      prompt=TRAJECTORY_ACCURACY_PROMPT,
  )

  def run_agent(inputs):
      """返回轨迹消息的代理函数。"""
      return agent.invoke(inputs)["messages"]

  experiment_results = client.evaluate(
      run_agent,
      data="your_dataset_name",
      evaluators=[trajectory_evaluator]
  )
  ```

  结果将自动记录到 LangSmith。
</Accordion>

<Tip>
  要了解有关评估代理的更多信息，请参阅 [LangSmith 文档](/langsmith/pytest)。
</Tip>

## 记录和重放 HTTP 调用 (Recording & Replaying HTTP Calls)

调用真实 LLM API 的集成测试可能会缓慢且昂贵，特别是在 CI/CD 管道中频繁运行时。我们建议使用一个库来记录 HTTP 请求和响应，然后在后续运行中重放它们，而不进行实际的网络调用。

您可以使用 [`vcrpy`](https://pypi.org/project/vcrpy/1.5.2/) 来实现这一点。如果您使用 `pytest`，[`pytest-recording` 插件](https://pypi.org/project/pytest-recording/) 提供了一种简单的方法来启用此功能，只需最少的配置。请求/响应被记录在 cassettes 中，然后在后续运行中用于模拟真实的网络调用。

设置您的 `conftest.py` 文件以过滤掉 cassettes 中的敏感信息：

```py conftest.py theme={null}
import pytest

@pytest.fixture(scope="session")
def vcr_config():
    return {
        "filter_headers": [
            ("authorization", "XXXX"),
            ("x-api-key", "XXXX"),
            # ... other headers you want to mask
        ],
        "filter_query_parameters": [
            ("api_key", "XXXX"),
            ("key", "XXXX"),
        ],
    }
```

然后配置您的项目以识别 `vcr` 标记：

<CodeGroup>
  ```ini pytest.ini theme={null}
  [pytest]
  markers =
      vcr: record/replay HTTP via VCR
  addopts = --record-mode=once
  ```

  ```toml pyproject.toml theme={null}
  [tool.pytest.ini_options]
  markers = [
    "vcr: record/replay HTTP via VCR"
  ]
  addopts = "--record-mode=once"
  ```
</CodeGroup>

<Info>
  The `--record-mode=once` option records HTTP interactions on the first run and replays them on subsequent runs.
</Info>

现在，只需用 `vcr` 标记装饰您的测试：

```python  theme={null}
@pytest.mark.vcr()
def test_agent_trajectory():
    # ...
```

第一次运行此测试时，您的代理将进行真实的网络调用，pytest 将在 `tests/cassettes` 目录中生成一个 cassette 文件 `test_agent_trajectory.yaml`。后续运行将使用该 cassette 来模拟真实的网络调用，前提是代理的请求与上次运行相比没有变化。如果有变化，测试将失败，您需要删除 cassette 并重新运行测试以记录新的交互。

<Warning>
  当您修改提示、添加新工具或更改预期轨迹时，您保存的 cassettes 将变得过时，您现有的测试**将会失败**。您应该删除相应的 cassette 文件并重新运行测试以记录新的交互。
</Warning>

***

<Callout icon="pen-to-square" iconType="regular">
  [在 GitHub 上编辑此页面的源代码。](https://github.com/langchain-ai/docs/edit/main/src/oss/langchain/test.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [通过 MCP 以编程方式连接这些文档](/use-these-docs)到 Claude、VSCode 等，以获得实时答案。
</Tip>


---

> 要在此文档中查找导航和其他页面，请在以下位置获取 llms.txt 文件：https://docs.langchain.com/llms.txt