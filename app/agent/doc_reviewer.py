import ast
from typing import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
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

DOC_PROMPT = """你是一个代码文档和可读性专家。你的任务是审查代码的文档质量和可读性。

重点关注：
1. 函数和类是否有清晰的 docstring
2. 命名是否规范、有表达力
3. 复杂逻辑是否有注释说明
4. 代码整体可读性

给出具体改进建议，附上行号。
"""

doc_llm = ChatOpenAI(
    model=settings.deepseek_model,
    temperature=0.2,
    openai_api_key=settings.deepseek_api_key,  # type: ignore
    openai_api_base=settings.deepseek_base_url,  # type: ignore
).bind_tools(doc_tools)


class AgentState(TypedDict):
    messages: list


def reviewer(state: AgentState):
    """文档审查节点"""
    response = doc_llm.invoke(state["messages"])
    return {"messages": state["messages"] + [response]}


def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


def build_doc_pipeline():
    graph = StateGraph(AgentState)
    graph.add_node("reviewer", reviewer)
    graph.add_node("tools", ToolNode(doc_tools))
    graph.set_entry_point("reviewer")
    graph.add_conditional_edges(
        "reviewer", should_continue, {"tools": "tools", END: END}
    )
    graph.add_edge("tools", "reviewer")
    return graph.compile()


def review_docs(diff_content: str) -> str:
    """对一段代码 diff 执行文档与可读性审查"""
    pipeline = build_doc_pipeline()
    messages = [
        SystemMessage(content=DOC_PROMPT),
        HumanMessage(content=f"请审查以下代码变更的文档和可读性：\n\n```python\n{diff_content}\n```"),
    ]
    result = pipeline.invoke({"messages": messages})
    return result["messages"][-1].content