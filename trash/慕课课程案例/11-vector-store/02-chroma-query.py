# 导入LangChain的HuggingFace嵌入模型类
from langchain_huggingface import HuggingFaceEmbeddings
# 导入LangChain的Chroma向量数据库类
from langchain_chroma import Chroma

# 定义HuggingFace模型的本地路径
# bge-large-zh-v1.5: BGE（BAAI General Embedding）大型中文嵌入模型
embeddings_path = "d:/HuggingFace/bge-large-zh-v1.5"
# 创建HuggingFace嵌入模型实例
embeddings = HuggingFaceEmbeddings(model_name=embeddings_path)

# 定义Chroma数据库的持久化目录
persist_dir =  "chroma_bge"

# 创建Chroma向量数据库实例，连接到已存在的数据库
chroma_db = Chroma(
    persist_directory=persist_dir,        # 持久化目录路径
    embedding_function=embeddings,        # 嵌入函数，用于将查询文本转换为向量
    collection_name="laogu",             # 集合名称，与存储时保持一致
    collection_metadata={"hnsw:space": "cosine"}  # HNSW索引的空间类型
                                                # "l2"：欧氏距离（L2 范数）
                                                # "ip"：点积（Inner Product）
                                                # "cosine"：余弦相似度（默认，无需显式指定）
)

# 定义查询文本
query = "天龙八部是什么时间创作的？"

# 执行相似性搜索
# similarity_search: 在向量数据库中查找与查询文本最相似的文档
# k=2: 返回最相似的2个文档
docs = chroma_db.similarity_search(query,k=2)

# 遍历并打印搜索到的文档内容
for doc in docs:
    print(doc.page_content)  # 打印文档的文本内容
    print("=====")
    
print("==========================")

# 执行带相关性分数的相似性搜索
# similarity_search_with_relevance_scores: 返回文档及其相似性分数
# 分数越接近1表示相似度越高，越接近0表示相似度越低
docs_score = chroma_db.similarity_search_with_relevance_scores(query,k=2)

# 遍历并打印文档内容及其相似性分数
for doc,score in docs_score:
    print(f"内容：{doc.page_content}---->相似度分:{score:.4f}")  # 格式化输出相似度分数，保留4位小数
    print("=====")