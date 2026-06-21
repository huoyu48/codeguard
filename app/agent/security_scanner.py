from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import get_settings
import re

settings = get_settings()


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


security_llm = ChatOpenAI(
    model=settings.deepseek_model,
    temperature=0.1,
    openai_api_key=settings.deepseek_api_key,  # type: ignore
    openai_api_base=settings.deepseek_base_url,  # type: ignore
)

SECURITY_PROMPT = """你是一个应用安全专家。你的任务是审查代码变更中的安全隐患。

重点关注：
1. 注入漏洞（SQL注入、命令注入、XSS）
2. 认证和授权缺陷
3. 敏感数据泄露
4. 不安全的依赖使用

对每个发现标注风险等级：高/中/低，并给出修复建议。
"""


def scan_security(diff_content: str) -> str:
    """对一段代码 diff 执行安全审查，返回安全审查报告"""
    # 预跑安全检测工具
    injection_result = check_injection_risks.invoke({"code": diff_content})

    messages = [
        SystemMessage(content=SECURITY_PROMPT),
        HumanMessage(content=f"工具检测结果：\n{injection_result}\n\n请审查以下代码变更中的安全隐患：\n\n```python\n{diff_content}\n```"),
    ]

    response = security_llm.invoke(messages)
    return response.content
