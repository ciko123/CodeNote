# 代理聊天界面 (Agent Chat UI)

[代理聊天界面](https://github.com/langchain-ai/agent-chat-ui) 是一个 Next.js 应用程序，为与任何 LangChain 代理交互提供对话界面。它支持实时聊天、工具可视化以及时间旅行调试和状态分叉等高级功能。代理聊天界面与使用 [`create_agent`](../langchain/agents) 创建的代理无缝协作，为您的代理提供交互式体验，只需最少的设置，无论您是在本地运行还是在部署环境中（例如 [LangSmith](/langsmith/home)）。

代理聊天界面是开源的，可以根据您的应用程序需求进行调整。

<Frame>
  <iframe className="w-full aspect-video rounded-xl" src="https://www.youtube.com/embed/lInrwVnZ83o?si=Uw66mPtCERJm0EjU" title="Agent Chat UI" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen />
</Frame>

<Tip>
  您可以在代理聊天界面中使用生成式 UI。有关更多信息，请参见 [使用 LangGraph 实现生成式用户界面](/langsmith/generative-ui-react)。
</Tip>

### 快速开始 (Quick start)

开始的最快方法是使用托管版本：

1. **访问 [代理聊天界面](https://agentchat.vercel.app)**
2. **连接您的代理**，输入您的部署 URL 或本地服务器地址
3. **开始聊天** - UI 将自动检测并渲染工具调用和中断

### 本地开发 (Local development)

对于自定义或本地开发，您可以在本地运行代理聊天界面：

<CodeGroup>
  ```bash 使用 npx theme={null}
  # 创建新的代理聊天界面项目
  npx create-agent-chat-app --project-name my-chat-ui
  cd my-chat-ui

  # 安装依赖并启动
  pnpm install
  pnpm dev
  ```

  ```bash 克隆仓库 theme={null}
  # 克隆仓库
  git clone https://github.com/langchain-ai/agent-chat-ui.git
  cd agent-chat-ui

  # 安装依赖并启动
  pnpm install
  pnpm dev
  ```
</CodeGroup>

### 连接到您的代理 (Connect to your agent)

代理聊天界面可以连接到[本地代理](/oss/python/langchain/studio#setup-local-agent-server)和[部署的代理](/oss/python/langchain/deploy)。

启动代理聊天界面后，您需要配置它以连接到您的代理：

1. **Graph ID**：输入您的图名称（在您的 `langgraph.json` 文件中的 `graphs` 下找到）
2. **Deployment URL**：您的代理服务器端点（例如，本地开发使用 `http://localhost:2024`，或您部署的代理的 URL）
3. **LangSmith API 密钥（可选）**：添加您的 LangSmith API 密钥（如果您使用本地代理服务器则不需要）

配置完成后，代理聊天界面将自动获取并显示来自您的代理的任何中断线程。

<Tip>
  代理聊天界面具有开箱即用的工具调用和工具结果消息渲染支持。要自定义显示的消息，请参见 [在聊天中隐藏消息](https://github.com/langchain-ai/agent-chat-ui?tab=readme-ov-file#hiding-messages-in-the-chat)。
</Tip>

***

<Callout icon="pen-to-square" iconType="regular">
  [在 GitHub 上编辑此页面的源代码。](https://github.com/langchain-ai/docs/edit/main/src/oss/langchain/ui.mdx)
</Callout>

<Tip icon="terminal" iconType="regular">
  [通过 MCP 以编程方式连接这些文档](/use-these-docs)到 Claude、VSCode 等，以获得实时答案。
</Tip>


---

> 要在此文档中查找导航和其他页面，请在以下位置获取 llms.txt 文件：https://docs.langchain.com/llms.txt