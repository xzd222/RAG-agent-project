from langchain.agents import create_agent

from agent.tools.agent_tools import (
    get_current_month,
    get_user_id,
    get_weather,
    rag_summarize,
)
from model.factory import chat_model
from utils.prompt_loader import load_system_prompts


class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model=chat_model,
            system_prompt=load_system_prompts(),
            tools=[get_current_month, get_user_id, get_weather, rag_summarize],
            middleware=(),
        )

    def execute_stream(self, query: str):
        input_dict = {
            "messages": [
                {"role": "user", "content": query}
            ]
        }
        for chunk in self.agent.stream(input_dict, stream_mode="values"):
            latest_message = chunk["messages"][-1]
            if latest_message.content:
                yield latest_message.content.strip() + "\n"
