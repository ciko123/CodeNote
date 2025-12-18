# LangChain 全局常量配置

# OpenAI 模型配置
OPENAI_MODEL = "gpt-4.1-nano"

# 为了兼容性，提供别名
open_model = OPENAI_MODEL

# 其他常用模型选项
MODEL_OPTIONS = {
    "fastest": "gpt-4.1-nano",
    "balanced": "gpt-4o-mini", 
    "standard": "gpt-4o",
    "advanced": "gpt-5-nano"
}

def get_model(model_type="default"):
    """获取指定类型的模型
    
    Args:
        model_type: 模型类型 (default, fastest, balanced, standard, advanced)
    
    Returns:
        str: 模型名称
    """
    if model_type == "default":
        return OPENAI_MODEL
    return MODEL_OPTIONS.get(model_type, OPENAI_MODEL)

print(f"✅ 已加载全局配置，默认模型: {open_model}")