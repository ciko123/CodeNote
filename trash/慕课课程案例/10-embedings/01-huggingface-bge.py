# 导入LangChain的HuggingFace嵌入模型类
# HuggingFaceEmbeddings: 用于加载和使用HuggingFace上的预训练嵌入模型
from langchain_huggingface import HuggingFaceEmbeddings

# 定义HuggingFace模型的本地路径
# bge-large-zh-v1.5: BGE（BAAI General Embedding）大型中文嵌入模型
embedings_path = "D:/HuggingFace/bge-large-zh-v1.5"

# 创建HuggingFace嵌入模型实例
# model_name: 指定要加载的模型名称或路径
# HuggingFaceEmbeddings会自动下载或加载指定的嵌入模型
embedings = HuggingFaceEmbeddings(model_name=embedings_path)

# 定义要生成嵌入向量的文本列表
texts = [
    "你好,中国",
    "你好,美国",
    "你好,日本",
]

# 批量生成文本的嵌入向量
# embed_documents: 为多个文本同时生成嵌入向量，返回向量列表
vectors = embedings.embed_documents(texts)

# 遍历并打印每个文本的嵌入向量信息
for i,vector in enumerate(vectors):
    print(f"第{i}个文本维度: {len(vector)}")  # 打印向量的维度大小
    print(f"第{i}个文本向量: {vector}")      # 打印完整的向量值


# 为单个查询文本生成嵌入向量（注释掉的代码）
# vector = embedings.embed_query("你好,中国")

# 打印单个查询向量的维度（注释掉的代码）
# print(len(vector))