import os
from autogen import UserProxyAgent, GroupChat, GroupChatManager

from utils.llm_config import llm_config
from tools.send_email import escalate_with_email
from agents.classifier_agent import get_classifier_agent
from agents.notification_agent import get_notification_agent
from agents.knowledge_base_agent import get_knowledge_base_agent


def is_termination_msg(msg):
    return isinstance(msg, dict) and msg.get("content", "").strip().upper() == "TERMINATE"
clf_agent = get_classifier_agent()
kb_agent = get_knowledge_base_agent()
notification_agent = get_notification_agent()

## registering tool
# notification_agent.register_for_llm(
#     name="escalate_with_email",
#     description="Escalates an issue by sending an email",
# )(escalate_with_email)

## Bind this manually to the agent
## This bypasses the LLM entirely — it hardwires the agent's reply logic so that every single message unconditionally calls escalate_with_email
notification_agent.generate_reply = lambda messages, sender: escalate_with_email(issue=messages[0]["content"])

user_agent = UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    code_execution_config=False,
    is_termination_msg=is_termination_msg,
)

# In AutoGen, GroupChat maintains the full message history between agents. 
# The messages=[] parameter initializes that history
group_chat = GroupChat(
    agents=[user_agent, clf_agent, kb_agent],
    messages=[],
    speaker_selection_method="auto",
    allow_repeat_speaker=False,
    max_round=6,
)
chat_manager_agent = GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config,
    is_termination_msg=is_termination_msg,
)


if __name__ == "__main__":
    user_agent.initiate_chat(
        recipient=chat_manager_agent,
        # message="Please help me resolve, my laptop is not turning on"
        message="I cannot connect to my wifi"
    )