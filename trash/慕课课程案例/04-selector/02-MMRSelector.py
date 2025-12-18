# 导入LangChain社区的FAISS向量数据库
from langchain_community.vectorstores import FAISS
# 导入LangChain核心的示例选择器类
from langchain_core.example_selectors import LengthBasedExampleSelector, MaxMarginalRelevanceExampleSelector
# 导入LangChain核心的提示词模板类
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
# 导入HuggingFace的嵌入模型
from langchain_huggingface import HuggingFaceEmbeddings
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv
# 导入LangChain的OpenAI聊天模型
from langchain_openai import ChatOpenAI

# 从.env文件加载环境变量
load_dotenv()

# 示例数据 ,模拟数据库存放的数据
# 每个示例包含id和特征描述
examples = [
    {"id": "1", "features": ', '.join(["时尚", "运动鞋", "跑步"])},
    {"id": "2", "features": ', '.join(["休闲", "运动鞋", "篮球"])},
    {"id": "3", "features": ', '.join(["商务", "皮鞋", "正装"])},
    {"id": "4", "features": ', '.join(["户外", "徒步鞋", "探险"])},
    {"id": "5", "features": ', '.join(["时尚", "板鞋", "滑板"])},
    {"id": "6", "features": ', '.join(["咖啡厅", "商务餐", "包厢"])},
]

# 创建示例格式化模板
example_prompt = PromptTemplate(
    input_variables=["id", "features"],
    template="id: {id}\n描述: {features}",
)

# 设置HuggingFace嵌入模型路径
embeddings_path = "D:/HuggingFace/bge-large-zh-v1.5"
# 创建嵌入模型实例
embeddings = HuggingFaceEmbeddings(model_name=embeddings_path)

# 调用MMR（最大边际相关性）示例选择器
# MaxMarginalRelevanceExampleSelector: 基于向量相似度和多样性的示例选择器
example_selector = MaxMarginalRelevanceExampleSelector.from_examples(
    # 传入示例组
    examples,
    # 使用HuggingFace上的模型
    embeddings,
    # 设置使用的向量数据库是什么
    FAISS,
    # 结果条数
    k=3,
)

# 使用少样本prompt模板
dynamic_prompt = FewShotPromptTemplate(
    # 我们提供一个ExampleSelector而不是示例。
    example_selector=example_selector,
    example_prompt=example_prompt,
    prefix="查询和描述相似度最高的id，不需要输出其他信息，只需要输出id",
    suffix="关键词为：{word}",
    input_variables=["word"],
)

# 示例：输入关键词，选择最相关的例子
prompt = dynamic_prompt.format(word="签合同")
print(prompt)

print("===============")

# 创建模型实例并生成回复
model = ChatOpenAI(model="gpt-4o", temperature=0)
res = model.invoke(prompt)
print(res)