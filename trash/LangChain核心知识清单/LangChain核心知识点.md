# LangChain 1.0 核心知识体系

## 基础层：LLM 调用与 Prompt 管理

### LLM 调用
- **ChatOpenAI**
- **ChatAnthropic / ChatGroq**（可选）
- **核心参数**
  - model
  - temperature
  - max_tokens
  - response_format（结构化输出）
  - async/await（异步）

### Prompt 系统
- **PromptTemplate**
- **ChatPromptTemplate**
- **MessagesPlaceholder**
- **模板变量、系统提示词、多角色提示词**

## 数据层：文档、Embedding、向量数据库（RAG 基础）

### Document 加载
- **TextLoader**
- **JSONLoader**
- **WebBaseLoader**
- **自定义 Loader**

### Text Splitter
- **RecursiveCharacterTextSplitter**（唯一需要掌握）
- **核心参数**
  - chunk_size
  - chunk_overlap

### Embedding
- **OpenAIEmbeddings**
- **HuggingFaceEmbeddings**（可选）

### Vector Store（向量数据库）
- **FAISS**（本地常用）
- **Chroma**（轻量持久化）
- **Milvus / Weaviate**（云端可选）

### Retriever（检索器）
- **VectorStoreRetriever**
- **设置 k / score_threshold**
- **放入 RAG pipeline**

## 编排层（LangChain 1.0 核心）：LCEL + Runnable

### Runnable（统一抽象）
- **RunnableMap**
- **RunnablePassthrough**
- **RunnableLambda**

### 常见 LCEL 管道写法
- **prompt | llm | parser**

### Output Parser
- **StrOutputParser**
- **JsonOutputParser**
- **PydanticOutputParser**（可选）
- **结构化输出**

## RAG（Retrieval-Augmented Generation）

### 基础 RAG（必须掌握）
- **文档加载 → 文档切分 → 向量化 → 向量库 → 检索 → Prompt → LLM**

### 关键组件
- **Loader**
- **Splitter**
- **Embedding**
- **VectorStore**
- **Retriever**
- **PromptTemplate**
- **ChatModel**
- **LCEL Chain**

### 高级 RAG
- **Reranker**（重排序）
- **Multi-Vector Retriever**（多向量检索）
- **Metadata Filter**（过滤）
- **RAG Fusion**（多策略融合）

## 行动层：Tools + Agents

### Tools（工具）
- **@tool 装饰器**
- **工具函数输入 / 输出结构化**

### Agent
- **AgentExecutor**
- **create_react_agent**（最常用）
- **ReAct 思想：Reasoning → Action → Observation**

### 多工具协作
- **工具列表注册**
- **工具错误处理**
- **Agent 调用外部 API**

## 应用层：构建完整 Pipeline（工程能力）

### 最小可运行应用（MVP）
- **用户输入 → 检索 → LLM 回答**

### 项目中需要掌握
- **配置管理**（.env）
- **缓存**（memory / redis / local）
- **FastAPI 集成**
- **异步 pipeline**
- **LangSmith 调试**
- **Chunk + Token 优化策略**

## 代码模板体系（强烈建议自己整理）

- **最小 LLM 调用模板**
- **PromptTemplate 模板**
- **Loader + Splitter 模板**
- **FAISS/Chroma 构建模板**
- **最小 RAG（十行）模板**
- **Agent + Tool 模板**
- **LCEL Pipeline 模板**

## 常用 API 文档板块（必看）

- **Models**
- **Prompts**
- **Document Loaders**
- **Text Splitters**
- **Vector Stores**
- **Retrievers**
- **Chains**（LCEL）
- **Agents & Tools**
- **LangGraph**（可选）