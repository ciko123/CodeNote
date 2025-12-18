# 导入JSON模块，用于处理JSON格式的数据
import json
# 导入LangChain的OpenAI聊天模型类
from langchain_openai import ChatOpenAI
# 导入LangChain核心的聊天提示模板类
from langchain_core.prompts import ChatPromptTemplate
# 导入LangChain核心的直通运行类，用于数据传递
from langchain_core.runnables import RunnablePassthrough
# 导入LangChain社区的DuckDuckGo搜索API包装器（未使用）
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
# 导入LangChain核心的工具装饰器
from langchain_core.tools import tool
# 导入dotenv用于加载环境变量
from dotenv import load_dotenv
# 从.env文件加载环境变量
load_dotenv()

# 创建天气查询工具
# 第一个参数是工具名称，第二个参数表示解析文档字符串
@tool("get_weather",parse_docstring=True)
def weather_tool(location: str) -> str:
    """获取指定位置的当前天气

    Args:
        location: 地点
    """
    # 返回模拟的天气信息
    return f"在{location}的天气晴朗，温度25°C"

# 导入LangChain社区的Tavily搜索结果工具
from langchain_community.tools import TavilySearchResults

# 创建搜索工具
@tool("tavily_search",parse_docstring=True)
def search_tool(query: str) -> str:
    """用于查询搜索引擎的工具

    Args:
        query: 查询内容
    """
    # 创建Tavily搜索结果实例
    tsr = TavilySearchResults(
        max_results=1,                    # 最大返回结果数
        include_answer=True,              # 包含答案摘要
        include_raw_content=True,         # 包含原始内容
        include_images=False,             # 不包含图片
        include_image_descriptions=False, # 不包含图片描述
    )
    
    # 执行搜索并返回结果
    return tsr.run(query)


# 创建OpenAI聊天模型实例
# temperature: 控制输出随机性，0表示确定性输出
# model: 使用的模型名称
llm = ChatOpenAI(temperature=0, model="gpt-4o")

# 将工具绑定到LLM
# bind_tools(): 将工具列表绑定到LLM，使LLM能够调用这些工具
llm_with_tools = llm.bind_tools([search_tool,weather_tool])

# 创建聊天提示模板
# from_messages(): 从消息列表创建提示模板
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "你是一个有用的AI助手，可以回答问题和提供信息。你可以使用工具来帮助你。"),
    ("human", "{question}")
])



# 定义执行工具的函数
def exec_tools(result):
    """执行LLM返回的工具调用
    
    Args:
        result: LLM的响应结果，包含工具调用信息
        
    Returns:
        str: 工具执行结果
    """
    # 从LLM响应中获取工具调用信息
    tool_calls = result.additional_kwargs.get("tool_calls", [])
    # 遍历所有工具调用
    for call in tool_calls:
        # 检查是否为函数类型的工具调用
        if call["type"] == "function":
            # 获取工具名称和参数
            tool_name = call["function"]["name"]
            tool_args = call["function"]["arguments"]
            print(f"{tool_name} {tool_args}")
             # 如果 tool_args 是字符串，先解析成字典
            if isinstance(tool_args, str):
                tool_args_dict = json.loads(tool_args)
                
            # 根据 tool_name 找到对应的工具并执行
            if tool_name == "tavily_search":
                # 调用搜索工具的底层函数
                tool_response = search_tool.func(**tool_args_dict)
            elif tool_name == "get_weather":
                # 调用天气工具的底层函数
                tool_response = weather_tool.func(**tool_args_dict)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

            print(f"Tool '{tool_name}' returned: {tool_response}")
            return tool_response

# 导入LangChain核心的Lambda运行类
# RunnableLambda: 将函数转换为可运行的组件
from langchain_core.runnables import RunnableLambda
# 将工具执行函数转换为可运行组件
exec_tool_runnable = RunnableLambda(exec_tools)


# 创建完整的链
# 链的执行流程：数据传递 -> 提示模板 -> LLM（带工具） -> 工具执行
chain = (
    {"question": RunnablePassthrough()}  # 将输入数据直接传递
    | prompt_template                     # 应用提示模板
    | llm_with_tools                      # LLM处理并可能调用工具
    | exec_tool_runnable                  # 执行工具调用
)

# 调用链并传入问题
result = chain.invoke({"question": "明天北京天气如何"})