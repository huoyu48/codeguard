import ast
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import get_settings

settings = get_settings()


@tool
def check_docstrings(code: str) -> str:
    """检查代码中缺少 docstring 的公共函数和类。当需要评估代码文档完整性时使用。"""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"代码存在语法错误（{e}），无法检查 docstring"
    missing = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            if not ast.get_docstring(node):
                missing.append(f"{type(node).__name__}: {node.name} (第{node.lineno}行)")
    if not missing:
        return "所有公共函数和类都有 docstring ✓"
    return "缺少 docstring 的定义：\n" + "\n".join(f"  - {m}" for m in missing)


@tool
def check_naming_conventions(code: str) -> str:
    """检查变量和函数命名是否符合 Python 规范（snake_case）。当需要评估代码命名规范时使用。"""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return "代码存在语法错误，无法检查命名规范"
    issues = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name != node.name.lower() and not node.name.startswith("_"):
                issues.append(f"函数 {node.name} 建议使用 snake_case 命名")
    return "\n".join(issues) if issues else "命名规范 ✓"


doc_llm = ChatOpenAI(
    model=settings.deepseek_model,
    temperature=0.2,
    openai_api_key=settings.deepseek_api_key,  # type: ignore
    openai_api_base=settings.deepseek_base_url,  # type: ignore
)

DOC_PROMPT = """你是一个代码文档和可读性专家。你的任务是审查代码的文档质量和可读性。

重点关注：
1. 函数和类是否有清晰的 docstring
2. 命名是否规范、有表达力
3. 复杂逻辑是否有注释说明
4. 代码整体可读性

给出具体改进建议，附上行号。
"""


def review_docs(diff_content: str) -> str:
    """对一段代码 diff 执行文档与可读性审查"""
    docstring_result = check_docstrings.invoke({"code": diff_content})
    naming_result = check_naming_conventions.invoke({"code": diff_content})

    messages = [
        SystemMessage(content=DOC_PROMPT),
        HumanMessage(content=f"工具检测结果：\n{docstring_result}\n{naming_result}\n\n请审查以下代码变更的文档和可读性：\n\n```python\n{diff_content}\n```"),
    ]

    response = doc_llm.invoke(messages)
    return response.content
