# 导入LangChain社区的文本加载器类
from langchain_community.document_loaders import TextLoader
# 导入LangChain的字符文本分割器类
from langchain.text_splitter import CharacterTextSplitter

# 定义文本文件所在目录路径
path = "d:/test/"

# 创建文本加载器实例并加载文档
# encoding: 使用utf-8编码支持中文字符
loader = TextLoader(path + "金庸书籍.txt",encoding="utf-8")

# 加载文本文件内容
documents  = loader.load()

# 创建字符文本分割器实例
# CharacterTextSplitter: 按指定分隔符分割文本的分割器
text_splitter = CharacterTextSplitter(
    separator="\n",        # 分隔符：使用换行符作为分割点
    chunk_size=20,          # 每个文本块的最大字符数
    chunk_overlap=0,        # 文本块之间的重叠字符数
    length_function=len     # 计算文本长度的函数
)

# 分割文档
# split_documents: 将文档列表分割成更小的文本块
chunks = text_splitter.split_documents(documents)

# 打印分割后的文档数量
print("分割文档数量：",len(chunks))

# 遍历并打印每个分割文档的内容
# page_content: 文档的文本内容
for i,doc in enumerate(chunks):
    print("==文档",i,"内容==：",doc.page_content)