import ast
import re
from langchain_core.tools import tool


@tool
def analyze_code_structure(code: str) -> str:
    """分析 Python 代码结构，提取类、函数、导入信息。
    当需要了解代码的整体组织和模块划分时使用。"""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"代码存在语法错误（{e}），无法进行结构分析，将基于文本审查"
    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    functions = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    imports = [
        n.names[0].name
        for n in ast.walk(tree)
        if isinstance(n, ast.Import)
    ]
    return f"Classes: {classes}\nFunctions: {functions}\nImports: {imports}"


@tool
def scan_security_issues(code: str) -> str:
    """扫描代码中的安全隐患（eval/exec 调用、硬编码密钥、SQL 拼接等）。
    当需要检查代码安全性时使用。"""
    patterns = {
        "eval() 调用": r"\beval\s*\(",
        "exec() 调用": r"\bexec\s*\(",
        "硬编码密钥": r'(password|secret|api_key)\s*=\s*["\']',
        "SQL 拼接": r'(execute|cursor)\s*\(.*%s|f".*SELECT',
    }
    issues = []
    for name, pattern in patterns.items():
        if re.search(pattern, code):
            issues.append(f"[安全] 发现 {name}")
    return "\n".join(issues) if issues else "未发现安全隐患"


@tool
def calculate_complexity(code: str) -> str:
    """计算代码的圈复杂度（分支数量）。
    当需要评估代码是否需要重构时使用。圈复杂度 > 10 建议重构。"""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return "代码存在语法错误，无法计算圈复杂度"
    complexity = 1
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
            complexity += 1
    level = "低" if complexity <= 5 else "中" if complexity <= 10 else "高（建议重构）"
    return f"圈复杂度: {complexity} ({level})"