# 导入LangChain的集成检索器类
# EnsembleRetriever: 组合多个检索器的结果，提高检索准确性和覆盖率
from langchain.retrievers import EnsembleRetriever
# 导入LangChain社区的Chroma向量数据库类
from langchain_community.vectorstores import Chroma
# 导入LangChain的HuggingFace嵌入模型类
from langchain_huggingface import HuggingFaceEmbeddings

# 第一个文档列表，包含关于苹果和橘子的基础信息
doc_list_1 = [
    "张三喜欢苹果",
    "李四喜欢橘子",
    "苹果和橘子都是水果",
    "苹果的果肉又脆又多汁，有酸甜的味道。",
    "苹果含有膳食纤维（果胶）和抗氧化剂，如维生素C",
    "苹果和橘子都是水果，但是苹果的果肉更甜，而橘子的果肉更酸。",
    "苹果和橘子都是水果，但是苹果含有膳食纤维（果胶）和抗氧化剂，如维生素C，而橘子没有。",
]

# 第二个文档列表，包含关于苹果的额外信息
doc_list_2 = [
    "王五喜欢苹果",
    "赵六喜欢橘子",
    "苹果呈圆形，表皮光滑，通常呈红色、绿色或黄色",
    "在多元文化中，苹果象征着健康和知识",
    "苹果可以生吃，也可以煮成美味的甜点，还可以榨成果汁"
]

# 定义HuggingFace模型的本地路径
# bge-large-zh-v1.5: BGE（BAAI General Embedding）大型中文嵌入模型
embeddings_path = "d:/HuggingFace/bge-large-zh-v1.5"
# 创建HuggingFace嵌入模型实例
embeddings = HuggingFaceEmbeddings(model_name=embeddings_path)

# 从文本列表创建第一个Chroma向量数据库
# from_texts: 从文本列表创建向量数据库
# doc_list_1: 文档列表
# embeddings: 嵌入模型，用于将文本转换为向量
# metadatas: 元数据列表，为每个文档添加来源标识
# persist_directory: 持久化目录，用于保存数据库
db1 = Chroma.from_texts(doc_list_1, embeddings,metadatas=[{"source": 1}] * len(doc_list_1), persist_directory = "chroma_db_1")
# 从文本列表创建第二个Chroma向量数据库
db2 = Chroma.from_texts(doc_list_2, embeddings,metadatas=[{"source": 2}] * len(doc_list_2), persist_directory = "chroma_db_2")

# 将第一个数据库转换为检索器
# as_retriever(): 将向量数据库转换为可调用的检索器对象
# search_kwargs: 搜索参数，k=1表示返回最相似的1个文档
retriever1 = db1.as_retriever(search_kwargs={"k": 1})
# 将第二个数据库转换为检索器
retriever2 = db2.as_retriever(search_kwargs={"k": 1})

# 创建集成检索器实例
# EnsembleRetriever: 组合多个检索器的结果，使用权重合并相似度分数
# retrievers: 检索器列表，包含要组合的多个检索器
# weights: 权重列表，对应每个检索器的重要性权重，总和为1
ensemble_retriever = EnsembleRetriever(
    retrievers=[retriever1, retriever2],  # 组合两个检索器
    weights=[0.5, 0.5],                  # 两个检索器权重相等
)

# 使用集成检索器进行查询
# invoke(): 执行集成检索，返回合并和排序后的文档
docs = ensemble_retriever.invoke("谁喜欢苹果？")

# 遍历并打印检索到的文档内容
for doc in docs:
    print(doc)  # 打印完整的文档对象，包含内容和元数据
    print("------")