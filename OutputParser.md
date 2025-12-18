完美！我已经收集到足够的最新 API 文档。现在为你创建一份完整的教学文档。

---

# LangChain OutputParser 完整教学文档

## 目录

1. [概述](#概述)
2. [基础概念](#基础概念)
3. [常见解析器类型](#常见解析器类型)
4. [结构化输出 - 新 API](#结构化输出---新-api)
5. [实战示例](#实战示例)
6. [高级特性](#高级特性)
7. [最佳实践](#最佳实践)

---

## 概述

OutputParser（输出解析器）是 LangChain 中用于将 LLM 的原始文本输出转换为**结构化、类型安全的数据**的核心组件。它是构建生产级应用程序的关键，确保 LLM 的输出符合预期的格式和数据类型。

### 为什么需要 OutputParser？

LLM 默认返回自由格式的文本，难以在程序中直接使用。OutputParser 通过以下方式解决这个问题：

- **类型安全**：确保输出符合预定义的数据类型
- **自动验证**：验证数据是否符合模式，失败时自动重试
- **无缝集成**：与 LangChain 的管道（Pipeline）无缝协作
- **减少成本**：避免手动字符串解析和数据清理

---

## 基础概念

### OutputParser 的工作流程

```
LLM Output → Parser → Validated Result
   (string)   (处理)   (结构化对象)
```

### 主要组件

| 组件 | 作用 |
|------|------|
| **输入** | LLM 生成的原始文本响应 |
| **处理逻辑** | 解析和验证逻辑 |
| **输出** | Python 对象（字符串、Pydantic 模型、JSON 等） |

---

## 常见解析器类型

### 1. StrOutputParser（字符串解析器）

最简单的解析器，直接返回 LLM 的字符串输出，不做任何处理。

**安装**：
```bash
pip install langchain langchain-openai
```

**基础示例**：

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. 创建提示模板
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant"),
    ("user", "{input}")
])

# 2. 创建模型
model = ChatOpenAI(model="gpt-4o-mini")

# 3. 创建输出解析器
output_parser = StrOutputParser()

# 4. 组成链（使用 | 操作符）
chain = prompt | model | output_parser

# 5. 调用
result = chain.invoke({"input": "请用中文解释什么是 AI"})
print(result)
# 输出：字符串类型的响应
```

**工作流解析**：
```
input → prompt template → model → output_parser → string
```

---

### 2. 结构化输出解析器

现代 LangChain 推荐使用 `with_structured_output()` 方法，这是最新且最强大的方式。

#### Python 版本

```python
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

# 定义输出数据结构
class MovieInfo(BaseModel):
    """电影信息"""
    title: str = Field(..., description="电影标题")
    year: int = Field(..., description="发布年份")
    director: str = Field(..., description="导演名字")
    rating: float = Field(..., description="评分 (1-10)")

# 创建模型
model = ChatOpenAI(model="gpt-4o")

# 添加结构化输出支持
structured_model = model.with_structured_output(MovieInfo)

# 调用
response = structured_model.invoke("告诉我关于电影《Inception》的信息")
print(response)
# 输出：
# MovieInfo(
#     title='Inception',
#     year=2010,
#     director='Christopher Nolan',
#     rating=8.8
# )
```

#### 获取原始消息和解析结果

有时需要同时获取原始 LLM 响应和解析结果（例如获取 token 计数）：

```python
# 使用 include_raw=True
structured_model = model.with_structured_output(
    MovieInfo, 
    include_raw=True
)

response = structured_model.invoke("告诉我关于电影《Inception》的信息")
print(response)
# 输出：
# {
#     "raw": AIMessage(...),  # 原始 LLM 消息
#     "parsed": MovieInfo(...),  # 解析后的对象
#     "parsing_error": None
# }
```

#### 使用 TypedDict（更轻量级）

如果不需要完整的 Pydantic 验证，可以使用 Python 的 `TypedDict`：

```python
from typing import TypedDict

class MovieInfo(TypedDict):
    title: str
    year: int
    director: str
    rating: float

structured_model = model.with_structured_output(MovieInfo)
response = structured_model.invoke("关于 Inception 的信息")
```

#### JSON Schema（最大兼容性）

```python
movie_schema = {
    "type": "object",
    "description": "电影信息",
    "properties": {
        "title": {
            "type": "string",
            "description": "电影标题"
        },
        "year": {
            "type": "integer",
            "description": "发布年份"
        },
        "director": {
            "type": "string",
            "description": "导演"
        },
        "rating": {
            "type": "number",
            "description": "评分",
            "minimum": 1,
            "maximum": 10
        }
    },
    "required": ["title", "year", "director", "rating"]
}

structured_model = model.with_structured_output(movie_schema)
response = structured_model.invoke("关于 Inception 的信息")
```

---

## 结构化输出 - 新 API

### （v1.0+ 推荐）在 Agents 中使用结构化输出

LangChain v1.0 引入了 `create_agent` 函数，内置结构化输出支持。

#### 基础用法

```python
from langchain import create_agent
from pydantic import BaseModel, Field

# 定义输出模式
class WeatherResponse(BaseModel):
    temperature: float = Field(..., description="温度（摄氏度）")
    condition: str = Field(..., description="天气状况")
    location: str = Field(..., description="位置")

# 创建 Agent（带结构化输出）
agent = create_agent(
    model="gpt-4o-mini",
    tools=[get_weather_tool],
    response_format=WeatherResponse,
    system_prompt="你是一个天气助手"
)

# 调用
result = await agent.ainvoke({
    "messages": [
        {"role": "user", "content": "东京的天气如何？"}
    ]
})

print(result.structured_response)
# 输出：WeatherResponse(temperature=15.5, condition="晴朗", location="东京")
```

#### 使用多个可能的输出格式（Union Types）

```python
from pydantic import BaseModel
from langchain import create_agent

class ProductReview(BaseModel):
    rating: int
    sentiment: str
    key_points: list[str]

class CustomerComplaint(BaseModel):
    issue_type: str
    severity: str
    description: str

agent = create_agent(
    model="gpt-4o",
    tools=[],
    response_format=[ProductReview, CustomerComplaint]
)

result = await agent.ainvoke({
    "messages": [
        {"role": "user", "content": "分析这条反馈：很棒的产品，5 星。快速送货，但很贵。"}
    ]
})

# 根据返回的类型判断
if isinstance(result.structured_response, ProductReview):
    print(f"评分：{result.structured_response.rating}")
elif isinstance(result.structured_response, CustomerComplaint):
    print(f"问题类型：{result.structured_response.issue_type}")
```

---

## 实战示例

### 案例 1：电商产品信息提取

```python
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Optional

# 定义数据模型
class ProductInfo(BaseModel):
    name: str = Field(..., description="产品名称")
    price: float = Field(..., description="价格")
    category: str = Field(..., description="产品类别")
    rating: Optional[float] = Field(default=None, description="用户评分")
    in_stock: bool = Field(..., description="是否有货")

# 创建提示和模型
prompt = ChatPromptTemplate.from_template("""
从以下文本中提取产品信息：
{text}

请以结构化格式返回产品信息。
""")

model = ChatOpenAI(model="gpt-4o-mini")
structured_model = model.with_structured_output(ProductInfo)

# 组成链
chain = prompt | structured_model

# 使用
product_text = """
苹果 iPhone 15 Pro - 价格 $999
类别：智能手机
用户评分：4.8/5
目前有货，可以立即发货
"""

result = chain.invoke({"text": product_text})
print(f"产品名称: {result.name}")
print(f"价格: ${result.price}")
print(f"有货: {'是' if result.in_stock else '否'}")
```

### 案例 2：自动生成测试数据

```python
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from typing import List

class TestCase(BaseModel):
    test_name: str = Field(..., description="测试用例名称")
    input_data: str = Field(..., description="输入数据")
    expected_output: str = Field(..., description="期望的输出")

class TestSuite(BaseModel):
    feature: str = Field(..., description="测试的功能")
    test_cases: List[TestCase] = Field(..., description="测试用例列表")

model = ChatOpenAI(model="gpt-4o-mini")
structured_model = model.with_structured_output(TestSuite)

prompt = """
为登录功能生成 3 个测试用例。
要求：
1. 测试名称明确
2. 输入数据真实
3. 期望的输出清晰
"""

result = structured_model.invoke(prompt)

for test_case in result.test_cases:
    print(f"\n测试：{test_case.test_name}")
    print(f"输入：{test_case.input_data}")
    print(f"期望：{test_case.expected_output}")
```

### 案例 3：文档分类和摘要

```python
from pydantic import BaseModel, Field
from enum import Enum
from langchain_openai import ChatOpenAI

class DocumentType(str, Enum):
    NEWS = "新闻"
    RESEARCH = "学术研究"
    BLOG = "博客"
    TUTORIAL = "教程"

class DocumentAnalysis(BaseModel):
    title: str = Field(..., description="文档标题")
    document_type: DocumentType = Field(..., description="文档类型")
    summary: str = Field(..., description="内容摘要（100 字以内）")
    key_topics: list[str] = Field(..., description="关键主题")
    confidence: float = Field(..., description="分类置信度 (0-1)")

model = ChatOpenAI(model="gpt-4o")
analyzer = model.with_structured_output(DocumentAnalysis)

document = """
机器学习在自然语言处理中的应用
本研究探讨了 Transformer 模型在...
[完整的学术文本]
"""

result = analyzer.invoke(f"分析以下文档：\n{document}")
print(f"类型：{result.document_type.value}")
print(f"置信度：{result.confidence * 100:.1f}%")
print(f"关键主题：{', '.join(result.key_topics)}")
```

---

## 高级特性

### 1. 带验证的自动重试

当 LLM 生成的数据不符合模式时，系统会自动重试：

```python
from pydantic import BaseModel, Field, field_validator

class StrictMovieInfo(BaseModel):
    title: str
    year: int
    rating: float = Field(ge=1, le=10)  # 限制在 1-10 之间
    
    @field_validator('year')
    @classmethod
    def year_must_be_reasonable(cls, v):
        if v < 1800 or v > 2100:
            raise ValueError('年份必须在 1800-2100 之间')
        return v

model = ChatOpenAI(model="gpt-4o")
structured_model = model.with_structured_output(StrictMovieInfo)

# 如果 LLM 返回无效的评分（如 15），模型会自动修正并重试
result = structured_model.invoke("关于《教父》的信息")
```

### 2. 流式输出

```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(model="gpt-4o")
structured_model = model.with_structured_output(MovieInfo)

# 流式输出（部分内容）
for chunk in structured_model.stream("关于《星际穿越》的信息"):
    print(chunk)
```

### 3. 嵌套结构

```python
from pydantic import BaseModel
from typing import List

class Actor(BaseModel):
    name: str
    role: str

class MovieWithCast(BaseModel):
    title: str
    year: int
    main_cast: List[Actor]
    director: str

model = ChatOpenAI(model="gpt-4o")
structured_model = model.with_structured_output(MovieWithCast)

result = structured_model.invoke("列出《复仇者联盟》的主要演员和角色")
print(f"演员数量：{len(result.main_cast)}")
for actor in result.main_cast:
    print(f"  - {actor.name} 饰演 {actor.role}")
```

---

## 最佳实践

### ✅ 推荐做法

**1. 使用 Pydantic 模型定义清晰的模式**

```python
# ✅ 好的做法
from pydantic import BaseModel, Field

class UserProfile(BaseModel):
    """用户档案信息"""
    username: str = Field(..., description="用户名，长度 3-20 字符")
    email: str = Field(..., description="电子邮件地址")
    age: int = Field(..., ge=0, le=150, description="年龄")
    is_active: bool = Field(default=True, description="是否活跃")

# ❌ 避免：使用简单的字典
# response = model.invoke("...")  # 无类型验证
```

**2. 提供详细的 Field 描述**

```python
# ✅ 好的做法
class Article(BaseModel):
    title: str = Field(
        ..., 
        description="文章标题，应简洁且具有描述性，20-100 字符"
    )
    content: str = Field(
        ...,
        description="文章正文，至少 100 字，格式为纯文本"
    )
    category: str = Field(
        ...,
        description="文章分类：技术、商业、生活方式、其他"
    )

# ❌ 避免：模糊的描述
# title: str = Field(..., description="标题")
```

**3. 使用 Enum 处理离散选项**

```python
# ✅ 好的做法
from enum import Enum

class Sentiment(str, Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class ReviewAnalysis(BaseModel):
    sentiment: Sentiment  # 类型安全
    confidence: float = Field(..., ge=0, le=1)

# ❌ 避免：使用字符串作为枚举
# sentiment: str  # 可能收到意外值
```

**4. 设置默认值处理缺失数据**

```python
# ✅ 好的做法
from typing import Optional

class Product(BaseModel):
    name: str
    price: float
    description: Optional[str] = None  # 可选字段
    tags: list[str] = Field(default_factory=list)  # 默认空列表

# ❌ 避免：所有字段都必填
# class Product(BaseModel):
#     name: str
#     description: str  # 如果 LLM 遗漏会失败
```

**5. 添加字段验证器**

```python
# ✅ 好的做法
from pydantic import field_validator

class Event(BaseModel):
    name: str
    start_time: str
    end_time: str
    
    @field_validator('start_time', 'end_time')
    @classmethod
    def validate_time_format(cls, v):
        # 确保时间格式为 HH:MM
        if not isinstance(v, str) or len(v) != 5 or ':' not in v:
            raise ValueError('时间格式必须为 HH:MM')
        return v

# ❌ 避免：不验证输入
# class Event(BaseModel):
#     start_time: str  # 可能是任意格式
```

### ⚠️ 常见陷阱

**陷阱 1：过于复杂的嵌套结构**

```python
# ❌ 过度设计
class VeryComplex(BaseModel):
    level1: Level1
    level2: Level2
    level3: Level3
    # ... 太多层级，LLM 容易出错

# ✅ 简化结构
class Simplified(BaseModel):
    main_info: str
    details: list[str]  # 用列表代替复杂嵌套
```

**陷阱 2：不处理 LLM 的常见错误**

```python
# ❌ 假设 LLM 完美
model.with_structured_output(MySchema)

# ✅ 添加错误处理
try:
    result = model.with_structured_output(MySchema).invoke(prompt)
except Exception as e:
    print(f"解析失败，重试...")
    # 使用更简单的提示重试
```

**陷阱 3：未指定必填字段**

```python
# ❌ 不清楚哪些字段必填
class Config(BaseModel):
    api_key: str
    timeout: int

# ✅ 明确标记
from pydantic import Field

class Config(BaseModel):
    api_key: str = Field(..., description="必填")
    timeout: int = Field(default=30, description="可选，默认 30 秒")
```

### 性能优化建议

**1. 使用 include_raw=True 避免重复调用**

```python
# ✅ 高效做法
result = model.with_structured_output(
    schema,
    include_raw=True
)

structured_data = result.parsed
token_count = result.raw.usage.output_tokens

# ❌ 避免：分别调用两次
# result1 = model.invoke(...)
# result2 = model.with_structured_output(...).invoke(...)
```

**2. 选择合适的模型**

```python
# ✅ 根据复杂度选择
# 简单结构 → gpt-4o-mini (更快、更便宜)
# 复杂结构 → gpt-4o (更准确)

simple_schema = SimpleModel
complex_schema = ComplexModel

simple_model = ChatOpenAI(model="gpt-4o-mini")
complex_model = ChatOpenAI(model="gpt-4o")
```

**3. 缓存通用提示**

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_extraction_chain(schema_name):
    """缓存链的创建"""
    schema = get_schema(schema_name)
    return ChatOpenAI().with_structured_output(schema)

# 后续调用会使用缓存
chain = get_extraction_chain("product_info")
```

---

## 故障排除指南

### 问题 1：ValidationError - 数据不符合模式

**症状**：
```
ValidationError: 1 validation error for MyModel
age
  Input should be a valid integer [type=int_parsing, ...]
```

**解决方案**：
```python
# 1. 检查提示中是否明确指定数据类型
prompt = """
请提取以下信息（年龄必须是整数）：
{text}
"""

# 2. 添加字段验证器
class Person(BaseModel):
    age: int = Field(..., ge=0, le=150)
    
    @field_validator('age', mode='before')
    @classmethod
    def convert_age(cls, v):
        if isinstance(v, str):
            return int(v)
        return v
```

### 问题 2：多个工具调用导致结构化输出失败

**症状**：
```
Error: Model incorrectly returned multiple structured responses
```

**解决方案**：
```python
# 明确指定只能返回一个结构化响应
class SingleResponse(BaseModel):
    result: str

agent = create_agent(
    model="gpt-4o",
    tools=[],  # 不使用工具，或
    response_format=SingleResponse  # 明确指定格式
)
```

### 问题 3：LLM 忽略字段

**症状**：缺少某些字段的值

**解决方案**：
```python
# 1. 在提示中重复强调
prompt = """
请按以下格式提取信息（不要遗漏任何字段）：
- 名称
- 电子邮件（必填）
- 电话（必填）
"""

# 2. 使用 Field 的 description 提示
class Contact(BaseModel):
    name: str = Field(
        ..., 
        description="必须包括，格式为 'FirstName LastName'"
    )
    email: str = Field(
        ...,
        description="必须包括，必须是有效的电子邮件地址"
    )
    phone: str = Field(
        ...,
        description="必须包括，格式为 '+1-555-0000'"
    )
```

### 问题 4：结果与预期格式不一致

**症状**：收到的数据类型错误

**解决方案**：
```python
# 1. 添加类型转换
class StrictData(BaseModel):
    price: float = Field(..., description="价格，必须是数字")
    quantity: int = Field(..., description="数量，必须是整数")
    
    @field_validator('price', mode='before')
    @classmethod
    def parse_price(cls, v):
        if isinstance(v, str):
            return float(v.replace('$', ''))
        return float(v)

# 2. 在提示中给出示例
prompt = """
提取产品信息。示例格式：
- 价格：99.99（数字，不含货币符号）
- 数量：5（整数）
"""
```

---

## 完整工作示例：简历解析系统

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from enum import Enum
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# 定义数据模型
class EducationLevel(str, Enum):
    HIGHSCHOOL = "高中"
    BACHELOR = "本科"
    MASTER = "硕士"
    PHD = "博士"

class Experience(BaseModel):
    company: str = Field(..., description="公司名称")
    position: str = Field(..., description="职位")
    duration_years: float = Field(..., ge=0, le=50, description="工作年限")
    description: str = Field(..., description="工作描述")

class Education(BaseModel):
    school: str = Field(..., description="学校名称")
    degree: EducationLevel = Field(..., description="学位")
    major: str = Field(..., description="专业")
    graduation_year: int = Field(..., ge=1900, le=2100, description="毕业年份")

class ResumeAnalysis(BaseModel):
    """简历分析结果"""
    full_name: str = Field(..., description="全名")
    email: Optional[str] = Field(default=None, description="电子邮件")
    phone: Optional[str] = Field(default=None, description="电话号码")
    education: List[Education] = Field(..., description="教育背景")
    experience: List[Experience] = Field(..., description="工作经验")
    skills: List[str] = Field(..., description="技能列表")
    years_total_experience: float = Field(
        ..., 
        ge=0, 
        description="总工作经验（年）"
    )
    
    @field_validator('years_total_experience', mode='before')
    @classmethod
    def calculate_experience(cls, v, info):
        # 如果未提供，从 experience 字段计算
        if v is None and 'experience' in info.data:
            return sum(exp.duration_years for exp in info.data['experience'])
        return v

# 创建解析器
def create_resume_analyzer():
    model = ChatOpenAI(model="gpt-4o", temperature=0)
    
    prompt = ChatPromptTemplate.from_template("""
    请分析以下简历，并提取所有相关信息。

    简历内容：
    {resume_text}

    请确保：
    1. 包含所有教育背景
    2. 列出所有工作经验及工作年限
    3. 提取所有提到的技能
    4. 计算总工作年限
    """)
    
    analyzer = model.with_structured_output(
        ResumeAnalysis,
        include_raw=True
    )
    
    chain = prompt | analyzer
    return chain

# 使用示例
resume_text = """
约翰·史密斯
邮箱：john.smith@email.com
电话：+1-555-0123

教育背景：
- 斯坦福大学，计算机科学学位（本科），2015 年毕业
- 麻省理工学院，人工智能硕士学位，2017 年毕业

工作经验：
- Google，高级软件工程师（2017-2022），5 年
  领导机器学习团队，开发推荐系统
- Meta，资深研究员（2022-现在），2 年
  研究大规模语言模型

技能：Python、机器学习、深度学习、TensorFlow、PyTorch
"""

analyzer = create_resume_analyzer()
result = analyzer.invoke({"resume_text": resume_text})

# 访问结构化数据
parsed_data = result.parsed
print(f"姓名：{parsed_data.full_name}")
print(f"总经验：{parsed_data.years_total_experience} 年")
print(f"工作岗位：{[exp.position for exp in parsed_data.experience]}")
print(f"技能：{', '.join(parsed_data.skills)}")

# 访问原始响应（用于调试）
raw_response = result.raw
print(f"Token 使用：{raw_response.usage.output_tokens}")
```

**输出示例**：
```
姓名：约翰·史密斯
总经验：7.0 年
工作岗位：['高级软件工程师', '资深研究员']
技能：Python, 机器学习, 深度学习, TensorFlow, PyTorch
Token 使用：185
```

---

## 总结

| 主题 | 要点 |
|------|------|
| **基础** | StrOutputParser 用于简单字符串输出 |
| **推荐方案** | `with_structured_output()` 用于所有结构化数据 |
| **验证** | Pydantic 模型自动验证，失败时 LLM 自动重试 |
| **最佳实践** | 清晰的字段描述、合理的默认值、类型验证 |
| **性能** | 用 include_raw=True 获取元数据，避免多次调用 |
| **调试** | 使用详细的错误消息和字段验证器 |

---

## 参考资源

- [Models and Structured Output](https://docs.langchain.com/oss/python/langchain/models#structured-output)
- [Structured Output in Agents](https://docs.langchain.com/oss/python/langchain/structured-output)
- [Trace with LangChain](https://docs.langchain.com/langsmith/trace-with-langchain)
- [Pydantic Documentation](https://docs.pydantic.dev/)