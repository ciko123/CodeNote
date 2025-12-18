# 导入LangChain的Chroma向量数据库类
from langchain_chroma import Chroma
# 导入LangChain核心的文档类
from langchain_core.documents import Document
# 导入LangChain的HuggingFace嵌入模型类
from langchain_huggingface import HuggingFaceEmbeddings
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv
# 从.env文件加载环境变量
load_dotenv()

# 定义文档列表，每个文档包含内容和元数据
# Document: LangChain的文档类，包含page_content（内容）和metadata（元数据）
docs = [
    Document(
        page_content="一群科学家带回恐龙，混乱爆发",
        metadata={"year": 1993, "rating": 7.7, "genre": "科幻"},
    ),
    Document(
        page_content="里奥·迪卡普里奥迷失在梦中，在梦中迷失在梦里，在梦里迷失在。。。",
        metadata={"year": 2010, "director": "Christopher Nolan", "rating": 8.2},
    ),
    Document(
        page_content="一位心理学家/侦探在梦中的一系列梦中迷失了方向，《盗梦空间》再次使用了这个想法",
        metadata={"year": 2006, "director": "Satoshi Kon", "rating": 8.6, "genre": "科幻"},
    ),
    Document(
        page_content="一群正常体型的女人非常健康，有些男人对她们很渴望",
        metadata={"year": 2019, "director": "Greta Gerwig", "rating": 8.3},
    ),
    Document(
        page_content="玩具活了过来，玩得很开心",
        metadata={"year": 1995, "genre": "动画","rating": 9.0,},
    ),
    Document(
        page_content="三个人走进禁区，三个人走出禁区",
        metadata={
            "year": 1979,
            "director": "Andrei Tarkovsky",
            "genre": "惊悚",
            "rating": 9.9,
        },
    ),
]

# 定义HuggingFace模型的本地路径
# bge-large-zh-v1.5: BGE（BAAI General Embedding）大型中文嵌入模型
embeddings_path = "d:/HuggingFace/bge-large-zh-v1.5"
# 创建HuggingFace嵌入模型实例
embeddings = HuggingFaceEmbeddings(model_name=embeddings_path)

# 定义Chroma数据库的持久化目录
persist_directory = 'chroma_db_5'  # 数据库存储的目录

# 从文档列表创建Chroma向量数据库
# from_documents: 从文档列表创建向量数据库
# docs: 文档列表
# embeddings: 嵌入模型，用于将文本转换为向量
# persist_directory: 持久化目录，用于保存数据库
vectorstore = Chroma.from_documents(docs, embeddings, persist_directory = persist_directory)

# 定义查询问题
question = "请帮我推荐一些科幻类的电影"

# 定义过滤条件
# 使用MongoDB风格的查询语法进行元数据过滤
# $and: 逻辑与操作，所有条件都必须满足
# genre: "科幻": 类型必须是科幻
# rating: {"$gt": 8.0}: 评分大于8.0
filter_condition = {
    "$and": [
        {"genre": "科幻"},
        {"rating": {"$gt": 8.0}},
    ]
}

# 创建带过滤条件的检索器
# as_retriever(): 将向量数据库转换为可调用的检索器对象
# search_kwargs: 搜索参数
#   filter: 过滤条件，基于文档元数据进行过滤
#   k: 返回文档的最大数量
retriever = vectorstore.as_retriever(search_kwargs={"filter":filter_condition,"k": 3})

# 使用检索器进行查询
# invoke(): 执行检索，返回满足过滤条件且与查询最相关的文档
docs = retriever.invoke(question)

# 打印检索结果
print(docs)

