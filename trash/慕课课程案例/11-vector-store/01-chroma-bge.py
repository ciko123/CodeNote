# 导入LangChain社区的文本加载器类
from langchain_community.document_loaders import TextLoader
# 导入LangChain的HuggingFace嵌入模型类
from langchain_huggingface import HuggingFaceEmbeddings
# 导入LangChain的字符文本分割器类
from langchain.text_splitter import CharacterTextSplitter
# 导入LangChain社区的Chroma向量存储类
from langchain_community.vectorstores import Chroma

# 定义文本文件所在目录路径
path = "d:/test/"

# 创建文本加载器实例并加载文档
# encoding: 使用utf-8编码支持中文字符
loader = TextLoader(file_path= path + "金庸书籍.txt",encoding="utf-8")

# 加载文本文件内容
documents = loader.load()


# 创建字符文本分割器实例
# CharacterTextSplitter: 按指定分隔符分割文本的分割器
text_splitter = CharacterTextSplitter(
    separator="\n",    # 分隔符：使用换行符作为分割点
    chunk_size=15,      # 每个文本块的最大字符数
    chunk_overlap=0     # 文本块之间的重叠字符数
)

# 分割文档
# split_documents: 将文档列表分割成更小的文本块
docs = text_splitter.split_documents(documents)

# 定义HuggingFace模型的本地路径
# bge-large-zh-v1.5: BGE（BAAI General Embedding）大型中文嵌入模型
embeddings_path = "d:/HuggingFace/bge-large-zh-v1.5"
# 创建HuggingFace嵌入模型实例
embeddings = HuggingFaceEmbeddings(model_name=embeddings_path)

# 定义Chroma数据库的持久化目录
persist_dir =  "chroma_bge"
# 注释掉的代码：使用from_documents方法创建并持久化Chroma数据库
# Chroma.from_documents(docs, embeddings,collection_name="laogu",persist_directory=persist_dir)
# 创建Chroma向量数据库实例
chroma_db = Chroma(
    persist_directory=persist_dir,        # 持久化目录路径
    embedding_function=embeddings,        # 嵌入函数，用于将文本转换为向量
    collection_name="laogu",             # 集合名称，用于标识不同的文档集合
    collection_metadata={"hnsw:space": "cosine"}  # HNSW索引的空间类型
                                                # "l2"：欧氏距离（L2 范数）
                                                # "ip"：点积（Inner Product）
                                                # "cosine"：余弦相似度（默认，无需显式指定）
)

# 将分割后的文档添加到Chroma数据库
# add_documents: 将文档列表添加到向量数据库中，自动生成嵌入向量并建立索引
chroma_db.add_documents(docs)
