# 导入LangChain社区的文本加载器类
# TextLoader: 用于加载文本文件的文档加载器
from langchain_community.document_loaders import TextLoader

# 定义文本文件所在目录路径
path = "D:/test/"

# 创建文本加载器实例
# file_path: 要加载的文本文件路径
# encoding: 文件编码格式，utf-8支持中文字符
loader = TextLoader(file_path= path + "金庸书籍.txt",encoding="utf-8")

# 加载文本文件内容
# load(): 读取文件并返回文档列表
documents = loader.load()

# 打印加载的文档数量
print(len(documents))

print("================================")

# 遍历并打印每个文档的内容
# Document对象包含page_content和metadata两个属性
for doc in documents:
    print('==='*20)
    print(doc)