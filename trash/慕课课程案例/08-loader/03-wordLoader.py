# 导入LangChain社区的Word文档加载器类
# Docx2txtLoader: 用于加载Word文档(.docx)的文档加载器
from langchain_community.document_loaders import Docx2txtLoader

# 定义Word文档所在目录路径
path = "D:/test/"

# 创建Word文档加载器实例
# file_path: 要加载的Word文档路径
# Docx2txtLoader使用docx2txt库来提取Word文档中的文本内容
loader = Docx2txtLoader(file_path= path + "1.docx")

# 加载Word文档内容
# load(): 读取Word文档并返回文档列表
documents = loader.load()

# 打印加载的文档数量
print(len(documents))

# 遍历并打印每个文档片段的内容
# Word文档通常被作为一个完整的文档对象加载
for i,doc in enumerate(documents):
    print(f"文档片段{i+1}内容为：{doc}")
    print("============================================================")