# 导入LangChain社区的文本加载器类
from langchain_community.document_loaders import TextLoader
# 导入LangChain的HuggingFace嵌入模型类
from langchain_huggingface import HuggingFaceEmbeddings
# 导入LangChain的字符文本分割器类
from langchain.text_splitter import CharacterTextSplitter
# 导入LangChain的OpenAI聊天模型类
from langchain_openai import ChatOpenAI
# 导入LangChain的上下文压缩检索器类
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
# 导入LangChain的嵌入过滤器类
from langchain.retrievers.document_compressors.embeddings_filter import EmbeddingsFilter
# 导入LangChain的Chroma向量数据库类
from langchain_chroma import Chroma
# 导入LangChain核心的chain装饰器
from langchain_core.runnables import chain
# 导入类型提示模块：列表类型
from typing import List
# 导入LangChain核心的文档类
from langchain_core.documents import Document
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv
# 从.env文件加载环境变量
load_dotenv()

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
chroma_db = Chroma(
    persist_directory=persist_dir,        # 持久化目录路径
    embedding_function=embeddings,        # 嵌入函数，用于将查询文本转换为向量
    collection_name="liudehua",          # 集合名称，与存储时保持一致
    collection_metadata={"hnsw:space": "cosine"}  # HNSW索引的空间类型
                                                # "l2"：欧氏距离（L2 范数）
                                                # "ip"：点积（Inner Product）
                                                # "cosine"：余弦相似度（默认，无需显式指定）
)

# 注释掉的代码：创建OpenAI聊天模型实例
# llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 注释掉的代码：其他压缩器选项
# chroma_db.similarity_search_with_relevance_scores
# compressor = LLMChainExtractor.from_llm(llm)  # 使用LLM提取相关内容
# compressor = EmbeddingsFilter(embeddings=embeddings, similarity_threshold=0.45)  # 基于嵌入相似度的过滤器

# 注释掉的代码：直接创建上下文压缩检索器
# retriever = ContextualCompressionRetriever(base_compressor=compressor, base_retriever=chroma_db.as_retriever())
# 创建基于相似度分数阈值的检索器
# as_retriever(): 将向量数据库转换为可调用的检索器对象
# search_type: 搜索类型，"similarity_score_threshold"表示基于相似度分数阈值进行搜索
# search_kwargs: 搜索参数，score_threshold设置相似度阈值，只返回相似度高于此阈值的文档
retriever = chroma_db.as_retriever(
    search_type="similarity_score_threshold",   # 搜索类型：相似度分数阈值搜索
    search_kwargs={'score_threshold':0.45}       # 搜索参数：相似度阈值为0.45
)

# 使用检索器进行查询
# invoke(): 执行检索，返回相似度高于阈值的文档
docs = retriever.invoke("刘德华在电影《至尊无上》里是干什么？")

# 遍历并打印检索到的文档内容
for doc in docs:
    print(doc)  # 打印完整的文档对象，包含内容和元数据
    print("=====")