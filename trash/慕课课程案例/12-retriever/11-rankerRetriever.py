# 导入操作系统模块
import os
# 导入类型提示模块：列表类型
from typing import List
# 导入LangChain的Chroma向量数据库类
from langchain_chroma import Chroma
# 导入LangChain的HuggingFace嵌入模型类
from langchain_huggingface import HuggingFaceEmbeddings
# 在已有导入内容之后添加：
# 导入LangChain核心的基础检索器类
from langchain_core.retrievers import BaseRetriever
# 导入LangChain核心的文档类
from langchain_core.documents import Document
# 导入Pydantic的Field类，用于数据验证和设置
from pydantic import Field
# 导入类型提示模块：列表类型和可调用类型
from typing import List, Callable
# 导入LangChain的交叉编码器重排序器类
# CrossEncoderReranker: 使用交叉编码器对检索结果进行重排序的压缩器
from langchain.retrievers.document_compressors import CrossEncoderReranker
# 导入LangChain社区的HuggingFace交叉编码器类
# HuggingFaceCrossEncoder: HuggingFace交叉编码器的LangChain封装
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
# 导入LangChain的上下文压缩检索器类
from langchain.retrievers import ContextualCompressionRetriever


# 定义HuggingFace模型的本地路径
# bge-large-zh-v1.5: BGE（BAAI General Embedding）大型中文嵌入模型
embeddings_path = "d:/HuggingFace/bge-large-zh-v1.5"
# 创建HuggingFace嵌入模型实例
embeddings = HuggingFaceEmbeddings(model_name=embeddings_path)

# 定义Chroma数据库的持久化目录
persist_dir =  "chroma_bge"
# 注释掉的代码：使用from_documents方法创建并持久化Chroma数据库
# Chroma.from_documents(docs, embeddings,collection_name="laogu",persist_directory=persist_dir)
# 创建Chroma向量数据库实例，连接到已存在的数据库
vectorstore = Chroma(
    persist_directory=persist_dir,        # 持久化目录路径
    embedding_function=embeddings,        # 嵌入函数，用于将查询文本转换为向量
    collection_name="liudehua",          # 集合名称，与存储时保持一致
    collection_metadata={"hnsw:space": "cosine"}  # HNSW索引的空间类型
                                                # "l2"：欧氏距离（L2 范数）
                                                # "ip"：点积（Inner Product）
                                                # "cosine"：余弦相似度（默认，无需显式指定）
)

# 创建基础检索器
# as_retriever(): 将向量数据库转换为可调用的检索器对象
# search_kwargs: 搜索参数，k=5表示返回最相似的5个文档
base_retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

# 定义重排序模型的本地路径
# bge-reranker-base: BGE重排序模型，用于计算查询-文档相关性分数
embeddings_path1 = "d:/HuggingFace/bge-reranker-base"
# 创建HuggingFace交叉编码器实例
# HuggingFaceCrossEncoder: LangChain对HuggingFace交叉编码器的封装
# model_name: 交叉编码器模型的路径
cross_encoder_model = HuggingFaceCrossEncoder(model_name=embeddings_path1)

# 创建交叉编码器重排序压缩器
# CrossEncoderReranker: 使用交叉编码器对检索结果进行重排序的压缩器
# model: 交叉编码器模型，用于计算查询-文档相关性分数
# top_n: 重排序后返回的文档数量
reranker_compressor = CrossEncoderReranker(model=cross_encoder_model, top_n=5)

# 创建上下文压缩检索器
# ContextualCompressionRetriever: 包装基础检索器，对检索结果进行压缩和重排序
# base_compressor: 基础压缩器，这里使用交叉编码器重排序器
# base_retriever: 基础检索器，用于执行初始检索
compression_retriever = ContextualCompressionRetriever(
    base_compressor=reranker_compressor,
    base_retriever=base_retriever
)

# 定义查询文本
query = "刘德华曾经用过什么名字？"

# 使用上下文压缩检索器进行查询
# invoke(): 执行压缩检索，先进行基础检索，然后使用交叉编码器重排序
ranker_docs = compression_retriever.invoke(query)

# 输出结果
print(f"查询: {query}")
print("重排序后的结果:")

# 定义美化打印文档的函数
def pretty_print_docs(docs):
    # 将每个文档内容格式化打印，用分隔线分开
    print(
        f"\n{'-' * 100}\n".join(
            [f"文档 {i+1}:" + d.page_content for i, d in enumerate(docs)]
        )
    )

# 调用美化打印函数显示最终结果
pretty_print_docs(ranker_docs)