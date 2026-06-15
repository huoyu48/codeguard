from typing import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from app.agent.tools import (
    analyze_code_structure,
    scan_security_issues,
    calculate_complexity,
)
from app.config import get_settings

settings = get_settings()

tools = [analyze_code_structure, scan_security_issues, calculate_complexity]

llm = ChatOpenAI(
    model=settings.deepseek_model,
    temperature=0.2,
    openai_api_key=settings.deepseek_api_key,  # type: ignore
    openai_api_base=settings.deepseek_base_url,  # type: ignore
).bind_tools(tools)


class AgentState(TypedDict):
    messages: list


def reviewer(state: AgentState):
    """Agent 推理节点：思考下一步该做什么"""
    response = llm.invoke(state["messages"])
    return {"messages": state["messages"] + [response]}


def should_continue(state: AgentState):
    """条件边：Agent 是否还需要调用工具"""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END


def build_review_pipeline():
    """构建 Agent 审查流水线"""
    graph = StateGraph(AgentState)
    graph.add_node("reviewer", reviewer)
    graph.add_node("tools", ToolNode(tools))
    graph.set_entry_point("reviewer")
    graph.add_conditional_edges(
        "reviewer", should_continue, {"tools": "tools", END: END}
    )
    graph.add_edge("tools", "reviewer")  # 工具执行完回到 reviewer 继续思考
    return graph.compile()