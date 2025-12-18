# 导入LangChain社区的Web基础加载器类
# WebBaseLoader: 用于加载网页内容的文档加载器
from langchain_community.document_loaders import WebBaseLoader

# 创建Web基础加载器实例
# web_path: 要加载的网页URL地址
# WebBaseLoader会自动提取网页中的文本内容，去除HTML标签和脚本
loader = WebBaseLoader(web_path="http://www.surexian.com/html/2024/03/05/68057.html")

# 加载网页内容
# load(): 访问网页并返回文档列表，通常包含一个文档对象
documents = loader.load()

# 打印加载的文档数量
print(len(documents))

print("===============================================================================================================")

# 打印第一个文档的内容
# Document对象包含page_content（网页文本内容）和metadata（如source URL等）
print(documents[0])