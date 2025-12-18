LangChain 1.0 核心知识体系
	二、基础层：LLM + Prompt
		ChatModels（ChatOpenAI / Groq / Anthropic）
			知识点说明
				ChatModels 是与 LLM 对话的核心接口，统一调用不同厂商大模型（如 OpenAI、Groq、Anthropic）。
				通过参数（model、temperature、max_tokens 等）控制输出风格。
			案例要求
				使用 ChatOpenAI 或 Groq 运行一次简单对话：
					设置 temperature = 0 与 1 对比输出差异
					设置 max_tokens 限制长度
				验证点：能根据不同参数调节模型输出风格

		参数：model / temperature / max_tokens / response_format
			知识点说明
				这些参数用于控制 LLM 的行为，如生成长度、随机性、输出结构化格式等。
			案例要求
				编写一个简单 Prompt：
					分别调整 temperature = 0, 0.7, 1
					设置 response_format = "json_schema"
				验证点：输出 JSON 是否结构化且稳定

		PromptTemplate
			知识点说明
				PromptTemplate 用于创建可复用的提示词模板，实现参数化填充。
			案例要求
				编写一个 PromptTemplate("写一段关于 {topic} 的介绍")：
					输入不同 topic（AI、Python）
				验证点：模板能动态生成 prompt 并传入 LLM

		ChatPromptTemplate
			知识点说明
				ChatPromptTemplate 是专为多轮对话设计的提示词模板体系，支持 system/user/assistant 三角色。
			案例要求
				创建一个 ChatPromptTemplate：
					system：你是一个数学老师
					user：请讲解 {concept}
				验证点：能正确填充变量并按角色生成聊天消息格式

		MessagesPlaceholder
			知识点说明
				用于在提示词模板中保留“历史消息占位”，适配 Memory。
			案例要求
				创建带 MessagesPlaceholder("history") 的 ChatPromptTemplate：
					模拟两轮对话
				验证点：占位符能被 Memory 的历史消息动态填充

		多角色提示词
			知识点说明
				LangChain 支持多个 system 角色、工具角色、或辅助角色实现复杂控制。
			案例要求
				创建包含 system + developer + user 三角色的 Prompt：
				验证点：不同角色信息能正确传递给模型

		Structured Output（结构化输出）
			知识点说明
				通过 OutputParser 或 response_format，让 LLM 输出 JSON、Pydantic 等结构化格式。
			案例要求
				要求模型输出 JSON 格式：
					字段：title、summary
				验证点：输出是否满足 schema 并能被解析

	三、数据层：文档、Embedding、向量库
		Document Loaders（Text / JSON / HTML / Web）
			知识点说明
				Loaders 用于从多类型数据源加载文档，是 RAG 的起点。
			案例要求
				加载本地 txt 和远程网页：
					比较不同 loader 的效果
				验证点：能正常返回 Document[] 结构

		Splitters：RecursiveCharacterTextSplitter
			知识点说明
				文本切片器用于将文档按规则切分成 chunk，保证向量化质量。
			案例要求
				分别使用 chunk_size=200 和 800 对同一文档切片
				验证点：观察切片数量及内容变化

		Embedding（OpenAI / HF）
			知识点说明
				Embedding 将文本转换为向量，是向量检索的基础。
			案例要求
				对同一句话使用两种 Embedding（OpenAI + BGE）进行向量化
				验证点：向量维度和相似度差异明显

		Vector Stores（FAISS / Chroma）
			知识点说明
				向量库用于存储 Embedding 并进行相似度检索。
			案例要求
				创建 Chroma 向量库：
					插入 10 条向量
					执行相似度检索
				验证点：能返回不同 Query 的 Top-K 结果

		Retriever（k / score threshold）
			知识点说明
				Retriever 封装了向量库检索逻辑，通过参数 k、阈值控制检索结果。
			案例要求
				设置 Retriever(k=3) 与 k=10：
					对比检索结果数量与相关性
				验证点：能正确控制结果范围

	四、编排层：LCEL + Runnable（核心）
		Runnable
			知识点说明
				Runnable 是 LangChain 1.0 的核心抽象，所有步骤（prompt、llm、parser）都能用 Runnable 链式拼接。
			案例要求
				实现 prompt → llm 的 Runnable 链
				验证点：链条能顺序执行且可复用

		RunnableMap
			知识点说明
				并行执行多个 Runnable，并将结果组合成一个字典。
			案例要求
				并行执行两个 LLM 调用：
					一个写摘要，一个写标题
				验证点：输出结果包含两个字段

		RunnablePassthrough
			知识点说明
				用于在链中保留原始输入，做多路分发时非常常用。
			案例要求
				构建包含 Passthrough 的链：
					输入 → 复制 → LLM → 合并
				验证点：输入值在链路中不会丢失

		prompt | llm | parser（最重要写法）
			知识点说明
				LangChain 1.0 通过 “|” 操作符创建 LCEL 流水线，是推荐写法。
			案例要求
				构建完整链：
					ChatPromptTemplate | LLM | JSONParser
				验证点：输出 JSON 与链式写法是否正确

		OutputParser（JSON / Pydantic）
			知识点说明
				用于严格解析模型输出，使其强制符合结构化格式。
			案例要求
				使用 PydanticOutputParser：
					解析 title、summary 字段
				验证点：解析失败时能报错提示

		Streaming + Callbacks
			知识点说明
				支持流式输出与调试回调，可实时查看每一步执行情况。
			案例要求
				实现流式输出到控制台
				验证点：每个 token 能实时输出

	五、Memory（对话记忆）
		BufferMemory
			知识点说明
				保存完整对话记录，适合短会话。
			案例要求
				实现两轮对话记忆
				验证点：第二轮能引用第一轮信息

		SummaryMemory
			知识点说明
				将长对话总结成较短摘要，防止 token 爆炸。
			案例要求
				进行 5 轮对话 → 自动生成摘要
				验证点：摘要内容准确且能被引用

		TokenBufferMemory
			知识点说明
				根据 token 数截断记忆，适合受限模型。
			案例要求
				限制 200 token：
					长对话中自动滚动窗口
				验证点：旧内容自动丢弃

		与 LCEL 组合方式（configurable）
			知识点说明
				Memory 可与 LCEL 链结合，通过 config 注入对话历史。
			案例要求
				将 Memory 放入链配置中运行
				验证点：能正常影响 prompt

	六、RAG（核心能力）
		RAG Pipeline（Loader → Splitter → Embedding → VectorStore → Retriever → LLM）
			知识点说明
				RAG 是 LangChain 最核心能力，用检索增强生成。
			案例要求
				实现最小 RAG 管线
				验证点：回答必须引用检索内容

		Reranker（BGE Reranker / CoT Reranker）
			知识点说明
				用于对初级检索结果再排序，提升准确率。
			案例要求
				将检索的 Top-10 用 Reranker 重排取 Top-3
				验证点：结果比原始检索更精准

		高级 RAG：Fusion、Filters
			知识点说明
				Fusion：多路检索融合  
				Filters：基于 metadata 的过滤
			案例要求
				实现 Query Expansion + 多检索融合
				验证点：结果比单路检索更稳定

	七、行动层：Tools + Agents
		@tool 装饰器
			知识点说明
				通过 Python 函数注册成 Agent 工具。
			案例要求
				创建一个 calculator 工具
				验证点：Agent 能调用工具并给出答案

		输入输出结构化
			知识点说明
				定义工具的输入输出 schema，确保 Agent 能正确调用。
			案例要求
				定义工具输入为 {"a": int, "b": int}：
				验证点：错误输入能自动报错

		create_react_agent
			知识点说明
				创建 ReAct 风格 Agent，支持思考→行动→观察循环。
			案例要求
				创建一个能使用搜索工具的 Agent
				验证点：能执行“思考 → 调用工具 → 总结”

		AgentExecutor
			知识点说明
				用于执行 Agent 的主循环，管理工具调用。
			案例要求
				运行一个包含 2 个工具的 Agent
				验证点：多工具协作正常

		ReAct 思想
			知识点说明
				基于“推理 + 行动”模式驱动 Agent 高效解决任务。
			案例要求
				要求模型显式输出思考（Thought）步骤
				验证点：推理链路清晰且合理

	八、LangGraph（可控 Agent）
		状态（State）
			知识点说明
				状态用于在图执行过程中存储信息，是 LangGraph 的最小单元。
			案例要求
				定义一个包含 query 和 history 的 State
				验证点：每个节点都能读写 State

		节点（Node）
			知识点说明
				每个 Node 是执行一个可重复步骤（如检索、思考、执行工具）。
			案例要求
				创建两个节点：
					NodeA：生成搜索词
					NodeB：调用搜索工具
				验证点：节点能按顺序执行

		边（Edge）
			知识点说明
				边负责控制节点的执行顺序，可做条件分支。
			案例要求
				实现条件边（score > 0.8 → NodeC）
				验证点：条件逻辑生效

		多 Agent 协作
			知识点说明
				LangGraph 可让多个专长 Agent 互相调用与协作。
			案例要求
				创建 写作Agent + 校对Agent：
					先写草稿 → 传递给校对
				验证点：State 在多 Agent 间共享成功

		更安全可控的对话与推理
			知识点说明
				通过图结构，让推理步骤可视化、可审核、可拦截，减少幻觉。
			案例要求
				建立一个图：
					LLM → 校验节点 → 继续/中断
				验证点：LLM 输出不合规时能自动中断

	九、应用工程能力
		FastAPI + LCEL Pipeline
			知识点说明
				通过 FastAPI 将 LCEL 流水线发布为可调用接口，形成生产服务。
			案例要求
				用 FastAPI 包装一个 LLM Chain
				验证点：能通过 HTTP 调用

		缓存（Memory / Redis）
			知识点说明
				通过缓存减少重复 embedding、检索或 LLM 调用，降低成本。
			案例要求
				实现 Embedding 缓存
				验证点：第二次相同文本不再调用 Embedding 接口

		Token & Chunk 优化
			知识点说明
				通过减少 chunk 大小、上下文优化降低费用与延迟。
			案例要求
				对 Raw 文档做不同 chunk 大小实验
				验证点：确认最佳 chunk 方案

		LangSmith 调试与 Trace
			知识点说明
				用于可视化调试链路、追踪错误和观察每个步骤。
			案例要求
				开启 LangSmith 日志，执行 RAG
				验证点：能在平台看到每个节点的输入/输出
