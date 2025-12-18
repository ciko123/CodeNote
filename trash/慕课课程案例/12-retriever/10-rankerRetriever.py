# 导入操作系统模块
import os
# 导入类型提示模块：列表类型
from typing import List
# 导入LangChain的Chroma向量数据库类
from langchain_chroma import Chroma
# 导入LangChain的HuggingFace嵌入模型类
from langchain_huggingface import HuggingFaceEmbeddings
# 导入LangChain的OpenAI聊天模型类
from langchain_openai import ChatOpenAI
# 导入sentence_transformers的交叉编码器类
# CrossEncoder: 用于计算查询-文档对的相关性分数，实现重排序功能
from sentence_transformers import CrossEncoder
# 在已有导入内容之后添加：
# 导入LangChain核心的基础检索器类
from langchain_core.retrievers import BaseRetriever
# 导入LangChain核心的文档类
from langchain_core.documents import Document
# 导入Pydantic的Field类，用于数据验证和设置
from pydantic import Field
# 导入类型提示模块：列表类型和可调用类型
from typing import List, Callable

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
# 创建交叉编码器实例
# CrossEncoder: 用于计算查询-文档对的相关性分数，实现重排序功能
reranker_model = CrossEncoder(model_name_or_path=embeddings_path1)

# 自定义重排序检索器类
class RerankerRetriever(BaseRetriever):
    # 基础检索器，用于初始检索
    base_retriever: BaseRetriever = Field(..., description="基础检索器")
    # 重排序函数，用于对检索结果进行重新排序
    reranker_fn: Callable =Field(..., description="reranker模型，排序函数")
    
    # 重写获取相关文档的方法
    def _get_relevant_documents(self, query: str) -> List[Document]:
        # 使用基础检索器进行初始检索
        initial_docs = self.base_retriever.invoke(query)
        # 使用重排序函数对检索结果进行重新排序
        reranked_docs = self.reranker_fn(query, initial_docs)
        return reranked_docs
    
# 定义重排序文档的函数
def rerank_docs(query, docs):
    # 准备查询-文档对
    # 将每个文档的内容与查询组合成对，用于计算相关性分数
    query_doc_pairs = [(query, doc.page_content) for doc in docs]

    # 打印重排序前的文档
    print(f"没有重排序前的文档:")
    for i, (q, content) in enumerate(query_doc_pairs):
        print(f"文档 {i+1} 的内容: {content}")

    # 计算相关性分数
    # predict(): 使用交叉编码器计算查询-文档对的相关性分数
    scores = reranker_model.predict(query_doc_pairs)
    # 将分数与文档关联并排序
    print(f"利用排序模型 计算文档的相关性分数:")
    doc_score_pairs = list(zip(docs, scores))
    for i, (doc, score) in enumerate(doc_score_pairs):
        print(f"文档 {i+1} 的相关性分数: {score}")
        # 将相关性分数添加到文档的元数据中
        doc.metadata["score"] = score
    
    # 打印带有分数的文档
    for doc in docs:
        print(f"文档 {doc.metadata['score']} 的内容: {doc.page_content}")
    
    # 按相关性分数降序排序
    # sorted(): 对文档-分数对进行排序，reverse=True表示降序
    sorted_pairs = sorted(doc_score_pairs, key=lambda x: x[1], reverse=True)
    # 返回排序后的文档
    return [doc for doc, _ in sorted_pairs]


# 创建重排序检索器实例
# RerankerRetriever: 自定义的重排序检索器，结合基础检索器和重排序函数
reranker_retriever = RerankerRetriever(base_retriever=base_retriever, reranker_fn=rerank_docs)

# 定义查询文本
query = "刘德华曾经用过什么名字？"
# 使用重排序检索器进行查询
ranker_docs = reranker_retriever.invoke(query)

# 打印结果
print("问题:", query)
print("\n使用的文档（经过重排序）:")


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