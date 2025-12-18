# 导入LangChain的令牌文本分割器类
# TokenTextSplitter: 基于令牌数量分割文本的分割器，适用于LLM的令牌限制
from langchain.text_splitter import TokenTextSplitter
# 导入tiktoken库，OpenAI的令牌编码工具
import tiktoken

# 定义测试文本，用于演示基于令牌的文本分割
text = "LangChain是一个用于开发由语言模型驱动的应用程序的框架。它提供了各种工具和组件，帮助开发者构建强大、灵活的语言模型应用。使用LangChain，你可以轻松地将大型语言模型集成到你的应用中，创建聊天机器人、问答系统、文本生成工具等等。"

# 创建令牌文本分割器实例
# TokenTextSplitter: 按令牌数量而不是字符数来分割文本
text_splitter = TokenTextSplitter(
    encoding_name="cl100k_base",  # 使用的编码名称，cl100k_base是GPT-4和text-embedding-ada-002的编码
    chunk_size=50,                 # 每个文本块的最大令牌数
    chunk_overlap=10               # 文本块之间的重叠令牌数，保持上下文连贯性
)

# 获取指定的编码器
# tiktoken.get_encoding(): 根据编码名称获取编码器实例
enc = tiktoken.get_encoding("cl100k_base")

# 分割文本
# split_text: 将文本字符串按令牌数量分割成多个文本块
chunks = text_splitter.split_text(text)

# 遍历并打印每个文本块的内容和令牌数量
for i,chunk in enumerate(chunks):
    print(f"文本块 {i+1}: {chunk}")
    # enc.encode(): 将文本编码为令牌列表
    # len(): 计算令牌数量
    print(f"token数量: {len(enc.encode(chunk))}")