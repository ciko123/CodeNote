# LangChain 检索器示例集合

本目录包含了11个Python脚本，演示了LangChain中各种检索器的使用方法，从基础的向量检索到高级的重排序技术。

## 文件概览

### 1. 01-base.py - 基础检索器
**功能**: 演示最基础的检索器设置和使用
**技术栈**: Chroma + HuggingFaceEmbeddings
**核心概念**: 
- `as_retriever()` 方法将向量数据库转换为检索器
- 基本的相似性搜索
- 向量数据库的连接和持久化

### 2. 02-multiqueryretriever.py - 多查询检索器
**功能**: 使用LLM生成多个查询来提高检索覆盖率
**技术栈**: MultiQueryRetriever + OpenAI GPT-4o + Chroma
**核心概念**:
- LLM自动生成查询变体
- 提高检索的召回率和准确性
- 日志配置观察查询生成过程

### 3. 03-contextcompressionretriver.py - 上下文压缩检索器
**功能**: 对检索结果进行压缩和过滤，提取最相关内容
**技术栈**: ContextualCompressionRetriever + EmbeddingsFilter + @chain装饰器
**核心概念**:
- 文档压缩和过滤
- 基于相似度阈值的内容筛选
- 自定义检索链的创建

### 4. 04-retriver-score.py - 相似度分数阈值检索器
**功能**: 基于相似度分数阈值控制检索结果质量
**技术栈**: Chroma + similarity_score_threshold
**核心概念**:
- 相似度分数阈值设置
- 质量控制机制
- 搜索类型配置

### 5. 05-ensembleRetriever.py - 集成检索器
**功能**: 组合多个检索器的结果，提高检索性能
**技术栈**: EnsembleRetriever + 多个Chroma检索器
**核心概念**:
- 多检索器结果合并
- 权重分配机制
- 检索结果优化

### 6. 06-ensembleRetriever.py - 混合检索器
**功能**: 结合向量检索和BM25关键词检索
**技术栈**: EnsembleRetriever + FAISS + BM25Retriever + ContextualCompressionRetriever
**核心概念**:
- 向量检索与关键词检索的混合
- LLM链提取器压缩
- 不同检索策略的优势互补

### 7. 07-longcontextReorder.py - 长上下文重排序
**功能**: 优化长上下文处理，将相关文档放在开头和结尾
**技术栈**: LongContextReorder + InMemoryVectorStore + create_stuff_documents_chain
**核心概念**:
- 长上下文优化策略
- 文档重排序算法
- LLM上下文窗口利用优化

### 8. 08-selfretriever.py - 手动元数据过滤检索器
**功能**: 基于文档元数据进行手动过滤
**技术栈**: Chroma + MongoDB风格过滤语法
**核心概念**:
- 元数据过滤语法
- 复合条件查询
- 结构化数据检索

### 9. 09-selfretriever.py - 自查询检索器
**功能**: 使用LLM自动解析查询中的过滤条件
**技术栈**: SelfQueryRetriever + AttributeInfo + OpenAI GPT-4o
**核心概念**:
- 自然语言查询解析
- 自动过滤条件生成
- 元数据字段描述

### 10. 10-rankerRetriever.py - 自定义重排序检索器
**功能**: 自定义实现基于交叉编码器的重排序
**技术栈**: 自定义RerankerRetriever + sentence_transformers.CrossEncoder
**核心概念**:
- 自定义检索器实现
- 交叉编码器重排序
- 查询-文档相关性分数计算

### 11. 11-rankerRetriever.py - 内置重排序检索器
**功能**: 使用LangChain内置的交叉编码器重排序器
**技术栈**: CrossEncoderReranker + HuggingFaceCrossEncoder + ContextualCompressionRetriever
**核心概念**:
- LangChain内置重排序器
- 上下文压缩与重排序结合
- 简化的重排序实现

## 技术栈统一说明

### 嵌入模型
- **模型**: `bge-large-zh-v1.5` (BAAI General Embedding)
- **路径**: `d:/HuggingFace/bge-large-zh-v1.5`
- **用途**: 将中文文本转换为向量表示

### 重排序模型
- **模型**: `bge-reranker-base`
- **路径**: `d:/HuggingFace/bge-reranker-base`
- **用途**: 计算查询-文档相关性分数

### 向量数据库
- **主要**: Chroma (持久化存储)
- **辅助**: FAISS (内存存储)
- **集合名称**: `liudehua`, `laogu`

### LLM模型
- **主要**: OpenAI GPT-4o
- **用途**: 查询生成、解析、内容提取

## 使用建议

### 选择合适的检索器

1. **简单场景**: 使用 `01-base.py` 的基础检索器
2. **提高召回率**: 使用 `02-multiqueryretriever.py` 的多查询检索器
3. **质量控制**: 使用 `03-contextcompressionretriver.py` 或 `04-retriver-score.py`
4. **多数据源**: 使用 `05-ensembleRetriever.py` 或 `06-ensembleRetriever.py`
5. **长文档处理**: 使用 `07-longcontextReorder.py`
6. **结构化查询**: 使用 `08-selfretriever.py` 或 `09-selfretriever.py`
7. **精确排序**: 使用 `10-rankerRetriever.py` 或 `11-rankerRetriever.py`

### 性能优化

1. **向量检索**: 适合语义相似性查询
2. **BM25检索**: 适合关键词匹配查询
3. **混合检索**: 结合两者优势，提高整体性能
4. **重排序**: 提高最相关文档的排名准确性
5. **压缩**: 减少上下文长度，提高LLM处理效率

### 配置参数

- **k值**: 控制返回文档数量 (通常3-10)
- **相似度阈值**: 控制文档质量 (通常0.4-0.8)
- **权重分配**: 集成检索器中的权重比例
- **top_n**: 重排序后保留的文档数量

## 运行要求

1. **环境变量**: 需要配置OpenAI API密钥
2. **模型文件**: 需要下载指定的HuggingFace模型
3. **依赖包**: 安装langchain、chromadb、sentence-transformers等
4. **Python版本**: 建议Python 3.8+

## 学习路径

建议按以下顺序学习：
1. 基础检索器 (01-base.py)
2. 相似度控制 (04-retriver-score.py)
3. 多查询检索 (02-multiqueryretriever.py)
4. 上下文压缩 (03-contextcompressionretriver.py)
5. 集成检索 (05-ensembleRetriever.py, 06-ensembleRetriever.py)
6. 高级技术 (07-longcontextReorder.py, 08-selfretriever.py, 09-selfretriever.py)
7. 重排序技术 (10-rankerRetriever.py, 11-rankerRetriever.py)
