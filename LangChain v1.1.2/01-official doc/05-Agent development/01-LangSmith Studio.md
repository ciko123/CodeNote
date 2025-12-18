# LangSmith Studio

当使用 LangChain 在本地构建代理时，可视化代理内部发生的情况、实时与之交互以及调试问题是非常有帮助的。**LangSmith Studio** 是一个免费的视觉界面，用于从本地机器开发和测试您的 LangChain 代理。

Studio 连接到您本地运行的代理，向您显示代理采取的每个步骤：发送到模型的提示、工具调用及其结果，以及最终输出。您可以测试不同的输入、检查中间状态，并迭代代理的行为，而无需额外的代码或部署。

本页面描述如何使用本地 LangChain 代理设置 Studio。

## 先决条件 (Prerequisites)

在开始之前，请确保您具备以下条件：

* **一个 LangSmith 账户**：在 [smith.langchain.com](https://smith.langchain.com) 注册（免费）或登录。
* **一个 LangSmith API 密钥**：按照 [创建 API 密钥](/langsmith/create-account-api-key#create-an-api-key) 指南操作。
* 如果您不希望数据被[追踪](/langsmith/observability-concepts#traces)到 LangSmith，请在应用程序的 `.env` 文件中设置 `LANGSMITH_TRACING=false`。禁用追踪后，不会有数据离开您的本地服务器。

## 设置本地代理服务器 (Set up local Agent server)

### 1. 安装 LangGraph CLI (Install the LangGraph CLI)

[LangGraph CLI](/langsmith/cli) 提供了一个本地开发服务器（也称为[代理服务器](/langsmith/agent-server)），将您的代理连接到 Studio。

```shell  theme={null}
# 需要 Python >= 3.11。
pip install --upgrade "langgraph-cli[inmem]"
```

### 2. 准备您的代理 (Prepare your agent)

如果您已经有 LangChain 代理，可以直接使用。本示例使用一个简单的邮件代理：

```python title="agent.py" theme={null}
from langchain.agents import create_agent

def send_email(to: str, subject: str, body: str):
    """发送邮件"""
    email = {
        "to": to,
        "subject": subject,
        "body": body
    }
    # ... 邮件发送逻辑

    return f"邮件已发送至 {to}"

agent = create_agent(
    "gpt-4o",
    tools=[send_email],
    system_prompt="您是一个邮件助手。始终使用 send_email 工具。",
)
```

### 3. 环境变量 (Environment variables)

Studio 需要 LangSmith API 密钥来连接您的本地代理。在项目根目录中创建一个 `.env` 文件，并添加您从 [LangSmith](https://smith.langchain.com/settings) 获取的 API 密钥。

<Warning>
  确保您的 `.env` 文件不被提交到版本控制系统（如 Git）。
</Warning>

```bash .env theme={null}
LANGSMITH_API_KEY=lsv2...
```

### 4. 创建 LangGraph 配置文件 (Create a LangGraph config file)

LangGraph CLI 使用配置文件来定位您的代理并管理依赖项。在您的应用程序目录中创建一个 `langgraph.json` 文件：

```json title="langgraph.json" theme={null}
{
  "dependencies": ["."],
  "graphs": {
    "agent": "./src/agent.py:agent"
  },
  "env": ".env"
}
```

[`create_agent`](https://reference.langchain.com/python/langchain/agents/#langchain.agents.create_agent) 函数自动返回一个编译的 LangGraph 图，这就是配置文件中 `graphs` 键所期望的内容。

<Info>
  有关配置文件 JSON 对象中每个键的详细说明，请参阅 [LangGraph 配置文件参考](/langsmith/cli#configuration-file)。
</Info>

此时，项目结构将如下所示：

```bash  theme={null}
my-app/
├── src
│   └── agent.py
├── .env
└── langgraph.json
```

### 5. 安装依赖项 (Install dependencies)

从根目录安装您的项目依赖项：

<CodeGroup>
  ```shell pip theme={null}
  pip install -e .
  ```

  ```shell uv theme={null}
  uv sync
  ```
</CodeGroup>

### 6. 在 Studio 中查看您的代理 (View your agent in Studio)

启动开发服务器以将您的代理连接到 Studio：

```shell  theme={null}
langgraph dev
```

<Warning>
  Safari 阻止对 Studio 的 `localhost` 连接。要解决此问题，请使用 `--tunnel` 运行上述命令，通过安全隧道访问 Studio。
</Warning>

一旦服务器运行，您的代理既可以通过 API 在 `http://127.0.0.1:2024` 访问，也可以通过 Studio UI 在 `https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024` 访问：

<Frame>
    <img src="https://mintcdn.com/langchain-5e9cc07a/TCDks4pdsHdxWmuJ/oss/images/studio_create-agent.png?fit=max&auto=format&n=TCDks4pdsHdxWmuJ&q=85&s=ebd259e9fa24af7d011dfcc568f74be2" alt="Agent view in the Studio UI" data-og-width="2836" width="2836" data-og-height="1752" height="1752" data-path="oss/images/studio_create-agent.png" data-optimize="true" data-opv="3" srcset="https://mintcdn.com/langchain-5e9cc07a/TCDks4pdsHdxWmuJ/oss/images/studio_create-agent.png?w=280&fit=max&auto=format&n=TCDks4pdsHdxWmuJ&q=85&s=cf9c05bdd08661d4d546c540c7a28cbe 280w, https://mintcdn.com/langchain-5e9cc07a/TCDks4pdsHdxWmuJ/oss/images/studio_create-agent.png?w=560&fit=max&auto=format&n=TCDks4pdsHdxWmuJ&q=85&s=484b2fd56957d048bd89280ce97065a0 560w, https://mintcdn.com/langchain-5e9cc07a/TCDks4pdsHdxWmuJ/oss/images/studio_create-agent.png?w=840&fit=max&auto=format&n=TCDks4pdsHdxWmuJ&q=85&s=92991302ac24604022ab82ac22729f68 840w, https://mintcdn.com/langchain-5e9cc07a/TCDks4pdsHdxWmuJ/oss/images/studio_create-agent.png?w=1100&fit=max&auto=format&n=TCDks4pdsHdxWmuJ&q=85&s=ed366abe8dabc42a9d7c300a591e1614 1100w, https://mintcdn.com/langchain-5e9cc07a/TCDks4pdsHdxWmuJ/oss/images/studio_create-agent.png?w=1650&fit=max&auto=format&n=TCDks4pdsHdxWmuJ&q=85&s=d5865d3c4b0d26e9d72e50d474547a63 1650w, https://mintcdn.com/langchain-5e9cc07a/TCDks4pdsHdxWmuJ/oss/images/studio_create-agent.png?w=2500&fit=max&auto=format&n=TCDks4pdsHdxWmuJ&q=85&s=6b254add2df9cc3c10ac0c2bcb3a589c 2500w" />
</Frame>

与 Studio 连接后，您可以快速迭代代理的行为。运行测试输入，检查完整的执行跟踪，包括提示、工具参数、返回值和令牌/延迟指标。当出现问题时，Studio 捕获异常并显示周围状态，以帮助您了解发生了什么。

开发服务器支持热重载——在代码中对提示或工具签名进行更改，Studio 会立即反映这些更改。从任何步骤重新运行对话线程来测试您的更改，而无需从头开始。此工作流程从简单的单工具代理扩展到复杂的多节点图。

有关如何运行 Studio 的更多信息，请参阅 [LangSmith 文档](/langsmith/home)中的以下指南：

* [运行应用程序](/langsmith/use-studio#run-application)
* [管理助手](/langsmith/use-studio#manage-assistants)
* [管理线程](/langsmith/use-studio#manage-threads)
* [迭代提示](/langsmith/observability-studio)
* [调试 LangSmith 跟踪](/langsmith/observability-studio#debug-langsmith-traces)
* [将节点添加到数据集](/langsmith/observability-studio#add-node-to-dataset)

## 视频指南 (Video guide)

<Frame>
  <iframe className="w-full aspect-video rounded-xl" src="https://www.youtube.com/embed/Mi1gSlHwZLM?si=zA47TNuTC5aH0ahd" title="Studio" frameBorder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen />
</Frame>

<Tip>
  有关本地和部署代理的更多信息，请参阅[设置本地代理服务器](/oss/python/langchain/studio#setup-local-agent-server)和[部署](/oss/python/langchain/deploy)。
</Tip>

***

<Callout icon="pen-to-square" iconType="regular">
  [在 GitHub 上编辑此页面的源代码。](https://github.com/langchain-ai/docs/edit/main/src/oss/langchain/studio.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [通过 MCP 以编程方式连接这些文档](/use-these-docs)到 Claude、VSCode 等，以获得实时答案。
</Tip>


---

> 要在此文档中查找导航和其他页面，请在以下位置获取 llms.txt 文件：https://docs.langchain.com/llms.txt