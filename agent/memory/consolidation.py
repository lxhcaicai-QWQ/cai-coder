import os

from langchain_openai import ChatOpenAI

from agent.memory.manager import MemoryManager
from agent.memory.templates import CONSOLIDATION_PROMPT, WEEKLY_TEMPLATE, MONTHLY_TEMPLATE
from agent.utils.logger import get_logger

log = get_logger("memory_consolidation")


def consolidate_weekly(memory_manager: MemoryManager) -> None:
    """Read recent L1 logs, distill into this-week.md."""
    recent_logs = memory_manager.read_recent_logs(days=7)
    if not recent_logs.strip():
        log.info("No recent L1 logs to consolidate for weekly memory.")
        return

    existing_weekly = memory_manager.read_this_week()
    prompt = CONSOLIDATION_PROMPT.format(
        layer="weekly",
        template=WEEKLY_TEMPLATE,
        existing=existing_weekly or "(empty)",
        logs=recent_logs,
    )
    new_content = _call_llm_for_consolidation(prompt)
    memory_manager.write_this_week(new_content)
    log.info("Weekly memory consolidated.")


def consolidate_monthly(memory_manager: MemoryManager) -> None:
    """Read L2 weekly + recent L1 logs, distill into this-month.md."""
    recent_logs = memory_manager.read_recent_logs(days=30)
    existing_monthly = memory_manager.read_this_month()
    existing_weekly = memory_manager.read_this_week()

    combined_logs = (
        f"=== WEEKLY ===\n{existing_weekly}\n\n"
        f"=== RAW LOGS ===\n{recent_logs}"
    )
    prompt = CONSOLIDATION_PROMPT.format(
        layer="monthly",
        template=MONTHLY_TEMPLATE,
        existing=existing_monthly or "(empty)",
        logs=combined_logs,
    )
    new_content = _call_llm_for_consolidation(prompt)
    memory_manager.write_this_month(new_content)
    log.info("Monthly memory consolidated.")


def _call_llm_for_consolidation(prompt: str) -> str:
    """Use LLM to generate consolidated memory content."""
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.3,
    )
    response = llm.invoke([{"role": "user", "content": prompt}])
    return response.content