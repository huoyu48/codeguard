from langchain_core.messages import HumanMessage, SystemMessage
from app.agent.pipeline import build_review_pipeline

# System Prompt：给 AI 设定角色
CODE_REVIEWER_PROMPT = """你是一个资深 Python 代码审查专家。你的任务是审查代码变更（diff），找出其中的问题并给出改进建议。

审查时请关注以下方面：
1. 代码质量和可读性
2. 潜在的 Bug 和逻辑错误
3. 性能问题
4. 是否遵循 Python 最佳实践

请使用提供的工具分析代码结构和安全问题，然后输出结构化的审查报告。

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
    pipeline = build_review_pipeline()

    messages = [
        SystemMessage(content=CODE_REVIEWER_PROMPT),
        HumanMessage(content=f"请审查以下代码变更：\n\n```python\n{diff_content}\n```"),
    ]

    result = pipeline.invoke({"messages": messages})

    # 取最后一条消息作为审查结论
    last_message = result["messages"][-1]
    return last_message.content