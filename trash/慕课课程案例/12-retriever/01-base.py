# 导入LangChain社区的文本加载器类
from langchain_community.document_loaders import TextLoader
# 导入LangChain的HuggingFace嵌入模型类
from langchain_huggingface import HuggingFaceEmbeddings
# 导入LangChain的字符文本分割器类
from langchain.text_splitter import CharacterTextSplitter
# 导入LangChain的Chroma向量数据库类
from langchain_chroma import Chroma

# 注释掉的代码：文档加载和分割流程
# path = "d:/test/"

# loader = TextLoader(file_path= path + "刘德华.txt",encoding="utf-8")

# documents = loader.load()


# text_splitter = CharacterTextSplitter(
#     separator="\n",
#     chunk_size=100,
#     chunk_overlap=0
# )

# docs = text_splitter.split_documents(documents)

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

# 将Chroma向量数据库转换为检索器
# as_retriever(): 将向量数据库转换为可调用的检索器对象
retriever = chroma_db.as_retriever()

# 使用检索器进行查询
# invoke(): 执行检索，返回与查询最相关的文档
docs = retriever.invoke("刘德华的曾用名是什么？")

# 遍历并打印检索到的文档内容
for doc in docs:
    print(doc.page_content)  # 打印文档的文本内容
    print("=====")