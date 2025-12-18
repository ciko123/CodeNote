# 导入LangChain的集成检索器类
# EnsembleRetriever: 组合多个检索器的结果，提高检索准确性和覆盖率
from langchain.retrievers import EnsembleRetriever
# 导入LangChain社区的BM25检索器类
# BM25Retriever: 基于BM25算法的关键词检索器，适用于关键词匹配
from langchain_community.retrievers import BM25Retriever
# 导入LangChain社区的FAISS向量数据库类
# FAISS: Facebook AI Similarity Search，高效的向量相似性搜索库
from langchain_community.vectorstores import FAISS
# 导入LangChain的HuggingFace嵌入模型类
from langchain_huggingface import HuggingFaceEmbeddings
# 导入LangChain的字符文本分割器类
from langchain.text_splitter import CharacterTextSplitter
# 导入LangChain的OpenAI聊天模型类
from langchain_openai import ChatOpenAI
# 导入LangChain的LLM链提取器类
# LLMChainExtractor: 使用LLM提取文档中与查询相关的内容
from langchain.retrievers.document_compressors import LLMChainExtractor
# 导入LangChain的上下文压缩检索器类
from langchain.retrievers import ContextualCompressionRetriever
# 导入LangChain的文档类
from langchain.docstore.document import Document
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv
# 从.env文件加载环境变量
load_dotenv()

# 定义关于人工智能的示例文本
sample_text = """
人工智能(AI)是计算机科学的一个分支，致力于创造能够模拟人类智能的系统。
人工智能的历史可以追溯到20世纪50年代，当时科学家们开始探索让计算机执行需要人类智能的任务。

人工智能主要分为弱人工智能和强人工智能。弱人工智能专注于特定任务，如语音识别、图像识别或下棋。
而强人工智能则具有通用智能，能够理解、学习并应用知识解决各种问题。

机器学习是人工智能的一个重要子领域，它使计算机能够从数据中学习而无需明确编程。
深度学习作为机器学习的一个分支，使用神经网络，特别是深度神经网络，来模拟人脑的学习方式。

自然语言处理(NLP)是人工智能的另一个重要领域，它使计算机能够理解、解释和生成人类语言。
计算机视觉则专注于使计算机能够从数字图像或视频中获取高层次的理解。

人工智能在医疗保健、金融、交通、教育和娱乐等多个领域都有广泛应用。
例如，在医疗保健中，AI可用于疾病诊断和药物研发；在交通领域，自动驾驶汽车是AI的一个重要应用。

然而，人工智能也带来了一些挑战和伦理问题，如工作岗位自动化、隐私问题、算法偏见和安全风险。
确保AI系统的透明度、问责制和公平性是当前AI研究的重要方向。

未来，人工智能有望继续发展，与其他技术如物联网、大数据和云计算相结合，创造更智能的系统和解决方案。
随着计算能力的提升和数据的增长，AI的潜力几乎是无限的。
"""

# 定义获取文档列表的函数
def get_docs(retriever_type)-> list[Document]:
    # 创建文档对象
    # Document: LangChain的文档类，包含内容和元数据
    # page_content: 文档的文本内容
    # metadata: 文档的元数据，包含检索器类型标识
    document_vector = Document(page_content=sample_text, metadata={"retriever": retriever_type})

    # 将文档放入列表中
    documents_vector = [document_vector]

    # 分割文档
    # CharacterTextSplitter: 按字符数分割文本的分割器
    # chunk_size: 每个文本块的最大字符数
    # chunk_overlap: 文本块之间的重叠字符数，保持上下文连贯性
    text_splitter = CharacterTextSplitter(chunk_size=50, chunk_overlap=5)
    return text_splitter.split_documents(documents_vector)

# 定义HuggingFace模型的本地路径
# bge-large-zh-v1.5: BGE（BAAI General Embedding）大型中文嵌入模型
embeddings_path = "d:/HuggingFace/bge-large-zh-v1.5"
# 创建HuggingFace嵌入模型实例
embeddings = HuggingFaceEmbeddings(model_name=embeddings_path)

# 从文档创建FAISS向量数据库
# from_documents: 从文档列表创建FAISS向量数据库
# get_docs("vector_retriever"): 获取分割后的文档列表
vectorstore = FAISS.from_documents(get_docs("vector_retriever"), embeddings)
# 将FAISS向量数据库转换为检索器
# search_kwargs: 搜索参数，k=2表示返回最相似的2个文档
vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

# 创建OpenAI聊天模型实例
# temperature: 控制输出随机性，0表示确定性输出
llm = ChatOpenAI(temperature=0)
# 创建LLM链提取器实例
# from_llm: 从LLM创建文档内容提取器
compressor = LLMChainExtractor.from_llm(llm)

# 创建上下文压缩检索器实例
# ContextualCompressionRetriever: 包装基础检索器，对检索结果进行压缩和过滤
# base_retriever: 基础检索器，用于执行初始检索
# base_compressor: 基础压缩器，用于提取相关内容
vector_compression_retriever = ContextualCompressionRetriever(
    base_retriever=vector_retriever,
    base_compressor=compressor
)

# 创建BM25检索器实例
# from_documents: 从文档列表创建BM25检索器
# BM25: 基于词频-逆文档频率的关键词检索算法
bm25_retriever = BM25Retriever.from_documents(get_docs("bm25_retriever"))
# 设置BM25检索器返回的文档数量
bm25_retriever.k = 2

# 创建集成检索器实例
# EnsembleRetriever: 组合多个检索器的结果，使用权重合并相似度分数
# retrievers: 检索器列表，包含要组合的多个检索器
# weights: 权重列表，对应每个检索器的重要性权重
ensemble_retriever = EnsembleRetriever(
    retrievers=[vector_compression_retriever, bm25_retriever],  # 组合向量压缩检索器和BM25检索器
    weights=[0.6, 0.4]                                          # 向量检索器权重更高
)

# 使用集成检索器进行查询
# invoke(): 执行集成检索，返回合并和排序后的文档
docs = ensemble_retriever.invoke("人工智能的主要应用领域有哪些？")
print(f"检索到 {len(docs)} 个相关文档:")
# 遍历并打印检索到的文档内容
for i, doc in enumerate(docs):
    # 打印文档内容，如果超过300字符则截断并添加省略号
    print(f"\n文档 {i+1}:")
    print(doc.page_content.strip()[:300] + "..." if len(doc.page_content) > 300 else doc.page_content.strip())
    # 打印文档的元数据信息
    print(f"元数据: {doc.metadata}")
    print("-------------------------")