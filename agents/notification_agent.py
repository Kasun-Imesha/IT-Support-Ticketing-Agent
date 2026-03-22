from autogen import AssistantAgent

from utils.llm_config import llm_config
from utils.prompts import notification_agent_prompt


def get_notification_agent():
    return AssistantAgent(
        name="NotificationAgent",
        system_message=notification_agent_prompt,
        llm_config=llm_config,
    )