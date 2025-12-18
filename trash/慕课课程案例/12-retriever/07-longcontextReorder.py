# 导入LangChain核心的内存向量数据库类
# InMemoryVectorStore: 在内存中存储向量的数据库，适用于临时存储和快速测试
from langchain_core.vectorstores import InMemoryVectorStore
# 导入LangChain的HuggingFace嵌入模型类
from langchain_huggingface import HuggingFaceEmbeddings
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv
# 从.env文件加载环境变量
load_dotenv()

# 定义HuggingFace模型的本地路径
# bge-large-zh-v1.5: BGE（BAAI General Embedding）大型中文嵌入模型
embeddings_path = "d:/HuggingFace/bge-large-zh-v1.5"
# 创建HuggingFace嵌入模型实例
embeddings = HuggingFaceEmbeddings(model_name=embeddings_path)

# 定义文本列表，包含各种主题的文档
texts = [
    "篮球是一项很棒的运动。",
    "《Fly me to the moon》是我最喜欢的歌曲之一。",
    "凯尔特人队是我最喜欢的球队。",
    "这是一篇关于波士顿凯尔特人队的文档。",
    "我特别喜欢去看电影。",
    "波士顿凯尔特人队以20分的优势赢得了比赛。",
    "这只是一个随机文本。",
    "《艾尔登法环》是过去15年中最好的游戏之一。",
    "L·科内特是凯尔特人队最好的球员之一。",
    "拉里·伯德是一位标志性的NBA球员。"
]

# 创建内存向量数据库并转换为检索器
# from_texts: 从文本列表创建向量数据库
# embedding: 嵌入模型，用于将文本转换为向量
# as_retriever(): 将向量数据库转换为可调用的检索器对象
# search_kwargs: 搜索参数，k=5表示返回最相似的5个文档
retriever = InMemoryVectorStore.from_texts(texts, embedding=embeddings).as_retriever(
    search_kwargs={"k": 5}
)

# 定义查询文本
query = "你能告诉我关于凯尔特人队的哪些信息？"

# 使用检索器进行查询
# invoke(): 执行检索，返回与查询最相关的文档
docs = retriever.invoke(query)
# 打印原始检索结果
for doc in docs:
    print(f"- {doc}")

print("=" * 50)

# 导入LangChain社区的长上下文重排序器类
# LongContextReorder: 重新排序文档，将相关文档放在开头和结尾，提高LLM处理长上下文的性能
from langchain_community.document_transformers import LongContextReorder

# 创建长上下文重排序器实例
reorder = LongContextReorder()
# 对检索结果进行重新排序
# transform_documents: 重新排序文档列表，优化长上下文处理
reordered_docs = reorder.transform_documents(docs)

# 打印重新排序后的文档
for doc in reordered_docs:
    print(f"-> {doc.page_content}")

print("=" * 50)

# 导入LangChain的文档组合链创建函数
# create_stuff_documents_chain: 创建将所有文档内容填入提示模板的链
from langchain.chains.combine_documents import create_stuff_documents_chain
# 导入LangChain核心的提示模板类
from langchain_core.prompts import PromptTemplate
# 导入LangChain的OpenAI聊天模型类
from langchain_openai import ChatOpenAI

# 创建OpenAI聊天模型实例
# model: 使用的模型名称 (gpt-4o)
llm = ChatOpenAI(model="gpt-4o")

# 定义提示模板
# 将文档内容和查询填入模板，让LLM基于文档回答问题
prompt_template = """
Given these texts:
-----
{context}
-----
Please answer the following question:
{query}
"""

# 创建提示模板实例
# template: 提示模板字符串
# input_variables: 输入变量列表，指定模板中的占位符
prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "query"],
)

# 创建并调用链
# create_stuff_documents_chain: 创建将文档内容填入提示模板的链
# chain.invoke(): 调用链，传入上下文和查询，生成回答
chain = create_stuff_documents_chain(llm, prompt)
response = chain.invoke({"context": reordered_docs, "query": query})
print(response)