import random

from langchain_core.tools import tool

from rag.rag_service import RagSummarizeService


_rag_service = None
user_ids = ["01", "02", "03", "04"]
month_arr = ["2026-01", "2026-02", "2026-03", "2026-04"]


def get_rag_service() -> RagSummarizeService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RagSummarizeService()
    return _rag_service


@tool(description="从向量知识库中检索参考资料，并基于资料回答用户问题。输入为用户问题，输出为回答文本。")
def rag_summarize(query: str) -> str:
    return get_rag_service().rag_summarize(query)


@tool(description="获取指定城市的天气。当前为 mock 工具，输入城市名称，输出模拟天气文本。")
def get_weather(city: str) -> str:
    return f"城市 {city} 的天气为晴天。"


@tool(description="获取当前用户 ID。当前为 mock 工具，输出模拟用户 ID 字符串。")
def get_user_id() -> str:
    return random.choice(user_ids)


@tool(description="获取当前月份。当前为 mock 工具，输出 YYYY-MM 格式的模拟月份。")
def get_current_month() -> str:
    return random.choice(month_arr)
