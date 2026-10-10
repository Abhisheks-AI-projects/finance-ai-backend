from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from app.core.config import settings
from langchain.agents import create_agent

from core_brain.prompts.finance_prompt import FINANCE_SYSTEM_PROMPT, TITLE_GENERATION_PROMPT
from core_brain.tools.transaction_tool import make_transaction_tools

model = init_chat_model(
    "qwen/qwen3.8-27b",
    model_provider="groq",
    api_key=settings.groq_api_key,
    temperature=0,
)


async def chat_with_finance_agent(messages: list, user_id: str):
    agent = create_agent(
        model=model,
        tools=make_transaction_tools(user_id),
    )
    async for event in agent.astream_events({"messages": messages}, version="v2"):
        if event["event"] == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                yield content

async def generate_thread_title_agent(user_message: str) -> str:
    prompt = [
        SystemMessage(content=TITLE_GENERATION_PROMPT),
        HumanMessage(content=user_message),
    ]
    response = await model.ainvoke(prompt)
    return response.content.strip().strip('"\'')

