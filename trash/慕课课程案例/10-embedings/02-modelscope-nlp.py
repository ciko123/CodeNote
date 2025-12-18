# 导入LangChain社区的ModelScope嵌入模型类
# ModelScopeEmbeddings: 用于加载和使用ModelScope平台上的预训练嵌入模型
from langchain_community.embeddings import ModelScopeEmbeddings

# 安装依赖包的说明（注释形式）
# pip install modelscope
# pip install addict  
# pip install datasets==3.0.2
# pip install simplejson==3.3.0
# pip install sortedcontainers==2.4.0

# 定义ModelScope模型的本地路径
# nlp_corom_sentence-embedding_chinese-base: 中文句子嵌入模型，用于生成中文文本的向量表示
embeding_path = "D:/ModelScope/hub/models/iic/nlp_corom_sentence-embedding_chinese-base"

# 创建ModelScope嵌入模型实例
# model_id: 指定要加载的模型ID或路径
# model_revision: 指定模型的版本号，确保使用特定版本的模型
embedings = ModelScopeEmbeddings(model_id=embeding_path,model_revision="v1.0.0")

# 定义要生成嵌入向量的文本列表
texts = ["你好，中国", "中国是个伟大的国家"]

# 批量生成文本的嵌入向量
# embed_documents: 为多个文本同时生成嵌入向量，返回向量列表
vectors = embedings.embed_documents(texts)

# 遍历并打印每个文本的嵌入向量信息
for i,vector in enumerate(vectors):
    print(f"第{i}个文本维度: {len(vector)}")  # 打印向量的维度大小
    print(f"第{i}个文本向量: {vector}")      # 打印完整的向量值