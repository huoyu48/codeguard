import ast
from langchain_core.tools import tool
from app.config import get_settings

settings = get_settings()
#文档审查专属工具
@tool
def check_docstrings(code: str)->str:
    """检查代码中缺少docstring的公共函数和类。当需要评估代码文档完整性时使用。"""
    tree = ast.parse(code)
    missing = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if not ast.get_docstring(node):
                missing.append(f"{type(node).__name__}: {node.name} (第{node.lineno}行)")
    if not missing:
        return "所有公共函数和类都有 docstring ✓"
    return f"缺少 docstring 的定义：\n" + "\n".join(f"  - {m}" for m in missing)


@tool
def check_naming_conventions(code: str)->str:
    """检查变量和函数命名是否符合python规范（snake_case）。当需要评估代码命名规范时使用。"""
    tree = ast.parse(code)
    issues = []
    for node in ast.walk(tree):
        if isinstance(node,ast.FunctionDef):
            #函数名应该小写加下划线
            if node.name != node.name.lower() and not node.name.startswith("_"):
                issues.append(f"函数 {node.name} 建议使用 snake_case 命名")
    return "\n".join(issues) if issues else "命名规范 ✓"


doc_tools = [check_docstrings, check_naming_conventions]

# doc_llm 和 DOC_PROMPT 的创建方式与 security_scanner.py 类似
DOC_PROMPT = """你是一个代码文档和可读性专家。你的任务是审查代码的文档质量和可读性。

重点关注：
1. 函数和类是否有清晰的 docstring
2. 命名是否规范、有表达力
3. 复杂逻辑是否有注释说明
4. 代码整体可读性

给出具体改进建议，附上行号。
"""