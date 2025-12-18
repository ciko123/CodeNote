# 导入LangChain社区的PDF加载器类
# PyPDFLoader: 用于加载PDF文件的文档加载器
from langchain_community.document_loaders import PyPDFLoader

# 定义PDF文件所在目录路径
path = "d:/test/"

# 创建PDF加载器实例
# file_path: 要加载的PDF文件路径
# PyPDFLoader会自动将PDF按页面分割成多个文档片段
loader = PyPDFLoader(file_path= path + "1.pdf")

# 加载PDF文件内容
# load(): 读取PDF文件并返回文档列表，每个页面对应一个文档对象
documents = loader.load()

# 打印加载的文档数量（通常等于PDF页数）
print(len(documents))

print("============================================================")

# 遍历并打印每个文档片段的内容
# enumerate(): 获取文档的索引和内容
# PDF的每个页面都会被转换为一个Document对象
for i,doc in enumerate(documents):
    print(f"文档片段{i+1}内容为：\n{doc}\n")
    print("============================================================")