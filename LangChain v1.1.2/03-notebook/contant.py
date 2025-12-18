# LangChain 全局常量配置

# OpenAI 模型配置
OPENAI_MODEL = "gpt-4.1-nano"

# 为了兼容性，提供别名
open_model = OPENAI_MODEL


# 添加能够打印任何对象的json美化print方法
import json
from datetime import datetime

def pretty_print(obj, title=None):
    """美化打印任何对象为JSON格式
    
    Args:
        obj: 要打印的对象
        title: 可选的标题
    """
    def json_serializer(obj):
        """处理不可序列化的对象"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        elif hasattr(obj, 'model_dump'):
            return obj.model_dump()
        else:
            return str(obj)
    
    if title:
        print(f"\n {title}")
        print("=" * (len(title) + 4))
    
    try:
        pretty_json = json.dumps(obj, indent=2, ensure_ascii=False, default=json_serializer)
        print(pretty_json)
    except Exception as e:
        print(f"  序列化失败: {e}")
        print(f"原始对象: {obj}")
    
    if title:
        print("=" * (len(title) + 4))

# 添加简化的别名
print_json = pretty_print

# LangChain Agent 结果打印方法
def print_last_message(result, title=None):
    """打印Agent结果的最后一条消息
    
    Args:
        result: Agent invoke 的返回结果
        title: 可选的标题
    """
    try:
        if isinstance(result, dict) and 'messages' in result:
            last_message = result['messages'][-1]
            content = last_message.content
            
            if title:
                print(f"\n{title}")
                print("=" * (len(title) + 4))
            
            print(f"Agent: {content}")
            
            if title:
                print("=" * (len(title) + 4))
        else:
            print("⚠️  结果格式不正确，需要包含 'messages' 字段")
            pretty_print(result, "原始结果")
    except Exception as e:
        print(f"⚠️  打印失败: {e}")
        pretty_print(result, "错误结果")

print(f"已加载全局配置")

print("\n🎯 模型常量:")
print("  OPENAI_MODEL, open_model")

print("\n🎨 打印方法:")
print("  pretty_print, print_json")
print("  print_agent")
