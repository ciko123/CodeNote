---
trigger: always_on
---

# 技术文档精简提示词

## 核心指令

请将以下英文技术文档进行精简处理并翻译成中文，要求：
- **保持所有技术要点不变**
- **移除冗余描述和重复内容**
- **保持代码示例和API签名完整**
- **准确翻译技术术语，保持一致性**
- **符合中文技术文档表达习惯**
- **直接修改原文件，不创建新文件**

## 处理原则

### 1. 保留内容（不可修改，需准确翻译）
- 所有代码示例、配置文件、命令行工具（保持原文）
- API参数、返回值、异常处理（技术术语统一翻译）
- 技术规格、版本要求、依赖关系
- 关键技术术语和概念定义（建立术语对照表）
- 实际的操作步骤

### 2. 精简内容（需要压缩并翻译）
- 冗长的介绍性和背景描述
- 重复的解释和说明
- 营销性语言和过度修饰
- 不必要的过渡句和连接词
- 过于详细的实现原理说明

### 3. 翻译原则
- **LangChain专业术语标准化**（参考下方术语对照表）
- **产品名称保留英文**：LangChain、LangGraph、LangSmith、OpenAI等
- 技术术语保持一致性（如：agent → 代理，middleware → 中间件）
- 代码注释和字符串保持原文
- 符合中文技术文档表达习惯
- 避免直译，使用自然流畅的中文表达
- **始终显示格式**：agent (代理)，middleware (中间件)

## LangChain 专业术语对照表

### 核心概念
- **agent** → 代理
- **chain** → 链
- **prompt** → 提示词
- **template** → 模板
- **tool** → 工具
- **tool call** → 工具调用
- **middleware** → 中间件
- **runtime** → 运行时
- **state** → 状态
- **context** → 上下文

### 数据处理
- **embedding** → 嵌入/向量嵌入
- **vector store** → 向量存储
- **retrieval** → 检索
- **RAG (Retrieval-Augmented Generation)** → 检索增强生成
- **document** → 文档
- **chunk** → 文档块
- **splitter** → 分割器

### 消息与通信
- **message** → 消息
- **HumanMessage** → 人类消息
- **AIMessage** → AI消息
- **ToolMessage** → 工具消息
- **SystemMessage** → 系统消息
- **streaming** → 流式传输

### 执行与控制
- **invoke** → 调用
- **execute** → 执行
- **checkpoint** → 检查点
- **persistence** → 持久化
- **memory** → 记忆
- **store** → 存储

### 高级功能
- **human-in-the-loop (HITL)** → 人在回路
- **guardrails** → 防护机制
- **fallback** → 降级/回退
- **retry** → 重试
- **rate limit** → 频率限制

### 产品与生态
- **LangChain** → LangChain (不翻译)
- **LangGraph** → LangGraph (不翻译)
- **LangSmith** → LangSmith (不翻译)
- **MCP (Model Context Protocol)** → 模型上下文协议

### 注意事项
- 始终使用：`英文术语 (中文翻译)` 格式
- 如果翻译可能引起歧义，可保留英文术语
- API名称、类名、方法名保持原文

### 4. 保持原文结构 (Maintain Original Structure)
- **最小重构**：保持原文档的结构和组织方式，避免添加新的章节或小标题
- **直接翻译**：对简单描述进行直接翻译，不要转换为复杂的中文式结构化内容
- **避免过度组织**：不要添加"核心功能"、"适用场景"、"配置选项"等额外的结构化章节
- **保留原有格式**：如果原文是简单的描述+代码示例，保持这种格式不变

**处理原则**：
- 原文简单的 → 翻译后也简单
- 原文结构化的 → 翻译后保持结构化
- 不要为了"更符合中文习惯"而改变文档组织方式

### 5. HTML标签清理 (HTML Tag Removal)
- **移除文档平台特定标记**：删除所有HTML样式的标签，这些是Mintlify等文档平台的装饰性标记
- **需删除的标签列表**：
  - `<ParamField body="..." type="...">` 和 `</ParamField>`
  - `<Accordion title="...">` 和 `</Accordion>`
  - `<Note>` 和 `</Note>`
  - `<Card>` 和 `</Card>`
  - `<Callout ...>` 和 `</Callout>`
  - `<Tip ...>` 和 `</Tip>`
- **清理图标属性**：删除 `icon="..."` 和 `iconType="..."` 等属性
- **处理孤立片段**：清理标签删除后剩余的 `body="..."`、`type="..."` 等文本片段
- **保留内容**：删除标签包装器，但保留标签内的实际内容和信息

**示例处理**：
```
原始：<Accordion title="Configuration options">配置说明</Accordion>
处理后：配置说明

原始：<ParamField body="model" type="string">模型参数</ParamField>
处理后：模型参数
```

### 5. 重构方式
- 将长段落转换为要点列表
- 合并相似的技术要点
- 使用更简洁的中文表达方式
- 保持逻辑层次清晰

## 输出格式要求

```markdown
# 标题不变

## 核心概念
- 要点1：简洁描述
- 要点2：简洁描述

## 代码示例
[保持原代码不变]

## 使用方法
[步骤化、要点化说明]

## 注意事项
[关键提醒，去除冗余解释]
```

## 示例对比

### 原始文档（英文啰嗦版）
> In modern software development, we frequently encounter the need to process large amounts of data and handle complex business logic. In order to better manage these complexities, developers have designed various tools and frameworks. This article will provide a detailed introduction on how to use our tools to solve these problems, helping you improve development efficiency...

### 精简翻译后（目标版）
> # 数据处理工具
> 
> ## 核心功能
> - 批量数据处理
> - 业务逻辑简化
> - 开发效率提升
> 
> ## 快速开始
> [直接进入使用方法]

## 质量检查标准

处理完成后，请确认：
1. [ ] 所有技术要点都已保留并准确翻译
2. [ ] 代码示例完整无误，保持原文
3. [ ] 技术术语翻译一致
4. [ ] 中文表达自然流畅
5. [ ] 逻辑结构清晰易懂
6. [ ] 没有丢失关键信息
7. [ ] 内容简洁，去除冗余描述
8. [ ] 所有HTML样式标签已清理（ParamField、Accordion、Note、Card、Callout、Tip等）
9. [ ] 图标属性和孤立标签片段已删除
10. [ ] 保持原文档结构，未添加额外的结构化章节
11. [ ] 翻译风格与原文结构匹配（简单→简单，结构化→结构化）

## 特殊指令

- 如果遇到技术性很强的内容，宁可保留多一些文字也不要丢失关键信息
- 保持原文档的技术准确性和专业性
- 建立术语对照表，确保同一术语全文翻译一致
- 代码中的注释和字符串保持原文不翻译
- 使用地道的中文技术文档表达方式

---

*使用方法：将需要精简翻译的英文文档粘贴在此提示词下方，AI将按照上述规则进行处理*
