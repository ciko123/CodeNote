# 自定义表达式基类，用于实现类似LCEL的管道操作
class Expression:
    """表达式基类，所有组件都继承自此类"""
    def __init__(self, func):
        # 初始化时传入函数对象
        self.func = func
        
    def __call__(self, value):
        # 使对象可调用，直接调用内部函数
        return self.func(value)
    
    def __or__(self, other):
        """重载 | 运算符，返回一个新的串联表达式"""
        # lambda x: other(self(x)) 创建新的函数，先执行self(x)，然后将结果传递给other
        return Expression(lambda x: other(self(x)))
    
# 定义字符串处理函数
def upper(s):
    # 将字符串转换为大写
    return s.upper()

def lower(s):
    # 将字符串转换为小写
    return s.lower()

def reverse(s):
    # 反转字符串
    return s[::-1]

# 将普通函数包装为表达式对象
Upper = Expression(upper)
Lower = Expression(lower)
Reverse = Expression(reverse)

# 使用管道操作符组合表达式
# Upper | Reverse | Lower: 先转换为大写，然后反转，最后转换为小写
result =  Upper | Reverse | Lower

# 调用组合表达式并传入测试字符串
print(result("hello world"))