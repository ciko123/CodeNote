# 导入LangChain的HuggingFace嵌入模型类
from langchain_huggingface import HuggingFaceEmbeddings
# 导入NumPy库，用于数值计算和数组操作
import numpy as np

# 定义HuggingFace模型的本地路径
# bge-large-zh-v1.5: BGE（BAAI General Embedding）大型中文嵌入模型
embedings_path = "D:/HuggingFace/bge-large-zh-v1.5"

# 创建HuggingFace嵌入模型实例
embedings = HuggingFaceEmbeddings(model_name=embedings_path)

# 定义三个测试文本，用于演示余弦相似性计算
# text1和text2语义相似，text3与它们语义不相关
text1 = "猫在垫子上"
text2 = "垫子上有一只猫"
text3 = "中国很伟大"

# 为每个文本生成嵌入向量
# embed_query: 为单个查询文本生成嵌入向量
text1_vector = embedings.embed_query(text1)
text2_vector = embedings.embed_query(text2)
text3_vector = embedings.embed_query(text3)

# 方法1：使用scikit-learn的余弦相似性函数
from sklearn.metrics.pairwise import cosine_similarity
# 将向量重塑为二维数组，sklearn要求输入为二维格式
text1_vector_reshape = np.array(text1_vector).reshape(1, -1)
text2_vector_reshape = np.array(text2_vector).reshape(1, -1)
text3_vector_reshape = np.array(text3_vector).reshape(1, -1)

# 计算text1和text2的余弦相似性
# cosine_similarity: 计算两个向量之间的余弦相似性，返回值在[-1,1]之间
similarity = cosine_similarity(text1_vector_reshape, text2_vector_reshape)[0][0]

print(f"1-2句子的余弦相似性: {similarity}")

# 计算text1和text3的余弦相似性
similarity1 = cosine_similarity(text1_vector_reshape, text3_vector_reshape)[0][0]

print(f"1-3句子的余弦相似性: {similarity1}")

print("=======================================深度学习=========================================")

# 方法2：使用sentence_transformers的余弦相似性函数
from sentence_transformers.util import cos_sim

# 直接计算向量间的余弦相似性，不需要重塑数组
s = cos_sim(text1_vector, text2_vector)
s1 = cos_sim(text1_vector, text3_vector)

# 使用.item()方法将tensor转换为标量值
print(f"1-2句子的余弦相似性: {s.item()}")
print(f"1-3句子的余弦相似性: {s1.item()}")

print("=======================================自定义=========================================")

# 方法3：手动实现余弦相似性计算
# 导入NumPy库（已导入，重复导入无影响）
import numpy as np
def cosine_similarity_manual(vec1, vec2):
    # 计算两个向量的点积
    dot_product = np.dot(vec1, vec2)
    # 计算第一个向量的L2范数（欧几里得范数）
    norm_vec1 = np.linalg.norm(vec1)
    # 计算第二个向量的L2范数
    norm_vec2 = np.linalg.norm(vec2)
    # 余弦相似性公式：点积 / (向量1范数 * 向量2范数)
    return dot_product / (norm_vec1 * norm_vec2)

# 使用自定义函数计算余弦相似性
similarity4 = cosine_similarity_manual(text1_vector, text2_vector)
print(f"自定义的余弦相似性: {similarity4}")