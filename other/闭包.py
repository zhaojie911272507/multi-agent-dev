def outer_function(message):
    # 外部函数
    def inner_function():
        # 内嵌函数（闭包）
        print(message)  # 捕获外部函数的变量

    return inner_function  # 返回内嵌函数引用


# 创建闭包实例
closure1 = outer_function("你好，闭包！")
closure2 = outer_function("另一个闭包示例")

# 调用闭包函数
closure1()  # 输出：你好，闭包！
closure2()  # 输出：另一个闭包示例


# 闭包实际应用示例 - 计数器
def create_counter():
    count = 0  # 自由变量

    def counter():
        nonlocal count  # 声明非局部变量
        count += 1
        return count

    return counter


# 测试计数器闭包
counter1 = create_counter()
counter2 = create_counter()

print(counter1())  # 输出：1
print(counter1())  # 输出：2
print(counter2())  # 输出：1 (独立的计数器)
print(counter1())  # 输出：3
