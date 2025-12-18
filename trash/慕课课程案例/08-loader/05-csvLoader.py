# 导入LangChain社区的CSV加载器类
# CSVLoader: 用于加载CSV文件的文档加载器
from langchain_community.document_loaders import CSVLoader

# 定义CSV文件所在目录路径
path = "D:/test/"

# 创建CSV加载器实例
# file_path: 要加载的CSV文件路径
# CSVLoader会将CSV文件的每一行转换为一个Document对象
loader = CSVLoader(file_path= path + "1.csv")

# 加载CSV文件内容
# load(): 读取CSV文件并返回文档列表，每行对应一个文档对象
docments = loader.load()

# 打印加载的文档数量（通常等于CSV行数，不包括表头）
print(len(docments))

print("=================")

# 遍历并打印前3个文档记录的内容
# CSV的每一行都会被转换为一个Document对象，包含该行的所有字段
for record in docments[:3]:
    print(record)
    print("===============================")

