from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.agent.tools import analyze_code_structure, scan_security_issues, calculate_complexity
from app.config import get_settings

settings = get_settings()

llm = ChatOpenAI(
    model=settings.deepseek_model,
    temperature=0.2,
    openai_api_key=settings.deepseek_api_key,  # type: ignore
    openai_api_base=settings.deepseek_base_url,  # type: ignore
)

CODE_REVIEWER_PROMPT = """你是一个资深 Python 代码审查专家。你的任务是审查代码变更（diff），找出其中的问题并给出改进建议。

审查时请关注以下方面：
1. 代码质量和可读性
2. 潜在的 Bug 和逻辑错误
3. 性能问题
4. 是否遵循 Python 最佳实践

报告格式：
## 审查总结
（一段话概括整体情况）

## 发现的问题
- [严重] / [建议] / [信息] 问题描述 + 修改建议

## 亮点
（代码中做得好的地方）
"""


def review_code(diff_content: str) -> str:
    """对一段代码 diff 执行审查，返回审查报告"""
    # 1. 预跑工具，收集分析结果
    structure = analyze_code_structure.invoke({"code": diff_content})
    security = scan_security_issues.invoke({"code": diff_content})
    complexity = calculate_complexity.invoke({"code": diff_content})

    analysis = f"""工具分析结果：
- 代码结构：{structure}
- 安全扫描：{security}
- 圈复杂度：{complexity}"""

    # 2. 把分析结果 + 代码一起发给 LLM
    messages = [
        SystemMessage(content=CODE_REVIEWER_PROMPT),
        HumanMessage(content=f"{analysis}\n\n请审查以下代码变更：\n\n```python\n{diff_content}\n```"),
    ]

    # 3. LLM 直接生成报告
    response = llm.invoke(messages)
    return response.content