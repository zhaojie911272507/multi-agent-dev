import subprocess

# 示例：通过管道连接 "ls" 和 "grep .txt"（查找当前目录下的txt文件）
# 进程1：执行 ls，输出到管道
ls_process = subprocess.Popen(["ls"], stdout=subprocess.PIPE)
# 进程2：从管道读取输入，执行 grep .txt
grep_process = subprocess.Popen(
    ["grep", ".txt"],
    stdin=ls_process.stdout,  # 连接到 ls 的输出
    stdout=subprocess.PIPE,
    text=True  # 输出为字符串（而非字节）
)

# 获取最终结果
output, _ = grep_process.communicate()
print("TXT files:")
print(output)

# 这种管道本质是操作系统提供的进程间通信机制，Python 只是通过 API 调用封装了这一功能
