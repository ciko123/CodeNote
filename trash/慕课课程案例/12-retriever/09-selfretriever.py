# 导入LangChain的Chroma向量数据库类
from langchain_chroma import Chroma
# 导入LangChain核心的文档类
from langchain_core.documents import Document
# 导入LangChain的HuggingFace嵌入模型类
from langchain_huggingface import HuggingFaceEmbeddings
# 导入LangChain查询构造器的属性信息类
# AttributeInfo: 定义文档元数据字段的描述信息，用于自查询检索器
from langchain.chains.query_constructor.schema import AttributeInfo
# 导入LangChain的自查询检索器类
# SelfQueryRetriever: 使用LLM自动解析查询中的过滤条件，无需手动编写过滤逻辑
from langchain.retrievers.self_query.base import SelfQueryRetriever
# 导入LangChain的OpenAI聊天模型类
from langchain_openai import ChatOpenAI
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
persist_directory = 'chroma_db_11'  # 数据库存储的目录

# 从文档列表创建Chroma向量数据库
# from_documents: 从文档列表创建向量数据库
# docs: 文档列表
# embeddings: 嵌入模型，用于将文本转换为向量
# persist_directory: 持久化目录，用于保存数据库
vectorstore = Chroma.from_documents(docs, embeddings, persist_directory = persist_directory)

# 定义元数据字段信息
# 这些信息将帮助LLM理解如何解析查询中的过滤条件
metadata_field_info = [
    AttributeInfo(
        name="genre",
        description="电影的类型。[“科幻”、“喜剧”、“戏剧”、“惊悚”、“浪漫”、“动作”、“动画”]之一",
        type="string",
    ),
    AttributeInfo(
        name="year",
        description="电影上映的那一年",
        type="integer",
    ),
    AttributeInfo(
        name="director",
        description="电影导演的名字",
        type="string",
    ),
    AttributeInfo(
        name="rating", description="电影的评分为1-10", type="float"
    ),
]


# 创建自查询检索器实例
# SelfQueryRetriever: 使用LLM自动解析查询中的过滤条件，无需手动编写过滤逻辑
# from_llm: 从LLM创建自查询检索器
# llm: 用于解析查询的LLM模型
# vectorstore: 向量数据库，用于存储和检索文档
# document_contents: 文档内容的描述，帮助LLM理解文档的用途
# metadata_field_info: 元数据字段信息，帮助LLM理解可用的过滤条件
retriever = SelfQueryRetriever.from_llm(
    llm=ChatOpenAI(model_name="gpt-4o", temperature=0),
    vectorstore=vectorstore,
    document_contents="电影的简介",
    metadata_field_info=metadata_field_info,
)

# 定义包含复杂过滤条件的查询问题
# LLM会自动解析这个查询，提取出时间范围、主题和类型等过滤条件
question = "给我推荐一个1990年之后但2005年之前的电影都是关于玩具的，最好是动画的"

# 使用自查询检索器进行查询
# invoke(): 执行自查询检索，LLM会自动解析查询并生成相应的过滤条件
docs = retriever.invoke(question)

# 遍历并打印检索到的文档内容
for doc in docs:
    print(doc)  # 打印完整的文档对象，包含内容和元数据
    print("==============")

