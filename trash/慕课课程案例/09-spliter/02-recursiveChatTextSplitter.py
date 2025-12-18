# 导入LangChain的递归字符文本分割器类
# RecursiveCharacterTextSplitter: 智能递归分割文本的分割器，能在语义边界处进行分割
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 定义长文本内容，用于演示文本分割功能
long_text = """
大型语言模型(LLM)已经成为自然语言处理领域的重要工具。它们能够生成连贯的文本、回答问题、进行摘要等多种任务。

然而，处理长文本是一个挑战。大多数LLM都有输入长度限制，例如GPT-3的最大输入长度约为4000个token。这意味着长文档需要被分割成较小的块才能被处理。

RecursiveCharacterTextSplitter是LangChain提供的一个强大工具，它可以智能地将长文本分割成适合LLM处理的小块。与简单的按固定长度分割不同，它会尝试在语义边界处进行分割，例如段落、句子或单词之间。

使用这个工具时，我们可以指定最大块大小(chunk_size)和重叠部分(chunk_overlap)。重叠部分确保相邻块之间有一些共同内容，有助于保持上下文的连贯性。

下面是一个使用RecursiveCharacterTextSplitter的简单示例：

首先，我们需要导入必要的库并创建一个文本分割器实例：
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 创建文本分割器，设置块大小为100个字符，重叠20个字符
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=20,
    length_function=len
)

# 假设我们有一篇长文章
long_document = "这是一篇很长的文章..."

# 将文档分割成块
text_chunks = text_splitter.split_text(long_document)

# 打印分割后的块数
print(f"文档被分割成 {len(text_chunks)} 个块")

# 打印第一个块
print(text_chunks[0])
通过这种方式，我们可以有效地处理任意长度的文档，使其适合LLM处理。

文本分割是构建文档问答系统、长文本摘要系统和其他基于LLM的应用的重要步骤。正确的分割策略可以显著提高这些系统的性能和准确性。
"""

# 创建递归字符文本分割器实例
# RecursiveCharacterTextSplitter: 按优先级递归尝试不同分隔符进行分割
# 分隔符优先级：段落 -> 句子 -> 单词 -> 字符
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 300,        # 每个文本块的最大字符数
    chunk_overlap  = 50,     # 文本块之间的重叠字符数，保持上下文连贯性
    length_function = len    # 计算文本长度的函数
)

# 分割长文本
# split_text: 将文本字符串分割成多个文本块
chunks = text_splitter.split_text(long_text)

# 打印分割后的文本块数量
print(len(chunks))

# 遍历并打印前5个文本块的内容
for i,chunk in enumerate(chunks[:5]):
    print("块",i,"内容：")
    print(chunk)