# 导入LangChain社区的文本加载器类
from langchain_community.document_loaders import TextLoader
# 导入LangChain的HuggingFace嵌入模型类
from langchain_huggingface import HuggingFaceEmbeddings
# 导入LangChain的字符文本分割器类
from langchain.text_splitter import CharacterTextSplitter
# 导入LangChain的OpenAI聊天模型类
from langchain_openai import ChatOpenAI
# 导入LangChain的多查询检索器类
from langchain.retrievers.multi_query import MultiQueryRetriever
# 导入LangChain的Chroma向量数据库类
from langchain_chroma import Chroma
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

# 创建OpenAI聊天模型实例
# model: 使用的模型名称 (gpt-4o)
# temperature: 控制输出随机性，0表示确定性输出
llm = ChatOpenAI(model="gpt-4o", temperature=0)
# 创建多查询检索器实例
# MultiQueryRetriever: 使用LLM生成多个不同的查询，提高检索覆盖率和准确性
# from_llm: 从LLM和基础检索器创建多查询检索器
retriever = MultiQueryRetriever.from_llm(llm=llm, retriever=chroma_db.as_retriever())

# 导入日志模块
import logging
# 配置日志系统
logging.basicConfig()
# 设置多查询检索器的日志级别为INFO，显示生成的查询信息
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)

# 使用多查询检索器进行查询
# invoke(): 执行检索，LLM会自动生成多个相关查询并合并结果
# k=2: 返回最相似的2个文档
docs = retriever.invoke("刘德华在电影《至尊无上》里是干什么？",k=2)

# 遍历并打印检索到的文档内容
for doc in docs:
    print(doc.page_content)  # 打印文档的文本内容
    print("=====")