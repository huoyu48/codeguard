from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from app.config import get_settings
import re

settings = get_settings()

# 安全专属工具
@tool
def check_injection_risks(code: str) -> str:
    """检查代码中的注入风险（SQL注入、命令注入、XSS等）。
    当需要评估代码是否存在注入漏洞时使用。"""
    patterns = {
        "SQL 字符串拼接": r'f["\'].*SELECT.*\{',
        "os.system 调用": r'os\.system\s*\(',
        "subshell 执行": r'`.*`|os\.popen\s*\(',
        "未转义的用户输入": r'request\.(args|form|data)',
    }
    risks = []
    for name, pattern in patterns.items():
        if re.search(pattern, code):
            risks.append(f"[注入风险] {name}")
    return "\n".join(risks) if risks else "未发现注入风险"


security_tools = [check_injection_risks]

security_llm = ChatOpenAI(
    model=settings.deepseek_model,
    temperature=0.1,  # 安全扫描需要更高的确定性
    openai_api_key=settings.deepseek_api_key,  # type: ignore
    openai_api_base=settings.deepseek_base_url,  # type: ignore
).bind_tools(security_tools)

SECURITY_PROMPT = """你是一个应用安全专家。你的任务是审查代码变更中的安全隐患。

重点关注：
1. 注入漏洞（SQL注入、命令注入、XSS）
2. 认证和授权缺陷
3. 敏感数据泄露
4. 不安全的依赖使用

对每个发现标注风险等级：高/中/低，并给出修复建议。
"""


from typing import TypedDict


class AgentState(TypedDict):
    messages: list


def reviewer(state: AgentState):
    """安全审查节点"""
    response = security_llm.invoke(state["messages"])
    return {"messages": state["messages"] + [response]}


def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


def build_security_pipeline():
    graph = StateGraph(AgentState)
    graph.add_node("reviewer", reviewer)
    graph.add_node("tools", ToolNode(security_tools))
    graph.set_entry_point("reviewer")
    graph.add_conditional_edges(
        "reviewer", should_continue, {"tools": "tools", END: END}
    )
    graph.add_edge("tools", "reviewer")
    return graph.compile()


def scan_security(diff_content: str) -> str:
    """对一段代码 diff 执行安全审查，返回安全审查报告"""
    pipeline = build_security_pipeline()
    messages = [
        SystemMessage(content=SECURITY_PROMPT),
        HumanMessage(content=f"请审查以下代码变更中的安全隐患：\n\n```python\n{diff_content}\n```"),
    ]
    result = pipeline.invoke({"messages": messages})
    return result["messages"][-1].content