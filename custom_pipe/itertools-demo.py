import itertools

# 生成器1：读取文件行
def read_lines(file_path):
    with open(file_path, "r") as f:
        for line in f:
            yield line.strip()  # 逐行输出

# 生成器2：过滤空行
def filter_empty(lines):
    for line in lines:
        if line:
            yield line

# 生成器3：统计每行长度
def count_length(lines):
    for line in lines:
        yield (line, len(line))


# 构建管道：read_lines → filter_empty → count_length
file_path = "data.txt"
# 添加自定义的pipe函数
def pipe(input_data, *funcs):
    for func in funcs:
        input_data = func(input_data)
    return input_data

# 修改管道构建部分
pipeline = pipe(
    read_lines(file_path),
    filter_empty,
    count_length
)


# pipeline = itertools.pipe(
#     read_lines(file_path),
#     filter_empty,
#     count_length
# )

# 执行管道（惰性计算，仅在迭代时处理）
for line, length in pipeline:
    print(f"Line: {line}, Length: {length}")