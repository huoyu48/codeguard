"""示例：一段故意写得很差的代码，用于测试 CodeGuard 的审查能力"""
import os
import sqlite3

password = "admin123"  # 硬编码密码

def process_user_input(user_input):
    # SQL 注入风险
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE name = '" + user_input + "'"
    cursor.execute(query)
    return cursor.fetchall()

def run_command(cmd):
    # 命令注入风险
    os.system("echo " + cmd)

def calc(items):
    t = 0
    for i in range(len(items)):
        t = t + items[i]
    return t / len(items)  # 零除风险

# 使用 eval
def dynamic_exec(code_str):
    return eval(code_str)

if __name__ == "__main__":
    result = process_user_input("test")
    print(result)
    run_command("hello world")
    print(calc([]))
    dynamic_exec("print('hello')")

# TODO: 需要重构这段代码
