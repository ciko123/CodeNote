# 导入正则表达式模块，用于模式匹配
import re
# 导入类型提示模块：任意类型和列表类型
from typing import Any, List
# 导入LangChain的文本分割器基类
from langchain.text_splitter import TextSplitter


# 定义测试文本，包含章节结构，用于演示自定义文本分割器
text = """
前言

这是本书的前言部分，介绍了写作背景和目的。

第1章 介绍
1.1 什么是人工智能
人工智能是研究如何使计算机能够像人一样思考和学习的学科。

1.2 人工智能的历史
人工智能的发展经历了多个阶段，从早期的符号主义到现代的深度学习。

第2章 机器学习基础
2.1 监督学习
监督学习是指从标记数据中学习预测模型的方法。

2.2 无监督学习
无监督学习是指从无标记数据中发现模式的方法。

"""

# 自定义章节文本分割器类，继承自TextSplitter
class ChapterTextSplitter(TextSplitter):
    """基于章节标题的文本分割器，将文档按章节结构分割"""
    
    def __init__(self, 
                 chapter_patterns: List[str] = None,    # 章节标题的正则表达式模式列表
                 keep_separator: bool = True,           # 是否保留章节标题
                 **kwargs: Any,                         # 其他关键字参数
    ):
        # 调用父类初始化方法
        super().__init__(**kwargs)
        
        # 默认章节标题模式，支持多种章节格式
        if chapter_patterns is None:
            chapter_patterns = [
                # 中文章节：第X章/节/卷/部/篇 + 可选的标题
                r"第[一二三四五六七八九十百千万\d]+[章节卷部篇](?:\s+[^\n]+)?",
                # 数字点格式：1. 标题
                r"[一二三四五六七八九十百千万\d]+\.\s+[^\n]+",
                # 英文章节：Chapter/Section X + 可选的标题
                r"(?:Chapter|Section)\s+[IVXivx\d]+(?:\.\s+[^\n]+)?",
                # 多级标题：1.2.3 标题
                r"^(?:\d+\.)+\d+\s+[^\n]+"
            ]
        
        self.chapter_patterns = chapter_patterns
        self.keep_separator = keep_separator
        
        # 编译所有正则表达式模式，提高匹配效率
        # re.MULTILINE: 多行模式，允许^和$匹配每行的开始和结束
        self.chapter_regexes = [re.compile(pattern, re.MULTILINE) for pattern in chapter_patterns]
        
    def split_text(self, text)-> List[str]:
        # 找到所有章节标题的位置信息
        chapter_positions = []
        for regex in self.chapter_regexes:
            # finditer: 查找所有匹配项，返回匹配对象的迭代器
            for match in regex.finditer(text):
                start, end = match.span()  # 获取匹配的起始和结束位置
                chapter_positions.append((start, end, match.group(0)))  # 保存位置和匹配的文本
        
        # 按起始位置排序，确保章节顺序正确
        chapter_positions.sort(key=lambda x: x[0])
        
        chunks = []
        # 添加第一个章节前的内容（如果有）
        if chapter_positions and chapter_positions[0][0] > 0:
            chunks.append(text[:chapter_positions[0][0]])
        
        # 添加所有章节内容
        for i in range(len(chapter_positions)):
            start, end, title = chapter_positions[i]
            # 确定下一个章节的起始位置，如果是最后一个章节则到文本末尾
            next_start = chapter_positions[i+1][0] if i+1 < len(chapter_positions) else len(text)
            
            # 根据keep_separator决定是否保留章节标题
            chunk_start = start if self.keep_separator else end
            chunks.append(text[chunk_start:next_start])
        
        return chunks
    

# 创建自定义章节文本分割器实例
text_splitter = ChapterTextSplitter()

# 分割文本
chunks = text_splitter.split_text(text)

# 打印分割后的段落数量
print(f"分割的段落数：{len(chunks)}")

# 遍历并打印每个分割块的内容
for i, chunk in enumerate(chunks):
    print(f"====块{i+1}：=====")
    print(chunk)