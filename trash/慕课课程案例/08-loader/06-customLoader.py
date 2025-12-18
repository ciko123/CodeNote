# 导入类型提示模块：异步迭代器和迭代器
from typing import AsyncIterator, Iterator

# 导入LangChain核心的基础加载器类和文档类
from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

# 自定义文档加载器类，继承自BaseLoader
class CustomLoader(BaseLoader):
    
    # 初始化方法，接收文件路径参数
    def __init__(self,file_path:str):
        self.file_path = file_path
    
    # 懒加载方法，返回文档迭代器
    # lazy_load: 逐行读取文件，每行创建一个Document对象
    def lazy_load(self) -> Iterator[Document]:
        # 打开文件并逐行读取
        with open(self.file_path, encoding="utf-8") as f:
            line_number = 0
            for line in f:
                # 生成Document对象，包含行内容和元数据
                yield Document(
                    page_content=line,  # 文档内容：当前行文本
                    metadata={"line_number": line_number,"length":len(line),"source":self.file_path}  # 元数据：行号、长度、来源文件
                )
                line_number += 1
    
    # 异步懒加载方法，返回异步文档迭代器
    # alazy_load: 异步逐行读取文件，提高大文件读取性能
    async def alazy_load(self) -> AsyncIterator[Document]:
        # 导入异步文件操作库
        import aiofiles
        # 异步打开文件并逐行读取
        async with aiofiles.open(self.file_path, encoding="utf-8") as f:
            line_number = 0
            async for line in f:
                # 异步生成Document对象
                yield Document(
                    page_content=line,  # 文档内容：当前行文本
                    metadata={"line_number": line_number,"length":len(line),"source":self.file_path}  # 元数据：行号、长度、来源文件
                )
                line_number += 1
                

# 创建自定义加载器实例
loader = CustomLoader(file_path="d:/test/金庸书籍.txt")

# 加载文档内容
# load(): 调用lazy_load方法并收集所有文档
documents = loader.load()

# 打印加载的文档数量
print(len(documents))
print("====")
# 遍历并打印每个文档的内容和元数据
for doc in documents: 
    print(doc)
    print("====")